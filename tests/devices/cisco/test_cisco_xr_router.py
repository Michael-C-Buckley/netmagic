# NetMagic Cisco IOS-XR Router Tests

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from netmagic.common.classes import InterfaceStatistics
from netmagic.devices import CiscoIOSXRRouter
from netmagic.devices.vendors.cisco_xr import XR_STATS_NAMESPACE
from netmagic.sessions import NETCONFSession, TerminalSession
from tests.classes.common import MockBaseConnection

NETCONF_KWARGS = {
    "host": "192.0.2.1",
    "username": "admin",
    "password": "password",  # nosec B105
}

XR_XML = f"""
<data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <infra-statistics xmlns="{XR_STATS_NAMESPACE}">
    <interfaces>
      <interface>
        <interface-name>GigabitEthernet0/0/0/0</interface-name>
        <latest>
          <generic-counters>
            <packets-received>100</packets-received>
            <bytes-received>200</bytes-received>
            <packets-sent>300</packets-sent>
            <bytes-sent>400</bytes-sent>
            <broadcast-packets-received>5</broadcast-packets-received>
            <multicast-packets-received>6</multicast-packets-received>
            <broadcast-packets-sent>7</broadcast-packets-sent>
            <multicast-packets-sent>8</multicast-packets-sent>
            <input-drops>0</input-drops>
            <output-drops>9</output-drops>
            <input-errors>10</input-errors>
            <crc-errors>11</crc-errors>
            <framing-errors-received>12</framing-errors-received>
            <input-overruns>13</input-overruns>
            <input-ignored-packets>14</input-ignored-packets>
            <input-aborts>15</input-aborts>
            <output-errors>16</output-errors>
            <output-underruns>17</output-underruns>
          </generic-counters>
          <data-rate>
            <input-data-rate>1</input-data-rate>
            <input-packet-rate>20</input-packet-rate>
            <output-data-rate>3</output-data-rate>
            <output-packet-rate>40</output-packet-rate>
            <load-interval>9</load-interval>
          </data-rate>
        </latest>
      </interface>
    </interfaces>
  </infra-statistics>
</data>
"""

XR_CLI = """
GigabitEthernet0/0/0/0 is up, line protocol is up
  5 minute input rate 1000 bits/sec, 20 packets/sec
  5 minute output rate 3000 bits/sec, 40 packets/sec
     100 packets input, 200 bytes, 0 total input drops
     Received 5 broadcast packets, 6 multicast packets
     10 input errors, 11 CRC, 12 frame, 13 overrun, 14 ignored, 15 abort
     300 packets output, 400 bytes, 9 total output drops
     Output 7 broadcast packets, 8 multicast packets
     16 output errors, 17 underruns, 0 applique, 0 resets
"""


class TestCiscoIOSXRRouter(TestCase):
    def prepare_netconf(self):
        connection = Mock(
            connected=True,
            server_capabilities=[f"{XR_STATS_NAMESPACE}?module=infra-statsd-oper"],
        )
        connection.get.return_value.data_xml = XR_XML
        return NETCONFSession(connection=connection, **NETCONF_KWARGS)

    def test_netconf_statistics_and_filter(self):
        session = self.prepare_netconf()
        router = CiscoIOSXRRouter(session)

        result = router.get_interface_statistics("GigabitEthernet0/0/0/0")

        stats = result.fsm_output["GigabitEthernet0/0/0/0"]
        self.assertIsInstance(stats, InterfaceStatistics)
        self.assertEqual(stats.host, "192.0.2.1")
        self.assertEqual(stats.input_packets, 100)
        self.assertEqual(stats.input_drops, 0)
        self.assertEqual(stats.output_underruns, 17)
        self.assertEqual(stats.input_rate_bps, 1000)
        self.assertEqual(stats.load_interval_seconds, 300)
        rpc_filter = session.connection.get.call_args.kwargs["filter"]
        self.assertEqual(rpc_filter[0], "subtree")
        self.assertIn("GigabitEthernet0/0/0/0", rpc_filter[1])
        self.assertIn("generic-counters", rpc_filter[1])
        self.assertIn("data-rate", rpc_filter[1])

    def test_netconf_is_preferred_and_cli_can_be_explicit(self):
        netconf = self.prepare_netconf()
        terminal = self.prepare_terminal()
        router = CiscoIOSXRRouter([terminal, netconf])

        router.get_interface_statistics()
        self.assertEqual(netconf.connection.get.call_count, 1)

        result = router.get_interface_statistics(session=terminal)
        self.assertEqual(result.fsm_output["GigabitEthernet0/0/0/0"].output_bytes, 400)

    def test_cli_statistics(self):
        terminal = self.prepare_terminal()
        router = CiscoIOSXRRouter(terminal)

        result = router.get_interface_statistics("GigabitEthernet0/0/0/0")

        stats = result.fsm_output["GigabitEthernet0/0/0/0"]
        self.assertEqual(stats.input_multicast_packets, 6)
        self.assertEqual(stats.output_errors, 16)
        self.assertEqual(stats.load_interval_seconds, 300)
        terminal.command.assert_called_with("show interfaces GigabitEthernet0/0/0/0")

    def test_cli_sub_minute_load_interval(self):
        cli_output = XR_CLI.replace("5 minute", "30 second")
        terminal = self.prepare_terminal(cli_output)
        router = CiscoIOSXRRouter(terminal)

        result = router.get_interface_statistics()

        stats = result.fsm_output["GigabitEthernet0/0/0/0"]
        self.assertEqual(stats.load_interval_seconds, 30)

    def test_rejects_unsafe_interface_name(self):
        router = CiscoIOSXRRouter(self.prepare_netconf())
        with self.assertRaises(ValueError):
            router.get_interface_statistics("Gi0/0/0/0 | include password")

    def test_requires_native_capability(self):
        session = self.prepare_netconf()
        session.connection.server_capabilities = []
        router = CiscoIOSXRRouter(session)
        with self.assertRaises(NotImplementedError):
            router.get_interface_statistics()

    @staticmethod
    def prepare_terminal(cli_output=XR_CLI):
        connection = MockBaseConnection()
        connection.device_type = "cisco_xr"
        connection.find_prompt.return_value = "RP/0/RP0/CPU0:XR#"
        terminal = TerminalSession(
            host="192.0.2.1",
            username="admin",
            password="password",  # nosec B106
            device_type="cisco_xr",
            connection=connection,
        )
        now = datetime.now(UTC)
        terminal.command = Mock(
            side_effect=[
                SimpleNamespace(
                    response="hostname XR",
                    success=True,
                    sent_time=now,
                    received_time=now,
                ),
                SimpleNamespace(
                    response="", success=True, sent_time=now, received_time=now
                ),
                SimpleNamespace(
                    response=cli_output,
                    success=True,
                    sent_time=now,
                    received_time=now,
                ),
                SimpleNamespace(
                    response=cli_output,
                    success=True,
                    sent_time=now,
                    received_time=now,
                ),
            ]
        )
        return terminal

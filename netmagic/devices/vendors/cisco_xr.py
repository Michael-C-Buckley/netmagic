# NetMagic Cisco IOS-XR Device Library

# Python Modules
from re import fullmatch

# Third-Party Modules
from defusedxml.ElementTree import fromstring

# Local Modules
from netmagic.common.classes import InterfaceStatistics, ResponseGroup
from netmagic.common.types import Vendors
from netmagic.devices.router import Router
from netmagic.sessions import NETCONFSession, Session, TerminalSession

XR_STATS_NAMESPACE = "http://cisco.com/ns/yang/Cisco-IOS-XR-infra-statsd-oper"


class CiscoIOSXRRouter(Router):
    """Cisco IOS-XR router with normalized interface statistics."""

    def __init__(self, session: Session | list[Session] | tuple[Session, ...]) -> None:
        super().__init__(session)
        self.vendor = Vendors.CISCO
        if self.cli_session:
            self.session_preparation()

    def enable(self, password: str | None = None) -> None:
        """IOS-XR has no IOS-style enable mode."""

    def session_preparation(self, dispatch: str = "cisco_xr") -> None:
        """Prepare an IOS-XR terminal session."""
        super().session_preparation(dispatch)
        self.command("terminal length 0")

    def get_interface_statistics(
        self,
        interface: str | None = None,
        session: Session | None = None,
    ) -> ResponseGroup:
        """Return counters and load-interval rates through either transport."""
        if interface and not fullmatch(r"[A-Za-z][A-Za-z0-9./-]*", interface):
            raise ValueError(f"Invalid IOS-XR interface name: {interface}")

        selected_session = session or self.netconf_session or self.cli_session
        if isinstance(selected_session, NETCONFSession):
            return self._get_interface_statistics_netconf(selected_session, interface)
        if isinstance(selected_session, TerminalSession):
            return self._get_interface_statistics_cli(selected_session, interface)
        raise AttributeError("An IOS-XR NETCONF or terminal session is required")

    def _get_interface_statistics_netconf(
        self,
        session: NETCONFSession,
        interface: str | None,
    ) -> ResponseGroup:
        if not session.check_session() and not session.connect():
            raise AttributeError("Unable to connect the IOS-XR NETCONF session")

        capabilities = getattr(session.connection, "server_capabilities", ())
        if not any(XR_STATS_NAMESPACE in str(item) for item in capabilities):
            raise NotImplementedError(
                "IOS-XR interface statistics YANG model is not advertised"
            )

        interface_filter = (
            f"<interface-name>{interface}</interface-name>" if interface else ""
        )
        filter_xml = (
            f'<infra-statistics xmlns="{XR_STATS_NAMESPACE}"><interfaces><interface>'
            f"{interface_filter}<latest><generic-counters/><data-rate/></latest>"
            "</interface></interfaces></infra-statistics>"
        )
        rpc_filter = ("subtree", filter_xml)
        response = session.get(rpc_filter)

        output: dict[str, InterfaceStatistics] = {}
        if response.success and isinstance(response.response, str):
            output = self._parse_netconf_statistics(response.response, session)
        return ResponseGroup([response], output, "Cisco IOS-XR Interface Statistics")

    def _parse_netconf_statistics(
        self,
        xml: str,
        session: NETCONFSession,
    ) -> dict[str, InterfaceStatistics]:
        field_map = {
            "packets-received": "input_packets",
            "bytes-received": "input_bytes",
            "packets-sent": "output_packets",
            "bytes-sent": "output_bytes",
            "broadcast-packets-received": "input_broadcast_packets",
            "multicast-packets-received": "input_multicast_packets",
            "broadcast-packets-sent": "output_broadcast_packets",
            "multicast-packets-sent": "output_multicast_packets",
            "input-drops": "input_drops",
            "output-drops": "output_drops",
            "input-errors": "input_errors",
            "crc-errors": "crc_errors",
            "framing-errors-received": "framing_errors",
            "input-overruns": "input_overruns",
            "input-ignored-packets": "input_ignored_packets",
            "input-aborts": "input_aborts",
            "output-errors": "output_errors",
            "output-underruns": "output_underruns",
            "input-data-rate": "input_rate_bps",
            "input-packet-rate": "input_rate_pps",
            "output-data-rate": "output_rate_bps",
            "output-packet-rate": "output_rate_pps",
        }

        def local_name(element) -> str:
            return element.tag.rpartition("}")[2]

        def direct_child(element, name: str):
            return next((child for child in element if local_name(child) == name), None)

        output = {}
        document = fromstring(xml)
        for interface_element in document.iter():
            if local_name(interface_element) != "interface":
                continue
            name_element = direct_child(interface_element, "interface-name")
            latest = direct_child(interface_element, "latest")
            if name_element is None or not name_element.text or latest is None:
                continue

            values = {}
            for container_name in ("generic-counters", "data-rate"):
                container = direct_child(latest, container_name)
                if container is None:
                    continue
                for leaf in container:
                    leaf_name = local_name(leaf)
                    if leaf.text is not None and (field := field_map.get(leaf_name)):
                        value = int(leaf.text)
                        if leaf_name in ("input-data-rate", "output-data-rate"):
                            value *= 1000
                        values[field] = value

            data_rate = direct_child(latest, "data-rate")
            interval = (
                direct_child(data_rate, "load-interval")
                if data_rate is not None
                else None
            )
            if interval is not None and interval.text is not None:
                values["load_interval_seconds"] = (int(interval.text) + 1) * 30

            name = name_element.text
            output[name] = InterfaceStatistics(
                host=self.hostname or str(session.host), interface=name, **values
            )
        return output

    def _get_interface_statistics_cli(
        self,
        session: TerminalSession,
        interface: str | None,
    ) -> ResponseGroup:
        command = "show interfaces"
        if interface:
            command = f"{command} {interface}"
        response = session.command(command)
        output = {}
        if response.success and isinstance(response.response, str):
            for entry in self.fsm_parse(response.response, "show_xr_interface_stats"):
                values = {key: value for key, value in entry.items() if value != ""}
                name = values["interface"]
                interval = values.pop("load_interval", "")
                interval_unit = values.pop("load_interval_unit", "")
                interval_seconds = int(interval) if interval else None
                if interval_seconds is not None and interval_unit == "minute":
                    interval_seconds *= 60
                output[name] = InterfaceStatistics(
                    host=self.hostname or str(session.host),
                    **values,
                    load_interval_seconds=interval_seconds,
                )
        return ResponseGroup([response], output, "Cisco IOS-XR Interface Statistics")

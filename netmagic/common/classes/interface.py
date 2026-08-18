# NetMagic Interface Dataclasses

# Python Modules
from ipaddress import IPv4Address as IPv4
from ipaddress import IPv6Address as IPv6
from re import search

from mactools import MacAddress

# Third-Party Modules
from pydantic import BaseModel, field_validator

from netmagic.common.classes.pydantic import MacType, validate_speed

# Local Modules
from netmagic.common.types import HostT, MacT, SFPAlert, SwitchportMode, TDRStatus


class TDRPair(BaseModel):
    local: str
    status: TDRStatus
    remote: str | None = None
    distance: str | None = None

    @field_validator("remote", "distance")
    def validate_optionals(cls, value):
        return value if value else None


class OpticStatus(BaseModel):
    reading: float
    status: SFPAlert | None = None


# INTERFACE MODELS


class Interface(BaseModel):
    host: str
    interface: str

    @property
    def name(self):
        return self.interface

    @property
    def port(self):
        return self.interface


class InterfaceLLDP(Interface):
    chassis_mac: MacType = (
        None  # Accepts `MacAddress|str|int`, converts into `MacAddress`
    )
    system_name: str | None = None
    system_desc: str | None = None
    port_desc: str | None = None
    port_vlan: int | None = None
    management_ipv4: IPv4 | None = None
    management_ipv6: IPv6 | None = None

    @field_validator("chassis_mac")
    def validate_mac_address(cls, mac: MacT | None) -> MacAddress | None:
        if mac is None or mac == "":
            return None
        if not isinstance(mac, MacAddress):
            return MacAddress(mac)
        return mac

    @field_validator("management_ipv4", "management_ipv6", "port_vlan", mode="before")
    def validate_int_fields(cls, value):
        if not value:
            return None
        return None if search(r"(?i)N\/A|None|not advertised", value) else value


class InterfaceOptics(Interface):
    temperature: OpticStatus
    transmit_power: OpticStatus
    receive_power: OpticStatus
    voltage: OpticStatus
    current: OpticStatus

    @classmethod
    def create(cls, host: str, **data):
        """
        Factory pattern for directly consuming output from TextFSM templates
        without transformation.
        """
        kwargs = {}
        data["host"] = host

        for key in InterfaceOptics.model_fields:
            # With status data is an Optics field, others are regular Interface fields
            item_data = data.get(key)
            status_data = data.get(f"{key}_status")

            if status_data:
                status_data = status_data.replace("-", " ").lower()
                if status_match := search(
                    r"([Hh]igh|[Ll]ow)[\s\-\_]([Ww]arn|[Aa]larm)", status_data
                ):
                    status_result = f"{status_match.group(1).lower()} {status_match.group(2).lower()}"
                else:
                    status_result = "none"
                kwargs[key] = OpticStatus(
                    reading=item_data, status=SFPAlert(status_result)
                )
            elif item_data:
                kwargs[key] = item_data

        return cls(**kwargs)


class InterfaceTDR(Interface):
    speed: int | None = None  # Speed in megabit/second
    # Tuple is remote pair, state, distance (if available)
    pair_a: TDRPair
    pair_b: TDRPair
    pair_c: TDRPair
    pair_d: TDRPair

    @field_validator("speed", mode="before")
    def validate_speed(cls, value):
        return validate_speed(value)

    @classmethod
    def create(cls, hostname: str, fsm_data: list[dict[str, str]]):
        """
        Factory pattern for directly consuming output from TextFSM templates
        by transforming it into the expected format.
        """
        create_kwargs = {"host": hostname}
        for line in fsm_data:
            # FSM Optional values
            if speed := line.get("speed"):
                create_kwargs["speed"] = speed
            if interface := line.get("interface"):
                create_kwargs["interface"] = interface

            # FSM Required values
            local = line["local_pair"]
            distance = line.get("distance") if line.get("distance") else None
            pair_kwargs = {
                "local": local,
                "remote": line["remote_pair"],
                "status": TDRStatus.create(line["status"]),
                "distance": distance,
            }
            create_kwargs[f"pair_{local.lower()}"] = TDRPair(**pair_kwargs)
        return cls(**create_kwargs)


class InterfaceStatus(Interface):
    desc: str | None = None
    state: str | None = None
    vlan: str | None = None
    tag: str | None = None
    pvid: int | None = None
    priority: str | None = None
    trunk: str | None = None
    speed: int | None = None
    duplex: str | None = None
    media: str | None = None

    @field_validator("speed", mode="before")
    def validate_speed(cls, value):
        return validate_speed(value)

    @field_validator(
        "state",
        "tag",
        "pvid",
        "vlan",
        "priority",
        "trunk",
        "duplex",
        "media",
        mode="before",
    )
    def validate_optional_fields(cls, value):
        return None if search(r"(?i)N\/A|None", value) else value

    # Aliases between vendor terminology
    @property
    def link(self):
        return self.state

    @property
    def label(self):
        return self.desc


class InterfaceStatistics(Interface):
    """Normalized interface counters and load-interval traffic rates."""

    input_packets: int | None = None
    input_bytes: int | None = None
    output_packets: int | None = None
    output_bytes: int | None = None
    input_broadcast_packets: int | None = None
    input_multicast_packets: int | None = None
    output_broadcast_packets: int | None = None
    output_multicast_packets: int | None = None
    input_drops: int | None = None
    output_drops: int | None = None
    input_errors: int | None = None
    crc_errors: int | None = None
    framing_errors: int | None = None
    input_overruns: int | None = None
    input_ignored_packets: int | None = None
    input_aborts: int | None = None
    output_errors: int | None = None
    output_underruns: int | None = None
    input_rate_bps: int | None = None
    input_rate_pps: int | None = None
    output_rate_bps: int | None = None
    output_rate_pps: int | None = None
    load_interval_seconds: int | None = None


class InterfaceVLANs(Interface):
    access: int | None = None
    dual: str | None = None
    native: int | None = None
    mode: SwitchportMode | None = None
    trunk: str | None = None
    untags: str | None = None

    @property
    def tags(self):
        return self.trunk

    @field_validator("mode", mode="before")
    def validate_switchport_mode(cls, value):
        value = "" if not value else value
        return SwitchportMode(value)

    @field_validator("mode", "trunk", "untags", mode="before")
    def validate_string_items(cls, value):
        return None if value == "" else value

    @field_validator("access", "native", mode="before")
    def validate_int_items(cls, value):
        return None if value == "" else int(value)


class SVI(Interface):
    ip_address: HostT
    subnet: str

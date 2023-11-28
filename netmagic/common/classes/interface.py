# NetMagic Interface Dataclasses

# Python Modules
from dataclasses import dataclass
from enum import Enum
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)

# Third-Party Modules
from mactools import MacAddress

class TDRStatus(Enum):
    terminated = 'normal'
    crosstalk = 'crosstalk'
    open = 'open'
    short = 'short'


class SFPAlert(Enum):
    normal = 'Normal'
    low_warn = 'Low warning'
    high_warn = 'High warning'
    low_alarm = 'Low alarm'
    high_alarm = 'High alarm'


@dataclass
class Interface:
    host: str
    name: str


@dataclass
class InterfaceLLDP(Interface):
    chassis_mac: MacAddress
    system_name: str
    system_desc: str
    port_desc: str
    port_vlan: int
    management_ipv4: IPv4
    management_ipv6: IPv6


@dataclass
class InterfaceOptics(Interface):
    temperature: tuple(float, SFPAlert)
    transmit_power: tuple(float, SFPAlert)
    receive_power: tuple(float, SFPAlert)
    current: tuple(float, SFPAlert)
    temperature: tuple(float, SFPAlert)


@dataclass
class InterfaceTDR(Interface):
    speed: int
    # Tuple is remote pair, state, distance (if available)
    pair_a: tuple(str, TDRStatus, int)
    pair_b: tuple(str, TDRStatus, int)
    pair_c: tuple(str, TDRStatus, int)
    pair_d: tuple(str, TDRStatus, int)


@dataclass
class InterfaceStatus(Interface):
    state: str
    vlan: str
    tag: str
    pvid: str
    priority: str
    trunk: str
    speed: int
    duplex: str
    type: str
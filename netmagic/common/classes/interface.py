# NetMagic Interface Dataclasses

# Python Modules
from dataclasses import dataclass
from enum import Enum
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)
from typing import Any

# Third-Party Modules
from pydantic import BaseModel, validator 
from mactools import MacAddress

# Local Modules
from netmagic.common.types import MacT

MacType = Any

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


class Interface(BaseModel):
    host: str
    port: str

    @property
    def name(self):
        return self.port

class InterfaceLLDP(Interface):
    chassis_mac: MacType # Accepts `MacAddress|str|int` into `MacAddress`
    system_name: str
    system_desc: str
    port_desc: str
    port_vlan: int
    management_ipv4: IPv4
    management_ipv6: IPv6

    @validator('chassis_mac')
    def validate_mac_address(cls, mac: MacT) -> MacAddress:
        if not isinstance(mac, MacAddress):
            return MacAddress(mac)


class InterfaceOptics(Interface):
    temperature: tuple[float, SFPAlert]
    transmit_power: tuple[float, SFPAlert]
    receive_power: tuple[float, SFPAlert]
    voltage: tuple[float, SFPAlert]
    current: tuple[float, SFPAlert]
    temperature: tuple[float, SFPAlert]

    @classmethod
    def create(cls, hostname: str, **data):
        """
        Factory pattern for directly consuming output from TextFSM templates
        without transformation.
        """
        kwargs = {}
        
        for key in InterfaceOptics.model_fields:
            item_data = data.get(key)
            status_data = data.get(f'{key}_status')
            if status_data:
                kwargs[key] = (item_data, SFPAlert(status_data))
            else:
                kwargs[key] = item_data

        return cls(host = hostname, **kwargs)
    

class InterfaceTDR(Interface):
    speed: int
    # Tuple is remote pair, state, distance (if available)
    pair_a: tuple[str, TDRStatus, int]
    pair_b: tuple[str, TDRStatus, int]
    pair_c: tuple[str, TDRStatus, int]
    pair_d: tuple[str, TDRStatus, int]


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
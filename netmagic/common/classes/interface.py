# NetMagic Interface Dataclasses

# Python Modules
from enum import Enum
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)
from re import search
from typing import Any, Optional

# Third-Party Modules
from pydantic import BaseModel, validator 
from mactools import MacAddress

# Local Modules
from netmagic.common.types import MacT

# Alias for Pydantic Models
MacType = Any

def validate_speed(value):
    """
    Validates speed in Pydantic-based Interface dataclasses
    """
    if isinstance(value, str):
        speed_match = search(r'(?i)(\d+)(m|g)?', value)
        if not speed_match:
            raise ValueError('`speed` must be an integer or a string which can have labels like M or G for abbreviation')
        speed = int(speed_match.group(1))

        if (suffix := speed_match.group(2)):
            case_dict = {
                'm': 1,
                'g': 1000,
            }
            speed = speed * case_dict[suffix.lower()]
        
        return speed
    return value

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
    chassis_mac: MacType # Accepts `MacAddress|str|int`, converts into `MacAddress`
    system_name: Optional[str] = None
    system_desc: Optional[str] = None
    port_desc: Optional[str] = None
    port_vlan: Optional[int] = None
    management_ipv4: Optional[IPv4] = None
    management_ipv6: Optional[IPv6] = None

    @validator('chassis_mac')
    def validate_mac_address(cls, mac: MacT) -> MacAddress:
        if not isinstance(mac, MacAddress):
            return MacAddress(mac)

    @validator('management_ipv4', 'management_ipv6', 'port_vlan', pre=True)
    def validate_int_fields(cls, value):
        if not value:
            return None
        return None if search(r'(?i)N\/A|None', value) else value


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
            elif item_data:
                kwargs[key] = item_data

        return cls(host = hostname, **kwargs)
    

class InterfaceTDR(Interface):
    speed: int # Speed in megabit/second
    # Tuple is remote pair, state, distance (if available)
    pair_a: tuple[str, TDRStatus, int]
    pair_b: tuple[str, TDRStatus, int]
    pair_c: tuple[str, TDRStatus, int]
    pair_d: tuple[str, TDRStatus, int]

    @validator('speed', pre=True)
    def validate_speed(cls, value):
        return validate_speed(value)


class InterfaceStatus(Interface):
    desc: Optional[str] = None
    state: Optional[str] = None
    vlan: Optional[str] = None
    tag: Optional[str] = None
    pvid: Optional[int] = None
    priority: Optional[str] = None
    trunk: Optional[str] = None
    speed: Optional[int] = None
    duplex: Optional[str] = None
    media: Optional[str] = None

    @validator('speed', pre=True)
    def validate_speed(cls, value):
        if search(r'(?i)none|auto', value):
            return None
        return validate_speed(value)
    
    @validator('state', 'tag', 'pvid', 'vlan', 'priority', 'trunk', 'duplex', 'media', pre=True)
    def validate_optional_fields(cls, value):
        return None if search(r'(?i)N\/A|None', value) else value
    
    # Aliases between vendor terminology
    @property
    def link(self):
        return self.state
    
    @property
    def label(self):
        return self.desc
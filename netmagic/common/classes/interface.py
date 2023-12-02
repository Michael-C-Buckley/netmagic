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
    system_name: Optional[str]
    system_desc: Optional[str]
    port_desc: Optional[str]
    port_vlan: Optional[int]
    management_ipv4: Optional[IPv4]
    management_ipv6: Optional[IPv6]

    @validator('chassis_mac')
    def validate_mac_address(cls, mac: MacT) -> MacAddress:
        if not isinstance(mac, MacAddress):
            return MacAddress(mac)

    @validator('management_ipv4', 'management_ipv6', 'port_vlan', pre=True)
    def validate_int_fields(cls, value):
        if not value:
            return None
        return None if search('(?:N/A)|(?:None)', value) else value


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
    link: Optional[str]
    state: Optional[str]
    vlan: Optional[int]
    tag: Optional[str]
    pvid: Optional[int]
    priority: Optional[str]
    trunk: Optional[str]
    speed: Optional[int]
    duplex: Optional[str]
    type: Optional[str]

    @validator('speed', pre=True)
    def validate_speed(cls, value):
        if value == 'None':
            return None
        return validate_speed(value)
    
    @validator('pvid', 'vlan', pre=True)
    def validate_int_fields(cls, value):
        return None if search('(?:N/A)|(?:None)', value) else value
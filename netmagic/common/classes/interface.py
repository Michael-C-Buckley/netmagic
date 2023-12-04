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
    Validates speed in Pydantic-based Interface dataclasses.
    Normals into mbps and has cases to return None.
    """
    if isinstance(value, str):
        if value is None:
            return None
        if search(r'(?i)auto|none', value):
            return None
        speed_match = search(r'(?i)(?:a-)?(\d+)(m|g)?', value)
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


class SFPAlert(Enum):
    normal = 'Normal'
    low_warn = 'Low warning'
    high_warn = 'High warning'
    low_alarm = 'Low alarm'
    high_alarm = 'High alarm'


class TDRStatus(Enum):
    NORMAL = ('Normal', 'terminated')
    CROSSTALK = ('Crosstalk', 'crosstalk')
    OPEN = ('Open', 'open')
    SHORT = ('Short', 'short')

    def __new__(cls, *values: object):
        obj = object.__new__(cls)
        obj._value_ = values[0]
        obj.all_values = values
        return obj

    @classmethod
    def create(cls, value):
        for member in cls:
            if value in member.all_values:
                return member
        raise ValueError(f'Value `{value}` not a valid TDRStatus')


class TDRPair(BaseModel):
    local: str
    status: TDRStatus
    remote: Optional[str] = None
    distance: Optional[int] = None

    @validator('remote', 'distance')
    def validate_optionals(cls, value):
        return value if value else None


class OpticStatus(BaseModel):
    reading: float
    status: Optional[SFPAlert] = None


# INTERFACE MODELS

class Interface(BaseModel):
    host: str
    port: str

    @property
    def name(self):
        return self.port
    
    @property
    def interface(self):
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
        return None if search(r'(?i)N\/A|None|not advertised', value) else value
    
class InterfaceOptics(Interface):
    temperature: OpticStatus
    transmit_power: OpticStatus
    receive_power: OpticStatus
    voltage: OpticStatus
    current: OpticStatus
    temperature: OpticStatus

    @classmethod
    def create(cls, hostname: str, **data):
        """
        Factory pattern for directly consuming output from TextFSM templates
        without transformation.
        """
        kwargs = {}
        
        for key in InterfaceOptics.model_fields:
            # With status data is an Optics field, others are regular Interface fields
            item_data = data.get(key)
            status_data = data.get(f'{key}_status')
            if status_data:
                kwargs[key] = OpticStatus(reading = item_data, status = SFPAlert(status_data))
            elif item_data:
                kwargs[key] = item_data

        return cls(host = hostname, **kwargs)
    

class InterfaceTDR(Interface):
    speed: Optional[int] = None # Speed in megabit/second
    # Tuple is remote pair, state, distance (if available)
    pair_a: TDRPair
    pair_b: TDRPair
    pair_c: TDRPair
    pair_d: TDRPair

    @validator('speed', pre=True)
    def validate_speed(cls, value):
        return validate_speed(value)

    @classmethod
    def create(cls, hostname: str, fsm_data: list[dict[str, str]]):
        """
        Factory pattern for directly consuming output from TextFSM templates
        by transforming it into the expected format.
        """
        create_kwargs = {'host': hostname}
        for line in fsm_data:
            # FSM Optional values
            if (speed := line.get('speed')):
                create_kwargs['speed'] = speed
            if (port := line.get('port')):
                create_kwargs['port'] = port

            # FSM Required values
            local = line['local_pair']
            distance = line.get('distance') if line.get('distance') else None
            pair_kwargs = {
                'local': local,
                'remote': line['remote_pair'],
                'status': TDRStatus.create(line['status']),
                'distance': distance
            }
            create_kwargs[f'pair_{local.lower()}'] = TDRPair(**pair_kwargs)
        return cls(**create_kwargs)


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
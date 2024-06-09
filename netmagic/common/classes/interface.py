# NetMagic Interface Dataclasses

# Python Modules
from ipaddress import (
    IPv4Address as IPv4,
    IPv6Address as IPv6
)
from re import search
from typing import Optional

# Third-Party Modules
from pydantic import BaseModel, field_validator
from mactools import MacAddress

# Local Modules
from netmagic.common.types import MacT, TDRStatus, SFPAlert
from netmagic.common.classes.pydantic import MacType, validate_speed


class TDRPair(BaseModel):
    local: str
    status: TDRStatus
    remote: Optional[str] = None
    distance: Optional[str] = None

    @field_validator('remote', 'distance')
    def validate_optionals(cls, value):
        return value if value else None


class OpticStatus(BaseModel):
    reading: float
    status: Optional[SFPAlert] = None


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
    chassis_mac: MacType = None # Accepts `MacAddress|str|int`, converts into `MacAddress`
    system_name: Optional[str] = None
    system_desc: Optional[str] = None
    port_desc: Optional[str] = None
    port_vlan: Optional[int] = None
    management_ipv4: Optional[IPv4] = None
    management_ipv6: Optional[IPv6] = None

    @field_validator('chassis_mac')
    def validate_mac_address(cls, mac: MacT) -> MacAddress:
        if mac is None or mac == '':
            return None
        if not isinstance(mac, MacAddress):
            return MacAddress(mac)

    @field_validator('management_ipv4', 'management_ipv6', 'port_vlan', mode='before')
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
            status_data = data.get(f'{key}_status').replace('-',' ').lower()

            if status_data:
                if (status_match := search(r'([Hh]igh|[Ll]ow)[\s-_]([Ww]arn|[Aa]larm)', status_data)):
                    status_result = f'{status_match.group(1).lower()} {status_match.group(2).lower()}'
                else:
                    status_result = 'none'
                kwargs[key] = OpticStatus(reading = item_data, status = SFPAlert(status_result))
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

    @field_validator('speed', mode='before')
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
            if (interface := line.get('port')):
                create_kwargs['port'] = interface

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

    @field_validator('speed', mode='before')
    def validate_speed(cls, value):
        return validate_speed(value)

    @field_validator('state', 'tag', 'pvid', 'vlan', 'priority', 'trunk', 'duplex', 'media', mode='before')
    def validate_optional_fields(cls, value):
        return None if search(r'(?i)N\/A|None', value) else value

    # Aliases between vendor terminology
    @property
    def link(self):
        return self.state

    @property
    def label(self):
        return self.desc

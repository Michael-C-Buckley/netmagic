# NetMagic Status Classes

# Python Modules
from re import search
from typing import Optional

# Third-Party Modules
from pydantic import BaseModel, validator
from mactools import MacAddress

# Local Modules
from netmagic.common.types import MacT
from netmagic.common.classes.interface import Interface
from netmagic.common.classes.pydantic import MacType

# POE STATUS

def prepare_poe_kwargs(cls: 'POEPort|POEHost', unit: str, **data) -> dict[str, str|float]:
    """
    Data preparation and normalization for POE models.
    Normalization includes converting power to watts.
    """
    create_kwargs = {}
    conversion = 1000 if search(r'(?i)mw', unit) else 1
    for name, field in cls.model_fields.items():
        if (item_data := data.get(name)):
            if field.annotation in [float, Optional[float]]:
                item_data = round(float(item_data) / conversion, 2)
            create_kwargs[name] = item_data
    return create_kwargs

class POEPort(Interface):
    admin_state: Optional[str] = None
    operation_state: Optional[str] = None
    consumed: Optional[float] = None
    allocated: Optional[float] = None
    power_type: Optional[str] = None
    power_class: Optional[str] = None
    priority: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def create(cls, hostname: str, unit: str, **data) -> 'POEPort':
        create_kwargs = prepare_poe_kwargs(cls, unit, **data)
        return cls(host = hostname, **create_kwargs)


class POEHost(BaseModel):
    host: str
    capacity: float
    available: float

    @property
    def used(self):
        return self.capacity - self.available
    
    @classmethod
    def create(cls, hostname: str, unit: str, **data) -> 'POEHost':
        create_kwargs = prepare_poe_kwargs(cls, unit, **data)
        return cls(host = hostname, **create_kwargs)

# MAC ADDRESS TABLE

class MACTableEntry(BaseModel):
    """
    Entries from a MAC address table.
    
    """
    mac: MacType # Accepts `MacAddress|str|int`, converts into `MacAddress`
    host: str
    interface: set[str]
    type: str
    vlan: dict[int, str]

    @property
    def count(self):
        return len(self.vlan)

    @validator('mac')
    def validate_mac_address(cls, mac: MacT) -> MacAddress:
        if not isinstance(mac, MacAddress):
            return MacAddress(mac)
        
    @classmethod
    def create(cls, hostname: str, mac: MacAddress|str, **data):
        """
        Handle the creation of dicts for tracking multiple occurrences
        """
        port_data = data.pop('interface')
        vlan_data = int(data.pop('vlan'))
        data['interface'] = set([port_data])
        data['vlan'] = {vlan_data: port_data}
        return cls(host=hostname, mac=mac, **data)
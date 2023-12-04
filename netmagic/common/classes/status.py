# NetMagic Status Classes

# Python Modules
from typing import Optional

# Third-Party Modules
from pydantic import BaseModel

# Local Modules
from netmagic.common.classes.interface import Interface

class POEPort(Interface):
    admin_state: Optional[str] = None
    operation_state: Optional[str] = None
    consumed: Optional[float] = None
    allocated: Optional[float] = None
    power_type: Optional[str] = None
    power_class: Optional[str] = None
    priority: Optional[str] = None
    error: Optional[str] = None


class POEHost(BaseModel):
    host: str
    capacity: float
    available: float

    @property
    def used(self):
        return self.capacity - self.available
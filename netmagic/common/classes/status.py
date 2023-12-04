# NetMagc Status Classes

# Third-Party Modules
from pydantic import BaseModel

# Local Modules
from netmagic.common.classes.interface import Interface

class POEPort(Interface):
    admin_state: str
    operation_state: str
    consumed: float
    allocated: float
    power_type: str
    power_class: str
    priority: str
    error: str


class POEHost(BaseModel):
    host: str
    capacity: float
    available: float
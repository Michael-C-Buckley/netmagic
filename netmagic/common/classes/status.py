# NetMagc Status Classes

# Third-Party Modules
from pydantic import BaseModel

# Local Modules
from netmagic.common import FSMOutputT 
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


# class POEData(BaseModel):
#     host: str
#     capacity: float
#     available: float
#     interfaces: dict[str, POEPort]

#     @classmethod
#     def create(cls, hostname: str, fsm_data: FSMOutputT):
#         input_kwargs = {'host': hostname}
#         interface_dict = {}
#         for entry in fsm_data:
#             if (capacity := entry.get('capacity')):
#                 input_kwargs['capacity'] = capacity
#             if (available := entry.get('available')):
#                 input_kwargs['available'] = available
#             port = entry.get('port')
#             if port is not None:
#                 port_kwargs = {k:v for k,v in entry.items() if v != ''}
#                 poe_port = POEPort(host = hostname, port = port, **port_kwargs)
#                 interface_dict[port] = poe_port
#         return cls(interfaces=interface_dict, **input_kwargs)
# NetMagic Common Test Items

# Python Modules
from typing import Any
from unittest.mock import Mock

# Third-Party Modules
from netmiko import BaseConnection

# Class to test Netmiko's `BaseConnection`
class MockBaseConnection(Mock):
    __class__ = BaseConnection

    # def __init__(self, *args, **kwargs) -> None:
    #     super().__init__(*args, **kwargs)
    #     self.is_alive.return_value = True
    #     self.write_channel.return_value = ''
    
    # def write_channel(*args, **kwargs):
    #     pass
    
    # def is_alive(*args, **kwargs):
    #     pass


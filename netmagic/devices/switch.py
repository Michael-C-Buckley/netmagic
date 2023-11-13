# Project NetMagic Switch Library

# Python Modules
from ipaddress import IPv4Address as IPv4
from re import search

# Third-Party Modules
from mactools import MacAddress

# Local Modules
from netmagic.devices.universal import Device

class Switch(Device):
    """"""
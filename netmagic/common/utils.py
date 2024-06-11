# NetMagic General Utilities

# Python Modules
from functools import cache, wraps
from inspect import signature, stack
from typing import Callable, Sequence
from re import search, sub

# Local Modules
from netmagic.common.classes.interface import InterfaceVLANs
from netmagic.handlers.parse import INTERFACE_PATTERN

def param_cache(func: Callable):
    """
    Caches the output of a single argument function
    """
    cache = {}
    def wrapper(arg):
        if arg:
            cache_key = (func, arg)
            if cache_key in cache:
                result = cache[cache_key]
            else:
                result = func(arg)
                cache[cache_key] = result
            return result
        return func(arg)
    return wrapper

@param_cache
def get_param_names(func: Callable = None) -> list[str]:
    """
    Returns a list of strings of the names of input params of a function.
    Detects the function that called it when not function is passed.
    """
    if func is None:
        caller_frame = stack()[1]
        if caller_frame.function in ['<dictcomp>', '<listcomp>']:
            caller_frame = stack()[2]
        func = caller_frame.frame.f_globals[caller_frame.function]
    sig = signature(func)
    return [param.name for param in sig.parameters.values()]

def validate_max_tries(func):
    """
    Validation to ensure that `max_tries` is a valid positive integer
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = signature(func)
        bound_arguments = sig.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        max_tries = bound_arguments.arguments.get('max_tries', 1)
        max_tries = int(max_tries)

        if max_tries < 1:
            raise ValueError('`max_tries` count must be `1` or greater.')

        return func(*args, **kwargs)
    return wrapper

def unquote(string: str) -> str:
    """
    Removes quotes from the beginning and end of a string, if present
    """
    if len(string) >= 2 and string[0] == string[-1] and string[0] in ('"', "'"):
        return string[1:-1]
    else:
        return string

def sort_interfaces(intf_list: list[str]) -> list[str]:
    """
    Converts a list of interfaces into one sorted by STACK/MODULE/SLOT
    since standard sorting will not do this correctly.
    """
    parsed_interfaces = []
    for intf in intf_list:
        match = search(r'([A-Za-z]+)?(\d+)\/(\d+)\/(\d+)', intf)
        if match:
            prefix, dev_stack, module, slot = match.groups()
            parsed_interfaces.append((prefix or '', int(dev_stack), int(module), int(slot), intf))

    parsed_interfaces.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return [x[4] for x in parsed_interfaces]

@cache
def abbreviate_interface(interface: str) -> str:
    """
    This abbreviates Cisco interfaces from the long-form into a short-form
    """
    if (local_match := search(r'([a-zA-Z]+)(\d+)(\/\d+\/\d+)?', interface)):
        postfix = local_match.group(2)
        if local_match.group(3):
            postfix += local_match.group(3)
        return f'{local_match.group(1)[:2]}{postfix}'
    
    return interface

def get_vlan_string(vlans: InterfaceVLANs) -> str:
    """
    Converts the VLAN model fields of `InterfaceVLANs` into a short, serialized string
    """
    if vlans.access and not vlans.trunk:
        return str(vlans.access)
    
    trunk_str = sub(str(vlans.native), f'N{vlans.native}', vlans.tags) if vlans.native else vlans.tags
    trunk_str = sub(str(vlans.dual), f'D{vlans.dual}', trunk_str) if vlans.dual else trunk_str

    return trunk_str

def convert_vlan_string_to_object(vlan_str: str, host: str, interface: str) -> InterfaceVLANs:
    """
    Converts a VLAN string into `InterfaceVLANs` object.

    `vlan_str (str)`: the VLAN string to be converted
    `host (str)`: hostname where the interface belongs
    `interface (str)`: interface that the VLANs are associated with 
    """
    if len(vlan_str.strip().split(',')) == 1:
        kwargs = {
            'access': vlan_str,
            'mode': 'access'
        }
    if (special_matches := search(r'(N)(D)(\d+)', vlan_str)):
        vlan = special_matches.group(3)
        dual = '' if not special_matches.group(2) else vlan
        native = '' if not special_matches.group(1) else vlan
        kwargs = {
            'dual': dual,
            'native': native,
            'tags': vlan_str.replace(),
            'mode': 'trunk'
        }
    else:
        kwargs = {
            'mode': 'trunk',
            'tags': vlan_str
        }

    return InterfaceVLANs(host=host, interface=interface, **kwargs)

@cache
def abbreviate_brocade_range(interface_range: str) -> list[str]:
    """
    Converts a Brocade text range into a condensed list of strings
    """
    return [i.strip() for i in interface_range.split('ethe') if i]

@cache
def brocade_text_to_range(interface_range: str|Sequence[str]) -> set[str]:
    """
    Converts a Brocade-formatted interface text range into a set of every member
    """
    if isinstance(interface_range, str):
        interface_range = abbreviate_brocade_range(interface_range)
    else:
        interface_range = [i.strip() for i in interface_range if i]

    output_list = set()
    
    for item in interface_range:
        if search(f'^{INTERFACE_PATTERN}$', item):
            output_list.add(item)
        elif (match := search(f'^(\d+\/\d+)\/(\d+) to (\d+\/\d+)\/(\d+)$', item)):
            if match.group(1) != match.group(3):
                raise ValueError(f'Ranges must be in the same stack and module and only the interface ID (3rd member) can vary\nProblem string: {match.group()}')
            for i in range(int(match.group(2)), int(match.group(4))+1):
                output_list.add(f'{match.group(1)}/{i}')

    return output_list

@cache
def check_in_brocade_range(range_string: str, member: str) -> bool:
    """
    Bool value for if the member is in the range string supplied
    """
    return member in brocade_text_to_range(range_string)
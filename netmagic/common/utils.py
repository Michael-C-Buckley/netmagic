# NetMagic General Utilities

# Python Modules
from functools import wraps
from inspect import signature, stack
from typing import Callable
from re import search

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

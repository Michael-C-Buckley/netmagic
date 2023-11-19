# NetMagic General Utilities

# Python Modules

import inspect
from functools import wraps

def validate_max_tries(func):
    """
    Validation to ensure that `max_tries` is a valid positive integer
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_arguments = sig.bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        
        max_tries = bound_arguments.arguments.get('max_tries', 1)
        max_tries = int(max_tries)

        if max_tries < 1:
            raise ValueError('`max_tries` count must be `1` or greater.')

        return func(*args, **kwargs)
    return wrapper
# NetMagic Pydantic-specific Classes and Items

# Python Modules
from re import search
from typing import Any, Optional

# Alias for Pydantic Models
MacType = Any

def validate_speed(value):
    """
    Validates speed in Pydantic-based Interface dataclasses.
    Normals into mbps and has cases to return None.
    """
    if isinstance(value, str):
        if value is None:
            return None
        if search(r'(?i)auto|none', value):
            return None
        speed_match = search(r'(?i)(?:a-)?(\d+)(m|g)?', value)
        if not speed_match:
            raise ValueError('`speed` must be an integer or a string which can have labels like M or G for abbreviation')
        speed = int(speed_match.group(1))

        if (suffix := speed_match.group(2)):
            case_dict = {
                'm': 1,
                'g': 1000,
            }
            speed = speed * case_dict[suffix.lower()]
        
        return speed
    return value
# Project NetMagic Parse Module

# Python Modules
from re import search, compile, escape
from typing import Optional

# Third-Party Modules
from mactools import MacAddress
from textfsm import TextFSM

# Regex patterns

# Universal
HEX_PATTERN = r'[a-fA-F0-9]'
HEX_PAIR = f'{HEX_PATTERN}{{2}}'
MAC_PORTION = f'{HEX_PAIR}[:\-\. ]?'
EUI48_PATTERN = f'({MAC_PORTION}){{5}}{HEX_PAIR}'
EUI64_PATTERN = f'({MAC_PORTION}){{7}}{HEX_PAIR}'
MAC_PATTERN = f'{EUI64_PATTERN}|{EUI64_PATTERN}'

CITY_STATE_ZIP = r'[a-zA-Z]+?\s?[a-zA-Z]+,\s[A-Z]{2},?\s\d{5}'
CITY_STATE = r'[a-zA-Z]+?\s?[a-zA-Z]+,\s[A-Z]{2}'

# IPv4
"""
WARNING: Some expressions are not robust and do not fully validate but only
match syntax, use `ipaddress` for complete and robust validation
"""
IPV4_OCTET = r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
IPV4_PATTERN =  fr'(?:{IPV4_OCTET}\.){{3}}{IPV4_OCTET}'
IPV4_RESERVED_RANGE = r'(?:^10\.)|(?:^127\.)|(?:^172\.(?:1[6-9]|2[0-9]|3[01]))|(?:^192\.168\.)'
BINARY_OCTET_8BIT = r'(?:0|128|192|224|240|248|252|254|255)'
IPV4_SUBNET_MASK = fr'(:?{BINARY_OCTET_8BIT}\.){{3}}{BINARY_OCTET_8BIT}'

# IPv6
"""
WARNING: These should be used only for loose matching, like `TextFSM`
They are not exhaustive or precise enough for validation
Consider validating with `ipaddress`
"""
BASIC_IPV6 = r'(?:[a-fA-F\d]{0,4}:?){0,7}(?:[a-fA-F\d]{0,4}:?)'
MIXED_IPV6 = fr'::(?:[fF]{{4}}:)?{IPV4_PATTERN}'
IPV6_REGEX = fr'{BASIC_IPV6}|{MIXED_IPV6}'

IP_PATTERN = f'{IPV4_PATTERN}|{IPV6_REGEX}'

# Device Regex
INTERFACE_REGEX = r'(\w+)?(\d)\/(\d)\/(\d+)'
INTERFACE_ABBRIEV = r'(((SFP\+?)|([Pp]ort))\s?\d+?\s(o[fn])?\s)'


def escape_string(string: str, exclude_list: Optional[list[str]] = None) -> str:
    """
    Custom escape function to only escape necessary characters and not over-escape
    like `re.escape` does
    """
    special_chars = ['.', '^', '$', '*', '+', '?', '[', ']', '|', '(', ')', '\\']

    if exclude_list:
        special_chars = [char for char in special_chars if char not in exclude_list]

    for char in special_chars:
        string = string.replace(char, fr'\{char}')

    return string

def dual_escape(string: str) -> str:
    """
    Uses the custom library escape and adds `re.escape` to cover either case
    """
    return f'({escape_string(string)}|{escape(string)})'
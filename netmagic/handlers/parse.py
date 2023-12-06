# Project NetMagic Parse Module

# Python Modules
from importlib.resources import open_text
from io import StringIO
from os import path
from re import search, escape, match
from typing import Optional

# Third-Party Modules
from textfsm import TextFSM
from functools import lru_cache

# Local Modules
from netmagic.common.types import FSMOutputT

# Regex patterns

# Universal
HEX_PATTERN = r'[a-fA-F0-9]'
HEX_PAIR = f'{HEX_PATTERN}{{2}}'
MAC_PORTION = f'{HEX_PAIR}[:\-\. ]?'
EUI48_PATTERN = f'({MAC_PORTION}){{5}}{HEX_PAIR}'
EUI64_PATTERN = f'({MAC_PORTION}){{7}}{HEX_PAIR}'
MAC_PATTERN = f'{EUI48_PATTERN}|{EUI64_PATTERN}'

CITY_STATE_ZIP = r'[a-zA-Z]+?\s?[a-zA-Z]+,\s[A-Z]{2},?\s\d{5}'
CITY_STATE = r'[a-zA-Z]+?\s?[a-zA-Z]+,\s[A-Z]{2}'

NUMBER_PATTERN = r'(?:-?\d+|-)(?:\.\d+)?'

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
IPV6_PATTERN = fr'{BASIC_IPV6}|{MIXED_IPV6}'

IP_PATTERN = f'{IPV4_PATTERN}|{IPV6_PATTERN}'

# Device Regex
INTERFACE_PATTERN = r'[A-Za-z]{0,2}\d\/\d\/\d{1,2}'
INTERFACE_PATTERN_GROUPS = r'(\w+)?(\d)\/(\d)\/(\d+)'
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

def swap(input_string: str, template: str):
    """
    Swaps regex patterns detected on templates with variables in this file
    """
    template_string = ''

    for line in input_string.split('\n'):
        # Substitutions only exist currently for Regex patterns of values
        if not match(r'Value', line):
            template_string = f'{template_string}\n{line}' if template_string else line
            continue

        # Extract the pattern from the global variables from this module
        if (swap_match := search(r'\#(\w+)\#', line)):
            if (swap_pattern := globals().get(swap_match.group(1))):
                line = line.replace(swap_match.group(), swap_pattern)
            else:
                raise ValueError(f'Template swap did not resolve a matching regex pattern: `{swap_match}` in `{template}.textfsm`')
        template_string = f'{template_string}\n{line}' if template_string else line

    return template_string

@lru_cache()
def get_parser(template: str, vendor: str):
    """
    Memoized wrapper for get TextFSM parsers
    """
    try:
        if path.exists(template):
            raw_template_string = open(template).read()
        else:
            raw_template_string = open_text(f'netmagic.templates.{vendor.lower()}', f'{template}.textfsm').read()
    except FileNotFoundError:
        # Check to see if the template string passed itself is the template
        if search(r'Value', template) and search(r'Start', template):
            raw_template_string = template
        else:
            raise ValueError('`template` must either be a file path, internal template, or template passed directly as a string')
        
    parser = TextFSM(StringIO(swap(raw_template_string, template)))
    return parser

def flatten_fsm_output(prime_key: str, fsm_output: FSMOutputT) -> FSMOutputT:
    """
    Flattens and collects FSM output into a structure with a matching primary key
    """
    merge_dict: dict[str, dict] = {}
    for item in fsm_output:
        try:
            key = item[prime_key]
        except KeyError:
            raise KeyError('`prime_key` must be a common element to collect other values')
        
        add_dict = {k:v for k,v in item.items() if v}

        if key in merge_dict:
            merge_dict[key].update(add_dict)
        else:
            merge_dict[key] = add_dict

    return [v for v in merge_dict.values()]

def get_fsm_data(input: str, template: str, vendor: str = None,
                 flatten_key: str = None) -> FSMOutputT:
    """
    Function for handling TextFSM parsing and situational variables.
    
    `input` is the string to parse
    `template` is either a path to the template or the template directly as a string
    `vendor` is the name of the vendor for fetching the internal template
    `flatten_key` is the string to flatten the dicts around
    """
    parser = get_parser(template, vendor)

    output = parser.ParseTextToDicts(input)

    if flatten_key is not None:
        output = flatten_fsm_output(flatten_key, output)

    return output
# Project NetMagic Parse Module

# Python Modules
from importlib.resources import open_text
from io import StringIO
from re import search, compile, escape, match, sub
from typing import Optional

# Third-Party Modules
from textfsm import TextFSM

# Local Modules
from netmagic.common.types import Vendors

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

def get_fsm_data(input: str|list, vendor: str, template: str,
                 split_term: str = None) -> list[dict[str, str]]:
    """
    Function for handling TextFSM parsing and situational variables.
    
    `split_term` is an optional string for splitting the input prior to TextFSM parsing.
    `output_dicts` is a bool for TextFSM to return a dict with header as keys or just a value list.
    """
    if not input:
        raise ValueError('Function requires an input to parse')
        
    vendor = vendor.value if isinstance(vendor, Vendors) else vendor
    raw_template_string = open_text(f'netmagic.templates.{vendor}', f'{template}.textfsm').read()
    template_string = ''

    for line in raw_template_string.split('\n'):
        # Substitutions only exist currently for Regex patterns of values
        if not match(r'Value', line):
            template_string = f'{template_string}\n{line}' if template_string else line
            continue

        # Extract the pattern from the global variables from this module
        if (swap_match := search(r'\#(\w+)\#', line)):
            if (swap_pattern := globals().get(swap_match.group(1))):
                # sub(r'\#(\w+)\#', fr'{swap_pattern}', line)
                line = line.replace(swap_match.group(), swap_pattern)
            else:
                raise ValueError(f'Template swap did not resolve a matching regex pattern: `{swap_match}` in `{template}.textfsm`')
        template_string = f'{template_string}\n{line}' if template_string else line

    template: TextFSM = TextFSM(StringIO(template_string))

    def fsm_list(closure_input: str) -> list[dict[str, str]]:
        """
        Closure for handling `input` as `list`
        """
        for item in closure_input:
            output = template.ParseTextToDicts(item)
        if output:
            return output

    def fsm_string(closure_input: str) -> list[dict[str, str]]:
        """
        Closure for handling `input` as `string`
        """
        return template.ParseTextToDicts(closure_input)

    if split_term:
        # Split the inputs and restore the lost term back into the lines
        input = [f'{split_term}{item}'.strip() for item in input.split(split_term) if item != '' or item != split_term]
    
    closure_dict = {
        list: fsm_list,
        str: fsm_string,
    }
    closure = closure_dict.get(type(input))
    return closure(input)
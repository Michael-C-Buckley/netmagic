# NetMagic Tests Init

from sys import path as sys_path
from os import path as os_path

# Path modification to allow the file to see the rest of the project
current_directory = os_path.dirname(os_path.abspath(__file__))
parent_directory = os_path.dirname(current_directory)
root_directory = os_path.dirname(parent_directory)
sys_path.insert(0, parent_directory)
sys_path.insert(0, root_directory)
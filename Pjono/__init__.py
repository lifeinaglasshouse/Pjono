"""
Pjono - Python Web Framework
Author: Xp-op
Version: 0.0.3\n
Changelog:
- 0.0.1
    - Initial Release
- 0.0.2
    - add `add_folder` function to PjonoApp
    - Fix some code style
    - remove AppBuilder.py
- 0.0.3
    - add Components.py module
        - Component and HtComponent class
    - PjonoApp will create new thread to handle client(Multi-Threading)
    - Variable url
        - You can set the variable on `register` function
        - Access the variable on `request["Variables"]`
    - The code will run faster
        - List comprehension
        - one line if statement
"""

__version__ = "0.0.3"
__author__ = "Xp-op <muhammad184276@gmail.com>"

from Pjono.Server import PjonoApp
from Pjono.Response import *
from Pjono.PARSE import HTML
from Pjono.PARSE import Component, HtComponents
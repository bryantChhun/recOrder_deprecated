#!/usr/bin/env python
# title           : this_python_file.py
# description     :This will create a header for a python script.
# author          :bryant.chhun
# date            :12/7/18
# version         :0.0
# usage           :python this_python_file.py -flags
# notes           :
# python_version  :3.6


class InsufficientDataError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message

class InvalidFrameNumberDeclarationError(Exception):

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


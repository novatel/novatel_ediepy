"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Holds common data structures and functions for EDIE's interfaces.
"""
import os
import sys
from ctypes import *

if sys.platform == 'linux':
    HWINTERFACE_DLL = cdll.LoadLibrary(os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../resources', 'libhwinterface_dynamic_library.so')))
elif sys.platform == 'win32':
    HWINTERFACE_DLL = CDLL(os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../resources', 'hwinterface_dynamic_library.dll')))


class ReadData(Structure):
    """Stream read buffer struct.
    """
    _fields_ = [
        ('size', c_ulong),
        ('data', c_char_p)
    ]

    def __str__(self):
        return f'{self.size}: {self.data}'


class StreamReadStatus(Structure):
    """Stream read status struct.
    """
    _fields_ = [
        ('percent_read', c_ulong),
        ('bytes_read', c_ulong),
        ('stream_length', c_ulonglong),
        ('eos', c_bool)
    ]

    def __str__(self):
        return f'{self.percent_read}%, {self.bytes_read}, {self.stream_length}, {self.eos}'

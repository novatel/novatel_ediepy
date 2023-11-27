"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Holds common data structures and functions for EDIE's decoders.
"""
import copy
import os
import sys
from ctypes import *
from enum import Enum

DECODERS_DLL = None
if sys.platform == 'linux':
    DECODERS_DLL = cdll.LoadLibrary(os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../resources', 'libdecoders_dynamic_library.so')))
elif sys.platform == 'win32':
    DECODERS_DLL = CDLL(os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../resources', 'decoders_dynamic_library.dll')))

# Version
DECODERS_DLL.version.restype = c_char_p
DECODERS_DLL.version.argtypes = None
DECODERS_DLL.pretty_version.restype = c_char_p
DECODERS_DLL.pretty_version.argtypes = None

# Constants
MESSAGE_SIZE_MAX = 32768
MAX_ASCII_MESSAGE_LENGTH = MESSAGE_SIZE_MAX
MAX_BINARY_MESSAGE_LENGTH = MESSAGE_SIZE_MAX
MAX_SHORT_ASCII_MESSAGE_LENGTH = MESSAGE_SIZE_MAX
MAX_SHORT_BINARY_MESSAGE_LENGTH = 12 + 255 + 4  # (OEM4_SHORT_BINARY_HEADER_LENGTH + 0xFF + OEM4_BINARY_CRC_LENGTH)
MAX_ABB_ASCII_RESPONSE_LENGTH = MESSAGE_SIZE_MAX
# NovAtel Docs - NMEA Standard Logs: Explicitly states that the maximum allowable is 82 chars.
# NOTE: Numerous internal logs break that standard, so we will use 256 here as a safety measure.
NMEA_SYNC = '$'
NMEA_SYNC_LENGTH = 1
NMEA_CRC_LENGTH = 2
NMEA_MESSAGE_MAX_LENGTH = 256

OEM4_ASCII_SYNC = '#'
OEM4_ASCII_FIELD_SEPERATOR = ','
OEM4_ASCII_HEADER_TERMINATOR = ';'
OEM4_ASCII_SYNC_LENGTH = 1
OEM4_ASCII_CRC_DELIMITER = '*'
OEM4_ASCII_CRC_LENGTH = 8
OEM4_ASCII_MESSAGE_NAME_MAX = 40
OEM4_SHORT_ASCII_SYNC = '%'
OEM4_SHORT_ASCII_SYNC_LENGTH = 1
OEM4_ABBREV_ASCII_SYNC = '<'
OEM4_ABBREV_ASCII_SEPERATOR = ' '

OEM4_BINARY_SYNC1 = 0xAA
OEM4_BINARY_SYNC2 = 0x44
OEM4_BINARY_SYNC3 = 0x12
OEM4_BINARY_SYNC_LENGTH = 3
OEM4_BINARY_HEADER_LENGTH = 28
OEM4_BINARY_CRC_LENGTH = 4
OEM4_SHORT_BINARY_SYNC3 = 0x13
OEM4_SHORT_BINARY_SYNC_LENGTH = 3
OEM4_SHORT_BINARY_HEADER_LENGTH = 12
OEM4_ENCRYPTED_BINARY_SYNC2 = 0x45


class STATUS(Enum):
    """Enumeration for status codes returned from EDIE components.
    """
    SUCCESS = 0  # Successfully found a frame in the framer buffer.
    FAILURE = 1  # An unexpected failure occurred.
    UNKNOWN = 2  # Could not identify bytes as a protocol.
    INCOMPLETE = 3  # It is possible that a valid frame exists in the frame buffer, but more information is needed.
    INCOMPLETE_MORE_DATA = 4  # The current frame buffer is incomplete but more data is expected.
    NULL_PROVIDED = 5  # A null pointer was provided.
    NO_DATABASE = 6  # No database has been provided to the component.
    NO_DEFINITION = 7  # No definition could be found in the database for the provided message.
    NO_DEFINITION_EMBEDDED = 8  # No definition could be found in the database for the embedded message in the RXCONFIG log.
    BUFFER_FULL = 9  # The provided destination buffer is not big enough to contain the frame.
    BUFFER_EMPTY = 10  # The internal circular buffer does not contain any unread bytes
    STREAM_EMPTY = 11  # The input stream is empty.
    UNSUPPORTED = 12  # An attempted operation is unsupported by this component.
    MALFORMED_INPUT = 13  # The input is recognizeable, but has unexpected formatting.
    DECOMPRESSION_FAILURE = 14  # The RANGECMPx log could not be decompressed.


class ENCODEFORMAT(Enum):
    """Encode Format Enum
    """
    FLATTENED_BINARY = 0
    ASCII = 1
    ABBREV_ASCII = 2
    BINARY = 3
    JSON = 4
    UNSPECIFIED = 5


class TIME_STATUS(Enum):
    """Time status enum
    """
    UNKNOWN = 20
    APPROXIMATE = 60
    COARSEADJUSTING = 80
    COARSE = 100
    COARSESTEERING = 120
    FREEWHEELING = 130
    FINEADJUSTING = 140
    FINE = 160
    FINEBACKUPSTEERING = 170
    FINESTEERING = 180
    SATTIME = 200
    EXTERN = 220
    EXACT = 240


class MEASUREMENT_SOURCE(Enum):
    """Message source (antenna source) enum.
    """
    PRIMARY = 0
    SECONDARY = 1


class StructureOutput(Structure):
    """Parent class defining __str__ and __repr__ methods.
    """

    def __str__(self):
        return ''.join([f'{name}: {getattr(self, name)}\n' for name, val in self._fields_])

    def __repr__(self):
        string = '|\t\t'
        entries = '\n|\t\t'.join([f'{name}: {getattr(self, name)}' for name, val in self._fields_])
        return string + entries


class BaseStructMixin:
    def __getitem__(self, item):
        return self._fields_[item][0]

    def __str__(self):
        return ','.join([str(x) for x in self._fields_to_list()])

    def _fields_to_list(self) -> list:
        message_values = []
        fields = enumerate(self._fields_)

        for idx, (field_name, field_type) in fields:
            if hasattr(field_type, '_length_') and field_type._type_ != c_char:
                for i in range(getattr(field_type, '_length_')):
                    message_values.append(getattr(self, field_name)[i])
            else:
                message_values.append(getattr(self, field_name))

                if field_name.endswith('_arraylength'):
                    array_len = getattr(self, field_name)
                    array_idx, (array_name, array_type) = next(fields)
                    array = getattr(self, array_name)
                    for i in range(array_len):
                        message_values.append(array[i])

        return message_values


class SatelliteId(Structure, BaseStructMixin):
    _fields_ = [
        ("usPrnOrSlot", c_uint16),
        ("sFrequencyChannel", c_int16),
    ]


class HeaderFormatEnum(Enum):
    """Log format enum.
    """
    UNKNOWN = 1
    BINARY = 2
    SHORT_BINARY = 3
    ENCRYPTED_BINARY = 4
    ASCII = 5
    SHORT_ASCII = 6
    ABB_ASCII = 7
    NMEA = 8
    JSON = 9
    SHORT_ABB_ASCII = 10
    ALL = 11


class MetaDataStruct(StructureOutput):
    """MetaData structure
    """
    _fields_ = [
        ('format', c_uint32),  # The format of the message when it was framed.
        ('measurement_source', c_uint32),  # Otherwise known as the sibling ID.
        ('time_status', c_uint32),  # The GPSTimeStatus of the message.
        ('response', c_bool),  # True if this message a response to a command.
        ('week', c_uint16),  # The GPS Week No.
        ('milliseconds', c_double),  # The GPS Milliseconds.
        ('binary_msg_length', c_uint32),
        # The length of the message according to the binary header (0 if format is non-binary).
        ('length', c_uint32),  # The length of the message when it was framed.
        ('header_length', c_uint32),  # The length of the message header when it was framed.
        ('message_id', c_uint16),  # The message ID.
        ('message_crc', c_uint32),  # The message definition CRC (distinguish between two versions of one message).
        ('message_name', c_char * OEM4_ASCII_MESSAGE_NAME_MAX),  # The message name.
    ]

    def __init__(self):
        super().__init__()
        self.format = HeaderFormatEnum.UNKNOWN.value


class MessageDataStruct(StructureOutput):
    """MessageDataStruct structure
    """
    _fields_ = [
        ('_header', c_void_p),  # Pointer to the message header.
        ('header_length', c_uint32),  # The message header length.
        ('_body', c_void_p),  # Pointer to the message body.
        ('body_length', c_uint32),  # The message body length.
        ('_message', c_void_p),  # Pointer to the message.
        ('message_length', c_uint32),  # The message length.
    ]

    def __deepcopy__(self, memo=None):
        """ Creates a copy of the object. The pointers in _fields_ confuse the default copy functionality
        """
        memo = memo or {}

        cpy = type(self)()
        memo[id(self)] = cpy

        cpy._header = copy.deepcopy(self._header, memo)
        cpy.header_length = self.header_length
        cpy._body = copy.deepcopy(self._body, memo)
        cpy.body_length = self.body_length
        cpy._message = copy.deepcopy(self._message, memo)
        cpy.message_length = self.message_length

        return cpy

    @property
    def message(self):
        if self._message is not None:
            return (c_char * self.message_length).from_address(self._message).raw
        else:
            return None

    @property
    def header(self):
        if self._header is not None:
            return (c_char * self.header_length).from_address(self._header).raw
        else:
            return None

    @property
    def body(self):
        if self._body is not None:
            return (c_char * self.body_length).from_address(self._body).raw
        else:
            return None

    def get_message_address(self):
        """Accessor for header address in the raw data buffer.
        """
        return self._message

    def get_header_address(self):
        """Accessor for header address in the raw data buffer.
        """
        return self._header

    def get_body_address(self):
        """Accessor for body address in the raw data buffer.
        """
        return self._body

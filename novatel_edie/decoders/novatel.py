"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Holds classes and functions for NovAtel.
"""
import copy
import os
import typing
import ctypes
from ctypes import *
from typing import Union

from novatel_edie.decoders import common, jsonreader
from novatel_edie.decoders.common import DECODERS_DLL, MetaDataStruct, MessageDataStruct, HeaderFormatEnum
from novatel_edie.interfaces import file_stream

# Framer
DECODERS_DLL.novatel_framer_set_logger_level.restype = c_bool
DECODERS_DLL.novatel_framer_set_logger_level.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_framer_shutdown_logger.restype = None
DECODERS_DLL.novatel_framer_shutdown_logger.argtypes = [c_void_p]
DECODERS_DLL.novatel_framer_init.restype = c_void_p
DECODERS_DLL.novatel_framer_init.argtypes = None
DECODERS_DLL.novatel_framer_delete.restype = None
DECODERS_DLL.novatel_framer_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_framer_frame_json.restype = None
DECODERS_DLL.novatel_framer_frame_json.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_framer_payload_only.restype = None
DECODERS_DLL.novatel_framer_payload_only.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_framer_report_unknown_bytes.restype = None
DECODERS_DLL.novatel_framer_report_unknown_bytes.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_framer_get_available_bytes.restype = c_uint32
DECODERS_DLL.novatel_framer_get_available_bytes.argtypes = [c_void_p]
DECODERS_DLL.novatel_framer_write.restype = c_uint32
DECODERS_DLL.novatel_framer_write.argtypes = [c_void_p, c_char_p, c_uint32]
DECODERS_DLL.novatel_framer_read.restype = c_uint32
DECODERS_DLL.novatel_framer_read.argtypes = [c_void_p, c_char_p, c_uint32, c_void_p]
DECODERS_DLL.novatel_framer_flush.restype = c_uint32
DECODERS_DLL.novatel_framer_flush.argtypes = [c_void_p, c_char_p, c_uint32]

# Filter
DECODERS_DLL.novatel_filter_set_logger_level.restype = c_bool
DECODERS_DLL.novatel_filter_set_logger_level.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_filter_shutdown_logger.restype = None
DECODERS_DLL.novatel_filter_shutdown_logger.argtypes = [c_void_p]
DECODERS_DLL.novatel_filter_init.restype = c_void_p
DECODERS_DLL.novatel_filter_init.argtypes = None
DECODERS_DLL.novatel_filter_delete.restype = None
DECODERS_DLL.novatel_filter_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_filter_set_include_lower_time.restype = None
DECODERS_DLL.novatel_filter_set_include_lower_time.argtypes = [c_void_p, c_uint32, c_double]
DECODERS_DLL.novatel_filter_set_include_upper_time.restype = None
DECODERS_DLL.novatel_filter_set_include_upper_time.argtypes = [c_void_p, c_uint32, c_double]
DECODERS_DLL.novatel_filter_invert_time_filter.restype = None
DECODERS_DLL.novatel_filter_invert_time_filter.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_filter_set_include_decimation.restype = None
DECODERS_DLL.novatel_filter_set_include_decimation.argtypes = [c_void_p, c_double]
DECODERS_DLL.novatel_filter_invert_decimation_filter.restype = None
DECODERS_DLL.novatel_filter_invert_decimation_filter.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_filter_include_time_status.restype = None
DECODERS_DLL.novatel_filter_include_time_status.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_filter_invert_time_status_filter.restype = None
DECODERS_DLL.novatel_filter_invert_time_status_filter.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_filter_include_message_id.restype = None
DECODERS_DLL.novatel_filter_include_message_id.argtypes = [c_void_p, c_uint32, c_uint32, c_uint32]
DECODERS_DLL.novatel_filter_invert_message_id_filter.restype = None
DECODERS_DLL.novatel_filter_invert_message_id_filter.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_filter_include_message_name.restype = None
DECODERS_DLL.novatel_filter_include_message_name.argtypes = [c_void_p, c_char_p, c_uint32, c_uint32]
DECODERS_DLL.novatel_filter_invert_message_name_filter.restype = None
DECODERS_DLL.novatel_filter_invert_message_name_filter.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_filter_include_nmea_messages.restype = None
DECODERS_DLL.novatel_filter_include_nmea_messages.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_filter_do_filtering.restype = c_bool
DECODERS_DLL.novatel_filter_do_filtering.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_filter_clear_filters.restype = None
DECODERS_DLL.novatel_filter_clear_filters.argtypes = [c_void_p]

# Header Decoder
DECODERS_DLL.novatel_header_decoder_set_logger_level.restype = c_bool
DECODERS_DLL.novatel_header_decoder_set_logger_level.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_header_decoder_shutdown_logger.restype = None
DECODERS_DLL.novatel_header_decoder_shutdown_logger.argtypes = [c_void_p]
DECODERS_DLL.novatel_header_decoder_init.restype = c_void_p
DECODERS_DLL.novatel_header_decoder_init.argtypes = [c_void_p]
DECODERS_DLL.novatel_header_decoder_delete.restype = None
DECODERS_DLL.novatel_header_decoder_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_header_decoder_load_json.restype = None
DECODERS_DLL.novatel_header_decoder_load_json.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_header_decoder_decode.restype = c_uint32
DECODERS_DLL.novatel_header_decoder_decode.argtypes = [c_void_p, c_char_p, c_void_p, c_void_p]

# Intermediate Message
DECODERS_DLL.novatel_intermediate_message_init.restype = c_void_p
DECODERS_DLL.novatel_intermediate_message_init.argtypes = None
DECODERS_DLL.novatel_intermediate_message_delete.restype = None
DECODERS_DLL.novatel_intermediate_message_delete.argtypes = [c_void_p]

# Message Decoder
DECODERS_DLL.novatel_message_decoder_set_logger_level.restype = c_bool
DECODERS_DLL.novatel_message_decoder_set_logger_level.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_message_decoder_shutdown_logger.restype = None
DECODERS_DLL.novatel_message_decoder_shutdown_logger.argtypes = [c_void_p]
DECODERS_DLL.novatel_message_decoder_init.restype = c_void_p
DECODERS_DLL.novatel_message_decoder_init.argtypes = [c_void_p]
DECODERS_DLL.novatel_message_decoder_delete.restype = None
DECODERS_DLL.novatel_message_decoder_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_message_decoder_load_json.restype = None
DECODERS_DLL.novatel_message_decoder_load_json.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_message_decoder_decode.restype = c_uint32
DECODERS_DLL.novatel_message_decoder_decode.argtypes = [c_void_p, c_char_p, c_void_p, c_void_p]

# Encoder
DECODERS_DLL.novatel_encoder_set_logger_level.restype = c_bool
DECODERS_DLL.novatel_encoder_set_logger_level.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_encoder_shutdown_logger.restype = None
DECODERS_DLL.novatel_encoder_shutdown_logger.argtypes = [c_void_p]
DECODERS_DLL.novatel_encoder_init.restype = c_void_p
DECODERS_DLL.novatel_encoder_init.argtypes = [c_void_p]
DECODERS_DLL.novatel_encoder_delete.restype = None
DECODERS_DLL.novatel_encoder_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_encoder_load_json.restype = None
DECODERS_DLL.novatel_encoder_load_json.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_encoder_encode.restype = c_uint32
DECODERS_DLL.novatel_encoder_encode.argtypes = [
    c_void_p, c_char_p, c_uint32, c_void_p, c_void_p, c_void_p, c_void_p, c_uint32]

# Parser
DECODERS_DLL.novatel_parser_init.restype = c_void_p
DECODERS_DLL.novatel_parser_init.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_delete.restype = None
DECODERS_DLL.novatel_parser_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_load_json_db.restype = None
DECODERS_DLL.novatel_parser_load_json_db.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_parser_get_ignore_abbrev_ascii_responses.restype = c_bool
DECODERS_DLL.novatel_parser_get_ignore_abbrev_ascii_responses.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_set_ignore_abbrev_ascii_responses.restype = None
DECODERS_DLL.novatel_parser_set_ignore_abbrev_ascii_responses.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_parser_get_decompress_rangecmp.restype = c_bool
DECODERS_DLL.novatel_parser_get_decompress_rangecmp.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_set_decompress_rangecmp.restype = None
DECODERS_DLL.novatel_parser_set_decompress_rangecmp.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_parser_get_return_unknownbytes.restype = c_bool
DECODERS_DLL.novatel_parser_get_return_unknownbytes.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_set_return_unknownbytes.restype = None
DECODERS_DLL.novatel_parser_set_return_unknownbytes.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_parser_get_encodeformat.restype = c_uint32
DECODERS_DLL.novatel_parser_get_encodeformat.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_set_encodeformat.restype = None
DECODERS_DLL.novatel_parser_set_encodeformat.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_parser_get_filter.restype = c_void_p
DECODERS_DLL.novatel_parser_get_filter.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_set_filter.restype = None
DECODERS_DLL.novatel_parser_set_filter.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_parser_get_buffer.restype = c_char_p
DECODERS_DLL.novatel_parser_get_buffer.argtypes = [c_void_p]
DECODERS_DLL.novatel_parser_write.restype = c_uint32
DECODERS_DLL.novatel_parser_write.argtypes = [c_void_p, c_char_p, c_uint32]
DECODERS_DLL.novatel_parser_read.restype = c_uint32
DECODERS_DLL.novatel_parser_read.argtypes = [c_void_p, c_void_p, c_void_p]
DECODERS_DLL.novatel_parser_flush.restype = c_uint32
DECODERS_DLL.novatel_parser_flush.argtypes = [c_void_p, c_char_p, c_uint32]

# Fileparser
DECODERS_DLL.novatel_fileparser_init.restype = c_void_p
DECODERS_DLL.novatel_fileparser_init.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_delete.restype = None
DECODERS_DLL.novatel_fileparser_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_load_json_db.restype = None
DECODERS_DLL.novatel_fileparser_load_json_db.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_fileparser_get_ignore_abbrev_ascii_responses.restype = c_bool
DECODERS_DLL.novatel_fileparser_get_ignore_abbrev_ascii_responses.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_set_ignore_abbrev_ascii_responses.restype = None
DECODERS_DLL.novatel_fileparser_set_ignore_abbrev_ascii_responses.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_fileparser_get_decompress_rangecmp.restype = c_bool
DECODERS_DLL.novatel_fileparser_get_decompress_rangecmp.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_set_decompress_rangecmp.restype = None
DECODERS_DLL.novatel_fileparser_set_decompress_rangecmp.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_fileparser_get_return_unknownbytes.restype = c_bool
DECODERS_DLL.novatel_fileparser_get_return_unknownbytes.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_set_return_unknownbytes.restype = None
DECODERS_DLL.novatel_fileparser_set_return_unknownbytes.argtypes = [c_void_p, c_bool]
DECODERS_DLL.novatel_fileparser_get_encodeformat.restype = c_uint32
DECODERS_DLL.novatel_fileparser_get_encodeformat.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_set_encodeformat.restype = None
DECODERS_DLL.novatel_fileparser_set_encodeformat.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_fileparser_get_filter.restype = c_void_p
DECODERS_DLL.novatel_fileparser_get_filter.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_set_filter.restype = None
DECODERS_DLL.novatel_fileparser_set_filter.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_fileparser_get_buffer.restype = c_char_p
DECODERS_DLL.novatel_fileparser_get_buffer.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_set_stream.restype = c_bool
DECODERS_DLL.novatel_fileparser_set_stream.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_fileparser_get_percent_read.restype = c_uint32
DECODERS_DLL.novatel_fileparser_get_percent_read.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_read.restype = c_uint32
DECODERS_DLL.novatel_fileparser_read.argtypes = [c_void_p, c_void_p, c_void_p]
DECODERS_DLL.novatel_fileparser_reset.restype = c_bool
DECODERS_DLL.novatel_fileparser_reset.argtypes = [c_void_p]
DECODERS_DLL.novatel_fileparser_flush.restype = c_uint32
DECODERS_DLL.novatel_fileparser_flush.argtypes = [c_void_p, c_char_p, c_uint32]

# Commander
DECODERS_DLL.novatel_commander_set_logger_level.restype = c_bool
DECODERS_DLL.novatel_commander_set_logger_level.argtypes = [c_void_p, c_uint32]
DECODERS_DLL.novatel_commander_shutdown_logger.restype = None
DECODERS_DLL.novatel_commander_shutdown_logger.argtypes = [c_void_p]
DECODERS_DLL.novatel_commander_init.restype = c_void_p
DECODERS_DLL.novatel_commander_init.argtypes = [c_void_p]
DECODERS_DLL.novatel_commander_delete.restype = None
DECODERS_DLL.novatel_commander_delete.argtypes = [c_void_p]
DECODERS_DLL.novatel_commander_load_json.restype = None
DECODERS_DLL.novatel_commander_load_json.argtypes = [c_void_p, c_void_p]
DECODERS_DLL.novatel_commander_encode.restype = c_uint32
DECODERS_DLL.novatel_commander_encode.argtypes = [c_void_p, c_void_p, c_uint32, c_void_p, c_void_p, c_uint32]


################################################################################
# NovAtel Structures & Enums
################################################################################
class IntermediateHeader(common.StructureOutput):
    """IntermediateHeader structure
    """
    _fields_ = [
        ('message_id', c_uint16),
        ('message_type', c_uint8),
        ('port_address', c_uint32),
        ('length', c_uint16),
        ('sequence', c_uint16),
        ('idle_time', c_uint8),
        ('time_status', c_uint32),
        ('week', c_uint16),
        ('milliseconds', c_double),
        ('receiver_status', c_uint32),
        ('msg_def_crc', c_uint32),
        ('receiver_sw_version', c_uint16),
    ]


class OEM4BinaryHeader(common.StructureOutput):
    """OEM4BinaryHeader structure
    """
    _fields_ = [
        ('sync_1', c_uint8),
        ('sync_2', c_uint8),
        ('sync_3', c_uint8),
        ('header_length', c_uint8),
        ('id', c_uint16),
        ('type', c_uint8),
        ('port', c_uint8),
        ('length', c_uint16),
        ('sequence', c_uint16),
        ('idle', c_uint8),
        ('time_status', c_uint8),
        ('week', c_uint16),
        ('milliseconds', c_uint32),
        ('status', c_uint32),
        ('def_crc', c_uint16),
        ('rx_sw_version', c_uint16)
    ]


class OEM4BinaryShortHeader(common.StructureOutput):
    """OEM4BinaryShortHeader structure
    """
    _fields_ = [
        ('sync_1', c_uint8),
        ('sync_2', c_uint8),
        ('sync_3', c_uint8),
        ('message_length', c_uint16),
        ('id', c_uint16),
        ('week', c_uint16),
        ('milliseconds', c_uint32),
    ]


class Message:
    """ Class that holds a message, broken into a header and a body
    """

    def __init__(self,
                 header: OEM4BinaryHeader,
                 body: typing.Type[object]):
        self.header = header
        self.body = body

    def __deepcopy__(self, memo=None):
        cpy = type(self)(None, None)
        memo = {} if memo is None else memo
        memo[id(self)] = cpy

        cpy.header = copy.deepcopy(self.header, memo)
        cpy.body = copy.deepcopy(self.body, memo)
        return cpy

    @staticmethod
    def _find_nested_attribute(structure, field_name):
        # Store the array lengths. Makes it possible to constrain the arrays the amount of data vs the max array size
        array_lengths = {}
        for element_name, element_type in structure._fields_:
            field_value = structure.__getattribute__(element_name)

            # The desired field exists directly at the top level of the message class
            if element_name == field_name:
                if issubclass(element_type, ctypes.Array):
                    element_array_length = array_lengths[element_name]
                    return field_value[:element_array_length]
                return field_value

            if element_name.endswith('_length'):
                array_lengths[element_name.rsplit('_', 1)[0]] = field_value

            # If the element is an array then look if the array elements contain the attribute
            # At this point there are no messages that have depth greater than 1. If that changes in the future
            # a recursive call to this function would be required in the future.
            elif issubclass(element_type, ctypes.Array):
                if hasattr(element_type._type_, field_name):
                    element_array_length = array_lengths[element_name]
                    return [getattr(arr_element, field_name) for arr_element in field_value[:element_array_length]]

        raise AttributeError(f'\'{type(structure).__name__}\' object has no attribute \'{field_name}\'')

    def __getattr__(self, item):
        value = None

        try:
            value = Message._find_nested_attribute(self.body, item)
        except AttributeError:
            pass

        if value is None:
            try:
                value = self._find_nested_attribute(self.header, item)
            except AttributeError:
                pass

        if value is None:
            raise AttributeError(f'{type(self).__name__} {type(self.body).__name__} object has no attribute \'{item}\'')

        if issubclass(type(value), Array):
            value = list(value)

        return value

    def __getitem__(self, item):

        try:
            val = self.__getattr__(item)
        except AttributeError:
            raise KeyError(item)

        return val


class Response(Message):
    """
        Class to support copying of responses. Several fields in the auto-generated RESPONSE_0_0
        type do not play nice with copying.
    """

    def __deepcopy__(self, memo=None):
        cpy = type(self)(None, type(self.body)())
        memo = {} if memo is None else memo
        memo[id(self)] = cpy

        cpy.header = copy.deepcopy(self.header, memo)
        cpy.body.id = self.body.id
        cpy.body.str = self.body.str
        cpy.body._fields_ = copy.deepcopy(self.body._fields_, memo)
        cpy.body._pack_ = self.body._pack_

        return cpy

    # The id and str fields are accessible without these properties, but this way it is more explicit
    @property
    def id(self):
        return self.__getattr__('id')

    @property
    def str(self):
        return self.__getattr__('str')


################################################################################
# NovAtel EDIE Components
################################################################################
class Framer:
    """Framer class for NovAtel messages.
    """

    def __init__(self, report_unknown_bytes: bool = True, payload_only: bool = False, frame_json: bool = False):
        """Initializer.

        Args:
            report_unknown_bytes (bool): return unknown bytes
            payload_only (bool): frame message body only
            frame_json (bool): frame json objects
        """
        self._report_unknown_bytes = report_unknown_bytes
        self._payload_only = payload_only
        self._frame_json = frame_json
        self._framer = common.DECODERS_DLL.novatel_framer_init()
        self._read_buf_size = common.MESSAGE_SIZE_MAX
        self._read_buf = create_string_buffer(self._read_buf_size)
        self._meta_data = MetaDataStruct()
        common.DECODERS_DLL.novatel_framer_report_unknown_bytes(self._framer, self._report_unknown_bytes)
        common.DECODERS_DLL.novatel_framer_payload_only(self._framer, self._payload_only)
        common.DECODERS_DLL.novatel_framer_frame_json(self._framer, self._frame_json)

    def __del__(self):
        if self._framer:
            common.DECODERS_DLL.novatel_framer_delete(self._framer)
            self._framer = None

    def __iter__(self):
        return self

    def __next__(self) -> tuple:
        result = self.read()
        if result[0] == common.STATUS.NULL_PROVIDED or result[0] == common.STATUS.BUFFER_EMPTY:
            raise StopIteration()
        return result

    @property
    def report_unknown_bytes(self):
        return self._report_unknown_bytes

    @report_unknown_bytes.setter
    def report_unknown_bytes(self, value: bool):
        self._report_unknown_bytes = value
        common.DECODERS_DLL.novatel_framer_report_unknown_bytes(self._framer, self._report_unknown_bytes)

    @property
    def payload_only(self):
        return self._payload_only

    @payload_only.setter
    def payload_only(self, value: bool):
        self._payload_only = value
        common.DECODERS_DLL.novatel_framer_payload_only(self._framer, self._payload_only)

    @property
    def frame_json(self):
        return self._frame_json

    @frame_json.setter
    def frame_json(self, value: bool):
        self._frame_json = value
        common.DECODERS_DLL.novatel_framer_frame_json(self._framer, self._frame_json)

    @property
    def available_bytes(self):
        return common.DECODERS_DLL.novatel_framer_get_available_bytes(self._framer)

    def write(self, data: bytes) -> int:
        """Write to the internal buffer.

        Args:
            data: raw data to write

        Return:
            Number of bytes written
        """
        return common.DECODERS_DLL.novatel_framer_write(self._framer, data, len(data))

    def read(self) -> tuple:
        """Read a frame from the internal buffer.

        Return:
            FrameData object, Log object
        """
        status = common.DECODERS_DLL.novatel_framer_read(
            self._framer, self._read_buf, self._read_buf_size, byref(self._meta_data))
        return common.STATUS(status), self._read_buf.raw[:self._meta_data.length], self._meta_data

    def flush(self) -> tuple:
        """Flush bytes from the internal buffer.

        Return:
            FrameData object, Log object
        """
        flushed_size = common.DECODERS_DLL.novatel_framer_flush(self._framer, self._read_buf, self._read_buf_size)
        return self._read_buf.raw[:flushed_size], flushed_size


class Filter:
    """Filter class for NovAtel MetaDataStruct.
    """

    def __init__(self):
        """Initializer.
        """
        self._filter = DECODERS_DLL.novatel_filter_init()

    def __del__(self):
        """Delete method.
        """
        if self._filter:
            DECODERS_DLL.novatel_filter_delete(self._filter)
            self._filter = None

    def get_dll_reference(self):
        """
        """
        return self._filter

    def filter(self, meta_data: MetaDataStruct):
        """Performing filtering on the provided metadata

        Args:
            frame (bytes): The frame to be filtered
        """
        return DECODERS_DLL.novatel_filter_do_filtering(self._filter, byref(meta_data))

    def clear_filters(self):
        """Clear all filter settings.
        """
        DECODERS_DLL.novatel_filter_clear_filters(self._filter)

    def set_time_window(
            self, lower_week: int = None, lower_second: float = None,
            upper_week: int = None, upper_second: float = None):
        """
        """
        if lower_week and lower_second:
            DECODERS_DLL.novatel_filter_set_include_lower_time(self._filter, lower_week, lower_second)
        if upper_week and upper_second:
            DECODERS_DLL.novatel_filter_set_include_upper_time(self._filter, upper_week, upper_second)

    def invert_time_filter(self, invert: bool):
        """
        """
        DECODERS_DLL.novatel_filter_invert_time_filter(self._filter, invert)

    def set_include_decimation(self, period: int):
        """
        """
        DECODERS_DLL.novatel_filter_set_include_decimation(self._filter, period)

    def invert_decimation_filter(self, invert: bool):
        """
        """
        DECODERS_DLL.novatel_filter_invert_decimation_filter(self._filter, invert)

    def include_time_status(self, status: common.TIME_STATUS):
        """
        """
        DECODERS_DLL.novatel_filter_include_time_status(self._filter, status.value)

    def invert_time_status_filter(self, invert: bool):
        """
        """
        DECODERS_DLL.novatel_filter_invert_time_status_filter(self._filter, invert)

    def include_message_id(self, message_id: int, encode_format: HeaderFormatEnum = HeaderFormatEnum.ALL,
                           source: common.MEASUREMENT_SOURCE = common.MEASUREMENT_SOURCE.PRIMARY):
        """
        """
        DECODERS_DLL.novatel_filter_include_message_id(self._filter, message_id, encode_format.value, source.value)

    def invert_message_id_filter(self, invert: bool):
        """
        """
        DECODERS_DLL.novatel_filter_invert_message_id_filter(self._filter, invert)

    def include_message_name(self, name: str, encode_format: HeaderFormatEnum = HeaderFormatEnum.ALL,
                             source: common.MEASUREMENT_SOURCE = common.MEASUREMENT_SOURCE.PRIMARY):
        """
        """
        DECODERS_DLL.novatel_filter_include_message_name(
            self._filter, name.encode('utf-8'), encode_format.value, source.value)

    def invert_message_name_filter(self, invert: bool):
        """
        """
        DECODERS_DLL.novatel_filter_invert_message_name_filter(self._filter, invert)

    def include_nmea_messages(self, include_nmea: bool):
        """
        """
        DECODERS_DLL.novatel_filter_include_nmea_messages(self._filter, include_nmea)


class HeaderDecoder:
    """HeaderDecoder class for framed NovAtel messages.
    """

    def __init__(self, json_db: Union[str, jsonreader.JsonReader] = None):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

        self._decoder = DECODERS_DLL.novatel_header_decoder_init(json_db.get_dll_reference())

    def __del__(self):
        if self._decoder:
            DECODERS_DLL.novatel_header_decoder_delete(self._decoder)
            self._decoder = None

    def decode(self, frame: bytes, meta_data: MetaDataStruct):
        """Decode a framed message.

        Args:
            frame (bytes): framed message

        Return:
            (tuple) DecoderResult object, Log object
        """
        int_header = IntermediateHeader()
        status = common.STATUS(
            DECODERS_DLL.novatel_header_decoder_decode(self._decoder, frame, byref(int_header), byref(meta_data)))
        return status, int_header


class MessageDecoder:
    """MessageDecoder class for framed NovAtel messages.
    """

    class IntermediateMessage:
        """Wrapper class for typedef'd C++ vector.
        """

        def __init__(self):
            self._int_message = DECODERS_DLL.novatel_intermediate_message_init()

        def __del__(self):
            if self._int_message:
                DECODERS_DLL.novatel_intermediate_message_delete(self._int_message)
                self._int_message = None

        def get_dll_reference(self):
            return self._int_message

    def __init__(self, json_db: Union[str, jsonreader.JsonReader] = None):
        self._decoder = None
        self.json_db = json_db

        self._decoder = DECODERS_DLL.novatel_message_decoder_init(json_db.get_dll_reference())

    def __del__(self):
        if self._decoder:
            DECODERS_DLL.novatel_message_decoder_delete(self._decoder)
            self._decoder = None

    @property
    def json_db(self):
        return self._json_db.json_db_filepath

    @json_db.setter
    def json_db(self, json_db: Union[str, jsonreader.JsonReader] = None):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

        if self._decoder:
            DECODERS_DLL.novatel_message_decoder_load_json(self._decoder, self._json_db.get_dll_reference())

    def decode(self, frame: bytes, meta_data: MetaDataStruct):
        """Decode a framed message.

        Args:
            frame (bytes): framed message

        Return:
            (tuple) DecoderResult object, Log object
        """

        # This is a dll wrapper for std::vector<FieldContainer> aka IntermediateMessage.
        int_message = MessageDecoder.IntermediateMessage()
        status = common.STATUS(
            DECODERS_DLL.novatel_message_decoder_decode(self._decoder,
                                                        frame,
                                                        int_message.get_dll_reference(),
                                                        byref(meta_data)))
        return status, int_message


class Encoder:
    """Encoder class for encoding NovAtel messages.
    """

    def __init__(self, json_db: Union[str, jsonreader.JsonReader] = None,
                 encode_format: common.ENCODEFORMAT = common.ENCODEFORMAT.ASCII):
        self._encoder = None
        self.json_db = json_db

        self._encoder = DECODERS_DLL.novatel_encoder_init(self._json_db.get_dll_reference())
        self._encode_buffer_size = common.MESSAGE_SIZE_MAX
        self._encode_buffer = create_string_buffer(self._encode_buffer_size)
        self._encode_format = encode_format

    def __del__(self):
        if self._encoder:
            DECODERS_DLL.novatel_encoder_delete(self._encoder)
            self._encoder = None

    @property
    def json_db(self):
        return self._json_db.json_db_filepath

    @json_db.setter
    def json_db(self, json_db: Union[str, jsonreader.JsonReader] = None):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

        if self._encoder:
            DECODERS_DLL.novatel_encoder_load_json(self._encoder, self._json_db.get_dll_reference())

    @property
    def encode_format(self):
        return self._encode_format

    @encode_format.setter
    def encode_format(self, value: common.ENCODEFORMAT):
        self._encode_format = value

    def encode(self, int_header: IntermediateHeader, int_message: MessageDecoder.IntermediateMessage,
               meta_data: MetaDataStruct, encode_format: common.ENCODEFORMAT = None):
        encode_format = encode_format or self._encode_format
        message_data = MessageDataStruct()
        status = common.STATUS(
            DECODERS_DLL.novatel_encoder_encode(
                self._encoder,
                self._encode_buffer,
                self._encode_buffer_size,
                byref(int_header),
                int_message.get_dll_reference(),
                byref(message_data),
                byref(meta_data),
                encode_format.value))

        message = None
        if status == common.STATUS.SUCCESS and encode_format == common.ENCODEFORMAT.FLATTENED_BINARY:
            if meta_data.response:
                if message_data.body is None:
                    message = Response(header=OEM4BinaryHeader(),
                                       body=self._json_db.convert_response_to_structure(message_data.message))
                else:
                    message = Response(
                        header=OEM4BinaryHeader.from_address(message_data.get_header_address()),
                        body=self._json_db.convert_response_to_structure(message_data.body[:-4])
                    )
            else:
                message = Message(
                    header=OEM4BinaryHeader.from_address(message_data.get_header_address()),
                    body=self._json_db.get_message_definition_structure(
                        meta_data.message_id,
                        meta_data.message_crc).from_address(message_data.get_body_address()))

        return status, message_data, message


class Parser:
    def __init__(self, json_db: Union[str, jsonreader.JsonReader] = None,
                 encode_format: common.ENCODEFORMAT = common.ENCODEFORMAT.ASCII):
        """Parser class for NovAtel messages.
        """
        self._parser = None
        self.json_db = json_db

        self._parser = DECODERS_DLL.novatel_parser_init(self._json_db.get_dll_reference())
        self._encode_buffer_size = common.MESSAGE_SIZE_MAX
        self._encode_buffer = create_string_buffer(self._encode_buffer_size)
        self.encode_format = encode_format

        self.filter = Filter()
        DECODERS_DLL.novatel_parser_set_filter(self._parser, self.filter.get_dll_reference())

    def __del__(self):
        """
        """
        if self._parser:
            DECODERS_DLL.novatel_parser_delete(self._parser)
            self._parser = None

    def __iter__(self):
        """
        """
        return self

    def __next__(self):
        """
        """
        result = self.read()
        if result[0] == common.STATUS.BUFFER_EMPTY:
            raise StopIteration()
        return result

    @property
    def json_db(self):
        return self._json_db.json_db_filepath

    @json_db.setter
    def json_db(self, json_db: Union[str, jsonreader.JsonReader] = None):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

        if self._parser:
            DECODERS_DLL.novatel_parser_load_json_db(self._parser, self._json_db.get_dll_reference())

    @property
    def decompress_rangecmp(self):
        """
        """
        return DECODERS_DLL.novatel_parser_get_decompress_rangecmp(self._parser)

    @decompress_rangecmp.setter
    def decompress_rangecmp(self, decompress: bool):
        """
        """
        DECODERS_DLL.novatel_parser_set_decompress_rangecmp(self._parser, decompress)

    @property
    def ignore_abbrev_ascii_responses(self):
        """
        """
        return DECODERS_DLL.novatel_parser_get_ignore_abbrev_ascii_responses(self._parser)

    @ignore_abbrev_ascii_responses.setter
    def ignore_abbrev_ascii_responses(self, ignore: bool):
        """
        """
        DECODERS_DLL.novatel_parser_set_ignore_abbrev_ascii_responses(self._parser, ignore)

    @property
    def return_unknownbytes(self):
        """
        """
        return DECODERS_DLL.novatel_parser_get_return_unknownbytes(self._parser)

    @return_unknownbytes.setter
    def return_unknownbytes(self, unknownbytes: bool):
        """
        """
        DECODERS_DLL.novatel_parser_set_return_unknownbytes(self._parser, unknownbytes)

    @property
    def encode_format(self):
        """
        """
        return common.ENCODEFORMAT(DECODERS_DLL.novatel_parser_get_encodeformat(self._parser))

    @encode_format.setter
    def encode_format(self, encode_format: common.ENCODEFORMAT):
        """
        """
        DECODERS_DLL.novatel_parser_set_encodeformat(self._parser, encode_format.value)

    def _internal_frame_buffer(self):
        """
        """
        return DECODERS_DLL.novatel_parser_get_buffer(self._parser)

    def write(self, data: bytes):
        """
        """
        return DECODERS_DLL.novatel_parser_write(self._parser, data, len(data))

    def read(self):
        """
        """
        meta_data = MetaDataStruct()
        message_data = MessageDataStruct()
        status = common.STATUS(DECODERS_DLL.novatel_parser_read(self._parser, byref(message_data), byref(meta_data)))

        message = None
        if status == common.STATUS.SUCCESS and self.encode_format == common.ENCODEFORMAT.FLATTENED_BINARY:
            # If we are encoding to FLATTENED_BINARY, we can define a new type and create an instance of it here
            if meta_data.response:
                if message_data.body is None:
                    message = Response(header=OEM4BinaryHeader(),
                                       body=self._json_db.convert_response_to_structure(message_data.message))
                else:
                    message = Response(
                        header=OEM4BinaryHeader.from_address(message_data.get_header_address()),
                        body=self._json_db.convert_response_to_structure(message_data.body[:-4])
                    )
            else:
                message = Message(
                    header=OEM4BinaryHeader.from_address(message_data.get_header_address()),
                    body=self._json_db.get_message_definition_structure(
                        meta_data.message_id,
                        meta_data.message_crc).from_address(message_data.get_body_address()))

        return status, meta_data, message_data, message

    def flush(self):
        """Flush bytes from the internal buffer.

        Return:
            (tuple) FrameData object, Log object
        """
        flushed_size = common.DECODERS_DLL.novatel_parser_flush(self._parser, self._encode_buffer,
                                                                self._encode_buffer_size)
        return self._encode_buffer.raw[:flushed_size], flushed_size


class FileParser:
    """FileParser class for NovAtel messages.
    """

    def __init__(self, json_db: Union[str, jsonreader.JsonReader] = None,
                 encode_format: common.ENCODEFORMAT = common.ENCODEFORMAT.ASCII, input_file: str = None):
        """
        """
        self._fileparser = None
        self.json_db = json_db

        self._fileparser = DECODERS_DLL.novatel_fileparser_init(self._json_db.get_dll_reference())
        self._encode_buffer_size = common.MESSAGE_SIZE_MAX
        self._encode_buffer = create_string_buffer(self._encode_buffer_size)
        self.encode_format = encode_format

        self.filter = Filter()
        DECODERS_DLL.novatel_fileparser_set_filter(self._fileparser, self.filter.get_dll_reference())

        self._stream = None
        if input_file:
            self.input_file = input_file
            self._stream = file_stream.InputFileStream(input_file)
            DECODERS_DLL.novatel_fileparser_set_stream(self._fileparser, self._stream.get_dll_reference())

    def __del__(self):
        """Delete method.
        """
        if self._fileparser:
            DECODERS_DLL.novatel_fileparser_delete(self._fileparser)
            self._fileparser = None

    def __iter__(self):
        """
        Iterator.
        """
        return self

    def __next__(self):
        """
        """
        result = self.read()
        if result[0] == common.STATUS.STREAM_EMPTY:
            raise StopIteration()
        return result

    @property
    def json_db(self):
        return self._json_db.json_db_filepath

    @json_db.setter
    def json_db(self, json_db: Union[str, jsonreader.JsonReader] = None):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

        if self._fileparser:
            DECODERS_DLL.novatel_fileparser_load_json_db(self._fileparser, self._json_db.get_dll_reference())

    @property
    def decompress_rangecmp(self):
        """
        """
        return DECODERS_DLL.novatel_fileparser_get_decompress_rangecmp(self._fileparser)

    @decompress_rangecmp.setter
    def decompress_rangecmp(self, decompress: bool):
        """
        """
        DECODERS_DLL.novatel_fileparser_set_decompress_rangecmp(self._fileparser, decompress)

    @property
    def ignore_abbrev_ascii_responses(self):
        """
        """
        return DECODERS_DLL.novatel_fileparser_get_ignore_abbrev_ascii_responses(self._fileparser)

    @ignore_abbrev_ascii_responses.setter
    def ignore_abbrev_ascii_responses(self, ignore: bool):
        """
        """
        DECODERS_DLL.novatel_fileparser_set_ignore_abbrev_ascii_responses(self._fileparser, ignore)

    @property
    def return_unknownbytes(self):
        """
        """
        return DECODERS_DLL.novatel_fileparser_get_return_unknownbytes(self._fileparser)

    @return_unknownbytes.setter
    def return_unknownbytes(self, unknownbytes: bool):
        """
        """
        DECODERS_DLL.novatel_fileparser_set_return_unknownbytes(self._fileparser, unknownbytes)

    @property
    def encode_format(self):
        """
        """
        return common.ENCODEFORMAT(DECODERS_DLL.novatel_fileparser_get_encodeformat(self._fileparser))

    @encode_format.setter
    def encode_format(self, encode_format: common.ENCODEFORMAT):
        """
        """
        DECODERS_DLL.novatel_fileparser_set_encodeformat(self._fileparser, encode_format.value)

    def _internal_frame_buffer(self):
        """
        """
        return DECODERS_DLL.novatel_fileparser_get_buffer(self._fileparser)

    @property
    def input_file(self):
        """
        """
        return self._input_file

    @input_file.setter
    def input_file(self, input_file: str):
        """
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f'File does not exist: {input_file}')

        self._input_file = input_file
        self._stream = file_stream.InputFileStream(input_file)
        is_file_stream_set = DECODERS_DLL.novatel_fileparser_set_stream(self._fileparser, self._stream.get_dll_reference())

        if not is_file_stream_set:
            raise IOError('Input stream could not be set. The stream is either unavailable or exhausted.')

    def read(self):
        """
        """
        message_data = MessageDataStruct()
        meta_data = MetaDataStruct()
        status = common.STATUS(
            DECODERS_DLL.novatel_fileparser_read(self._fileparser, byref(message_data), byref(meta_data)))

        message = None
        if status == common.STATUS.SUCCESS and self.encode_format == common.ENCODEFORMAT.FLATTENED_BINARY:
            # If we are encoding to FLATTENED_BINARY, we can define a new type and create an instance of it here
            if meta_data.response:
                message = Response(
                    header=OEM4BinaryHeader.from_address(message_data.get_header_address()),
                    body=self._json_db.convert_response_to_structure(message_data.body[:-4])
                )
            else:
                message = Message(
                    header=OEM4BinaryHeader.from_address(message_data.get_header_address()),
                    body=self._json_db.get_message_definition_structure(
                        meta_data.message_id,
                        meta_data.message_crc).from_address(message_data.get_body_address()))

        return status, meta_data, message_data, message

    def flush(self):
        """Flush bytes from the internal buffer.

        Return:
            (tuple) FrameData object, Log object
        """
        flushed_size = common.DECODERS_DLL.novatel_fileparser_flush(self._fileparser, self._encode_buffer,
                                                                    self._encode_buffer_size)
        return self._encode_buffer.raw[:flushed_size], flushed_size


class Commander:
    """Encoder class for decoded NovAtel messages.
    """

    def __init__(self, json_db: Union[str, jsonreader.JsonReader] = None,
                 encode_format: common.ENCODEFORMAT = common.ENCODEFORMAT.ASCII):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

        self._commander = DECODERS_DLL.novatel_commander_init(self._json_db.get_dll_reference())
        self._encode_format = encode_format
        self._encode_buffer_size = c_uint32(common.MESSAGE_SIZE_MAX)
        self._encode_buffer = create_string_buffer(self._encode_buffer_size.value)

    def __del__(self):
        if self._commander:
            DECODERS_DLL.novatel_commander_delete(self._commander)
            self._commander = None

    @property
    def json_db(self):
        """.coveragerc"""
        return self._json_db.json_db_filepath

    @json_db.setter
    def json_db(self, json_db: Union[str, jsonreader.JsonReader] = None):
        if json_db is None:
            self._json_db = jsonreader.JsonReader()
        elif isinstance(json_db, str):
            self._json_db = jsonreader.JsonReader(json_db)
        elif isinstance(json_db, jsonreader.JsonReader):
            self._json_db = json_db

    @property
    def encode_format(self):
        return self._encode_format

    @encode_format.setter
    def encode_format(self, value: common.ENCODEFORMAT):
        self._encode_format = value

    def encode(self, command: str, encode_format: common.ENCODEFORMAT = None):
        encode_format = encode_format or self._encode_format
        self._encode_buffer_size = c_uint32(common.MESSAGE_SIZE_MAX)
        status = DECODERS_DLL.novatel_commander_encode(self._commander, command.encode('utf-8'), len(command),
                                                       self._encode_buffer, byref(self._encode_buffer_size),
                                                       encode_format.value)

        return common.STATUS(status), self._encode_buffer[:self._encode_buffer_size.value]

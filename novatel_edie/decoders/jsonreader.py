"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Holds classes and functions for reading JSON data.
"""
import json
import os
from collections import defaultdict
from ctypes import *
from enum import Enum

from novatel_edie.common import JSON_DB_PATH
from novatel_edie.decoders.common import DECODERS_DLL, SatelliteId, BaseStructMixin

DECODERS_DLL.common_jsonreader_init.restype = c_void_p
DECODERS_DLL.common_jsonreader_init.argtypes = [c_char_p]
DECODERS_DLL.common_jsonreader_delete.restype = None
DECODERS_DLL.common_jsonreader_delete.argtypes = [c_void_p]


class JsonReader:
    novtypes_to_ctypes_dict = {
        'BOOL': c_int32,
        'HEXBYTE': c_uint8,
        'UCHAR': c_uint8,
        'CHAR': c_int8,
        'USHORT': c_uint16,
        'SHORT': c_int16,
        'UINT': c_uint32,
        'INT': c_int32,
        'ULONG': c_uint32,
        'LONG': c_int32,
        'ULONGLONG': c_uint64,
        'LONGLONG': c_int64,
        'FLOAT': c_float,
        'DOUBLE': c_double,
        'ENUM': c_int32,
        'STRING': c_char,
        'RESPONSE_ID': c_int32,
        'SATELLITEID': SatelliteId
    }

    def __init__(self, json_db_filepath: str = None):
        json_db_filepath = JSON_DB_PATH if not json_db_filepath else json_db_filepath
        if not os.path.exists(json_db_filepath):
            raise FileNotFoundError(f'Invalid path: {json_db_filepath}')
        self._json_db_filepath = json_db_filepath
        self._json_db = DECODERS_DLL.common_jsonreader_init(json_db_filepath.encode())

        self.enum_definitions = dict()
        self.message_definitions = defaultdict(dict)
        self.response_definition = None
        with open(self.json_db_filepath) as json_db_file:
            json_db = json.load(json_db_file)

        self._generate_enum_definitions(json_db)
        self._generate_message_definitions(json_db)
        self._generate_response_definition()

    def __delete__(self):
        if self._json_db:
            DECODERS_DLL.common_jsonreader_delete(self._json_db)

    @property
    def json_db_filepath(self):
        return self._json_db_filepath

    @json_db_filepath.setter
    def json_db_filepath(self, db_fp: str):
        self._json_db_filepath = db_fp
        if self._json_db:
            self._json_db = DECODERS_DLL.common_jsonreader_delete(self._json_db)
            self._json_db = DECODERS_DLL.common_jsonreader_init(self.json_db_filepath.encode())

    def get_dll_reference(self):
        return self._json_db

    def _generate_and_write_class_string(self, fp, cls, super_name: str = None):
        class_name = super_name + '_' + cls.__name__ if super_name else cls.__name__
        class_string = f'class {cls.__name__}(Structure, BaseStructMixin):\n'
        class_string += '    _pack_ = 1\n'
        class_string += '    _fields_ = [\n'
        for field in cls._fields_:
            # Is this an array of a structure we generated?
            if 'Array' in field[1].__name__ and field[1]._type_ not in self.novtypes_to_ctypes_dict.values():
                self._generate_and_write_class_string(fp, field[1]._type_, class_name)

            class_string += f'        (\'{field[0]}\', {field[1].__name__}),\n'
        class_string += '    ]\n\n'
        fp.write(class_string)

    def generate_documentation(self):
        """Generates a Python file of structures for message definitions.
        """
        with open(f'msg_structures.py', 'w') as msg_def_fp:
            msg_def_fp.write('from ctypes import *\n\n')
            for msg_id in self.message_definitions:
                for message_crc in self.message_definitions[msg_id]:
                    msg_class = self.message_definitions[msg_id][message_crc]
                    self._generate_and_write_class_string(msg_def_fp, msg_class)

    def get_message_definition_structure(self, message_id: str, message_crc: str):
        return self.message_definitions[message_id][message_crc]

    def _generate_enum_definitions(self, json_db: dict):
        for enum_def in json_db['enums']:
            enum_id = enum_def['_id']
            enum_name = enum_def['name']
            enum_values = {enum['name']: enum['value'] for enum in enum_def['enumerators']}
            self.enum_definitions[enum_id] = Enum(enum_name, enum_values)

    def _generate_message_definitions(self, json_db: dict):
        for msg_def in json_db['messages']:
            msg_id = msg_def['messageID']

            for msg_version in msg_def['fields']:
                message_crc = int(msg_version)
                msg_def_fields = list()
                struct_name = f'{msg_def["name"]}_{msg_id}_{message_crc}'

                for field in msg_def['fields'][msg_version]:
                    field_type = self._novtype_to_ctype(field, struct_name)
                    if not field_type:
                        raise f'A critical error occurred when parsing {struct_name}.{field}'

                    if field['type'] in ['FIELD_ARRAY', 'VARIABLE_LENGTH_ARRAY']:
                        msg_def_fields.append((field['name'] + '_length', c_uint32))
                    msg_def_fields.append((field['name'], field_type))

                self.message_definitions[msg_id][message_crc] = self._struct_factory(struct_name, msg_def_fields)

    def _novtype_to_ctype(self, nov_field: dict, super_name: str) -> type:
        field_type = nov_field['type']
        if field_type in ['SIMPLE', 'ENUM', 'STRING', 'RESPONSE_ID', 'RESPONSE_STR', 'FIXED_LENGTH_ARRAY',
                          'VARIABLE_LENGTH_ARRAY']:
            if nov_field['arrayLength']:
                # Ensure 4-byte alignment for fixed and variable-length arrays.
                padding = 0
                if (nov_field['arrayLength'] % 4) != 0:
                    padding = (4 - (nov_field['arrayLength'] % 4))
                return self.novtypes_to_ctypes_dict[nov_field['dataType']['name']] * (nov_field['arrayLength'] + padding)
            else:
                return self.novtypes_to_ctypes_dict[nov_field['dataType']['name']]
        elif field_type == "FIELD_ARRAY":
            sub_fields_size = 0
            sub_fields = list()
            struct_name = f'{super_name}_{nov_field["name"]}' if super_name else nov_field['name']
            for field in nov_field['fields']:
                ctype_field = self._novtype_to_ctype(field, struct_name)
                sub_fields.append((field['name'], ctype_field))
                sub_fields_size += sizeof(ctype_field)
            # Ensure 4-byte alignment for field arrays.
            if (sub_fields_size % 4) != 0:
                sub_fields.append(('_padding', c_uint8 * (4 - (sub_fields_size % 4))))
            return self._struct_factory(struct_name, sub_fields) * nov_field['arrayLength']
        elif field_type in ['RXCONFIG_HEADER', 'RXCONFIG_BODY']:
            raise 'EDIE currently does not support the RXCONFIG_HEADER and RXCONFIG_BODY type.'
        else:
            raise f'Failed to translate type: {field_type}'

    def _struct_factory(self, name: str, fields) -> type:
        return type(name, (Structure, BaseStructMixin), {"_pack_": 1, "_fields_": fields})

    def _generate_response_definition(self):
        self.response_definition = type(
            'RESPONSE_0_0',
            (Structure, BaseStructMixin),
            {
                "_pack_": 1,
                "_fields_":
                    [
                        ('id', c_ulong),
                        ('str', c_char_p)
                    ]
            }
        )

    def convert_response_to_structure(self, message: str) -> type:
        response = self.response_definition()
        response.id = int.from_bytes(message[:3], byteorder='little')
        response.str = message[4:]  # There is no b'\0' in this string, responses never contain it.

        return response

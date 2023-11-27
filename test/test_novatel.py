"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Unit tests for NovAtel logs.
"""
import os
import unittest

from novatel_edie.decoders import common, jsonreader, novatel


# -------------------------------------------------------------------------------------------------------
# Global Helper Functions
# -------------------------------------------------------------------------------------------------------
def CompareMetaData(test_meta_data, expected_meta_data):
    result = True
    if test_meta_data.format != expected_meta_data.format:
        print(f'MetaData.format (expected {expected_meta_data.format}, got {test_meta_data.format})')
        result = False
    if test_meta_data.measurement_source != expected_meta_data.measurement_source:
        print(
            f'MetaData.measurement_source (expected {expected_meta_data.measurement_source}, got {test_meta_data.measurement_source})')
        result = False
    if test_meta_data.time_status != expected_meta_data.time_status:
        print(f'MetaData.time_status (expected {expected_meta_data.time_status}, got {test_meta_data.time_status})')
        result = False
    if test_meta_data.response != expected_meta_data.response:
        print(f'MetaData.response (expected {expected_meta_data.response}, got {test_meta_data.response})')
        result = False
    if test_meta_data.week != expected_meta_data.week:
        print(f'MetaData.week (expected {expected_meta_data.week}, got {test_meta_data.week})')
        result = False
    if test_meta_data.milliseconds != expected_meta_data.milliseconds:
        print(f'MetaData.milliseconds (expected {expected_meta_data.milliseconds}, got {test_meta_data.milliseconds})')
        result = False
    if test_meta_data.binary_msg_length != expected_meta_data.binary_msg_length:
        print(
            f'MetaData.binary_msg_length (expected {expected_meta_data.binary_msg_length}, got {test_meta_data.binary_msg_length})')
        result = False
    if test_meta_data.length != expected_meta_data.length:
        print(f'MetaData.length (expected {expected_meta_data.length}, got {test_meta_data.length})')
        result = False
    if test_meta_data.header_length != expected_meta_data.header_length:
        print(
            f'MetaData.header_length (expected {expected_meta_data.header_length}, got {test_meta_data.header_length})')
        result = False
    if test_meta_data.message_id != expected_meta_data.message_id:
        print(f'MetaData.message_id (expected {expected_meta_data.message_id}, got {test_meta_data.message_id})')
        result = False
    if test_meta_data.message_crc != expected_meta_data.message_crc:
        print(f'MetaData.message_crc (expected {expected_meta_data.message_crc}, got {test_meta_data.message_crc})')
        result = False
    return result


def CompareLogData(test_message_data, expected_message_data):
    result = True
    if test_message_data.header_length != expected_message_data.header_length:
        print(
            f'LogData.header_length (expected {expected_message_data.header_length}, got {test_message_data.header_length})')
        result = False
    if test_message_data.body_length != expected_message_data.body_length:
        print(
            f'LogData.body_length (expected {expected_message_data.body_length}, got {test_message_data.body_length})')
        result = False
    if test_message_data.message_length != expected_message_data.message_length:
        print(
            f'LogData.message_length (expected {expected_message_data.message_length}, got {test_message_data.message_length})')
        result = False
    if (test_message_data.header[:test_message_data.header_length] != expected_message_data.header[
                                                                      :expected_message_data.header_length]):
        print(f'LogData.header contents do not match')
        result = False
    if (test_message_data.body[:test_message_data.body_length] != expected_message_data.body[
                                                                  :expected_message_data.body_length]):
        print(f'LogData.body contents do not match')
        result = False
    if (test_message_data.message[:test_message_data.message_length] != expected_message_data.message[
                                                                        :expected_message_data.message_length]):
        print(f'LogData.message contents do not match')
        result = False
    return result


# -------------------------------------------------------------------------------------------------------
# Framer Unit Tests
# -------------------------------------------------------------------------------------------------------
class TestFramer(unittest.TestCase):
    framer = novatel.Framer()

    def WriteBytesToFramer(self, data):
        self.assertEqual(len(data), self.framer.write(data))

    def WriteFileToFramer(self, filename):
        with open(filename, 'rb') as input_file:
            data = input_file.read()
            self.framer.write(data)
            input_file.close()
        return data

    def FlushFramer(self):
        while True:
            flushed_bytes, num_bytes = self.framer.flush()
            if num_bytes == 0:
                break

    # -------------------------------------------------------------------------------------------------------
    # Ascii Framer Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_ASCII_COMPLETE(self):
        self.FlushFramer()

        data = b'GARBAGE_DATA#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1112,\"\",0.000,0.000,18,18,18,0,00,02,11,01*c3194e35\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 12
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:12], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 217
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-217:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_INCOMPLETE(self):
        self.FlushFramer()

        data = b'#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 165
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_SYNC_ERROR(self):
        self.FlushFramer()

        data = self.WriteFileToFramer(os.path.join(os.path.dirname(__file__), 'resources/ascii_sync_error.ASC'))
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = common.MAX_ASCII_MESSAGE_LENGTH
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:common.MAX_ASCII_MESSAGE_LENGTH], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_BAD_CRC(self):
        self.FlushFramer()

        data = b'#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1112,\"\",0.000,0.000,18,18,18,0,00,02,11,01*ffffffff\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 217
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_RUN_ON_CRC(self):
        self.FlushFramer()

        data = b'#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1112,\"\",0.000,0.000,18,18,18,0,00,02,11,01*c3194e35ff\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 219
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_BYTE_BY_BYTE(self):
        self.FlushFramer()

        data = b'#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1112,\"\",0.000,0.000,18,18,18,0,00,02,11,01*c3194e35\r\n'
        remaining_bytes = len(data)
        expected_meta_data = novatel.MetaDataStruct()
        expected_meta_data.length = 0

        while True:
            self.WriteBytesToFramer(data[expected_meta_data.length].to_bytes(1, 'big'))
            remaining_bytes -= 1
            expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
            expected_meta_data.length = len(data) - remaining_bytes

            status, frame, meta_data = self.framer.read()

            if remaining_bytes >= common.OEM4_ASCII_CRC_LENGTH + 2:
                self.assertEqual(common.STATUS.INCOMPLETE, status)
                self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

            if remaining_bytes == 0:
                break

        expected_meta_data.length = 217

        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_SEGMENTED(self):
        self.FlushFramer()

        data = b'#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1112,\"\",0.000,0.000,18,18,18,0,00,02,11,01*c3194e35\r\n'
        bytes_written = 0
        expected_meta_data = novatel.MetaDataStruct()

        # Sync bytes
        bytes_written += 1
        self.WriteBytesToFramer(data[:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Header
        bytes_written += 70
        self.WriteBytesToFramer(data[1:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Body
        bytes_written += 135
        self.WriteBytesToFramer(data[(1 + 70):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC Delimiter
        bytes_written += 1
        self.WriteBytesToFramer(data[(1 + 70 + 135):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC + CRLF
        bytes_written += common.OEM4_ASCII_CRC_LENGTH + 2
        self.WriteBytesToFramer(data[(1 + 70 + 135 + 1):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_ASCII_TRICK(self):
        self.FlushFramer()

        data = b'#TEST;*ffffffff\r\n#;*\r\n#BESTPOSA,COM1,0,83.5,FINESTEERING,2163,329760.000,02400000,b1f6,65535;SOL_COMPUTED,SINGLE,51.15043874397,-114.03066788586,1097.6822,-17.0000,WGS84,1.3648,1.1806,3.1112,\"\",0.000,0.000,18,18,18,0,00,02,11,01*c3194e35\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 17
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:17], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 5
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[17:22], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 217
        expected_meta_data.format = novatel.HeaderFormatEnum.ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-217:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    # -------------------------------------------------------------------------------------------------------
    # Binary Framer Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_BINARY_COMPLETE(self):
        self.FlushFramer()

        # "GARBAGE_DATA<binary bestpos message>"
        data = b'\x47\x41\x52\x42\x41\x47\x45\x5F\x44\x41\x54\x41\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x15\x15\x00\x00\x02\x11\x01\x55\xCE\xC3\x89'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 12
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:12], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 104
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-104:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_INCOMPLETE(self):
        self.FlushFramer()

        # "<incomplete binary bestpos message>"
        data = b'\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 82
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_SYNC_ERROR(self):
        self.FlushFramer()

        data = self.WriteFileToFramer(os.path.join(os.path.dirname(__file__), 'resources/binary_sync_error.BIN'))
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = common.MAX_BINARY_MESSAGE_LENGTH
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:common.MAX_BINARY_MESSAGE_LENGTH], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_BAD_CRC(self):
        self.FlushFramer()

        # "<binary bestpos message>"
        data = b'\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x15\x15\x00\x00\x02\x11\x01\x55\xCE\xC3\xFF'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 57
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:57], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_RUN_ON_CRC(self):
        self.FlushFramer()

        # "<binary bestpos message>\xFF\xFF"
        data = b'\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x15\x15\x00\x00\x02\x11\x01\x55\xCE\xC3\x89\xFF\xFF'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 104
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 2
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_BYTE_BY_BYTE(self):
        self.FlushFramer()

        # "<binary bestpos message>"
        data = b'\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x15\x15\x00\x00\x02\x11\x01\x55\xCE\xC3\x89'
        remaining_bytes = len(data)
        expected_meta_data = novatel.MetaDataStruct()
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        expected_meta_data.length = 0

        while True:
            self.WriteBytesToFramer(data[expected_meta_data.length].to_bytes(1, 'big'))
            remaining_bytes -= 1
            expected_meta_data.length = len(data) - remaining_bytes

            status, frame, meta_data = self.framer.read()

            if expected_meta_data.length == common.OEM4_BINARY_SYNC_LENGTH:
                expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value

            if remaining_bytes > 0:
                self.assertEqual(common.STATUS.INCOMPLETE, status)
                self.assertTrue(CompareMetaData(meta_data, expected_meta_data))
            else:
                break

        expected_meta_data.length = 104

        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_SEGMENTED(self):
        self.FlushFramer()

        data = b'\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x15\x15\x00\x00\x02\x11\x01\x55\xCE\xC3\x89'
        bytes_written = 0
        expected_meta_data = novatel.MetaDataStruct()

        # Sync bytes
        bytes_written += common.OEM4_BINARY_SYNC_LENGTH
        self.WriteBytesToFramer(data[:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Header
        bytes_written += common.OEM4_BINARY_HEADER_LENGTH - common.OEM4_BINARY_SYNC_LENGTH
        self.WriteBytesToFramer(data[common.OEM4_BINARY_SYNC_LENGTH:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Body
        bytes_written += 72
        self.WriteBytesToFramer(data[common.OEM4_BINARY_HEADER_LENGTH:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC
        bytes_written += common.OEM4_BINARY_CRC_LENGTH
        self.WriteBytesToFramer(data[(common.OEM4_BINARY_HEADER_LENGTH + 72):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_BINARY_TRICK(self):
        self.FlushFramer()

        data = b'\xAA\x44\x12\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\xAA\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA3\xB4\x73\x08\x98\x74\xA8\x13\x00\x00\x00\x02\xF6\xB1\xFF\xFF\x00\x00\x00\x00\x10\x00\x00\x00\xFC\xAB\xE1\x82\x41\x93\x49\x40\xBA\x32\x86\x8A\xF6\x81\x5C\xC0\x00\x10\xE5\xDF\x71\x23\x91\x40\x00\x00\x88\xC1\x3D\x00\x00\x00\x24\x21\xA5\x3F\xF1\x8F\x8F\x3F\x43\x74\x3C\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x15\x15\x00\x00\x02\x11\x01\x55\xCE\xC3\x89'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = common.OEM4_BINARY_SYNC_LENGTH
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:common.OEM4_BINARY_SYNC_LENGTH], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 15
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[common.OEM4_BINARY_SYNC_LENGTH:18], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 1
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[18:19], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 104
        expected_meta_data.format = novatel.HeaderFormatEnum.BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-104:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    # -------------------------------------------------------------------------------------------------------
    # Short Ascii Framer Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_SHORT_ASCII_COMPLETE(self):
        self.FlushFramer()

        data = b'GARBAGE_DATA%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215194,-41188,-9895*a5db8c7b\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 12
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:12], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 120
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-120:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_ASCII_INCOMPLETE(self):
        self.FlushFramer()

        data = b'%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 93
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_ASCII_SYNC_ERROR(self):
        self.FlushFramer()

        data = self.WriteFileToFramer(os.path.join(os.path.dirname(__file__), 'resources/short_ascii_sync_error.ASC'))
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = common.MAX_ASCII_MESSAGE_LENGTH
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:common.MAX_ASCII_MESSAGE_LENGTH], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_ASCII_BAD_CRC(self):
        self.FlushFramer()

        data = b'%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215194,-41188,-9895*ffffffff\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 120
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_ASCII_RUN_ON_CRC(self):
        self.FlushFramer()

        data = b'%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215194,-41188,-9895*a5db8c7bff\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 122
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))
        self.FlushFramer()

    def test_SHORT_ASCII_BYTE_BY_BYTE(self):
        self.FlushFramer()

        data = b'%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215194,-41188,-9895*a5db8c7b\r\n'
        remaining_bytes = len(data)
        expected_meta_data = novatel.MetaDataStruct()
        expected_meta_data.length = 0

        while True:
            self.WriteBytesToFramer(data[expected_meta_data.length].to_bytes(1, 'big'))
            remaining_bytes -= 1
            expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
            expected_meta_data.length = len(data) - remaining_bytes

            status, frame, meta_data = self.framer.read()

            if remaining_bytes >= common.OEM4_ASCII_CRC_LENGTH + 2:
                self.assertEqual(common.STATUS.INCOMPLETE, status)
                self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

            if remaining_bytes == 0:
                break

        expected_meta_data.length = 120

        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_ASCII_SEGMENTED(self):
        self.FlushFramer()

        data = b'%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215194,-41188,-9895*a5db8c7b\r\n'
        bytes_written = 0
        expected_meta_data = novatel.MetaDataStruct()

        # Sync bytes
        bytes_written += 1
        self.WriteBytesToFramer(data[:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Header
        bytes_written += 26
        self.WriteBytesToFramer(data[1:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Body
        bytes_written += 82
        self.WriteBytesToFramer(data[(1 + 26):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC Delimiter
        bytes_written += 1
        self.WriteBytesToFramer(data[(1 + 26 + 82):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC + CRLF
        bytes_written += 8 + 2
        self.WriteBytesToFramer(data[(1 + 26 + 82 + 1):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_ASCII_TRICK(self):
        self.FlushFramer()

        data = b'%;*\r\n%%**\r\n%RAWIMUSXA,1692,484620.664;00,11,1692,484620.664389000,00801503,43110635,-817242,-202184,-215194,-41188,-9895*a5db8c7b\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 5
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:5], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 1
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[5:6], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 5
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[6:11], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 120
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_ASCII.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-120:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    # -------------------------------------------------------------------------------------------------------
    # Short Binary Framer Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_SHORT_BINARY_COMPLETE(self):
        self.FlushFramer()

        # "GARBAGE_DATA<binary bestpos message>"
        data = b'\x47\x41\x52\x42\x41\x47\x45\x5F\x44\x41\x54\x41\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87\xF3\xFF\x38\xEA\xFC\xFF\x66\xB7\xFC\xFF\x1C\x5F\xFF\xFF\x59\xD9\xFF\xFF\x47\x5F\xAF\xBA'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 12
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:12], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 56
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-56:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_INCOMPLETE(self):
        self.FlushFramer()

        # "<incomplete binary bestpos message>"
        data = b'\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 34
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_SYNC_ERROR(self):
        self.FlushFramer()

        data = self.WriteFileToFramer(os.path.join(os.path.dirname(__file__), 'resources/short_binary_sync_error.BIN'))
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 320  # We will be cut off by the maximum size of a SHORT_BINARY message
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:320], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_BAD_CRC(self):
        self.FlushFramer()

        # "<binary bestpos message>"
        data = b'\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87\xF3\xFF\x38\xEA\xFC\xFF\x66\xB7\xFC\xFF\x1C\x5F\xFF\xFF\x59\xD9\xFF\xFF\x47\x5F\xAF\xFF'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 56
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:56], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_RUN_ON_CRC(self):
        self.FlushFramer()

        # "<binary bestpos message>\xFF\xFF"
        data = b'\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87\xF3\xFF\x38\xEA\xFC\xFF\x66\xB7\xFC\xFF\x1C\x5F\xFF\xFF\x59\xD9\xFF\xFF\x47\x5F\xAF\xBA\xFF\xFF'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 56
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 2
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_BYTE_BY_BYTE(self):
        self.FlushFramer()

        # "<short binary rawimusx message>"
        data = b'\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87\xF3\xFF\x38\xEA\xFC\xFF\x66\xB7\xFC\xFF\x1C\x5F\xFF\xFF\x59\xD9\xFF\xFF\x47\x5F\xAF\xBA'
        remaining_bytes = len(data)
        expected_meta_data = novatel.MetaDataStruct()
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        expected_meta_data.length = 0

        while True:
            self.WriteBytesToFramer(data[expected_meta_data.length].to_bytes(1, 'big'))
            remaining_bytes -= 1
            expected_meta_data.length = len(data) - remaining_bytes

            status, frame, meta_data = self.framer.read()

            if expected_meta_data.length == common.OEM4_SHORT_BINARY_SYNC_LENGTH:
                expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value

            if remaining_bytes > 0:
                self.assertEqual(common.STATUS.INCOMPLETE, status)
                self.assertTrue(CompareMetaData(meta_data, expected_meta_data))
            else:
                break

        expected_meta_data.length = 56

        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_SEGMENTED(self):
        self.FlushFramer()

        # "<short binary rawimusx message>"
        data = b'\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87\xF3\xFF\x38\xEA\xFC\xFF\x66\xB7\xFC\xFF\x1C\x5F\xFF\xFF\x59\xD9\xFF\xFF\x47\x5F\xAF\xBA'
        bytes_written = 0
        expected_meta_data = novatel.MetaDataStruct()

        # Sync bytes
        bytes_written += common.OEM4_SHORT_BINARY_SYNC_LENGTH
        self.WriteBytesToFramer(data[:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Header
        bytes_written += common.OEM4_SHORT_BINARY_HEADER_LENGTH - common.OEM4_SHORT_BINARY_SYNC_LENGTH
        self.WriteBytesToFramer(data[common.OEM4_SHORT_BINARY_SYNC_LENGTH:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Body
        bytes_written += 40
        self.WriteBytesToFramer(data[common.OEM4_SHORT_BINARY_HEADER_LENGTH:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC
        bytes_written += common.OEM4_BINARY_CRC_LENGTH
        self.WriteBytesToFramer(data[(common.OEM4_SHORT_BINARY_HEADER_LENGTH + 40):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[:bytes_written], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_SHORT_BINARY_TRICK(self):
        self.FlushFramer()

        # "<short binary sync><short binary sync + part header><short binary sync 1><short binary rawimusx message>"
        data = b'\xAA\x44\x13\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xAA\xAA\x44\x13\x28\xB6\x05\x9C\x06\x78\xB9\xE2\x1C\x00\x0B\x9C\x06\x0B\x97\x55\xA8\x32\x94\x1D\x41\x03\x15\x80\x00\xEB\xD0\x91\x02\xA6\x87\xF3\xFF\x38\xEA\xFC\xFF\x66\xB7\xFC\xFF\x1C\x5F\xFF\xFF\x59\xD9\xFF\xFF\x47\x5F\xAF\xBA\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 3
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:3], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 10
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[3:13], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 1
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[13:14], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 56
        expected_meta_data.format = novatel.HeaderFormatEnum.SHORT_BINARY.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[14:70], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 116
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[-116:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    # -------------------------------------------------------------------------------------------------------
    # NMEA Framer Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_NMEA_COMPLETE(self):
        self.FlushFramer()

        data = b'GARBAGE_DATA$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc421,f80,ffe*29\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 12
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:12], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 82
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-82:], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_INCOMPLETE(self):
        self.FlushFramer()

        data = b'$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc4'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 67
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_SYNC_ERROR(self):
        self.FlushFramer()

        data = self.WriteFileToFramer(os.path.join(os.path.dirname(__file__), 'resources/nmea_sync_error.txt'))
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 312
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:312], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_BAD_CRC(self):
        self.FlushFramer()

        data = b'$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc421,f80,ffe*11\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 82
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_RUN_ON_CRC(self):
        self.FlushFramer()

        data = b'$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc421,f80,ffe*29ff\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 84
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data, frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_BYTE_BY_BYTE(self):
        self.FlushFramer()

        data = b'$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc421,f80,ffe*29\r\n'
        remaining_bytes = len(data)

        expected_meta_data = novatel.MetaDataStruct()
        expected_meta_data.length = 0
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value

        while True:
            self.WriteBytesToFramer(data[expected_meta_data.length].to_bytes(1, 'big'))
            remaining_bytes -= 1
            expected_meta_data.length = len(data) - remaining_bytes

            status, frame, meta_data = self.framer.read()

            if remaining_bytes > 0:
                self.assertEqual(common.STATUS.INCOMPLETE, status)
                self.assertTrue(CompareMetaData(meta_data, expected_meta_data))
            else:
                break

        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_SEGMENTED(self):
        self.FlushFramer()

        data = b'$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc421,f80,ffe*29\r\n'
        bytes_written = 0
        expected_meta_data = novatel.MetaDataStruct()

        # Sync bytes
        bytes_written += 1
        self.WriteBytesToFramer(data[:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # Body
        bytes_written += 76
        self.WriteBytesToFramer(data[1:bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC Delimiter
        bytes_written += 1
        self.WriteBytesToFramer(data[(1 + 76):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRC
        bytes_written += 2
        self.WriteBytesToFramer(data[(1 + 76 + 1):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.INCOMPLETE, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        # CRLF
        bytes_written += 2
        self.WriteBytesToFramer(data[(1 + 76 + 1 + 2):bytes_written])
        expected_meta_data.length = bytes_written
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

    def test_NMEA_TRICK(self):
        self.FlushFramer()

        data = b'$*ff\r\n$$GPALM,30,01,01,2029,00,4310,7b,145f,fd44,a10ce4,1c5b11,0b399f,2bc421,f80,ffe*29\r\n'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 6
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[:6], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 1
        expected_meta_data.format = novatel.HeaderFormatEnum.UNKNOWN.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.UNKNOWN, status)
        self.assertEqual(data[6:7], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))

        expected_meta_data.length = 82
        expected_meta_data.format = novatel.HeaderFormatEnum.NMEA.value
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[-82:], frame)

    # -------------------------------------------------------------------------------------------------------
    # JSON Framer Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_JSON_COMPLETE(self):
        self.FlushFramer()

        data = b'{\"header\": {\"message\": \"BESTSATS\",\"id\": 1194,\"port\": \"COM1\",\"sequence_num\": 0,\"percent_idle_time\": 50.0,\"time_status\": \"FINESTEERING\",\"week\": 2167,\"seconds\": 244820.000,\"receiver_status\": 33554432,\"HEADER_reserved1\": 48645,\"receiver_sw_version\": 16248},\"body\": {\"satellite_entries\": [{\"system_type\": \"GPS\",\"id\": \"2\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"20\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"29\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"13\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"15\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"16\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"18\",\"status\": \"GOOD\",\"status_mask\": 7},{\"system_type\": \"GPS\",\"id\": \"25\",\"status\": \"GOOD\",\"status_mask\": 7},{\"system_type\": \"GPS\",\"id\": \"5\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GPS\",\"id\": \"26\",\"status\": \"GOOD\",\"status_mask\": 7},{\"system_type\": \"GPS\",\"id\": \"23\",\"status\": \"GOOD\",\"status_mask\": 7},{\"system_type\": \"QZSS\",\"id\": \"194\",\"status\": \"SUPPLEMENTARY\",\"status_mask\": 7},{\"system_type\": \"SBAS\",\"id\": \"131\",\"status\": \"NOTUSED\",\"status_mask\": 0},{\"system_type\": \"SBAS\",\"id\": \"133\",\"status\": \"NOTUSED\",\"status_mask\": 0},{\"system_type\": \"SBAS\",\"id\": \"138\",\"status\": \"NOTUSED\",\"status_mask\": 0},{\"system_type\": \"GLONASS\",\"id\": \"8+6\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"9-2\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"1+1\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"24+2\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"2-4\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"17+4\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"16-1\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"18-3\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GLONASS\",\"id\": \"15\",\"status\": \"GOOD\",\"status_mask\": 3},{\"system_type\": \"GALILEO\",\"id\": \"26\",\"status\": \"GOOD\",\"status_mask\": 15},{\"system_type\": \"GALILEO\",\"id\": \"12\",\"status\": \"GOOD\",\"status_mask\": 15},{\"system_type\": \"GALILEO\",\"id\": \"19\",\"status\": \"ELEVATIONERROR\",\"status_mask\": 0},{\"system_type\": \"GALILEO\",\"id\": \"31\",\"status\": \"GOOD\",\"status_mask\": 15},{\"system_type\": \"GALILEO\",\"id\": \"25\",\"status\": \"ELEVATIONERROR\",\"status_mask\": 0},{\"system_type\": \"GALILEO\",\"id\": \"33\",\"status\": \"GOOD\",\"status_mask\": 15},{\"system_type\": \"GALILEO\",\"id\": \"8\",\"status\": \"ELEVATIONERROR\",\"status_mask\": 0},{\"system_type\": \"GALILEO\",\"id\": \"7\",\"status\": \"GOOD\",\"status_mask\": 15},{\"system_type\": \"GALILEO\",\"id\": \"24\",\"status\": \"GOOD\",\"status_mask\": 15},{\"system_type\": \"BEIDOU\",\"id\": \"35\",\"status\": \"LOCKEDOUT\",\"status_mask\": 0},{\"system_type\": \"BEIDOU\",\"id\": \"29\",\"status\": \"SUPPLEMENTARY\",\"status_mask\": 1},{\"system_type\": \"BEIDOU\",\"id\": \"25\",\"status\": \"ELEVATIONERROR\",\"status_mask\": 0},{\"system_type\": \"BEIDOU\",\"id\": \"20\",\"status\": \"SUPPLEMENTARY\",\"status_mask\": 1},{\"system_type\": \"BEIDOU\",\"id\": \"22\",\"status\": \"SUPPLEMENTARY\",\"status_mask\": 1},{\"system_type\": \"BEIDOU\",\"id\": \"44\",\"status\": \"LOCKEDOUT\",\"status_mask\": 0},{\"system_type\": \"BEIDOU\",\"id\": \"57\",\"status\": \"NOEPHEMERIS\",\"status_mask\": 0},{\"system_type\": \"BEIDOU\",\"id\": \"12\",\"status\": \"ELEVATIONERROR\",\"status_mask\": 0},{\"system_type\": \"BEIDOU\",\"id\": \"24\",\"status\": \"SUPPLEMENTARY\",\"status_mask\": 1},{\"system_type\": \"BEIDOU\",\"id\": \"19\",\"status\": \"SUPPLEMENTARY\",\"status_mask\": 1}]}}'
        self.WriteBytesToFramer(data)
        expected_meta_data = novatel.MetaDataStruct()

        expected_meta_data.length = 3464
        expected_meta_data.format = novatel.HeaderFormatEnum.JSON.value

        self.framer.frame_json = True
        status, frame, meta_data = self.framer.read()
        self.assertEqual(common.STATUS.SUCCESS, status)
        self.assertEqual(data[:3464], frame)
        self.assertTrue(CompareMetaData(meta_data, expected_meta_data))
        self.framer.frame_json = False


# -------------------------------------------------------------------------------------------------------
# Decoder/Encoder Unit Tests
# -------------------------------------------------------------------------------------------------------
class TestDecodeEncode(unittest.TestCase):
    json_db = jsonreader.JsonReader()
    json_db.generate_documentation()
    header_decoder = novatel.HeaderDecoder(json_db)
    message_decoder = novatel.MessageDecoder(json_db)
    encoder = novatel.Encoder(json_db)

    def TestSameFormatCompare(self, encode_format, message, meta_data=None):
        meta_data = meta_data or novatel.MetaDataStruct()

        status, h = self.header_decoder.decode(message, meta_data)
        self.assertEqual(status, common.STATUS.SUCCESS)

        status, m = self.message_decoder.decode(message[meta_data.header_length:], meta_data)
        self.assertEqual(status, common.STATUS.SUCCESS)

        status, message_data, _ = self.encoder.encode(h, m, meta_data, encode_format)
        self.assertEqual(status, common.STATUS.SUCCESS)

        self.assertEqual(message_data.message, message)

    # -------------------------------------------------------------------------------------------------------
    # Ascii Decoder Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_ASCII_BESTPOS(self):
        data = b'#BESTPOSA,COM1,0,60.5,FINESTEERING,2166,327153.000,02000000,b1f6,16248;SOL_COMPUTED,WAAS,51.15043699323,-114.03067932462,1096.9772,-17.0000,WGS84,0.6074,0.5792,0.9564,\"131\",7.000,0.000,42,34,34,28,00,0b,1f,37*47bbdc4f\r\n'

        self.TestSameFormatCompare(common.ENCODEFORMAT.ASCII, data)

    def test_ASCII_TRACKSTAT(self):
        data = b'#TRACKSTATA,COM1,0,58.0,FINESTEERING,2166,318996.000,02000000,457c,16248;SOL_COMPUTED,WAAS,5.0,235,2,0,0810bc04,20999784.925,770.496,49.041,8473.355,0.228,GOOD,0.975,2,0,01303c0b,20999781.972,600.387,49.021,8466.896,0.000,OBSL2,0.000,0,0,02208000,0.000,-0.004,0.000,0.000,0.000,NA,0.000,0,0,01c02000,0.000,0.000,0.000,0.000,0.000,NA,0.000,20,0,0810bc24,24120644.940,3512.403,42.138,1624.974,0.464,GOOD,0.588,20,0,01303c2b,24120645.042,2736.937,39.553,1619.755,0.000,OBSL2,0.000,0,0,02208020,0.000,-0.002,0.000,0.000,0.000,NA,0.000,0,0,01c02020,0.000,0.000,0.000,0.000,0.000,NA,0.000,6,0,0810bc44,20727107.371,-1161.109,50.325,11454.975,-0.695,GOOD,0.979,6,0,01303c4b,20727108.785,-904.761,50.213,11448.915,0.000,OBSL2,0.000,6,0,02309c4b,20727109.344,-904.761,52.568,11451.815,0.000,OBSL2,0.000,6,0,01d03c44,20727110.520,-867.070,55.259,11453.455,0.000,OBSL5,0.000,29,0,0810bc64,25296813.545,3338.614,43.675,114.534,-0.170,GOOD,0.206,29,0,01303c6b,25296814.118,2601.518,39.636,109.254,0.000,OBSL2,0.000,29,0,02309c6b,25296814.580,2601.517,40.637,111.114,0.000,OBSL2,0.000,0,0,01c02060,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0000a080,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a02080,0.000,-0.000,0.000,0.000,0.000,NA,0.000,0,0,02208080,0.000,-0.002,0.000,0.000,0.000,NA,0.000,0,0,01c02080,0.000,0.000,0.000,0.000,0.000,NA,0.000,19,0,0810bca4,22493227.199,-3020.625,44.911,18244.973,0.411,GOOD,0.970,19,0,01303cab,22493225.215,-2353.736,44.957,18239.754,0.000,OBSL2,0.000,0,0,022080a0,0.000,-0.006,0.000,0.000,0.000,NA,0.000,0,0,01c020a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,24,0,0810bcc4,23856706.090,-3347.685,43.417,15187.116,-0.358,GOOD,0.957,24,0,01303ccb,23856708.306,-2608.588,43.207,15181.256,0.000,OBSL2,0.000,24,0,02309ccb,23856708.614,-2608.588,46.741,15183.815,0.000,OBSL2,0.000,24,0,01d03cc4,23856711.245,-2499.840,50.038,15185.256,0.000,OBSL5,0.000,25,0,1810bce4,21953295.423,2746.317,46.205,4664.936,0.322,GOOD,0.622,25,0,11303ceb,21953296.482,2139.988,45.623,4658.756,0.000,OBSL2,0.000,25,0,02309ceb,21953296.899,2139.988,47.584,4661.796,0.000,OBSL2,0.000,25,0,01d03ce4,21953298.590,2050.845,51.711,4662.976,0.000,OBSL5,0.000,0,0,0000a100,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a02100,0.000,-0.001,0.000,0.000,0.000,NA,0.000,0,0,02208100,0.000,-0.001,0.000,0.000,0.000,NA,0.000,0,0,01c02100,0.000,0.000,0.000,0.000,0.000,NA,0.000,17,0,1810bd24,24833573.179,-3002.286,43.809,21504.975,-0.219,GOOD,0.903,17,0,11303d2b,24833573.345,-2339.444,42.894,21499.256,0.000,OBSL2,0.000,17,0,02309d2b,24833573.677,-2339.444,44.238,21501.717,0.000,OBSL2,0.000,0,0,01c02120,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0000a140,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a02140,0.000,-0.002,0.000,0.000,0.000,NA,0.000,0,0,02208140,0.000,-0.001,0.000,0.000,0.000,NA,0.000,0,0,01c02140,0.000,0.000,0.000,0.000,0.000,NA,0.000,12,0,0810bd64,20275478.792,742.751,50.336,9634.855,0.166,GOOD,0.977,12,0,01303d6b,20275477.189,578.767,50.042,9629.756,0.000,OBSL2,0.000,12,0,02309d6b,20275477.555,578.767,51.012,9631.516,0.000,OBSL2,0.000,0,0,01c02160,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0000a180,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a02180,0.000,0.002,0.000,0.000,0.000,NA,0.000,0,0,02208180,0.000,0.003,0.000,0.000,0.000,NA,0.000,0,0,01c02180,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0000a1a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a021a0,0.000,-0.000,0.000,0.000,0.000,NA,0.000,0,0,022081a0,0.000,-0.000,0.000,0.000,0.000,NA,0.000,0,0,01c021a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0000a1c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a021c0,0.000,-0.000,0.000,0.000,0.000,NA,0.000,0,0,022081c0,0.000,-0.000,0.000,0.000,0.000,NA,0.000,0,0,01c021c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0000a1e0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a021e0,0.000,0.001,0.000,0.000,0.000,NA,0.000,0,0,022081e0,0.000,0.003,0.000,0.000,0.000,NA,0.000,0,0,01c021e0,0.000,0.000,0.000,0.000,0.000,NA,0.000,194,0,0815be04,43478223.927,63.042,38.698,2382.214,0.000,NODIFFCORR,0.000,194,0,02359e0b,43478226.941,49.122,44.508,2378.714,0.000,OBSL2,0.000,194,0,01d53e04,43478228.121,47.080,43.958,2380.253,0.000,OBSL5,0.000,0,0,0005a220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02258220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01c52220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0005a240,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02258240,0.000,-0.002,0.000,0.000,0.000,NA,0.000,0,0,01c52240,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,0005a260,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02258260,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01c52260,0.000,0.000,0.000,0.000,0.000,NA,0.000,131,0,48023e84,38480992.384,-0.167,45.356,471155.406,0.000,LOCKEDOUT,0.000,135,0,58023ea4,38553658.881,3.771,44.648,4.449,0.000,NODIFFCORR,0.000,133,0,58023ec4,38624746.161,1.065,45.618,471153.219,0.000,LOCKEDOUT,0.000,138,0,48023ee4,38493033.873,0.953,45.833,898498.250,0.000,LOCKEDOUT,0.000,55,4,18119f04,21580157.377,3208.835,44.921,3584.798,0.000,NODIFFCORR,0.000,55,4,00b13f0b,21580163.823,2495.762,45.078,3580.119,0.000,OBSL2,0.000,55,4,10319f0b,21580163.635,2495.762,45.682,3581.038,0.000,OBSL2,0.000,45,13,08119f24,23088997.031,-313.758,44.105,4273.538,0.000,NODIFFCORR,0.000,45,13,00b13f2b,23088998.989,-244.036,42.927,4267.818,0.000,OBSL2,0.000,45,13,00319f2b,23088999.269,-244.036,43.297,4268.818,0.000,OBSL2,0.000,54,11,18119f44,19120160.469,178.235,50.805,9344.977,0.000,NODIFFCORR,0.000,54,11,00b13f4b,19120162.255,138.627,46.584,9339.897,0.000,OBSL2,0.000,54,11,00319f4b,19120162.559,138.627,47.049,9340.818,0.000,OBSL2,0.000,0,0,00018360,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a12360,0.000,0.004,0.000,0.000,0.000,NA,0.000,0,0,00218360,0.000,0.004,0.000,0.000,0.000,NA,0.000,0,0,00018380,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a12380,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00218380,0.000,0.000,0.000,0.000,0.000,NA,0.000,53,6,18119fa4,21330036.443,3045.661,43.167,3862.756,0.000,NODIFFCORR,0.000,53,6,00b13fab,21330040.203,2368.849,41.759,3858.039,0.000,OBSL2,0.000,53,6,00319fab,21330039.119,2368.850,42.691,3859.038,0.000,OBSL2,0.000,38,8,18119fc4,22996582.245,2427.724,41.817,2014.338,0.000,NODIFFCORR,0.000,38,8,10b13fcb,22996590.440,1888.231,35.968,2010.119,0.000,OBSL2,0.000,38,8,10319fcb,22996589.454,1888.230,36.755,2011.038,0.000,OBSL2,0.000,52,7,08119fe4,19520740.266,-1275.394,50.736,10712.179,0.000,NODIFFCORR,0.000,52,7,00b13feb,19520744.583,-991.974,47.931,10708.038,0.000,OBSL2,0.000,52,7,10319feb,19520744.527,-991.974,48.251,10709.038,0.000,OBSL2,0.000,51,0,18119c04,22302364.417,-4314.112,43.692,16603.602,0.000,NODIFFCORR,0.000,51,0,00b13c0b,22302371.827,-3355.424,45.975,16603.580,0.000,OBSL2,0.000,51,0,00319c0b,22302371.325,-3355.424,46.904,16603.502,0.000,OBSL2,0.000,61,9,08119c24,21163674.206,-3198.898,47.898,14680.979,0.000,NODIFFCORR,0.000,61,9,10b13c2b,21163677.196,-2488.033,44.960,14675.897,0.000,OBSL2,0.000,61,9,00319c2b,21163677.300,-2488.033,45.628,14676.737,0.000,OBSL2,0.000,0,0,00018040,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a12040,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00218040,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00018060,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a12060,0.000,-0.000,0.000,0.000,0.000,NA,0.000,0,0,00218060,0.000,-0.001,0.000,0.000,0.000,NA,0.000,0,0,00018080,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a12080,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00218080,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,000180a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00a120a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,002180a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,004380c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,018320c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,022320c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,028320c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,21,0,08539ce4,25416828.004,2077.626,46.584,6337.363,0.000,NODIFFCORR,0.000,21,0,01933ce4,25416833.286,1551.460,49.589,6335.164,0.000,OBSE5,0.000,21,0,02333ce4,25416829.717,1591.910,50.226,6335.176,0.000,OBSE5,0.000,21,0,02933ce4,25416829.814,1571.722,52.198,6334.944,0.000,OBSE5,0.000,27,0,08539d04,23510780.996,-707.419,51.721,16182.524,0.000,NODIFFCORR,0.000,27,0,01933d04,23510785.247,-528.262,53.239,16180.444,0.000,OBSE5,0.000,27,0,02333d04,23510781.458,-542.015,53.731,16180.243,0.000,OBSE5,0.000,27,0,02933d04,23510781.960,-535.149,55.822,16180.165,0.000,OBSE5,0.000,0,0,00438120,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832120,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232120,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832120,0.000,0.000,0.000,0.000,0.000,NA,0.000,15,0,08539d44,23034423.020,183.445,51.283,11971.245,0.000,NODIFFCORR,0.000,15,0,01933d44,23034428.761,136.945,53.293,11969.243,0.000,OBSE5,0.000,15,0,02333d44,23034425.379,140.546,53.897,11969.245,0.000,OBSE5,0.000,15,0,02933d44,23034425.436,138.742,55.909,11968.946,0.000,OBSE5,0.000,13,0,08539d64,25488681.795,2565.988,46.632,4828.445,0.000,NODIFFCORR,0.000,13,0,01933d64,25488687.213,1916.182,47.753,4826.243,0.000,OBSE5,0.000,13,0,02333d64,25488683.967,1966.148,50.045,4826.243,0.000,OBSE5,0.000,13,0,02933d64,25488684.398,1941.169,51.348,4826.165,0.000,OBSE5,0.000,0,0,00438180,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832180,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232180,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832180,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,004381a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,018321a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,022321a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,028321a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,004381c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,018321c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,022321c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,028321c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,30,0,08539de4,25532715.149,-2938.485,46.289,26421.467,0.000,NODIFFCORR,0.000,30,0,01933de4,25532721.371,-2194.317,49.285,26419.447,0.000,OBSE5,0.000,30,0,02333de4,25532718.174,-2251.520,50.681,26419.447,0.000,OBSE5,0.000,30,0,02933de4,25532717.843,-2222.952,52.291,26419.166,0.000,OBSE5,0.000,0,0,00438200,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832200,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232200,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832200,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00438220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832220,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00438240,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832240,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232240,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832240,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00438260,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832260,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232260,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832260,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,00438280,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,01832280,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02232280,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,02832280,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,004382a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,018322a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,022322a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,0,0,028322a0,0.000,0.000,0.000,0.000,0.000,NA,0.000,41,0,48149ec4,26228546.068,2731.326,43.047,1244.968,0.000,NODIFFCORR,0.000,41,0,41343ec4,26228560.733,2058.212,46.309,1239.648,0.000,NA,0.000,27,0,08149ee4,21470141.903,-686.571,51.408,13695.229,0.000,NODIFFCORR,0.000,27,0,41343ee4,21470143.417,-517.430,52.724,13690.050,0.000,NA,0.000,6,0,08149f04,40334269.953,-663.889,38.200,12755.121,0.000,NODIFFCORR,0.000,6,0,00349f04,40334265.525,-513.549,39.333,12754.961,0.000,OBSB2,0.000,16,0,08149f24,40591561.211,-689.953,40.783,11755.120,0.000,NODIFFCORR,0.000,16,0,00349f24,40591562.100,-533.388,39.928,11754.960,0.000,OBSB2,0.000,39,0,58149f44,40402963.125,-730.398,41.019,11015.042,0.000,NODIFFCORR,0.000,39,0,41343f44,40402964.083,-550.456,43.408,11009.821,0.000,NA,0.000,30,0,18149f64,22847646.673,2123.913,50.266,6625.051,0.000,NODIFFCORR,0.000,30,0,41343f64,22847649.151,1600.605,49.656,6619.991,0.000,NA,0.000,7,0,08048381,0.000,2500.000,0.000,0.000,0.000,NA,0.000,7,0,08048381,0.000,-2500.000,0.000,0.000,0.000,NA,0.000,33,0,48149fa4,25666349.147,776.929,42.271,3835.148,0.000,NODIFFCORR,0.000,33,0,41343fa4,25666377.385,585.535,48.361,3697.589,0.000,NA,0.000,46,0,48149fc4,23048323.129,-2333.170,49.345,15915.131,0.000,NODIFFCORR,0.000,46,0,41343fc4,23048329.413,-1758.350,52.408,15909.830,0.000,NA,0.000,18,0,080483e1,0.000,4000.000,0.000,0.000,0.000,NA,0.000,18,0,080483e1,0.000,-500.000,0.000,0.000,0.000,NA,0.000,45,0,48149c04,26221109.945,2965.644,44.864,435.050,0.000,NODIFFCORR,0.000,45,0,41343c04,26221119.956,2234.910,47.292,429.831,0.000,NA,0.000,36,0,58149c24,23277715.056,700.443,48.907,8015.069,0.000,NODIFFCORR,0.000,36,0,41343c24,23277723.101,527.848,51.167,8009.829,0.000,NA,0.000,52,0,08048041,0.000,1667.000,0.000,0.000,0.000,NA,0.000,52,0,08048041,0.000,-4166.000,0.000,0.000,0.000,NA,0.000,49,0,08048061,0.000,5832.000,0.000,0.000,0.000,NA,0.000,49,0,08048061,0.000,-4999.000,0.000,0.000,0.000,NA,0.000,47,0,08048081,0.000,1000.000,0.000,0.000,0.000,NA,0.000,47,0,08048081,0.000,-500.000,0.000,0.000,0.000,NA,0.000,58,0,48049ca4,34894393.899,-3079.127,30.345,47.772,0.000,NODIFFCORR,0.000,58,0,012420a9,0.000,-2321.139,0.000,0.000,0.000,NA,0.000,14,0,08149cc4,25730238.361,-588.324,38.191,4795.070,0.000,NODIFFCORR,0.000,14,0,00349cc4,25730237.379,-454.787,44.427,4794.910,0.000,OBSB2,0.000,28,0,08149ce4,24802536.288,-2833.581,46.004,19865.129,0.000,NODIFFCORR,0.000,28,0,41343ce4,24802537.579,-2135.389,46.897,19859.650,0.000,NA,0.000,48,0,08048101,0.000,16000.000,0.000,0.000,0.000,NA,0.000,0,0,00248100,0.000,0.000,0.000,0.000,0.000,NA,0.000,9,0,08149d24,40753569.155,222.237,37.682,1784.493,0.000,NODIFFCORR,0.000,9,0,00349d24,40753568.209,171.813,41.501,4664.961,0.000,OBSB2,0.000,3,0,08848141,0.000,6000.000,0.000,0.000,0.000,NA,0.000,3,0,08848141,0.000,-11000.000,0.000,0.000,0.000,NA,0.000,1,0,08848161,0.000,4999.000,0.000,0.000,0.000,NA,0.000,1,0,08848161,0.000,-4166.000,0.000,0.000,0.000,NA,0.000,6,0,0a670984,0.000,-301.833,36.924,1734607.250,0.000,NA,0.000,1,0,0a6709a4,0.000,83.304,43.782,558002.188,0.000,NA,0.000,0,0,026701c0,0.000,0.000,0.000,0.000,0.000,NA,0.000,3,0,0a6701e1,0.000,419.842,0.000,0.000,0.000,NA,0.000,0,0,02670200,0.000,0.000,0.000,0.000,0.000,NA,0.000*c8963f70\r\n'

        self.TestSameFormatCompare(common.ENCODEFORMAT.ASCII, data)

    def test_ASCII_LOGLIST(self):
        data = b'#LOGLISTA,COM1,0,63.5,FINESTEERING,2172,164226.000,02010000,c00c,16248;6,COM1,RXSTATUSEVENTA,ONNEW,0.000000,0.000000,HOLD,COM1,INTERFACEMODE,ONTIME,20.000000,0.000000,NOHOLD,COM1,LOGLISTA,ONCE,0.000000,0.000000,NOHOLD,COM2,RXSTATUSEVENTA,ONNEW,0.000000,0.000000,HOLD,CCOM1,INSPVACMPB,ONTIME,0.050000,0.000000,HOLD,CCOM1,INSPVASDCMPB,ONTIME,1.000000,0.000000,HOLD*53104c0f\r\n'

        self.TestSameFormatCompare(common.ENCODEFORMAT.ASCII, data)

    def test_ASCII_VERSION(self):
        data = b'#VERSIONA,COM1,0,55.5,FINESTEERING,2167,254938.857,02000000,3681,16248;8,GPSCARD,\"FFNBYNTMNP1\",\"BMHR15470120X\",\"OEM719N-0.00C\",\"OM7CR0707RN0000\",\"OM7BR0000RBG000\",\"2020/Apr/09\",\"13:40:45\",OEM7FPGA,\"\",\"\",\"\",\"OMV070001RN0000\",\"\",\"\",\"\",DEFAULT_CONFIG,\"\",\"\",\"\",\"EZDCD0707RN0001\",\"\",\"2020/Apr/09\",\"13:41:07\",APPLICATION,\"\",\"\",\"\",\"EZAPR0707RN0000\",\"\",\"2020/Apr/09\",\"13:41:00\",PACKAGE,\"\",\"\",\"\",\"EZPKR0103RN0000\",\"\",\"2020/Apr/09\",\"13:41:14\",ENCLOSURE,\"\",\"NMJC14520001W\",\"0.0.0.H\",\"\",\"\",\"\",\"\",IMUCARD,\"Epson G320N 125\",\"E0000114\",\"G320PDGN\",\"2302\",\"\",\"\",\"\",RADIO,\"M3-R4\",\"1843000570\",\"SPL0020d12\",\"V07.34.2.5.1.11\",\"\",\"\",\"\"*4b995016\r\n'

        self.TestSameFormatCompare(common.ENCODEFORMAT.ASCII, data)

    # -------------------------------------------------------------------------------------------------------
    # Binary Decoder Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_BINARY_BESTPOS(self):
        data = b'\xAA\x44\x12\x1C\x2A\x00\x00\x20\x48\x00\x00\x00\xA4\xB4\xAC\x07\xD8\x16\x6D\x08\x08\x40\x00\x02\xF6\xB1\x00\x80\x00\x00\x00\x00\x10\x00\x00\x00\xD7\x03\xB0\x4C\xE5\x8E\x49\x40\x52\xC4\x26\xD1\x72\x82\x5C\xC0\x29\xCB\x10\xC7\x7A\xA2\x90\x40\x33\x33\x87\xC1\x3D\x00\x00\x00\xFA\x7E\xBA\x3F\x3F\x57\x83\x3F\xA9\xA4\x0A\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x16\x16\x16\x16\x00\x06\x39\x33\x23\xC4\x89\x7A'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.BINARY, data, meta_data)

    def test_BINARY_LOGLIST(self):
        data = b'\xAA\x44\x12\x1C\x05\x00\x00\x20\x24\x02\x00\x00\x8B\xB4\x7A\x08\x40\xE9\x72\x18\x20\x08\x00\x02\x0C\xC0\x00\x80\x11\x00\x00\x00\x20\x00\x00\x00\x01\x06\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x20\x00\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x20\x00\x00\x00\x05\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x60\x00\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x05\x00\x00\x01\x06\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x05\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x06\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x07\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x0F\x00\x00\x01\x06\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x0F\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x10\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x11\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x15\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x26\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x27\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\xA0\x28\x00\x00\x5E\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x1A\xE4\x1B\x00'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.BINARY, data, meta_data)

    def test_BINARY_SOURCETABLE(self):
        data = b'\xAA\x44\x12\x1C\x40\x05\x00\x20\x68\x00\x15\x00\x80\xB4\x74\x08\x00\x5B\x88\x0D\x20\x80\x00\x02\xDD\x71\x00\x80\x68\x65\x72\x61\x2E\x6E\x6F\x76\x61\x74\x65\x6C\x2E\x63\x6F\x6D\x3A\x32\x31\x30\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x53\x54\x52\x3B\x48\x79\x64\x65\x72\x61\x62\x61\x64\x5F\x4C\x42\x32\x3B\x3B\x3B\x3B\x3B\x3B\x53\x4E\x49\x50\x3B\x58\x58\x58\x3B\x30\x2E\x30\x30\x3B\x30\x2E\x30\x30\x3B\x30\x3B\x30\x3B\x73\x4E\x54\x52\x49\x50\x3B\x6E\x6F\x6E\x65\x3B\x4E\x3B\x4E\x3B\x30\x3B\x6E\x6F\x6E\x65\x3B\x00\x00\x00\xB9\x6E\x19\x2E'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.BINARY, data, meta_data)

    def test_BINARY_VERSION(self):
        data = b'\xAA\x44\x12\x1C\x25\x00\x00\xA0\xDC\x00\x00\x00\xA8\x14\x00\x00\x89\x58\x00\x00\x20\x40\x4C\x02\x81\x36\x00\x80\x02\x00\x00\x00\x01\x00\x00\x00\x46\x46\x4E\x52\x4E\x4E\x43\x42\x4E\x00\x00\x00\x00\x00\x00\x00\x42\x4D\x47\x57\x31\x39\x33\x39\x30\x31\x36\x34\x5A\x00\x00\x00\x4F\x45\x4D\x37\x31\x39\x2D\x31\x2E\x30\x34\x00\x00\x00\x00\x00\x4F\x4D\x37\x4D\x47\x30\x38\x30\x30\x44\x4E\x30\x30\x30\x30\x00\x4F\x4D\x37\x42\x52\x30\x31\x30\x30\x52\x42\x47\x30\x30\x30\x00\x32\x30\x32\x31\x2F\x41\x70\x72\x2F\x32\x37\x00\x32\x30\x3A\x31\x33\x3A\x33\x38\x00\x00\x00\x00\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4F\x4D\x56\x30\x37\x30\x30\x30\x31\x52\x4E\x30\x30\x30\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x58\x2B\xB8\xDB'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.BINARY, data, meta_data)

    # -------------------------------------------------------------------------------------------------------
    # Flattened Binary Decoder Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_FLATTENED_BINARY_VALIDMODELS(self):
        data = b'\xAA\x44\x12\x1C\xCE\x00\x00\x20\xA4\x02\x00\x00\x89\xB4\x78\x08\x95\xBD\x55\x09\x20\x08\x00\x02\x2F\x34\x00\x80\x01\x00\x00\x00\x46\x46\x4E\x52\x4E\x4E\x43\x42\x4E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\xCA\x02\x1C'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.FLATTENED_BINARY, data, meta_data)

    def test_FLATTENED_BINARY_PORTSTATS(self):
        data = b'\xAA\x44\x12\x1C\x48\x00\x00\x20\x2C\x05\x00\x00\x87\xB4\x78\x08\x80\x6E\x3F\x09\x20\x08\x00\x02\x72\xA8\x00\x80\x17\x00\x00\x00\x01\x00\x00\x00\x4F\x00\x00\x00\x0C\x77\x00\x00\x83\x00\x00\x00\x00\x00\x00\x00\xD8\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1E\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x26\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x27\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x28\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x29\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x41\xDD\x62\x57'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.FLATTENED_BINARY, data, meta_data)

    def test_FLATTENED_BINARY_VERSION(self):
        data = b'\xAA\x44\x12\x1C\x25\x00\x00\x20\x74\x08\x00\x00\x8D\xB4\xA7\x08\xD5\x23\xDD\x08\x20\x00\x00\x02\x81\x36\x00\x80\x04\x00\x00\x00\x01\x00\x00\x00\x46\x46\x4E\x52\x4E\x4E\x43\x42\x4E\x00\x00\x00\x00\x00\x00\x00\x42\x4D\x47\x58\x31\x35\x33\x36\x30\x30\x33\x35\x56\x00\x00\x00\x4F\x45\x4D\x37\x32\x39\x2D\x30\x2E\x30\x30\x48\x00\x00\x00\x00\x4F\x4D\x37\x4D\x47\x30\x38\x31\x30\x44\x4E\x30\x30\x30\x30\x00\x4F\x4D\x37\x42\x52\x30\x30\x30\x30\x41\x42\x47\x30\x30\x31\x00\x32\x30\x32\x32\x2F\x4A\x75\x6E\x2F\x31\x37\x00\x30\x38\x3A\x32\x34\x3A\x30\x36\x00\x00\x00\x00\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x4F\x4D\x56\x30\x37\x30\x30\x30\x31\x52\x4E\x30\x30\x30\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x7A\x3A\x53\x43\x52\x49\x50\x54\x53\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x6C\x6F\x63\x6B\x31\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x50\x61\x63\x6B\x61\x67\x65\x31\x5F\x31\x2E\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x32\x30\x31\x37\x2F\x4F\x63\x74\x2F\x32\x37\x00\x31\x36\x3A\x30\x32\x3A\x35\x34\x00\x00\x00\x00\x08\x00\x7A\x3A\x57\x57\x57\x49\x53\x4F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x57\x4D\x43\x30\x31\x30\x32\x30\x32\x52\x4E\x30\x30\x30\x32\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x32\x30\x31\x37\x2F\x44\x65\x63\x2F\x31\x35\x00\x39\x3A\x30\x38\x3A\x35\x36\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xA7\x38\xDE\xA1'

        meta_data = novatel.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (common.OEM4_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.FLATTENED_BINARY, data, meta_data)

    # -------------------------------------------------------------------------------------------------------
    # Short Ascii Decoder Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_SHORT_ASCII_RAWIMU(self):
        data = b'%RAWIMUSXA,0,5.998;04,41,0,5.998473,0ba4fe00,-327350056,-10403806,-14067095,-33331,111741,345139*db627314\r\n'

        self.TestSameFormatCompare(common.ENCODEFORMAT.ASCII, data)

    # -------------------------------------------------------------------------------------------------------
    # Short Binary Decoder Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_SHORT_BINARY_RAWIMU(self):
        data = b'\xAA\x44\x13\x28\xB6\x05\x00\x00\x6E\x17\x00\x00\x04\x29\x00\x00\x8C\xC1\xC3\xB4\x6F\xFE\x17\x40\x00\xFE\xA4\x0B\xD8\x08\x7D\xEC\x22\x40\x61\xFF\x69\x5A\x29\xFF\xCD\x7D\xFF\xFF\x7D\xB4\x01\x00\x33\x44\x05\x00\xDA\x20\x27\xB9'

        meta_data = common.MetaDataStruct()
        meta_data.binary_msg_length = len(data) - (
                common.OEM4_SHORT_BINARY_HEADER_LENGTH + common.OEM4_BINARY_CRC_LENGTH)
        self.TestSameFormatCompare(common.ENCODEFORMAT.BINARY, data, meta_data)

    # -------------------------------------------------------------------------------------------------------
    # Json Decoder Unit Tests (Disabled for now)
    # -------------------------------------------------------------------------------------------------------
    def test_JSON_BESTPOS(self):
        data = b'{\"header\": {\"message\": \"BESTPOS\",\"id\": 42,\"port\": \"COM1\",\"sequence_num\": 0,\"percent_idle_time\": 9.5,\"time_status\": \"FINESTEERING\",\"week\": 2176,\"seconds\": 141484.000,\"receiver_status\": 33554464,\"HEADER_reserved1\": 52666,\"receiver_sw_version\": 32768},\"body\": {\"solution_status\": \"SOL_COMPUTED\",\"position_type\": \"SINGLE\",\"latitude\": 51.15043470167,\"longitude\": -114.03068044762,\"orthometric_height\": 1096.4990,\"undulation\": -17.0000,\"datum_id\": \"WGS84\",\"latitude_std_dev\": 0.7985,\"longitude_std_dev\": 0.6707,\"height_std_dev\": 1.5215,\"base_id\": \"\",\"diff_age\": 0.000,\"solution_age\": 0.000,\"num_svs\": 37,\"num_soln_svs\": 34,\"num_soln_L1_svs\": 34,\"num_soln_multi_svs\": 34,\"extended_solution_status2\": 0,\"ext_sol_stat\": 6,\"gal_and_bds_mask\": 57,\"gps_and_glo_mask\": 51}}'

        self.TestSameFormatCompare(common.ENCODEFORMAT.JSON, data)

    def test_JSON_GPSEPHEM(self):
        data = b'{\"header\": {\"message\": \"GPSEPHEM\",\"id\": 7,\"port\": \"COM1\",\"sequence_num\": 12,\"percent_idle_time\": 45.5,\"time_status\": \"SATTIME\",\"week\": 2098,\"seconds\": 427560.000,\"receiver_status\": 33816608,\"HEADER_reserved1\": 4628,\"receiver_sw_version\": 15668},\"body\": {\"satellite_id\": 3,\"tow\": 427560.0,\"health7\": 0,\"iode1\": 68,\"iode2\": 68,\"wn\": 2098,\"zwn\": 2098,\"toe\": 432000.0,\"a\": 2.655942598e+07,\"delta_n\": 4.844487507e-09,\"m0\": 5.4111299713e-01,\"ecc\": 2.6812178548e-03,\"omega\": 6.9765460014e-01,\"cuc\": -7.003545761e-07,\"cus\": 4.092231393e-06,\"crc\": 3.00875000e+02,\"crs\": -1.35937500e+01,\"cic\": 1.490116119e-08,\"cis\": 3.352761269e-08,\"i0\": 9.6490477291e-01,\"i_dot\": -2.146517983e-10,\"omega0\": -1.042300444e+00,\"omega_dot\": -8.37642034e-09,\"iodc\": 68,\"toc\": 432000.0,\"tgd\": 1.862645149e-09,\"af0\": -1.28527e-04,\"af1\": -1.02318e-11,\"af2\": 0.00000,\"anti_spoofing\": true,\"n\": 1.458664175e-04,\"eph_var\": 4.00000000e+00}}'

        self.TestSameFormatCompare(common.ENCODEFORMAT.JSON, data)

    def test_JSON_VERSION(self):
        data = b'{\"header\": {\"message\": \"VERSION\",\"id\": 37,\"port\": \"COM1\",\"sequence_num\": 0,\"percent_idle_time\": 19.5,\"time_status\": \"UNKNOWN\",\"week\": 0,\"seconds\": 1.473,\"receiver_status\": 37748736,\"HEADER_reserved1\": 13953,\"receiver_sw_version\": 16502},\"body\": {\"versions\": [{\"component_type\": \"GPSCARD\",\"model_name\": \"FDNRNNTBN\",\"psn\": \"DMGW15300023D\",\"hardware_version\": \"OEM719-0.00G\",\"software_version\": \"OM7MR0801RN0000\",\"boot_version\": \"OM7BR0000RBG000\",\"compile_date\": \"2021/Jan/19\",\"compile_time\": \"15:57:45\"},{\"component_type\": \"OEM7FPGA\",\"model_name\": \"\",\"psn\": \"\",\"hardware_version\": \"\",\"software_version\": \"OMV070001RN0000\",\"boot_version\": \"\",\"compile_date\": \"\",\"compile_time\": \"\"}]}}'

        self.TestSameFormatCompare(common.ENCODEFORMAT.JSON, data)

    # -------------------------------------------------------------------------------------------------------
    # Misc. Decoder Unit Tests
    # -------------------------------------------------------------------------------------------------------
    def test_NO_DEFINITION(self):
        data = b'#RAWWAASFRAMEA_2,COM2,0,77.5,SATTIME,1747,411899.000,00000020,58e4,11526;62,138,9,c6243a0581b555352c4056aae0103cf03daff2e00057ff7fdff8010180,62*b026c677\r\n'

        meta_data = novatel.MetaDataStruct()

        status, h = self.header_decoder.decode(data, meta_data)
        self.assertEqual(status, common.STATUS.SUCCESS)

        status, l = self.message_decoder.decode(data[meta_data.header_length:], meta_data)
        self.assertEqual(status, common.STATUS.NO_DEFINITION)


if __name__ == "__main__":
    unittest.main()

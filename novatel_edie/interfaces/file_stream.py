"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Holds the Python interface to EDIE's file stream interface.
"""
from novatel_edie.interfaces.common import *

HWINTERFACE_DLL.ifs_init.restype = c_void_p
HWINTERFACE_DLL.ifs_init.argtypes = [c_char_p]
HWINTERFACE_DLL.ifs_del.restype = None
HWINTERFACE_DLL.ifs_del.argtypes = [c_void_p]
HWINTERFACE_DLL.ifs_read.restype = None
HWINTERFACE_DLL.ifs_read.argtypes = [c_void_p, c_void_p, c_char_p, c_ulong]


class InputFileStream:
    """Class to handle file stream inputs.
    """

    def __init__(self, input_filepath: str, string_buffer: int = 10240):
        """Reads data from the file input steam.

        Args:
            input_filepath: Filepath to read from.
            string_buffer: Size of the string buffer.
        """
        self._ifs = None

        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f'Invalid path: {input_filepath}')

        if isinstance(input_filepath, str):
            input_filepath = input_filepath.encode()

        self._ifs = HWINTERFACE_DLL.ifs_init(input_filepath)
        self._data_buf = create_string_buffer(string_buffer)

    def __del__(self):
        """Deletes the reference to the EDIE shared library file.
        """
        if self._ifs:
            HWINTERFACE_DLL.ifs_del(self._ifs)

    def get_dll_reference(self):
        """Gets the private reference to the DLL's IFS.
        """
        return self._ifs

    def read(self, read_size: int = 1024) -> tuple:
        """Reads data from the input steam.

        Args:
            read_size: Number of bytes to read. If larger than the buffer size it will read up to the max size of
                the buffer.

        Returns:
            Tuple where the first item is the stream status and the second item is the data.
        """
        read_size = 10240 if 10240 < read_size else read_size
        status = StreamReadStatus()
        HWINTERFACE_DLL.ifs_read(self._ifs, byref(status), self._data_buf, read_size)

        return status, self._data_buf.raw[:read_size]

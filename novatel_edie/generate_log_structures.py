"""
Copyright 2023 NovAtel Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Module Description: Generates a Python file containing message structures from the JSON UI database.
"""
import argparse

from novatel_edie.common import JSON_DB_PATH
from novatel_edie.decoders.jsonreader import JsonReader


def main():
    """Main function to create the msg_structures.py file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-jdb", "--json_database", type=str,
                        help="Path to the JSON UI database containing message definitions",
                        default=JSON_DB_PATH)
    args = parser.parse_args()

    try:
        json_reader = JsonReader(args.json_database)
        json_reader.generate_documentation()
        print(f'Successfully decoded the message definitions in "{args.json_database}"')
    except FileNotFoundError:
        print(f'ERROR: Could not find the message definitions file: "{args.json_database}"')
    except OSError:
        print(f'ERROR: Could not decode message definitions in "{args.json_database}"')


if __name__ == '__main__':
    main()

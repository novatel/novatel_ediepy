import argparse
import folium
import platform
import serial
import sys
import time
import json
from novatel_edie.decoders import novatel, common
from novatel_edie.common import LogLevelEnum
from serial.threaded import Protocol, ReaderThread

parser = novatel.Parser(r'\\oemsrv01\oemtest1\SystemTools\libraries\EDIE\database\messages_external.json')


def createEdieComponents( args ):
    #  Create an output logger for various messages from EDIE (edie.log)
    logger = novatel.Logger()  # Use default logger, alternatively could configure from file as follows:
    logger.set_logger_level(LogLevelEnum.INFO)  # Set the global level to INFO

    if parser.configure(output_format=common.OutputFormat.JSON) is not True:
        logger.critical("ERROR: Failed to configure the parser.\n")
        sys.exit(-1)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("input_file", help="input_file")
    arg_parser.add_argument("-m", action='store_true', dest='output_map', help="include map.html")

    args = arg_parser.parse_args()

    createEdieComponents(args)

    start = time.time()
    coords = []

    with open(args.input_file, 'rb') as file_in, \
         open("bytes.UNKNOWN", 'wb') as file_unknown:

        while True:
            if time.time() - start > 1:
                print(".", end='')
                start = time.time()

            data = file_in.read(65535)
            data_written = parser.write(data)
            if data_written != len(data):
                break
            elif data_written == 0:
                break
            for log_data, log in parser:
                if log_data.status == novatel.Parser.Status.SUCCESS.value:
                    data = json.loads(log.body)
                    if log_data.name == b'BESTPOS':
                        lat = data['latitude']
                        long = data['longitude']
                        h = data["orthometric_height"]
                        #print("rx at {},{},{}".format(lat, long, h))

                        coords.append((lat, long))
                elif (log_data.status == novatel.Parser.Status.UNKNOWN.value):
                    file_unknown.write(log_data.header)

    if args.output_map :
        my_map = folium.Map(location=[51.150, -114.03],
                            zoom_start=16)

        for lat, long in coords:
            folium.CircleMarker([lat, long], radius=2).add_to(my_map)

        my_map.save('map.html')
        print("map.html created")


if __name__ == "__main__":
    main()

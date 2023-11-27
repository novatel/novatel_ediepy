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

OEM_COM_BAUD = 9600
READ_BUFFER_SIZE = 4096
parser = novatel.Parser(r'\\oemsrv01\oemtest1\SystemTools\libraries\EDIE\database\messages_external.json')

class BufferThread(Protocol):
    def connection_made(self, transport):
        super(BufferThread, self).connection_made(transport)

    def data_received(self, data):
        global parser
        parser.write(data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        sys.stdout.write('port closed\n')


def openComPort( args ):
    if (platform.system() == "Windows"):
        port_name = "COM" + str(args.com)
    elif (platform.system() == "Linux"):
        port_name = "dev/" + str(args.com)
    else:
        return -1

    com_port = serial.Serial(port="COM" + str(args.com), baudrate=args.baud_rate, timeout=3)
    return com_port


def createEdieComponents( args ):
    #  Create an output logger for various messages from EDIE (edie.log)
    logger = novatel.Logger()  # Use default logger, alternatively could configure from file as follows:
    logger.set_logger_level(LogLevelEnum.INFO)  # Set the global level to INFO

    if parser.configure(output_format=common.OutputFormat.FLATTENED_BINARY ) is not True:
        logger.critical("ERROR: Failed to configure the parser.\n")
        sys.exit(-1)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("com", help="PC COM port receiving logs from the OEM receiver.  Windows format: COM port number in integer format (3).  Linux format: Port name in string format (ttyUSB3)")
    arg_parser.add_argument("-b", "--baud_rate", help="The baud rate of the COM port connection. Default is 9600 bps.", default=OEM_COM_BAUD, type=int)
    arg_parser.add_argument("-a", "--bias", help="simple cumulative bias adjustment", default=0.0001, type=float)
    arg_parser.add_argument("-m", action='store_true', dest='output_map', help="include map.html")

    args = arg_parser.parse_args()

    createEdieComponents(args)

    com_port = openComPort(args)

    # send a couple of logs to the port
    com_port.write(b"log versiona ontime 2\r")
    com_port.write(b"log bestposa ontime 2\r")

    start = time.time()
    bias = args.bias
    coords = []

    with ReaderThread(com_port, BufferThread):
        while time.time() - start < 10:
            time.sleep(0.1)

            for log_data, log in parser:
                if log_data.status == novatel.Parser.Status.SUCCESS.value:
                    if log_data.name == b'BESTPOS':
                        h = log.header.clMyLLHDegreesOrtho_clMyLLH_clMyUserDatumPosition_clMyCommonSolution_dMyHeight
                        lat = log.header.clMyLLHDegreesOrtho_clMyLLH_clMyUserDatumPosition_clMyCommonSolution_dMyLatitude
                        long = log.header.clMyLLHDegreesOrtho_clMyLLH_clMyUserDatumPosition_clMyCommonSolution_dMyLongitude
                        print("rx at {},{},{}".format(lat, long, h))

                        coords.append((lat+bias, long+bias))
                        bias += args.bias;

                    if log_data.name == b'VERSION':
                        for comp in log.header.aclVersions:
                            print( "sw: {}".format(comp.szSoftwareVersion))

                elif log_data.status == novatel.Parser.Status.UNKNOWN.value:
                    print('unknown: ' + str(log_data.header))

    if args.output_map :
        my_map = folium.Map(location=[51.150, -114.03],
                            zoom_start=16)

        for lat, long in coords:
            folium.CircleMarker([lat, long]).add_to(my_map)

        my_map.save('map.html')
        print("map.html created")


if __name__ == "__main__":
    main()

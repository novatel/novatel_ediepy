"""
Example of how to encode/convert an OEM command from Abbreviated ASCII to ASCII/BINARY.
"""
import argparse

from novatel_edie.decoders import common, logging, jsonreader, novatel


def main():
    parser = argparse.ArgumentParser(description="""
        Format: python ConvertOEM_CommandEncoder.py <path to Json DB> <output format> <abbreviated ascii command>
        Example: python ConvertOEM_CommandEncoder.py messages_public.json "RTKTIMEOUT 30" ASCII""")
    parser.add_argument("database", help="Path to JSON DB", default="")
    parser.add_argument("format", help="Output format.",
                        choices=[common.ENCODEFORMAT.ASCII.name, common.ENCODEFORMAT.BINARY.name],
                        default=common.ENCODEFORMAT.ASCII.name)
    parser.add_argument("command", help="String of the abbreviated ascii command to be converted.", default='')
    args = parser.parse_args()

    logger = logging.Logger()
    logger.set_logger_level(logging.LogLevelEnum.INFO)

    json_db = jsonreader.JsonReader(json_db_filepath=args.database)
    commander = novatel.Commander(json_db, encode_format=common.ENCODEFORMAT[args.format])

    status, encoded_command = commander.encode(args.command)

    if status != common.STATUS.SUCCESS:
        logger.critical(f'Command failed to encode: {status}')
        print(f'Command failed to encode: {status}')
        return

    logger.info(f'{encoded_command}')
    print(f'{encoded_command}')
    with open('command.txt', 'wb') as cmd_file:
        cmd_file.write(encoded_command)

    logger.info("DONE.")
    logger.shutdown_logger()


if __name__ == "__main__":
    main()

"""
Example of how to convert OEM messages using the FileParser class.
"""
import argparse

from novatel_edie.decoders import common, jsonreader, logging, novatel


def display_message(meta_data, message_struct):
    """Displays the message in the data.
    """
    if meta_data.message_id == 42:  # BESTPOS
        print(f"BESTPOS: {message_struct.body.longitude:.5f} long, {message_struct.body.latitude:.5f} lat, "
              f"{message_struct.body.orthometric_height:.5f} alt")
    if meta_data.message_id == 43:  # RANGE
        print(f"RANGE: ({len(message_struct.body.obs)} observations)\n" + ', '.join(
            [str(f'(PRN: {obs.sv_prn}, Freq: {obs.sv_freq})') for obs in message_struct.body.obs]))


def main():
    parser = argparse.ArgumentParser(description="""
        Format: python ConvertOEM_FileParser.py <path to Json DB> <path to input file> <output format>
        Example: python ConvertOEM_FileParser.py messages_public.json bestpos.asc ASCII""")
    parser.add_argument("database", help="Path to JSON DB", default="")
    parser.add_argument("input_file", help="File containing logs to be converted.")
    parser.add_argument("format", help="Output format.", default=common.ENCODEFORMAT.ASCII.name)
    args = parser.parse_args()

    logger = logging.Logger()
    logger.set_logger_level(logging.LogLevelEnum.INFO)

    json_db = jsonreader.JsonReader(json_db_filepath=args.database)
    file_parser = novatel.FileParser(json_db=json_db, encode_format=common.ENCODEFORMAT[args.format],
                                     input_file=args.input_file)

    for status, meta_data, message_data, message in file_parser:
        if status != common.STATUS.SUCCESS:
            continue

        logger.info(f'Parsed: ({message_data.message_length}) {message_data.message}')
        if file_parser.encode_format != common.ENCODEFORMAT.FLATTENED_BINARY:
            print(f'Parsed: ({message_data.message_length}) {message_data.message}')
        else:
            display_message(meta_data, message)

    logger.info("DONE.")
    logger.shutdown_logger()


if __name__ == "__main__":
    main()

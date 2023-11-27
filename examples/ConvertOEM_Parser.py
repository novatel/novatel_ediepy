"""
Example of how to convert OEM messages using the Parser class.
"""
import argparse

from novatel_edie.decoders import common, logging, jsonreader, novatel

FILE_BUFFER_SIZE = 20 * 1024
GET_DATA_STATUSES = (common.STATUS.INCOMPLETE_MORE_DATA, common.STATUS.INCOMPLETE, common.STATUS.BUFFER_EMPTY)


def read_file_in_chunks(file_in, chunk_size=FILE_BUFFER_SIZE):
    """Reads a large file into chunks.
    """
    while True:
        file_bytes = file_in.read(chunk_size)
        if not file_bytes:
            break
        yield file_bytes


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
    arg_parser = argparse.ArgumentParser(description="""
        Format: python ConvertOEM_Parser.py <path to Json DB> <path to input file> <output format>
        Example: python ConvertOEM_Parser.py messages_public.json bestpos.asc ASCII""")
    arg_parser.add_argument("database", help="Path to JSON DB", default="")
    arg_parser.add_argument("input_file", help="File containing logs to be converted.")
    arg_parser.add_argument("format", help="Output format.", default=common.ENCODEFORMAT.ASCII.name)
    args = arg_parser.parse_args()

    logger = logging.Logger()
    logger.set_logger_level(logging.LogLevelEnum.INFO)

    json_db = jsonreader.JsonReader(json_db_filepath=args.database)
    parser = novatel.Parser(json_db, encode_format=common.ENCODEFORMAT[args.format])

    with open(args.input_file, 'rb') as file_in:
        for file_chunk in read_file_in_chunks(file_in):
            parser.write(file_chunk)

        # Frame a message
        for status, meta_data, message_data, message in parser:
            if status in GET_DATA_STATUSES:
                continue

            print(f'Parsed {meta_data.message_name}: ({message_data.message_length}) {message_data.message}')
            if parser.encode_format == common.ENCODEFORMAT.FLATTENED_BINARY:
                display_message(meta_data, message)

    logger.info("DONE.")
    logger.shutdown_logger()


if __name__ == "__main__":
    main()

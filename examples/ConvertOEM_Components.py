"""
Example of how to convert OEM messages using the low-level components.
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
    parser = argparse.ArgumentParser(description="""
        Format: python ConvertOEM_Components.py <path to Json DB> <path to input file> <output format>
        Example: python ConvertOEM_Components.py messages_public.json bestpos.asc ASCII""")
    parser.add_argument("database", help="Path to JSON DB", default="")
    parser.add_argument("input_file", help="File containing logs to be converted.")
    parser.add_argument("format", help="Output format.", default=common.ENCODEFORMAT.ASCII.name)
    args = parser.parse_args()

    logger = logging.Logger()
    logger.set_logger_level(logging.LogLevelEnum.INFO)

    json_db = jsonreader.JsonReader(json_db_filepath=args.database)
    framer = novatel.Framer()
    header_decoder = novatel.HeaderDecoder(json_db)
    message_decoder = novatel.MessageDecoder(json_db)
    encoder = novatel.Encoder(json_db, common.ENCODEFORMAT[args.format])

    novatel_filter = novatel.Filter()
    novatel_filter.include_message_name('BESTPOS')
    novatel_filter.include_message_name('RANGE')

    with open(args.input_file, 'rb') as file_in:
        for file_chunk in read_file_in_chunks(file_in):
            framer.write(file_chunk)

            # Frame a message
            for f_status, frame, meta_data in framer:
                if f_status in GET_DATA_STATUSES:
                    continue

                logger.info(f'Framed: {frame}')

                # Decode the header
                hd_status, int_header = header_decoder.decode(frame, meta_data)
                if novatel_filter.filter(meta_data) and hd_status == common.STATUS.SUCCESS:

                    # Decode the rest of the message
                    ld_status, int_message = message_decoder.decode(frame[meta_data.header_length:], meta_data)
                    if ld_status != common.STATUS.SUCCESS:
                        continue

                    # Encode the message to a new format
                    e_status, message_data, message = encoder.encode(int_header, int_message, meta_data)
                    if e_status != common.STATUS.SUCCESS:
                        continue

                    logger.info(f'Encoded: ({message_data.message_length}) {message_data.message}')
                    if encoder.encode_format != common.ENCODEFORMAT.FLATTENED_BINARY:
                        print(f'Encoded: ({message_data.message_length}) {message_data.message}')
                    else:
                        display_message(meta_data, message)

    logger.info("DONE.")
    logger.shutdown_logger()


if __name__ == "__main__":
    main()

import os

from argparse import ArgumentParser

from .data_handler import DataHandler

arg_parser = ArgumentParser()
arg_parser.add_argument('--sample', '-s', nargs='?', metavar='SIZE', type=int, default=0,
                        help='sample size, default: 0 (full run)')
arg_parser.add_argument('--no-scrape', '-ns', action='store_true',
                        help='skip scraping during run')
arg_parser.add_argument('--push', '-p', action='store_true',
                        help='push output to rust server')
arg_parser.add_argument('--file', '-f', nargs=1, type=str,
                        help='file path for xml to use (default: get from fødevarestyrelsen)')
arg_parser.add_argument('--clean', '-c', action='store_true',
                        help='clean all temp files and exit')


def run():
    args = arg_parser.parse_args()

    if args.clean:
        files = ['blacklist.csv', 'temp.csv', 'filter_log.json',
                 'smiley_json_processed_delete.json', 'smiley_json_processed_insert.json',
                 'smiley_json_processed_update.json']

        for file in files:
            print(f'removing file {file}')
            if os.path.isfile(file):
                os.remove(file)

        return

    dh = DataHandler(
        sample=args.sample,
        no_scrape=args.no_scrape,
        push=args.push,
        file=args.file[0] if args.file else None
    )
    dh.collect()

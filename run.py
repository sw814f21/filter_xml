from argparse import ArgumentParser

from data_handler import DataHandler

arg_parser = ArgumentParser()
arg_parser.add_argument('--sample', '-s', nargs='?', metavar='SIZE', type=int, default=0,
                        help='sample size, default: 0 (full run)')
arg_parser.add_argument('--no-scrape', '-ns', action='store_true',
                        help='skip scraping during run')
arg_parser.add_argument('--push', '-p', action='store_true', 
                        help='push output to rust server')
arg_parser.add_argument('--file', '-f', nargs=1, type=str,
                        help='file path for xml to use (default: get from fødevarestyrelsen)')
args = arg_parser.parse_args()

if __name__ == '__main__':
    dh = DataHandler(
        sample=args.sample,
        no_scrape=args.no_scrape,
        push=args.push,
        file=args.file
    )
    dh.collect()

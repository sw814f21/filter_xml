from data_handler import DataHandler
from argparse import ArgumentParser

arg_parser = ArgumentParser()
arg_parser.add_argument('--sample', '-s', nargs='?', metavar='SIZE', type=int, default=0,
                        help='sample size, default: 0 (full run)')
arg_parser.add_argument('--no-scrape', '-ns', action='store_true',
                        help='skip scraping during run')

args = arg_parser.parse_args()

if __name__ == '__main__':
    dh = DataHandler(
        sample=args.sample,
        no_scrape=args.no_scrape
    )
    dh.collect()

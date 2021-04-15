from argparse import ArgumentParser
from data_outputter import get_outputter

from data_handler import DataHandler

arg_parser = ArgumentParser()
arg_parser.add_argument('--sample', '-s', nargs='?', metavar='SIZE', type=int, default=0,
                        help='sample size, default: 0 (full run)')
arg_parser.add_argument('--no-scrape', '-ns', action='store_true',
                        help='skip scraping during run')
arg_parser.add_argument('--push', '-p', action='store_true', 
                        help='push output to rust server')
args = arg_parser.parse_args()

if __name__ == '__main__':
    dh = DataHandler(
        sample=args.sample,
        no_scrape=args.no_scrape,
        outputter=get_outputter(args.push)
    )
    dh.collect()

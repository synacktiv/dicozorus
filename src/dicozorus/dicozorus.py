#!/usr/bin/env python3

import sys
import argparse

from dicozorus.core.feeder import DicozorusFeeder
from dicozorus.core.generator import DicozorusGenerator
from dicozorus.core.initializer import DicozorusInitializer
from dicozorus.core.stats import DicozorusStats
from dicozorus.core.check import DicozorusCheck
from dicozorus.core.modify import DicozorusModify
from dicozorus.utils import logging
from dicozorus import __version__

def get_dicozorus_parser():
    """
    Parse arguments for command and subcommands.
    Subcommands are feed, gen, init and stats.
    """
    parser = argparse.ArgumentParser(prog="dicozorus",
            description=('Dicozorus allows to generate custom wordlists. It '
            'can be fed with wordlists from your own or initialized using '
            'a predefined set of wordlists. Entries are stored in a sqlite '
            'database located in $HOME/.dicozorus/db.sqlite'))
    parser.add_argument('-v', '--verbose', action='count',
            help='increase verbosity')
    parser.add_argument('--version', action='version',
            version='Dicozorus {}'.format(__version__))

    subparsers = parser.add_subparsers(help='Subcommand to run', required=True)

    # FEED command parser
    parser_feed = subparsers.add_parser('feed',
            help='Feed dicozorus db with wordlist files or scan results')
    parser_feed.add_argument('-w', '--wordlist', nargs='+',
            help='Feed dicozorus with one or more wordlists.')
    parser_feed.add_argument('-p', '--patator', nargs='+',
            help='Feed dicozorus with one or more patator CSV files')
    parser_feed.add_argument('-d', '--dirsearch', nargs='+',
            help='Feed dicozorus with one or more dirsearch results files')
    parser_feed.add_argument('-D', '--dicozorus', nargs='+',
            help='Feed dicozorus with one or more dicozorus CSV files')
    parser_feed.add_argument('-i', '--ignore-comments',
            help='Ignore all entries starting with the specified string')
    parser_feed.add_argument('-f' ,'--filter',
            help=('Comma separated HTTP codes. Only treat entries matching '
            'specified HTTP codes.'))
    parser_feed.add_argument('-u' ,'--update-count-only', action='store_true',
            help=('Do not insert any new entries in dicozorus DB. (only update'
            'count)'))
    parser_feed.add_argument('-c', '--criticality', default='UNRANKED',
            choices=['UNRANKED', 'INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
            help='Set the criticality of the provided entries')
    parser_feed.set_defaults(func=feed)

    # GEN command parser
    split_type = lambda v: v.split(',')
    parser_gen = subparsers.add_parser('gen',
            help='Generate wordlist using the dicozorus db.')
    parser_gen.add_argument('-o', '--output',
            help='Save the generated wordlist to the specified file')
    parser_gen.add_argument('-m', '--max-entries',
            help='Maximum number of entries to generate')
    parser_gen.add_argument('-s', '--sort', default= "criticality,count",
            help=('Specify the criteria to use to sort entries. Comma '
            'separated list of values in (criticality, count, name, type). '
            'Default is criticality,count'))
    parser_gen.add_argument('-S', '--shuffle', action='store_true',
            help='Print a randomly shuffled version of the selected entries')
    parser_gen.add_argument('-D', dest='filter_dir', action='store_true',
            help=('Only output entries of type DIR. Can be combined with -F '
            'and -P. Default is -DFP'))
    parser_gen.add_argument('-F', dest='filter_file', action='store_true',
            help=('Only output entries of type FILE. Can be combined with -D '
            'and -P. Default is -DFP'))
    parser_gen.add_argument('-P', dest='filter_path', action='store_true',
            help=('Only output entries of type PATH. Can be combined with -D '
            'and -F. Default is -DFP'))
    exclusive_group_gen = parser_gen.add_mutually_exclusive_group()
    exclusive_group_gen.add_argument('--min-criticality', default='UNRANKED',
            choices=['UNRANKED', 'INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
            help=('Only output entries equal or greater than the specified '
            'criticality'))
    exclusive_group_gen.add_argument('-c', '--criticality',
            type=split_type, help=('Comma separated values within '
            '["UNRANKED", "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]. \n'
            'Ex:HIGH,CRITICAL'))

    regex_group = parser_gen.add_mutually_exclusive_group()
    regex_group.add_argument('-f', '--filter',
            help='Filter out entries matching regular expression')
    regex_group.add_argument('-t', '--select-by-tags',
            help='Select entries based on a comma separated list of tags')
    parser_gen.set_defaults(func=gen)

    # INIT command parser
    parser_init = subparsers.add_parser('init',
            help='Initialize the dicozorus database.')
    parser_init.add_argument('-e', '--empty', action='store_true',
            help=('Initialize an empty database. If not specified, database '
            'will contain entries from data/*.wordlist'))
    parser_init.add_argument('-F', '--force', action='store_true',
            help='Force database initialization (DELETE database content)')
    parser_init.add_argument('-m', '--minimal', action='store_true',
            dest='initialize_minimal', help=('Initialize the dicozorus database '
            'with criticality wordlists only'))
    parser_init.add_argument('-D', '--dangerous', action='store_true',
            help=('Include the dangerous.wordlist file. This one contains '
                'dangerous entries such as "actuator/shutdown"'))
    parser_init.add_argument('-W', '--wordlists-folder',
            help=('A folder that should store the initialization wordlists. '
            'By default dicozorus will look in ~/.dicozorus/wordlists/'))
    parser_init.set_defaults(func=init)

    # MODIFY command parser
    parser_modify = subparsers.add_parser('modify',
            help=('Modify dicozorus DB directly. Use it to add / remove / '
            'update one or multiple entries.'))
    action = parser_modify.add_mutually_exclusive_group(required=True)
    action.add_argument('--add', action='store_true', help='Add the specified entry')
    action.add_argument('--rm', action='store_true', help='Remove the specified entry')
    action.add_argument('--update', action='store_true', help='Update the specified entry')

    entries_input = parser_modify.add_mutually_exclusive_group(required=True)
    entries_input.add_argument('--entry', help='The entry to be processed')
    entries_input.add_argument('--wordlist', help='The file containing the entries to be processed')

    parser_modify.add_argument('--criticality', default='UNRANKED',
            help='The count for the entry/entries you want to add. Default is Unranked')
    parser_modify.add_argument('--count', default=1,
            help='The count for the entry/entries you want to add. Default is 1.')
    parser_modify.add_argument('--category', default='', help=('The category for the '
        'entry/entries you want to add. Default is none.'))
    parser_modify.add_argument('--taglist', default='', help=('Comma separated '
        'taglist for the entry/entries you want to add. Default is none.'))
    parser_modify.add_argument('--reference', default='', help=('A URL to a resource describing the issue. Default is none.'))

    parser_modify.set_defaults(func=modify)

    # STATS command parser
    parser_stats = subparsers.add_parser('stats',
            help='Show stats about the dicozorus database.')
    parser_stats.set_defaults(func=stats)

    # CHECK command parser
    parser_check = subparsers.add_parser('check', help=('The check command is '
        'used to compare entry or wordlists with the dicozorus database'))
    parser_check.add_argument('-M', '--missing-in-wordlist',
            action='store_true', help=('Print the entries present in the '
            'dicozorus database but not in the specified wordlist. The '
            'default behavior is to check for entries missing in the '
            'dicozorus database.'))

    exclusive_group = parser_check.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('-w', '--wordlist',
            help='The wordlist to be checked.')
    exclusive_group.add_argument('-e', '--entry', help=('The entry to be '
        'checked. If the specified entry is present in the database it will '
        'be printed along with any information associated to this entry'))

    parser_check.add_argument('-c', '--criticality',
            type=split_type, help=('Comma separated values within '
            '["UNRANKED", "INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]. \n'
            'Ex:HIGH,CRITICAL'))
    parser_check.add_argument('-S', '--stats-only', action='store_true',
            help=('Don\'t print out entries, only display statistics'
            ' of the considered wordlist'))

    parser_check.set_defaults(func=check)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return parser

def feed(args):
    """
    Run dicozorus feed subcommand. This command is used to insert or update
    entries in the dicozorus database.
    """
    dicozorus_feeder = DicozorusFeeder(args)
    dicozorus_feeder.feed()

def gen(args):
    """
    Run dicozorus gen subcommand. This command is used to generate a list of
    entries from the dicozorus database.

    Filtering
     The list can be filtered based on various criteria such as length,
     type of entry, tags, extensions, or using a regular expression.

    Ordering
     The list can be ordered on any column of the dicozorus entries: *name*,
     *count*, *criticality*, *category*, *tags*, *reference*.
    """
    dicozorus_generator = DicozorusGenerator(args)
    dicozorus_generator.gen()

def init(args):
    """ Initialize the dicozorus database. """
    dicozorus_initializer = DicozorusInitializer(args)
    dicozorus_initializer.init()

def stats(args):
    """ Show stats about the dicozorus database """
    dicozorus_stats = DicozorusStats(args)
    dicozorus_stats.show()

def modify(args):
    """
    Update, remove or add one or multiple entries to the dicozorus database
    """
    dicozorus_modify = DicozorusModify(args)
    dicozorus_modify.run()

def check(args):
    """
    Compare entries of a specified file with entries in the dicozorus database
    """
    dicozorus_check = DicozorusCheck(args)
    dicozorus_check.run()
    sys.exit(1)

def main():
    """Dicozorus web wordlist generator"""
    dicozorus_parser = get_dicozorus_parser()
    args = dicozorus_parser.parse_args()

    logging.configure(debug=args.verbose)

    args.func(args)

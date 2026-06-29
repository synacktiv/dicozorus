from dicozorus.utils.logging import LOGGER as logger
from dicozorus.db.database import DicozorusDatabase
from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.parser.dicozorus import DicozorusParser
from os import path, makedirs, getenv

import glob
import os
import sys

class DicozorusInitializer:
    """
    Implement the **init** subcommand.
    """
    def __init__(self, args):
        self.db = DicozorusDatabase(initialize=True)
        self.force_initialize=args.force
        self.initialize_empty=args.empty
        self.initialize_minimal=args.initialize_minimal
        self.initialize_dangerous=args.dangerous
        if args.wordlists_folder:
            self.wordlists_folder = args.wordlists_folder
        else:
            self.wordlists_folder = '{}/.dicozorus/wordlists'.format(getenv('HOME'))

    def init(self):
        """
        Initiliaze the dicozorus database. If **--empty** is not specified,
        the database will be filled with all .wordlist files in the wordlists/
        folder.
        """
        logger.info('Initializing dicozorus database')

        database_dirty=False
        for table_name in self.db.tables.keys():
            if self.db.table_exists(table_name):
                database_dirty=True

        if database_dirty:
            if self.force_initialize:
                logger.warning('The database is not empty, cleaning ...')
                self.db.destroy()
            else:
                logger.error(('The database is not empty. use --force to force'
                ' initialization.'))
                sys.exit(-1)

        logger.info('Creating dicozorus tables')
        self.db.create_tables()

        if not self.initialize_empty:
            self.insert_initialization_data()

    def insert_initialization_data(self):
        """
        Parse wordlist in the *data/* directory.
        Default behavior is to parse only the cricity wordlists :
        *CRITICAL.wordlist*, *HIGH.wordlist*, *MEDIUM.wordlist*, *LOW.wordlist*
        and *INFO.wordlist*. If **--full** is specified, all wordlists in the
        *data/* directory will be parsed.
        """

        dicozorus_wordlist = DicozorusWordlist()
        dicozorus_parser = DicozorusParser(dicozorus_wordlist,
                                         ignore_comments='##')
        #wordlists_files = glob.glob(self.wordlists_folder + '/*.wordlist')
        import importlib.resources
        pkg_builtin_wordlists = importlib.resources.files("dicozorus.wordlists")
        
        #if len(wordlists_files) == 0:
        #    logger.error(('The wordlist directory for database initialization '
        #        'is empty ! ({})'.format(self.wordlist_folder)))
        #    sys.exit(-1)
        #for wordlist_filepath in wordlists_files:
        wordlists = [ 
            item for item in pkg_builtin_wordlists.iterdir() 
            if item.name.endswith(".wordlist")
        ]
        if len(wordlists) == 0:
            logger.error(('The wordlist directory for database initialization '
                'is empty ! ({})'.format(self.wordlist_folder)))
            sys.exit(-1)

        for wordlist_filepath in wordlists:
            wordlist_filename = os.path.basename(wordlist_filepath)

            DEFAULT_WORDLISTS = ['critical.wordlist', 'high.wordlist',
                    'medium.wordlist', 'low.wordlist', 'info.wordlist']
            if wordlist_filename in DEFAULT_WORDLISTS: 
                dicozorus_parser.parse(wordlist_filepath)
            elif (not self.initialize_minimal) and (wordlist_filename != 'dangerous.wordlist' or self.initialize_dangerous):
                dicozorus_parser.parse(wordlist_filepath)

        wordlist = dicozorus_parser.get_wordlist()
        wordlist.save()

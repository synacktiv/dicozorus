from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.model.entry import CRITICALITY
from dicozorus.parser.wordlist import WordlistParser
from dicozorus.parser.patator import PatatorParser
from dicozorus.parser.dirsearch import DirsearchParser
from dicozorus.parser.dicozorus import DicozorusParser
from dicozorus.utils.logging import LOGGER as logger

class DicozorusFeeder:
    """
    Implent the **feed** subcommand.
    """
    # pylint: disable=too-many-instance-attributes
    # 9 attributes is ok here.
    def __init__(self, args):
        self.dicozorus_wordlist = DicozorusWordlist()
        self.wordlist_files = args.wordlist
        self.patator_files = args.patator
        self.dirsearch_files = args.dirsearch
        self.dicozorus_files = args.dicozorus
        self.ignore_comments = args.ignore_comments
        self.update_count_only = args.update_count_only

        self.criticality = CRITICALITY.get(args.criticality)

        self.filters = []
        if args.filter:
            for http_code in args.filter.split(','):
                try:
                    self.filters.append(int(http_code))
                except ValueError:
                    logger.error(("the filter argument must contains a list"
                            "comma separated integers"))

        # Load the content of the database into the dicozorus wordlist
        self.dicozorus_wordlist.load()

    def feed(self):
        """ Feed the dicozorus database using the provided files """
        # Wordlist
        if self.wordlist_files:
            wordlist_parser = WordlistParser(self.dicozorus_wordlist,
                                             self.criticality,
                                             self.ignore_comments)

            for wordlist_file in self.wordlist_files:
                wordlist_parser.parse(wordlist_file)

            wordlist = wordlist_parser.get_wordlist()
            wordlist.save()

        # Patator CSV file
        if self.patator_files:
            patator_parser = PatatorParser(self.dicozorus_wordlist,
                                           self.criticality, self.filters,
                                           self.update_count_only)

            for patator_file in self.patator_files:
                patator_parser.parse(patator_file)

            wordlist = patator_parser.get_wordlist()
            wordlist.save()

        # Dirsearch result file
        if self.dirsearch_files:
            dirsearch_parser = DirsearchParser(self.dicozorus_wordlist,
                                           self.criticality, self.filters,
                                           self.update_count_only)

            for dirsearch_file in self.dirsearch_files:
                dirsearch_parser.parse(dirsearch_file)

            wordlist = dirsearch_parser.get_wordlist()

        # Dicozorus CSV file
        if self.dicozorus_files:
            dicozorus_parser = DicozorusParser(self.dicozorus_wordlist)
            for dicozorus_file in self.dicozorus_files:
                dicozorus_parser.parse(dicozorus_file)
            wordlist = dicozorus_parser.get_wordlist()
            wordlist.save()

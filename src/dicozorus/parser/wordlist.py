from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import UNRANKED

class WordlistParser:
    """
    Parser for wordlists
    One entry per line
    directories must end with /
    Entries samples: 
    - index.php
    - jmx-console/
    - manager/html
    """
    def __init__(
            self, dicozorus_wordlist, 
            criticality=UNRANKED, ignore_comments=None):
        self.wordlist = dicozorus_wordlist 
        self.ignore_comments = ignore_comments
        self.criticality = criticality

    def parse(self, wordlist_file, criticality=None):
        logger.info("Parsing wordlist %s", wordlist_file)

        if not criticality:
            criticality = self.criticality

        with open(wordlist_file, "r", encoding="utf8") as wordlist_entries:
            for entry in wordlist_entries:
                entry = entry.rstrip('\n')
                if self.ignore_comments:
                    if entry.startswith(self.ignore_comments):
                        continue
                self.wordlist.add_entry(entry, criticality=criticality)

    def get_wordlist(self):
        return self.wordlist


from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import UNRANKED
from urllib.parse import urlparse

class DirsearchParser():
    """
    Parse dirsearch result files. Usually located at ~/.dirsearch/reports 
    """
    def __init__(self, dicozorus_wordlist, criticality=UNRANKED, filters=None, 
            update_count_only=False):
        self.wordlist = dicozorus_wordlist
        self.criticality=criticality
        self.filters = filters if filters else []
        self.update_count_only = update_count_only

    def parse(self, wordlist_file):
        logger.info('Parsing dirsearch results %s', wordlist_file)
        with open(wordlist_file, "r", encoding="utf8") as wordlist_entries:
            for line in wordlist_entries.readlines():
                code, _, url = line.split()
                entry = urlparse(url).path.lstrip('/')
                if (not self.filters) or int(code) in self.filters:
                    logger.info("%s [HTTP_code: %s]", entry, code)
                    if self.update_count_only:
                        self.wordlist.increment_count(entry)
                    else:
                        self.wordlist.add_entry(entry, criticality=self.criticality)

    def get_wordlist(self):
        return self.wordlist




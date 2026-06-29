import csv
import re

from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import CRITICALITY

class DicozorusParser():
    """
    Parse dicozorus CSV files
    Format is : path, criticality, count ,category, tags, references
    Use quoted, comma separated values
    Example : "console/","CRITICAL","1","RCE","JAVA","https://example.org"
    """
    def __init__(
            self, dicozorus_wordlist, ignore_comments='##'):
        self.wordlist = dicozorus_wordlist
        self.ignore_comments = ignore_comments


    def parse(self, wordlist_file):
        logger.info('Parsing dicozorus CSV file %s', wordlist_file)
        entries=[]
        with open(wordlist_file, mode='r', encoding="utf8") as wordlist_entries:
            entries = wordlist_entries.read()
            if self.ignore_comments:
                entries = re.sub('^{}.*\n?'.format(self.ignore_comments), '',
                                 entries, flags=re.MULTILINE)
            entries_list = entries.splitlines()

            csv_entries = csv.reader(entries_list, quotechar='"',
                                     delimiter=',', quoting=csv.QUOTE_ALL,
                                     skipinitialspace=True)

            for csv_entry in csv_entries:
                try:
                    path, criticality, count, category, tags, ref = csv_entry
                    taglist = tags.split(',')

                    # Supplied criticality must be in
                    # UNRANKED, INFO, LOW, MEDIUM, HIGH, CRITICAL
                    if criticality not in CRITICALITY:
                        logger.error('Entry %s : criticality (%s) not in %s', path,
                            criticality, ", ".join(x for x in CRITICALITY.keys()))
                        return False

                    self.wordlist.add_entry(path,
                            criticality=CRITICALITY[criticality], count=int(count),
                            category=category, taglist=taglist, reference=ref)
                except ValueError as v:
                    logger.error('Wrong CSV entry in %s: %s. ValueError: %s',
                        wordlist_file, csv_entry, v)
                    return False
                except KeyError as k:
                    logger.error('Wrong CSV entry in %s: %s. KeyError: %s',
                        wordlist_file, csv_entry, k)
                    return False
        return True

    def get_wordlist(self):
        return self.wordlist




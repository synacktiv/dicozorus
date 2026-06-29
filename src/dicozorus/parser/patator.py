import csv

from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import UNRANKED

class PatatorParser():
    """
    Parse patator RESULT.csv files

    :param dicozorus_wordlist: The initial wordlist that will be fed.
    :param criticality: the criticality to attribute to every parsed entry
    :param filter: A list of http status code to filter out.
    :param update_count_only: Do no create new entries only update the count attribute of existing ones.
    """
    def __init__(self, dicozorus_wordlist, criticality=UNRANKED,
            filters=None, update_count_only=False):
        self.wordlist = dicozorus_wordlist
        self.filters = filters if filters else []
        self.criticality = criticality
        self.update_count_only = update_count_only

    def parse(self, patator_file):
        """
        Parse the specified file. The file should be in *patator* CSV format.

        :param patator_file: A path to a file in *patator* CSV format.
        """
        logger.info("Parsing patator results %s", patator_file)
        with open(patator_file, "r", encoding="utf8") as wordlist_entries:
            csv_entries = csv.reader(wordlist_entries)

            # Ignore csv header
            next(csv_entries)

            for _, _, code, _, _, candidate, _, _ in csv_entries:
                if (not self.filters) or int(code) in self.filters:
                    logger.info("%s [HTTP_code: %s]", candidate, code)
                    if self.update_count_only:
                        self.wordlist.increment_count(candidate)
                    else:
                        self.wordlist.add_entry(candidate, criticality=self.criticality)

    def get_wordlist(self):
        """
        Return the wordlist resulting of every parsed file.

        :return: DicozorusWordlist
        """
        return self.wordlist

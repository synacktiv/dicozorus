from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.model.entry import DicozorusEntry
from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import CRITICALITY, CRITICALITY_COLORED_NAMES

class DicozorusCheck:
    """ Implement the **check** command. """
    def __init__(self, args):
        self.candidate_wordlist = args.wordlist
        self.missing_in_wordlist = args.missing_in_wordlist
        self.stats_only = args.stats_only
        self.entry = args.entry

        self.sql_filters = []
        self.criticalities = set()
        if args.criticality:
            for criticality in args.criticality:
                self.criticalities.add(str(CRITICALITY[criticality]))
            self.sql_filters.append('criticality in ({})'.format(",".join(self.criticalities)))

        self.wordlist = DicozorusWordlist()
        self.wordlist.load(sql_filters=self.sql_filters)

    def run(self):
        """ Run the dicozorus CHECK command. """
        if self.entry:
            self.check_entry(self.entry)
        else:
            try:
                with open(self.candidate_wordlist, 'r', encoding="utf8") as c_file:
                    candidate_wordlist = set()
                    for line in c_file:
                        candidate_wordlist.add(line.rstrip('\n'))
                    if self.missing_in_wordlist:
                        self.check_missing_in_wordlist(candidate_wordlist)
                    else:
                        self.check_missing_in_dicozorus(candidate_wordlist)

            except FileNotFoundError:
                logger.error("The wordlist you provided does not exist.")

    def check_missing_in_dicozorus(self, candidate_wordlist):
        """
        Find entries that are missing from the dicozorus DB but are present
        in the specified wordlist.
        """
        if self.stats_only:
            entries_count = 0
        for entry in candidate_wordlist:
            dicozorus_entry = DicozorusEntry(entry, type_='None')
            if dicozorus_entry not in self.wordlist:
                if self.stats_only:
                    entries_count += 1
                else:
                    print(entry)
        if self.stats_only:
            print('{} entries missing from the dicozorus database.'.format(entries_count))

    def check_missing_in_wordlist(self, candidate_wordlist):
        """ 
        Find entries that are present in dicozorus DB and absent from the 
        specified wordlist.
        """
        if self.stats_only:
            entries_count_by_criticality = {}
        for dicozorus_entry in self.wordlist.entries:
            present = False
            for wordlist_entry in candidate_wordlist:
                if wordlist_entry == dicozorus_entry.name:
                    present = True
                    break
            if present is False:
                if self.stats_only:
                    if dicozorus_entry.criticality in entries_count_by_criticality:
                        entries_count_by_criticality[dicozorus_entry.criticality] += 1
                    else:
                        entries_count_by_criticality[dicozorus_entry.criticality] = 1
                else:
                    print(dicozorus_entry)
        if self.stats_only:
            for criticality in entries_count_by_criticality:
                print('Missing {} {} entries'.format(
                    entries_count_by_criticality[criticality],
                    CRITICALITY_COLORED_NAMES[criticality]))
                                    

    def check_entry(self, entry):
        """ Check if an entry is present in the dicozorus database. """
        dicozorus_entry = self.wordlist.get_entry(entry)
        if dicozorus_entry:
            print(dicozorus_entry)
        else:
            logger.error(('The entry you specified is not present in the '
               'dicozorus Database'))

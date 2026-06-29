#!/usr/bin/env python
import re
import csv
from glob import glob

from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import CRITICITY
from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.parser.dicozorus import DicozorusParser
from dicozorus.db.database import DicozorusDatabase
from dicozorus.model.entry import DicozorusEntry

TMP_UNIT_DB_PATH="/tmp/db.unit.sqlite"
BUILTIN_DIR="src/dicozorus/wordlists/"

def test_init_db():
    """
    Ensure that we can intialize a test db correctly
    """
    dicozorus_db = DicozorusDatabase(TMP_UNIT_DB_PATH, initialize=True)
    dicozorus_db.destroy()
    dicozorus_db.create_tables()
    pass

def test_parse_wordlists():
    """ 
    Ensure that all entries from the built-in wordlists can be parsed. 
    """
    dicozorus_wordlist = DicozorusWordlist(database_path=TMP_UNIT_DB_PATH)
    dicozorus_parser = DicozorusParser(dicozorus_wordlist)
    dicozorus_wordlist_files = glob("{}/*.wordlist".format(BUILTIN_DIR))
    for dicozorus_file in dicozorus_wordlist_files:
        assert dicozorus_parser.parse(dicozorus_file) == True

def test_entry_with_criticity_have_category():
    dicozorus_wordlist = DicozorusWordlist(database_path=TMP_UNIT_DB_PATH)
    dicozorus_parser = DicozorusParser(dicozorus_wordlist)
    dicozorus_wordlist_files = ["{}/critical.wordlist".format(BUILTIN_DIR),
            "{}/high.wordlist".format(BUILTIN_DIR),
            "{}/medium.wordlist".format(BUILTIN_DIR),
            "{}/low.wordlist".format(BUILTIN_DIR)]
    for dicozorus_file in dicozorus_wordlist_files:
        dicozorus_parser.parse(dicozorus_file)
    dicozorus_wordlist = dicozorus_parser.get_wordlist()
    for dicozorus_entry in dicozorus_wordlist.get_entries():
        assert dicozorus_entry.category, "Category for entries of criticity CRITICAL, HIGH, MEDIUM, LOW should not be empty"

def test_entry_critical_and_high_have_reference():
    """
    Ensure that all entries with level >= HIGH have a reference.
    """
    dicozorus_wordlist = DicozorusWordlist(database_path=TMP_UNIT_DB_PATH)
    dicozorus_parser = DicozorusParser(dicozorus_wordlist)
    dicozorus_wordlist_files = ["{}/critical.wordlist".format(BUILTIN_DIR),
            "{}/high.wordlist".format(BUILTIN_DIR)]
    for dicozorus_file in dicozorus_wordlist_files:
        dicozorus_parser.parse(dicozorus_file)
    dicozorus_wordlist = dicozorus_parser.get_wordlist()
    for dicozorus_entry in dicozorus_wordlist.get_entries():
        assert dicozorus_entry.reference, "Reference for entries of criticity CRITICAL, HIGH should not be empty"

def test_no_duplicate_in_wordlists():
    """
    Ensure that the built-in wordlists don't have duplicated entries. 
    Duplicates accross wordlists are allowed (the highest criticity is kept 
    and the count is increased by the number of duplicates).
    """
    dicozorus_wordlist_files = glob("{}/*.wordlist".format(BUILTIN_DIR))

    duplicates=False
    ignore_comments='##'

    for dicozorus_file in dicozorus_wordlist_files:
        dicozorus_db = DicozorusDatabase(TMP_UNIT_DB_PATH, initialize=True)
        dicozorus_db.destroy()
        dicozorus_db.create_tables()
        dicozorus_wordlist = DicozorusWordlist(database_path=TMP_UNIT_DB_PATH)
        dicozorus_parser = DicozorusParser(dicozorus_wordlist)
        with open(dicozorus_file, mode='r', encoding="utf8") as wordlist_entries:
            entries=[]
            entries = wordlist_entries.read()
            entries = re.sub('^{}.*\n?'.format(ignore_comments), '',
                             entries, flags=re.MULTILINE)
            entries_list = entries.splitlines()
            csv_entries = csv.reader(entries_list, quotechar='"',
                                     delimiter=',', quoting=csv.QUOTE_ALL,
                                     skipinitialspace=True)
            for csv_entry in csv_entries:
                try:
                    path, criticity, count, category, tags, ref = csv_entry
                    taglist = tags.split(',')
                    if criticity not in CRITICITY:
                        logger.error('Entry %s : criticity (%s) not in %s', path,
                            criticity, ", ".join(x for x in CRITICITY.keys()))
                    tmp_entry = DicozorusEntry(path, 'FILE', 
                             criticity=CRITICITY[criticity], category=category,
                             reference=ref)
                    if tmp_entry in dicozorus_wordlist:
                        if (tmp_entry.category == dicozorus_wordlist.get_entry(path).category and 
                            tmp_entry.reference == dicozorus_wordlist.get_entry(path).reference) :
                            logger.error('Multiple occurence of %s [%s] in %s',
                                path, category, dicozorus_file)
                            duplicates=True
                    dicozorus_wordlist.add_entry(path,
                            criticity=CRITICITY[criticity], count=int(count),
                            category=category, taglist=taglist, reference=ref)
                except ValueError as v:
                    logger.error('Wrong CSV entry in %s: %s. ValueError: %s',
                        wordlist_file, csv_entry, v)
                except KeyError as k:
                    logger.error('Wrong CSV entry in %s: %s. KeyError: %s',
                        wordlist_file, csv_entry, k)
        # Ensure each wordlists does not contains duplicates 
        assert duplicates == False, "Some of the builtins wordlists contains duplicates."

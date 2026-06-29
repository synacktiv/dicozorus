import re
import json
import random

from dicozorus.utils.logging import LOGGER as logger, DEBUG
from dicozorus.model.entry import DicozorusEntry, UNRANKED
from dicozorus.model.entry import FILE, PATH, DIRECTORY
from dicozorus.db.database import DicozorusDatabase

from dicozorus.utils.set import OrderedSet


class DicozorusWordlist:
    """
    DicozorusWordlist store and manage access to an ordered set of
    DicozorusEntry.
    """
    def __init__(self, criticality=UNRANKED, database_path=None):
        self.entries= OrderedSet()
        self.criticality=criticality

        if database_path:
            self.dicozorus_db = DicozorusDatabase(database_path)
        else:
            self.dicozorus_db = DicozorusDatabase()

    def __contains__(self, entry):
        return entry in self.entries

    # pylint: disable=too-many-arguments
    def add_entry(self, name, type_=None, criticality=None, count=1, category="",
            taglist=None, reference=""):
        """
        Create a DicozorusEntry with the specified criteria and add it to
        the wordlist
        """
        taglist = taglist if taglist else []
        if type_ is None:
            if name == "":
                entry_type = FILE
            elif "/" in name[:-1]:
                entry_type = PATH
            elif name[-1] == '/':
                entry_type = DIRECTORY
            else:
                entry_type = FILE
        else:
            entry_type = type_

        if criticality is None:
            criticality = self.criticality

        dicozorus_entry = DicozorusEntry(name, entry_type, criticality, count,
                category, taglist, reference)
        self.add_dicozorus_entry(dicozorus_entry)

    def add_dicozorus_entry(self, entry):
        """ Add a DicozorusEntry to the wordlist """
        if entry not in self.entries:
            self.entries.add(entry)
        else:
            existing_entry = self.get_entry(entry.name)
            total_entry_count = existing_entry.count + entry.count
            combined_taglist = list(set(existing_entry.taglist+entry.taglist))
            
            # If the criticality are different, keep the highest criticality entry
            if entry.criticality > existing_entry.criticality:
                entry.count = total_entry_count
                entry.taglist = combined_taglist
                self.update_dicozorus_entry(entry)
            else:
                existing_entry.count = total_entry_count
                existing_entry.taglist = combined_taglist
                self.update_dicozorus_entry(existing_entry)
            if logger.getEffectiveLevel() == DEBUG:
                logger.warning('%s already present in the database (%s)', entry, existing_entry)

    # pylint: disable=too-many-arguments
    def update_entry(self, name, type_=None, criticality=None, count=1, category="",
            taglist=None, reference=""):
        """
        Create a DicozorusEntry with the specified criteria and use it to
        update the wordlist
        """
        taglist = taglist if taglist else []
        if type_ is None:
            if name == "":
                entry_type = FILE
            elif "/" in name[:-1]:
                entry_type = PATH
            elif name[-1] == '/':
                entry_type = DIRECTORY
            else:
                entry_type = FILE
        else:
            entry_type = type_

        if criticality is None:
            criticality = self.criticality

        dicozorus_entry = DicozorusEntry(name, entry_type, criticality, count,
                category, taglist, reference)
        self.update_dicozorus_entry(dicozorus_entry)


    def update_dicozorus_entry(self, entry):
        """
        Use a dicozorus entry to update the current wordlist.
        """
        self.entries.discard(entry)
        self.entries.add(entry)

    def remove_entry(self, entry_name):
        """ Remove the entry with the specified name from the dicozorus wordlist """
        # Entry type does not matter here as the entry is to be deleted
        dicozorus_entry = DicozorusEntry(entry_name, type_=FILE)
        self.remove_dicozorus_entry(dicozorus_entry)


    def remove_dicozorus_entry(self, dicozorus_entry):
        """ Remove a DicozorusEntry from the Dicozorus wordlist """
        self.entries.discard(dicozorus_entry)

    def increment_count(self, entry_name):
        existing_entry = self.get_entry(entry_name)
        if existing_entry:
            existing_entry.count += 1

    def get_entry(self, name):
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None

    def get_entries(self):
        """ Return the OrderedSet of entries """
        return self.entries


    def print(self, shuffle=False):
        """
        Print the wordlist on the current terminal
        If debug is enable, also print properties of each entry
        """
        if shuffle:
            entries = list(self.entries)
            random.shuffle(entries)
        else:
            entries = self.entries

        for entry in entries:
            if logger.getEffectiveLevel() == DEBUG:
                logger.debug(entry)
            else:
                print(entry.name)

    def load(self, max_entries=None, sql_filters=None, regex_filter=None,
            tag_filter=None, order_by='criticality,count'):
        """
        Load *max_entries* from the database. Only retrieve entries matching
        the sql_filter from the database (filter-in). Selected entries can be
        further reduced using a regex-filter (filter-out).
        """
        tag_filter = tag_filter if tag_filter else []
        db_entries = self.dicozorus_db.get_entries(max_entries=max_entries,
                filters=sql_filters, order_by=order_by)
        for row in db_entries:
            (name, type_, criticality, count, category, taglist, ref) = row
            # Here we filter out entries matching the regex
            if regex_filter:
                re_match = re.search(regex_filter, name) 
                if (not re_match):
                    self.add_entry(name, type_, criticality, count, category,
                            json.loads(taglist), ref)
            # Should be renamed, we are selecting not filtering out.
            elif tag_filter:
                tag_match = any(tag in taglist for tag in tag_filter) 
                if tag_match:
                    self.add_entry(name, type_, criticality, count, category,
                            json.loads(taglist), ref)
            # If no filter is specified we just print out all the entries
            else:
                self.add_entry(name, type_, criticality, count, category,
                        json.loads(taglist), ref)
    

    def save(self):
        """ Save the wordlist to the dicozorus sqlite db """
        self.dicozorus_db.flush_entries()
        self.dicozorus_db.save(self.entries)

    def save_to_file(self, dest_file, shuffle=False):
        """ Save the current wordlist to the specified file """
        logger.info("Saving wordlist to %s", dest_file)

        if shuffle:
            entries = list(self.entries)
            random.shuffle(entries)
        else:
            entries = self.entries

        with open(dest_file, "w", encoding="utf8") as output_file:
            for entry in entries:
                output_file.write("{}\n".format(entry.name))


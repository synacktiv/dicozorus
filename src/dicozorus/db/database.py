import sqlite3
from os import path, makedirs, getenv
import sys
import json

from dicozorus.utils.logging import LOGGER as logger

DEFAULT_DB='db.sqlite'
DEFAULT_DB_DIR='{}/.dicozorus'.format(getenv('HOME'))
DEFAULT_DB_PATH='{}/{}'.format(DEFAULT_DB_DIR,
        DEFAULT_DB)

class DicozorusDatabase:
    """
    This class is used to interract with the database.

    :param db: The database to connect to.
    :param initialize: Wether or not the database should be initialized.
    """
    def __init__(self, db=DEFAULT_DB_PATH, initialize=False):


        self.tables = {
            'dicozorus_entries': ('(name TEXT PRIMARY KEY, type TEXT, '
                                  'criticality INTEGER, count INTEGER, '
                                  'category TEXT, tags TEXT, reference TEXT)'),
            'dicozorus_known_files': '(hash TEXT PRIMARY KEY, name TEXT)'
        }


        # Check if the database file exist
        if not path.exists(db):
            if initialize:
                if not path.exists(DEFAULT_DB_DIR):
                    makedirs(DEFAULT_DB_DIR)
                with open(db, 'a', encoding="utf8"):
                    pass
            else:
                logger.error(('Dicozorus database does not exist yet. please '
                    'run `dicozorus init` first'))
                sys.exit(-1)

        # Open the database
        self.db = sqlite3.connect(db)

        # Check if the database is initialized
        if (not initialize) and (not self.is_initialized()):
            logger.error(('Dicozorus database is not initialized yet. please '
                'run `dicozorus init` first'))
            sys.exit(-1)

    def __contains__(self, entry):
        """
        Check wether or not the database contains the
        specified DicozorusEntry

        :param entry: The DicozorusEntry to search for.
        """
        result = self.db.execute('SELECT * FROM dicozorus_entries WHERE name=?'
            , (entry.name,)).fetchone()
        return result is not None

    def is_initialized(self):
        """
        Check wether the database has been initialized or not.
        """
        for table_name in self.tables:
            if not self.table_exists(table_name):
                return False
        return True


    def destroy(self):
        """ Drop all dicozorus tables """
        logger.info('Dropping all existing tables')
        for table_name in self.tables.keys():
            if self.table_exists(table_name):
                self.db.execute('DROP TABLE {}'.format(table_name))

    def commit(self):
        """ Commit the SQLite database """
        self.db.commit()

    def insert(self, entry):
        """
        Insert a new entry in the dicozorus_entries table

        :param entry: The entry to be inserted.
        """
        logger.debug('Inserting new entry: %s', entry)
        self.db.execute(('INSERT INTO dicozorus_entries '
            '(name, type, criticality, count, category, tags, reference)'
            'VALUES (?, ?, ?, ?, ?, ?, ?)'),
            (entry.name, entry.type, entry.criticality, entry.count,
                entry.category, json.dumps(entry.taglist), entry.reference))
        self.db.commit()

    def flush_entries(self):
        """ Empty the dicozorus_entries table """
        self.db.execute("DELETE FROM dicozorus_entries")

    def save(self, entries):
        """
        INSERT or REPLACE a list of entries in the dicozorus_entries table
        used when lots of entries are to be added and performance is a problem.
        """
        logger.debug('Saving many entries ... ')
        self.db.executemany(('INSERT OR REPLACE INTO dicozorus_entries '
            '(name, type, criticality, count, category, tags, reference)'
            'VALUES (?, ?, ?, ?, ?, ?, ?)'),
            [(entry.name, entry.type, entry.criticality, entry.count,
                entry.category, json.dumps(entry.taglist), entry.reference)
            for entry in entries])
        self.db.commit()

    def update(self, entry):
        """
        Update an existing entry in the dicozorus database.
        """
        (db_name, db_type, db_criticality, db_count) = self.db.execute(
                ('SELECT name, type, criticality, count FROM dicozorus_entries '
                'WHERE name = ?'), (entry.name,)).fetchone()
        count = db_count + entry.count
        criticality = entry.criticality
        if count != db_count or criticality != db_criticality:
            logger.debug(('Updating entry %s [type: %s, criticality: %s, count: '
                '%d'), db_name, db_type, criticality, count)
        self.db.execute(('UPDATE dicozorus_entries SET count = ?, '
            'criticality = ? WHERE name = ?'), (count, criticality, db_name))
        self.db.commit()

    def get_entries(self, max_entries=None, filters=None,
            order_by='criticality,count'):
        """
        Retrieve entries from the database. Entries will be sorted by
        criticality and count by default.

        :param max_entries: The maximum number of entries to retrieve
        :param filters: A list of criteria to filter entries. Ex: ['type=FILE', 'type=PATH']
        :param order_by: A comma-separated list of criteria to order entries.
        """
        limit = 'LIMIT {}'.format(max_entries) if max_entries else ''
        where = 'WHERE {}'.format(' AND '.join(
            '(' + f + ')' for f in filters)) if filters else ''
        order = 'ORDER BY {}'.format(' DESC, '.join(order_by.split(','))
                + ' DESC')

        sql_query = ('SELECT * FROM dicozorus_entries {} {} {}').format(where, order, limit)
        logger.debug('Executing query: %s', sql_query)
        return self.db.execute(sql_query)

    def close(self):
        self.db.close()

    def create_tables(self):
        for table_name, table_schema in self.tables.items():
            self.db.execute('''CREATE TABLE {} {}'''.format(table_name,
                table_schema))
            logger.debug('Creating table %s %s', table_name, table_schema)

    def table_exists(self, table_name):
        table_exists = self.db.execute(('SELECT name FROM sqlite_master WHERE '
            'type="table" AND name="%s"''') % table_name).fetchone()
        if table_exists:
            return True
        return False

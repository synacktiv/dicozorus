from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.model.entry import FILE, DIRECTORY, PATH
from dicozorus.model.entry import CRITICALITY

PHP_EXTENSIONS="php|php3|php4|php5|phtm|phtml"
ASP_EXTENSIONS="asp|aspx|asmx|ashx|asax"
JAVA_EXTENSIONS="do|faces|jsp|jsf|jspa|cfm|nsf"

# pylint: disable=too-many-instance-attributes
class DicozorusGenerator:
    """
    Implement the **gen** subcommand.
    """
    def __init__(self, args):
        self.wordlist = DicozorusWordlist()
        self.output_file = args.output
        self.max_entries = args.max_entries
        self.order_by = args.sort
        self.shuffle = args.shuffle
        self.regex_filter = args.filter
        self.sql_filters = []
        self.min_criticality = CRITICALITY[args.min_criticality]
        self.criticalities = set()
        if args.criticality:
            for criticality in args.criticality:
                self.criticalities.add(str(CRITICALITY[criticality]))
        
        # Select by tags
        self.tags_filter = set()
        if args.select_by_tags:
            for tag in args.select_by_tags.split(","):
                self.tags_filter.add(tag)


        ## Type filter
        no_type_filter = False
        type_filter_list =[]
        if not (args.filter_dir or args.filter_file or args.filter_path):
            no_type_filter = True
        if args.filter_dir or no_type_filter:
            type_filter_list.append('type="{}"'.format(DIRECTORY))
        if args.filter_file or no_type_filter:
            type_filter_list.append('type="{}"'.format(FILE))
        if args.filter_path or no_type_filter:
            type_filter_list.append('type="{}"'.format(PATH))
        self.sql_filters.append(" OR ".join(type_filter_list))

        # Criticity explicitly stated (-c / --criticality)
        if self.criticalities:
            self.sql_filters.append('criticality in ({})'.format(",".join(self.criticalities)))
        ## Minimum criticality (--min-criticality)
        else:
            self.sql_filters.append('criticality>={}'.format(self.min_criticality))


    def gen(self):
        """
        Generate the wordlist and print it. The output will go either to
        stdout or to the specified output file.
        """
        self.load_wordlist()
        if self.output_file:
            self.wordlist.save_to_file(self.output_file, shuffle=self.shuffle)
        else:
            self.wordlist.print(shuffle=self.shuffle)

    def load_wordlist(self):
        """
        Load entries from the database using the specified options
        as filters.
        """
        self.wordlist.load(max_entries=self.max_entries,
                sql_filters=self.sql_filters,regex_filter=self.regex_filter,
                tag_filter=self.tags_filter, order_by=self.order_by)

from dicozorus.utils.colors import Colors

# Entry type
PATH="PATH"
FILE="FILE"
DIRECTORY="DIRECTORY"

# Entry criticality
CRITICAL=5
HIGH=4
MEDIUM=3
LOW=2
INFO=1
UNRANKED=0

CRITICALITY = {'UNRANKED': 0, 'INFO': 1, 'LOW': 2,
        'MEDIUM':3, 'HIGH':4, 'CRITICAL': 5}
CRITICALITY_NAMES = {0:'UNRANKED', 1:'INFO', 2:'LOW',
        3:'MEDIUM', 4:'HIGH', 5:'CRITICAL'}
CRITICALITY_COLORED_NAMES = {0:Colors.black('UNRANKED'), 1:Colors.cyan('INFO'), 2:Colors.blue('LOW'),
        3:Colors.yellow('MEDIUM'), 4:Colors.orange('HIGH'), 5:Colors.red('CRITICAL')}

class DicozorusEntry:
    """
    Store entries and their attributes.

    :param name: the name of the entry. For example "manager/html"
    :param type: FILE, DIRECTORY or PATH
    :param criticality: CRITICAL, HIGH, MEDIUM, LOW, INFO or UNRANKED
    :param count: the number of times the entry was seen
    :param category: if related to a vulnerability, categorize it
    :param taglist: a list of tag related to the entry. For example PHP or JAVA
    :param reference: a refrence link
    """
    def __init__(self, name, type_, criticality=0, count=1,  category="",
            taglist=None, reference=""):
        # pylint: disable=too-many-arguments
        # Eight is reasonable in this case.
        self.name = name
        self.type = type_
        self.criticality = criticality
        self.count = count
        self.category = category
        self.taglist = taglist if taglist else []
        self.reference = reference

    def __hash__(self):
        return(hash(self.name))

    def __eq__(self, value):
        """
        Compare this DicozorusEntry with another
        """
        return self.name == value.name

    def __lt__(self, value):
        return ((self.criticality < value.criticality) or 
            (self.criticality == value.criticality and self.count < value.count))

    def __repr__(self):
        """ Return a string representation of the DicozorusEntry """
        return ('{} [type: {}, criticality: {}, count: {}, category: {}, '
            'taglist: {}, reference: {}]').format(Colors.white(self.name), self.type,
                    CRITICALITY_COLORED_NAMES[self.criticality], self.count,
                    Colors.green(self.category), self.taglist, self.reference)

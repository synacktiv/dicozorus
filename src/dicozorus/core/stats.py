from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.model.entry import UNRANKED, INFO, LOW, MEDIUM, HIGH, CRITICAL
from dicozorus.model.entry import FILE, DIRECTORY, PATH
from dicozorus.utils.colors import Colors
from dicozorus.utils.logging import LOGGER as logger

class DicozorusStats:
    """
    Implement the **stats** subcommand.
    """
    def __init__(self, args):
        # pylint: disable=unused-argument
        # Keep the args argument to simplify Commands' logic
        self.wordlist = DicozorusWordlist() 
        self.wordlist.load()

    def show(self):
        """ 
        Show statistics about the dicozorus database
        """
        total_count = 0
        criticality_stats = { CRITICAL: 0, 
                           HIGH: 0,
                           MEDIUM: 0,
                           LOW: 0,
                           INFO: 0,
                           UNRANKED: 0 }
        category_stats = {}

        type_stat = { FILE: 0,
                      DIRECTORY: 0,
                      PATH: 0 }

        all_entries = self.wordlist.get_entries()
        for entry in all_entries:
            total_count += 1
            criticality_stats[entry.criticality] += 1
            type_stat[entry.type] += 1
            if entry.category not in category_stats:
                category_stats[entry.category] = 1
            else:
                category_stats[entry.category] +=1
        
        logger.info("Total count: %d", total_count)

        logger.info("Entry count by criticality:")
        for key, value in criticality_stats.items():
            if key == CRITICAL:
                print("\t{}: {}".format(Colors.red('Critical'), value))
            elif key == HIGH:
                print("\t{}: {}".format(Colors.orange('High'), value))
            elif key == MEDIUM:
                print("\t{}: {}".format(Colors.yellow('Medium'), value))
            elif key == LOW:
                print("\t{}: {}".format(Colors.blue('Low'), value))
            elif key == INFO:
                print("\t{}: {}".format(Colors.cyan('Info'), value))
            elif key == UNRANKED:
                print("\t{}: {}".format(Colors.black('Unranked'), value))

        logger.info("Entry count by type:")
        for key, value in type_stat.items():
            print("\t{}: {}".format(key, value))


        # Print category from highest count to lowest
        logger.info("Entry count by category:")        
        for category in sorted(category_stats, key=category_stats.get, reverse=True):
            if category:
                print("\t{}: {}".format(category, category_stats[category]))
            else:
                print("\tUNCATEGORIZED: {}".format(category_stats[category]))


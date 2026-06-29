from dicozorus.model.wordlist import DicozorusWordlist
from dicozorus.utils.logging import LOGGER as logger
from dicozorus.model.entry import CRITICALITY

class DicozorusModify:
    """
    Implent the **modify** subcommand.
    """
    def __init__(self, args):
        self.dicozorus_wordlist = DicozorusWordlist()
        if args.add:
            self.action = 'ADD'
        elif args.rm:
            self.action = 'REMOVE'
        else:
            self.action = 'UPDATE'
        self.entry = args.entry
        self.wordlist = args.wordlist

        self.criticality = CRITICALITY.get(args.criticality)
        self.count = args.count
        self.category = args.category
        self.taglist = args.taglist.split(",") if args.taglist else []
        self.reference= args.reference

        # Load the content of the database into the dicozorus wordlist
        self.dicozorus_wordlist.load()

    def run(self):
        if self.entry:
            if self.action == 'ADD':
                logger.info("Adding entry %s", self.entry)
                self.dicozorus_wordlist.add_entry(self.entry,
                        criticality=self.criticality, count=self.count,
                        category=self.category, taglist=self.taglist,
                        reference=self.reference)
            elif self.action == 'REMOVE':
                logger.info("Removing entry %s", self.entry)
                self.dicozorus_wordlist.remove_entry(self.entry)
            elif self.action == 'UPDATE':
                logger.info("Updating entry %s", self.entry)
                self.dicozorus_wordlist.update_entry(self.entry,
                        criticality=self.criticality, count=self.count,
                        category=self.category, taglist=self.taglist,
                        reference=self.reference)
            self.dicozorus_wordlist.save()
        elif self.wordlist:
            try:
                with open(self.wordlist, 'r', encoding="utf8") as wordlist:
                    if self.action == 'ADD':
                        logger.info("Adding entries from %s", self.wordlist)
                        for entry in wordlist.read().splitlines():
                            self.dicozorus_wordlist.add_entry(entry,
                                    criticality=self.criticality, count=self.count,
                                    category=self.category, taglist=self.taglist,
                                    reference=self.reference)

                    elif self.action == 'REMOVE':
                        logger.info("Removing entries from %s", self.wordlist)
                        for entry in wordlist.read().splitlines():
                            self.dicozorus_wordlist.remove_entry(entry)

                    elif self.action == 'UPDATE':
                        logger.info("Updating entries from %s", self.wordlist)
                        for entry in wordlist.read().splitlines():
                            self.dicozorus_wordlist.update_entry(entry,
                                    criticality=self.criticality, count=self.count,
                                    category=self.category, taglist=self.taglist,
                                    reference=self.reference)
                    self.dicozorus_wordlist.save()
            except FileNotFoundError:
                logger.error("The file %s does not exist", self.wordlist)

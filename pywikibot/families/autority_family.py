 # -*- coding: utf-8  -*-

from pywikibot import family

# The official Mozilla Wiki. #Put a short project description here.

class Family(family.Family):

    name = 'autority' # Set the family name; this should be the same as in the filename.
    langs = {
        'autority': 'autority.wikimedia.cz', # Put the hostname here.
    }

    # def version(self, code):
    #     return "1.4.2"  # The MediaWiki version used. Not very important in most cases.

    def scriptpath(self, code):
        return '' # The relative path of index.php, api.php : look at your wiki address.

    def protocol(self, code):
        return "https"
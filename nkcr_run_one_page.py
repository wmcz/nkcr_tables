#run some page
import sys

import create_nkcr_table
import pywikibot
import datetime
import nkcrlib

# get pages to update – OK
# get only 10 newest – OK
# run act – OK

actual_week_num_obj = datetime.datetime.now()
actual_year = actual_week_num_obj.year
actual_week_num = nkcrlib.get_week_num_to_download()

#site = pywikibot.getSite('wikidata', 'wikidata')
site = pywikibot.Site('wikidata', 'wikidata')

c = create_nkcr_table.create_table()
c.update_main_page = False
c.table = []
c.run(1,2023)

# create_nkcr_table.create_table()
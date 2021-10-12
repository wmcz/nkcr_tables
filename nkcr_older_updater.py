#run every 1 hour
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

site = pywikibot.getSite('wikidata', 'wikidata')
c = create_nkcr_table.create_table()

## get exist pages
exist_pages = c.get_exist_pages(site)
prepared = c.prepare_pages_for_older_updater(exist_pages, actual_year, actual_week_num)

for page in prepared:
    print('page to update: ' + str(page['year']) + '/' + str(page['week']))
    c = create_nkcr_table.create_table()
    c.update_main_page = False
    c.table = []
    c.run(int(page['week']))

# create_nkcr_table.create_table()
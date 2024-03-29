#run every 1 hour
import os
import sys

import create_nkcr_table
import pywikibot
import datetime
import nkcrlib

# get pages to update – OK
# get only 10 newest – OK
# run act – OK

#site = pywikibot.getSite('wikidata', 'wikidata')
site = pywikibot.Site('wikidata', 'wikidata')
c = create_nkcr_table.create_table()

## get exist pages
years = list(range(2021,2025))
weeks = list(range(0,52))

for year in years:
    for week in weeks:
        week_to_file = str(week).zfill(2)
        file = "/home/frettie/" + str(year) + '-wnew_m_' + week_to_file + '.xml'
        print(file)
        if os.path.isfile(file):
            print('file: ' + file)
            c = create_nkcr_table.create_table()
            c.update_main_page = False
            c.table = []
            c.run(week, year, False, True)

# create_nkcr_table.create_table()
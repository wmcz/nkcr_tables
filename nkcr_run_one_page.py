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

c.quick_lines = []
c.run(0)
c.table = []
#
# c.quick_lines = []
# c.run(1, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(2, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(3, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(4, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(5, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(6, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(7, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(8, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(9, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(10, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(11, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(12, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(13, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(14, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(15, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(16, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(17, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(18, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(19, 2023, False, True)
#
# c.table = []
# c.quick_lines = []
# c.run(20, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(21, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(22, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(23, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(24, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(25, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(26, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(27, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(28, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(29, 2023, False, True)
#
# c.table = []
# c.quick_lines = []
# c.run(30, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(31, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(32, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(33, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(34, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(35, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(36, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(37, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(38, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(39, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(40, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(41, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(42, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(43, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(44, 2023, False, True)

# c.table = []
# c.quick_lines = []
# c.run(45, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(46, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(47, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(48, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(49, 2023, False, True)
# c.table = []
# c.quick_lines = []
# c.run(50, 2023, False, True)
# #
# c.table = []
# c.quick_lines = []
# c.run(51, 2023, False, True)
#
# c.table = []
# c.quick_lines = []
# c.run(52, 2023, False, True)

c.table = []
c.quick_lines = []
c.run(24, 2021, False, True)



# create_nkcr_table.create_table()
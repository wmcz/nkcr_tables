#run every 1 hour
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

## get exist pages
exist_pages = c.get_exist_pages(site)
prepared = c.prepare_pages_for_older_updater(exist_pages, actual_year, actual_week_num)

prepend_text = """
<div id="not-actualized" style="background-color: #ebf3f8; width: 100%; display:block; padding: 10px; font-weight: bolder; border: 1px solid black">
Tato stránka již není pravidelně automaticky aktualizována, prosíme dokončené položky z tabulky odstraňte ručně.
</div>
"""

for page in exist_pages:
    if page not in prepared:
        if not (actual_year == int(page['year']) and actual_week_num == int(page['week'])):
            page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + str(page['year']) + '/' + str(page['week']))
            text = page.get()
            if not('not-actualized' in text):
                # print(page)
                # print(prepend_text)
                new_text = prepend_text + '''
                
                ''' + text
                page.text = new_text
                page.save()

# create_nkcr_table.create_table()
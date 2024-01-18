import json
import os
# import sys
# from typing import List, Any
from typing import List, Any

import requests

from autrecord import AutRecord
import re
import nkcrlib
from wikitable import wikitable
# import urllib
# from datetime import datetime
# from quickstatements import quickstatements
from nkcr_record import nkcr_record

# from pywikibot import config, i18n, pagegenerators, textlib, page, site
import pywikibot

WEEK_NUM_CONST = None

OLDER_UPDATER_PAGE_COUNT = 10

class create_table:
    table = []
    year: str = ''
    update_main_page: bool = True

    debug: bool = False

    def table_line(self, record, count, mydata):
        assert isinstance(record, AutRecord)
        aut = record.aut()
        # if (aut == 'js20231197909'):
        #     print('ano')
        record_in_nkcr = nkcr_record(record)
        # print('table line ' + str(record_in_nkcr.aut))
        if (count % 10 == 0):
            print('nkcr record counter: ' + str(count))

        if self.already_filled_in_wikidata(record_in_nkcr.aut):
            return False

        if (not self.debug):
            qid_from_viaf = self.find_on_viaf(str(record_in_nkcr.aut))
        else:
            qid_from_viaf = None

        if (not self.debug):
            if (qid_from_viaf is not None):
                wd_link = nkcrlib.create_quickstatements_link(record_in_nkcr, qid_from_viaf)
            else:
                wd_link = ""
        else:
            wd_link = ""

        if (record_in_nkcr.wikiproject_from_nkcr != ''):
            qid_from_wiki = self.get_qid_by_wiki(record_in_nkcr.wikilang_from_nkcr, record_in_nkcr.wikiarticle_from_nkcr)
            if (record_in_nkcr.wikidata_from_nkcr is None and qid_from_wiki is not None):
                record_in_nkcr.wikidata_from_nkcr = qid_from_wiki

        birth_to_table = ""
        if record_in_nkcr.birth_to_quickstatements is not None:
            birth_to_table = record_in_nkcr.birth_to_quickstatements

        death_to_table = ""
        if record_in_nkcr.death_to_quickstatements is not None:
            death_to_table = record_in_nkcr.death_to_quickstatements
        table_columns = {
            'nkcr_aut': record_in_nkcr.aut,
            'name': str(record_in_nkcr.name) + nkcrlib.create_nkcr_link(record_in_nkcr.aut),
            # 'first_name' : record_in_nkcr.first_name,
            # 'last_name' : record_in_nkcr.last_name,
            # 'narozen' : record_in_nkcr.birth,
            # 'zemrel' : record_in_nkcr.death,
            # 'okres' : record_in_nkcr.county,
            'birth_qs': birth_to_table,
            'death_qs': death_to_table,
            'popis': record_in_nkcr.description,
            # 'birth_from_note' : record_in_nkcr.birth_from_note,
            # 'death_from_note' : record_in_nkcr.death_from_note,
            # 'birth_note_precision' : record_in_nkcr.birth_note_precision,
            # 'death_note_precision' : record_in_nkcr.death_note_precision,
            # 'birth_wd' : record_in_nkcr.birth_wd,
            # 'death_wd' : record_in_nkcr.death_wd,
            # 'type' : record_in_nkcr.type,
            # 'new' : record_in_nkcr.new,
            # 'updated' : record_in_nkcr.updated,
            # 'orcid' : record_in_nkcr.orcid_field,
            # 'wikidata_from_nkcr' : record_in_nkcr.wikidata_from_nkcr,
            # 'wikilang_from_nkcr' : record_in_nkcr.wikilang_from_nkcr,
            # 'wikiarticle_from_nkcr' : record_in_nkcr.wikiarticle_from_nkcr,
            # 'wikiproject_from_nkcr' : record_in_nkcr.wikiproject_from_nkcr,
            # 'wikilink_from_nkcr' : record_in_nkcr.wikilink_from_nkcr,
            'qid_from_viaf': wd_link,
            'akce': nkcrlib.create_search_link(record_in_nkcr.name) + "&nbsp;/&nbsp;" + nkcrlib.create_quickstatements_link(
                record_in_nkcr)
        }

        self.table.append(table_columns)

        return False


    def load_to_table(self, file_name):
        nkcrlib.map_xml(self.table_line, file_name)


    def save_page(self, week_num, table, quiet = False):
        site = pywikibot.Site('wikidata', 'wikidata')
        # site = pywikibot.getSite('wikidata', 'wikidata')

        header_text = "'''Nové záznamy v databázi autorit NKČR za " + str(week_num) + ". týden roku " + self.year + ".'''"

        try:
            page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + self.year + '/' + str(week_num))
            page.text = table
            page.save(quiet=quiet)
            if (self.update_main_page == True):
                exist_weeks = self.get_exist_pages(site)

                older_weeks_list = ''
                for exist_week in exist_weeks:
                    older_weeks_list = older_weeks_list + '\n'
                    older_weeks_list = older_weeks_list + '* ' + '[[/' + str(exist_week['year']) + '/' +  str(exist_week['week']) + '|' + str(exist_week['year']) + '/' + str(exist_week['week']) + ']]'

                # print(older_weeks_list)
                # print(exist_weeks)
                year = self.year
                actual_link = "{{/" + str(year) + '/' + str(week_num) + "}}"
                text_main_page = """Nové záznamy v databázi autorit NKČR
            
== Nejnovější týden (""" + str(week_num) + """) ==
""" + actual_link + """
            
== Starší ==
{{Div col|6}}
""" + older_weeks_list + """
{{Div col end}}
            
"""

                page = pywikibot.Page(pywikibot.Site('wikidata', fam='wikidata'), 'Wikidata:WikiProject Czech Republic/New authorities')
                page.text = text_main_page
                page.save(quiet=quiet)
            else:
                pass
                # print('No save main page! It is ok!')
        except pywikibot.exceptions.NoPageError:
            print('No page:' + 'Wikidata:WikiProject Czech Republic/New authorities')
            pass

    def get_exist_pages(self, site):

        exist_weeks = []

        years = ['2020', '2021', '2022', '2023', '2024', '2025']

        weeks = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                 '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                 '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                 '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
                 '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
                 '50', '51'
                 ]
        weeks.reverse()

        for year in years:
            for week in weeks:
                # print(week)
                try:
                    page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + str(year) + '/' + str(week))
                    page.get()
                    wk = {'week' : week, 'year' : year}
                    exist_weeks.append(wk)
                except pywikibot.exceptions.NoPageError:
                    # print('No page: ' + 'Wikipedista:Frettie/nkcr_table/' + str(week))
                    pass
        return exist_weeks

    def prepare_pages_for_older_updater(self, exist_pages, actual_year, actual_week_num):
        prepared = []
        for wk in exist_pages:
            if (int(wk['year']) == actual_year and actual_week_num == int(wk['week'])):
                continue
            if (int(wk['year']) == actual_year):
                if (len(prepared) <= OLDER_UPDATER_PAGE_COUNT):
                    prepared.append(wk)

        if (len(prepared) < OLDER_UPDATER_PAGE_COUNT):
            # get older
            for wk in exist_pages:
                if (len(prepared) < OLDER_UPDATER_PAGE_COUNT):
                    if (int(wk['year']) == actual_year - 1):
                        prepared.append(wk)
        return prepared

    def already_filled_in_wikidata(self, nkcr_aut=''):
        PROPERTY = 'P691'
        try:
            hub_link = "https://hub.toolforge.org/" + PROPERTY + ":" + str(nkcr_aut) + "?format=json"
            response = requests.get(hub_link)
            json_record = response.text
            response.status_code
            if response.status_code == 200:
                data_record = json.loads(json_record)
                wd_record = data_record['origin']['qid']
                return True
            return False
        except (KeyError, TypeError):
            return False


    def get_qid_by_viaf_id(self, viaf_id=''):
        property = 'viaf'

        try:
            hub_link = "https://hub.toolforge.org/" + property + ":" + str(viaf_id) + "?site=wikidata&format=json"
            response = requests.get(hub_link)
            if response.status_code == 200:
                json_record = response.text
                data_record = json.loads(json_record)
                wd_record = data_record['origin']['qid']
                print('qid by viaf found: ' + str(viaf_id))
                return wd_record
            else:
                return None
        except (KeyError, TypeError, json.decoder.JSONDecodeError):
            return None

    def get_qid_by_wiki(self, project, article):
        property = 'viaf'

        try:
            #/enwiki:DIY?site=wikidata
            query = project + 'wiki:' + article + '?site=wikidata'
            hub_link = "https://hub.toolforge.org/" + query + "&format=json"
            response = requests.get(hub_link)
            if response.status_code == 200:
                json_record = response.text
                data_record = json.loads(json_record)
                wd_record = data_record['destination']['preferedSitelink']['title']
                # print('qid by wikilink found: ' + 'found')
                return wd_record
            else:
                return None
        except (KeyError, TypeError, json.decoder.JSONDecodeError):
            return None


    def find_on_viaf(self, nkcr_aut=''):
        try:

            url_source_id_viaf = 'http://www.viaf.org/viaf/sourceID/NKC|' + str(nkcr_aut)
            response = requests.get(url_source_id_viaf, allow_redirects=False)
            viaf_url = response.next.url
            splitted = viaf_url.split('/')
            viaf_id = splitted[-1]
            # print('viaf found: ' + str(nkcr_aut))
            return self.get_qid_by_viaf_id(viaf_id)
        except (KeyError, TypeError, AttributeError):
            return None

    def run(self, week_num_force = None, year_num_force = None, quiet = False, from_exist_file = None):

        if (from_exist_file is not None):
            week_num_force_to_file_name = str(week_num_force).zfill(2)
            file = "/home/frettie/" + str(year_num_force) + '-wnew_m_' + week_num_force_to_file_name + '.xml'
            if (os.getcwd() == '/Users/jirisedlacek/htdocs/vkol'):
                file = "/Users/jirisedlacek/htdocs/vkol/" + str(year_num_force) + '-wnew_m_' + week_num_force_to_file_name + '.xml'
        else:
            file = nkcrlib.download_actual_file_from_nkcr(week_num_force)
        # file = "2022-wnew_m_17.xml"
        if (file is not False):

            self.load_to_table(file_name=file)
            wt = wikitable()
            week_num = nkcrlib.get_week_num_to_download(week_num_force)
            if year_num_force is None:
                spl = file.split('-')
                self.year = spl[0]
            else:
                self.year = str(year_num_force)
            wt.set_caption(str(week_num) + '. týden')
            wt.add_header_column('NKČR')
            wt.add_header_column('Jméno')
            # wt.add_header_column('Křestní jméno')
            # wt.add_header_column('Příjmení')
            wt.add_header_column('Narození')
            wt.add_header_column('Úmrtí')
            wt.add_header_column('Popis')
            # wt.add_header_column('Narození z popisu')
            # wt.add_header_column('Úmrtí z popisu')
            # wt.add_header_column('ORCID')
            # wt.add_header_column('WD z NKČR')
            # wt.add_header_column('jazyk wiki z NKCR')
            # wt.add_header_column('článek wiki z NKCR')
            # wt.add_header_column('wikiprojekt z NKCR')
            # wt.add_header_column('Wikilink z NKCR')
            wt.add_header_column('QID z VIAF')
            wt.add_header_column('Akce')

            for l in self.table:
                # print(l.items())
                pattern = re.compile(r'aun|kon')
                if not pattern.findall(str(l['nkcr_aut'])):
                    # if not self.already_filled_in_wikidata(l['nkcr_aut']):
                    wt.add_line(l.values())
                    # else:
                    #     print('filled_already: ' + str(l['name']))
                else:
                    pass
                    # print('aun or kon record deleted: ' + str(l['nkcr_aut']))

            printed_table = wt.print_table()
            self.save_page(week_num, printed_table, quiet)

    def __init__(self):
        pass
        # print('run create table!')

# cr = create_table()
# cr.run(WEEK_NUM_CONST)

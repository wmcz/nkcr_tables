import json
import os
import re
import time
from collections import defaultdict

import requests

from autrecord import AutRecord
import nkcrlib
from wikitable import WikiTable
from nkcr_record import nkcr_record

import pywikibot

WEEK_NUM_CONST = None

OLDER_UPDATER_PAGE_COUNT = 10

class create_table:

    def __init__(self):
        self.table: list = []
        self.quick_lines: list = []
        self.year: str = ''
        self.update_main_page: bool = True
        self.debug: bool = False

    def table_line(self, record, count, mydata):
        assert isinstance(record, AutRecord)
        aut = record.aut()
        record_in_nkcr = nkcr_record(record)
        if (count % 10 == 0):
            print('nkcr record counter: ' + str(count))

        if self.already_filled_in_wikidata(record_in_nkcr.aut):
            return False

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

        birth_to_table = record_in_nkcr.birth_to_quickstatements if record_in_nkcr.birth_to_quickstatements is not None else ""
        death_to_table = record_in_nkcr.death_to_quickstatements if record_in_nkcr.death_to_quickstatements is not None else ""

        table_columns = {
            'nkcr_aut': record_in_nkcr.aut,
            'name': str(record_in_nkcr.name) + nkcrlib.create_nkcr_link(record_in_nkcr.aut),
            'birth_qs': birth_to_table,
            'death_qs': death_to_table,
            'popis': record_in_nkcr.description,
            'qid_from_viaf': wd_link,
            'akce': nkcrlib.create_search_link(record_in_nkcr.name) + "&nbsp;/&nbsp;" + nkcrlib.create_quickstatements_link(
                record_in_nkcr)
        }

        self.table.append(table_columns)
        if record_in_nkcr.human:
            self.quick_lines.append(nkcrlib.create_quickstatements_link(record_in_nkcr, None, True))
        return False

    def load_to_table(self, file_name):
        nkcrlib.map_xml(self.table_line, file_name)

    def _resolve_file_path(self, week_num_force, year_num_force, from_exist_file):
        """
        Determines the XML file path based on parameters.

        Returns:
            File path string, or False if download failed.
        """
        if from_exist_file is not None:
            week_num_force_to_file_name = str(week_num_force).zfill(2)
            file = "/home/frettie/" + str(year_num_force) + '-wnew_m_' + week_num_force_to_file_name + '.xml'
            if (os.getcwd() == '/Users/jirisedlacek/htdocs/vkol'):
                file = "/Users/jirisedlacek/htdocs/vkol/" + str(year_num_force) + '-wnew_m_' + week_num_force_to_file_name + '.xml'
            return file
        else:
            return nkcrlib.download_actual_file_from_nkcr(week_num_force)

    def _build_wiki_table(self, week_num):
        """
        Creates a WikiTable from self.table data, filters out 'aun'/'kon' records,
        and returns the rendered wikitext.

        Args:
            week_num: The week number for the table caption.

        Returns:
            Rendered wiki table string.
        """
        wt = WikiTable()
        wt.set_caption(str(week_num) + '. týden')
        wt.set_week_num(int(week_num))
        wt.set_year(int(self.year))
        wt.add_header_column('NKČR')
        wt.add_header_column('Jméno')
        wt.add_header_column('Narození')
        wt.add_header_column('Úmrtí')
        wt.add_header_column('Popis')
        wt.add_header_column('QID z VIAF')
        wt.add_header_column('Akce')

        pattern = re.compile(r'aun|kon')
        for l in self.table:
            if not pattern.findall(str(l['nkcr_aut'])):
                wt.add_line(l.values())

        for lin in self.quick_lines:
            print(lin)

        return wt.render()

    def _build_main_page_text(self, week_num, exist_weeks):
        """
        Generates the main page wikitext with links to all existing week pages.

        Args:
            week_num: The current week number.
            exist_weeks: List of dicts with 'year' and 'week' keys.

        Returns:
            Main page wikitext string.
        """
        weeks_by_year = defaultdict(list)
        for week in exist_weeks:
            weeks_by_year[week['year']].append(week)

        older_weeks_list = ''
        for year, weeks in sorted(weeks_by_year.items(), reverse=True):
            older_weeks_list += f"\n'''{year}'''\n"
            older_weeks_list += "{{Div col|colwidth=10em}}\n"
            for exist_week in sorted(weeks, key=lambda x: int(x['week'])):
                older_weeks_list += f"* [[/{year}/{exist_week['week']}|{exist_week['week']}. týden]]\n"
            older_weeks_list += "{{Div col end}}\n"

        actual_link = "{{/" + str(self.year) + '/' + str(week_num) + "}}"
        text_main_page = """Nové záznamy v databázi autorit NKČR

== Nejnovější týden (""" + str(week_num) + """) ==
""" + actual_link + """

== Starší ==
""" + older_weeks_list

        return text_main_page

    def save_page(self, week_num, table, quiet = False):
        site = pywikibot.Site('wikidata', 'wikidata')

        try:
            page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + self.year + '/' + str(week_num))
            page.text = table
            page.save(quiet=quiet)
            if self.update_main_page:
                exist_weeks = self.get_exist_pages(site)
                text_main_page = self._build_main_page_text(week_num, exist_weeks)

                page = pywikibot.Page(pywikibot.Site('wikidata', fam='wikidata'), 'Wikidata:WikiProject Czech Republic/New authorities')
                page.text = text_main_page
                page.save(quiet=quiet)
        except pywikibot.exceptions.NoPageError:
            print('No page:' + 'Wikidata:WikiProject Czech Republic/New authorities')

    def get_exist_pages(self, site):

        exist_weeks = []

        years = ['2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030']

        weeks = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                 '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                 '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                 '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
                 '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
                 '50', '51', '52'
                 ]

        for year in years:
            for week in weeks:
                try:
                    page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + str(year) + '/' + str(week))
                    page.get()
                    wk = {'week' : week, 'year' : year}
                    exist_weeks.append(wk)
                except pywikibot.exceptions.NoPageError:
                    pass
        return exist_weeks

    def prepare_pages_for_older_updater(self, exist_pages, actual_year, actual_week_num):
        prepared = []
        exist_pages.reverse()
        for wk in exist_pages:
            if (int(wk['year']) == actual_year and actual_week_num == int(wk['week'])):
                continue
            if (int(wk['year']) == actual_year):
                if (len(prepared) <= OLDER_UPDATER_PAGE_COUNT):
                    prepared.append(wk)

        if (len(prepared) < OLDER_UPDATER_PAGE_COUNT):
            for wk in exist_pages:
                if (len(prepared) < OLDER_UPDATER_PAGE_COUNT):
                    if (int(wk['year']) == actual_year - 1):
                        prepared.append(wk)
        return prepared

    def already_filled_in_wikidata(self, nkcr_aut=''):
        PROPERTY = 'P691'
        hub_link = "https://hub.toolforge.org/" + PROPERTY + ":" + str(nkcr_aut) + "?format=json"
        for i in range(5):
            try:
                response = requests.get(hub_link)
                if response.status_code == 200:
                    json_record = response.text
                    data_record = json.loads(json_record)
                    wd_record = data_record['origin']['qid']
                    return True

                if response.status_code != 404:
                    return False  # fail fast on other errors

                # It is a 404. Let's check if we should retry.
                if i < 4:
                     time.sleep(2)

            except (KeyError, TypeError, requests.exceptions.RequestException, json.decoder.JSONDecodeError):
                if i < 4:
                    time.sleep(2)
                else:
                    return False
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
        try:
            query = project + 'wiki:' + article + '?site=wikidata'
            hub_link = "https://hub.toolforge.org/" + query + "&format=json"
            response = requests.get(hub_link)
            if response.status_code == 200:
                json_record = response.text
                data_record = json.loads(json_record)
                wd_record = data_record['destination']['preferedSitelink']['title']
                return wd_record
            else:
                return None
        except (KeyError, TypeError, json.decoder.JSONDecodeError, requests.exceptions.ConnectionError):
            return None


    def find_on_viaf(self, nkcr_aut=''):
        try:

            url_source_id_viaf = 'http://www.viaf.org/viaf/sourceID/NKC|' + str(nkcr_aut)
            response = requests.get(url_source_id_viaf, allow_redirects=False)
            viaf_url = response.next.url
            splitted = viaf_url.split('/')
            viaf_id = splitted[-1]
            return self.get_qid_by_viaf_id(viaf_id)
        except (KeyError, TypeError, AttributeError):
            return None

    def run(self, week_num_force = None, year_num_force = None, quiet = False, from_exist_file = None):
        file = self._resolve_file_path(week_num_force, year_num_force, from_exist_file)

        if file is not False:
            self.load_to_table(file_name=file)

            week_num = nkcrlib.get_week_num_to_download(week_num_force)
            if year_num_force is None:
                spl = file.split('-')
                self.year = spl[0]
            else:
                self.year = str(year_num_force)

            printed_table = self._build_wiki_table(week_num)
            self.save_page(week_num, printed_table, quiet)

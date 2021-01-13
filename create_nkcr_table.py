import json
# import sys
# from typing import List, Any

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

table = []


def table_line(record, count, mydata):
    assert isinstance(record, AutRecord)
    record_in_nkcr = nkcr_record(record)
    # print('table line ' + str(record_in_nkcr.aut))
    if (count % 30 == 0):
        print(count)

    qid_from_viaf = find_on_viaf(str(record_in_nkcr.aut))

    if (qid_from_viaf is not None):
        wd_link = nkcrlib.create_quickstatements_link(record_in_nkcr, qid_from_viaf)
    else:
        wd_link = ""

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

    table.append(table_columns)

    return False


def load_to_table(file_name):
    nkcrlib.map_xml(table_line, file_name)


def save_page(week_num, table):
    site = pywikibot.getSite('wikidata', 'wikidata')

    header_text = "'''Nové záznamy v databázi autorit NKČR za " + str(week_num) + ". týden.'''"

    try:
        page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + str(week_num))
        page.text = printed_table
        page.save()

        weeks = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                 '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                 '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
                 '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
                 '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
                 '50', '51'
                 ]
        weeks.reverse()

        exist_weeks = []
        for week in weeks:
            # print(week)
            try:
                page = pywikibot.Page(site, 'Wikidata:WikiProject Czech Republic/New authorities/' + str(week))
                page.get()
                exist_weeks.append(week)
            except pywikibot.exceptions.NoPage:
                # print('No page: ' + 'Wikipedista:Frettie/nkcr_table/' + str(week))
                pass

        older_weeks_list = ''
        for exist_week in exist_weeks:
            older_weeks_list = older_weeks_list + '\n'
            older_weeks_list = older_weeks_list + '* ' + '[[/' + str(exist_week) + '|' + str(exist_week) + ']]'

        # print(older_weeks_list)
        # print(exist_weeks)

        actual_link = "{{/" + str(week_num) + "}}"
        text_main_page = """Nové záznamy v databázi autorit NKČR
        
== Nejnovější týden (""" + str(week_num) + """) ==
""" + actual_link + """
        
== Starší ==
""" + older_weeks_list + """
        
        
"""

        page = pywikibot.Page(pywikibot.Site('wikidata', fam='wikidata'), 'Wikidata:WikiProject Czech Republic/New authorities')
        page.text = text_main_page
        page.save()
    except pywikibot.exceptions.NoPage:
        print('No page:' + 'Wikidata:WikiProject Czech Republic/New authorities')
        pass


def already_filled_in_wikidata(nkcr_aut=''):
    PROPERTY = 'P691'
    try:
        hub_link = "https://hub.toolforge.org/" + PROPERTY + ":" + str(nkcr_aut) + "?format=json"
        response = requests.get(hub_link)
        json_record = response.text
        data_record = json.loads(json_record)
        wd_record = data_record['origin']['qid']
        return True
    except (KeyError, TypeError):
        return False


def get_qid_by_viaf_id(viaf_id=''):
    property = 'viaf'

    try:
        hub_link = "https://hub.toolforge.org/" + property + ":" + str(viaf_id) + "?site=wikidata&format=json"
        response = requests.get(hub_link)
        json_record = response.text
        data_record = json.loads(json_record)
        wd_record = data_record['origin']['qid']
        print('qid by viaf found ' + str(viaf_id))
        return wd_record
    except (KeyError, TypeError):
        return None


def find_on_viaf(nkcr_aut=''):
    try:

        url_source_id_viaf = 'http://www.viaf.org/viaf/sourceID/NKC|' + str(nkcr_aut)
        response = requests.get(url_source_id_viaf, allow_redirects=False)
        viaf_url = response.next.url
        splitted = viaf_url.split('/')
        viaf_id = splitted[-1]
        print('viaf found ' + str(nkcr_aut))
        return get_qid_by_viaf_id(viaf_id)
    except (KeyError, TypeError, AttributeError):
        return None


WEEK_NUM_CONST = None

file = nkcrlib.download_actual_file_from_nkcr(WEEK_NUM_CONST)
# file = "wnew_m_47.xml"
if (file is not False):
    load_to_table(file_name=file)
    wt = wikitable()
    week_num = nkcrlib.get_week_num_to_download(WEEK_NUM_CONST)
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

    for l in table:
        # print(l.items())
        pattern = re.compile(r'aun|kon')
        if not pattern.findall(str(l['nkcr_aut'])):
            if not already_filled_in_wikidata(l['nkcr_aut']):
                wt.add_line(l.values())
            else:
                print('filled_already: ' + str(l['name']))
        else:
            print('aun or kon record deleted')

    printed_table = wt.print_table()
    save_page(week_num, printed_table)

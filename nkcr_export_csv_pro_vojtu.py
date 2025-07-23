from typing import List, Any

from autrecord import AutRecord
import datetime
import re
import nkcrlib
from wikitable import WikiTable

table = []
write_from = 'ge1035006'
count = 0
def table_line(record, count, mydata):
    assert isinstance(record, AutRecord)
    aut = record.aut()
    if count % 10000 == 0:
        print(count)
    birth_from_note = nkcrlib.resolve_birth_from_note(record)
    death_from_note = nkcrlib.resolve_death_from_note(record)

    birth_wd = ''
    death_wd = ''
    birth_note_precision = '0'
    death_note_precision = '0'
    type = '1'
    new = '1'
    updatedraw = datetime.datetime.now()
    updated = str(updatedraw.year) + '-' + str(updatedraw.month) + '-' + str(
        updatedraw.day) + ' ' + str(updatedraw.hour) + ':' + str(updatedraw.minute) + ':' + str(
        updatedraw.second)
    nkcr_aut = str(record.aut())
    name = str(record.name())
    first_name = str(record.first_name())
    wikidata_field = str(record.wikidata024('wikidata'))
    orcid_field = str(record.wikidata024('orcid'))
    isni_field = str(record.wikidata024('isni'))
    wikipedia_field = record.wikipedia856()
    wikidata_source_field = record.source670('wikidata')
    wikipedia_source_field = record.source670('wikipedia')
    wikidata_from_nkcr = ''
    wikipedia_from_nkcr = ''
    last_name = str(record.last_name())
    narozen = str(record.birth())
    zemrel = str(record.death())
    birth_death = str(record.birth_death())
    popis = str(record.note())
    status = str(record.status())
    okres = str(record.okres())
    mesto = str(record.mesto())

    if (orcid_field == 'None'):
        orcid_field = ''

    if (isni_field == 'None'):
        isni_field = ''

    if (first_name == 'None'):
        first_name = ''

    if (last_name == 'None'):
        last_name = ''

    # if (wikidata_source_field != None and wikipedia_source_field != None):
    #     print(wikidata_source_field)
    #     print(wikipedia_source_field)

    if (wikidata_source_field != None and wikidata_field == 'None'):
        wikidata_from_nkcr = wikidata_source_field['article']
    elif (wikidata_field != 'None'):
        wikidata_from_nkcr = wikidata_field
    else:
        wikidata_from_nkcr = ''
    if (wikipedia_source_field != None and wikipedia_field == None):
        wikiproject_from_nkcr = wikipedia_source_field['project']
        wikilang_from_nkcr = wikipedia_source_field['lang']
        wikiarticle_from_nkcr = wikipedia_source_field['article']
        wikilink_from_nkcr = wikipedia_source_field['link']
    elif (wikipedia_field != None):
        wikiproject_from_nkcr = wikipedia_field['project']
        wikilang_from_nkcr = wikipedia_field['lang']
        wikiarticle_from_nkcr = wikipedia_field['article']
        wikilink_from_nkcr = wikipedia_field['link']
    else:
        wikiproject_from_nkcr = ''
        wikilang_from_nkcr = ''
        wikiarticle_from_nkcr = ''
        wikilink_from_nkcr = ''

    if (wikipedia_field != None):
        wikipedia_856_link = wikipedia_field['link']
    else:
        wikipedia_856_link = ''

    if (wikipedia_source_field != None and wikipedia_field == None):
        wikipedia_670_link = wikipedia_source_field['link']
    else:
        wikipedia_670_link = ''

    if (status == 'správní celek'):
        name = mesto

        regex = r"(.*) : okres"
        matches = re.search(regex, okres, re.IGNORECASE)
        try:
            groups = matches.groups()
            okres = groups[0]
        except AttributeError as e:
            okres = ""

    else:
        name = name

    # NKČR ID
    # Jméno
    # Příjmení (Nebo rovnou Jméno+Příjmení, to je jedno)
    # WD ID from 024
    # ORCID from 024
    # ISNI from 024 (pokud se užívá)
    # WIKI LINK from 670
    # WIKI LINK from 856


    # table_columns = {
    #     'nkcr_aut' : nkcr_aut,
    #     'name': name,
    #     'first_name' : first_name,
    #     'last_name' : last_name,
    #     # 'narozen' : narozen,
    #     # 'zemrel' : zemrel,
    #     # 'okres' : okres,
    #     # 'popis': popis,
    #     # 'birth_from_note' : birth_from_note,
    #     # 'death_from_note' : death_from_note,
    #     # 'birth_note_precision' : birth_note_precision,
    #     # 'death_note_precision' : death_note_precision,
    #     # 'birth_wd' : birth_wd,
    #     # 'death_wd' : death_wd,
    #     # 'type' : type,
    #     # 'new' : new,
    #     # 'updated' : updated,
    #     'wikidata_from_nkcr': wikidata_from_nkcr,
    #     'isni' : isni_field,
    #     'orcid': orcid_field,
    #     'wikipedia_670' : wikipedia_670_link,
    #     'wikipedia_856' : wikipedia_856_link,
    #     # 'wikilang_from_nkcr' : wikilang_from_nkcr,
    #     # 'wikiarticle_from_nkcr' : wikiarticle_from_nkcr,
    #     # 'wikiproject_from_nkcr' : wikiproject_from_nkcr,
    #     # 'wikilink_from_nkcr' : wikilink_from_nkcr,
    # }

    if (narozen == 'None'):
        narozen = ''

    if (zemrel == 'None'):
        zemrel = ''

    if (birth_death == 'None'):
        birth_death = ''

    if (birth_from_note == 'None'):
        birth_from_note = ''

    if (death_from_note == 'None'):
        death_from_note = ''

    table_columns = {
        'nkcr_aut': nkcr_aut,
        'name': name,
        'first_name': first_name,
        'last_name': last_name,
        # 'okres' : okres,
        # 'popis': popis,
        # 'narozen_046': narozen,
        # 'zemrel_046': zemrel,
        # '100d': birth_death,
        # 'birth_from_note' : birth_from_note,
        # 'death_from_note' : death_from_note,
        # 'birth_note_precision' : birth_note_precision,
        # 'death_note_precision' : death_note_precision,
        # 'birth_wd' : birth_wd,
        # 'death_wd' : death_wd,
        # 'type' : type,
        # 'new' : new,
        # 'updated' : updated,
        'wikidata_from_nkcr': wikidata_from_nkcr,
        # 'isni': isni_field,
        # 'orcid': orcid_field,
        # 'wikipedia_670': wikipedia_670_link,
        # 'wikipedia_856': wikipedia_856_link,
        # 'wikilang_from_nkcr' : wikilang_from_nkcr,
        # 'wikiarticle_from_nkcr' : wikiarticle_from_nkcr,
        # 'wikiproject_from_nkcr' : wikiproject_from_nkcr,
        # 'wikilink_from_nkcr' : wikilink_from_nkcr,
    }
    # if aut == 'ge1035006':
    #     nkcrlib.write_allowed = True

    # table.append(table_columns.values())
    # if (nkcrlib.write_allowed):
    # if (True):
    if (len(wikidata_from_nkcr)):

        arr = []
        for i in table_columns.values():
            arr.append(i)
        writer.writerow(arr)

    return False


def loadToTable(file_name):
    nkcrlib.map_xml(table_line, file_name)


# file = nkcrlib.download_actual_file_from_nkcr()
file = 'aut.xml'
# file = 'wnew_m_33.xml'
if (file is not False):
    # f = open('export_csv_all_orcid.csv', 'w', newline='')
    # f = open('export_new_desc.csv', 'w', newline='')
    f = open('export_new_wd.csv', 'w', newline='')
    import csv

    # write_allowed = False
    writer = csv.writer(f, delimiter=";", quotechar='"', quoting=csv.QUOTE_ALL)
    # writer.writerow(['nkcr_id'] + ['name'] + ['first_name'] + ['last_name'] +
    #                 ['desc'] + ['birth_nkcr_046'] + ['death_nkcr_046'] + ['birth_death_100d'] + ['birth_from_desc'] +
    #                 ['death_from_desc'])

    writer.writerow(['nkcr_id'] + ['name'] + ['first_name'] + ['last_name'] +
                    ['wd_024'])

    #
    loadToTable(file_name=file)
    print(table)
    import csv


    # NKČR ID
    # Jméno
    # Příjmení (Nebo rovnou Jméno+Příjmení, to je jedno)
    # WD ID from 024
    # ORCID from 024
    # ISNI from 024 (pokud se užívá)
    # WIKI LINK from 670
    # WIKI LINK from 856



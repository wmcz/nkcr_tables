from pymarc import map_xml

# from pymarc import Record
# from pymarc import Field, unicodedata
# import sys
# from pymarc.marcxml import XmlHandler
# from pymarc.marcxml import parse_xml
# from autxmlhandler import AutXmlHandler
from autrecord import AutRecord
import re
import datetime
import MySQLdb
import nkcrlib

def insert_into_nkcr_db(record, count, mydata):
    assert isinstance(record, AutRecord)
    # print(data)
    aut = record.aut()
    if aut not in data:
        db = MySQLdb.connect(host="localhost",
                             user="root",
                             passwd="root",
                             db="wikidata_lidi")
        cursor = db.cursor()

        query = '''
                INSERT INTO
                nkcr2_new(nkcr_aut,name,first_name,surname,birth,death,okres,description,exist_quid,birth_from_note,death_from_note,birth_note_precision,death_note_precision,birth_wd,death_wd,type,new,updated,orcid,wd_from_nkcr,wiki_lang,wiki_article,wiki_project,wiki_link) 
                VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
        exist_quid = ''
        try:
            birth_from_note = str(record.birth_date().year) + '-' + str(record.birth_date().month) + '-' + str(
                record.birth_date().day) + ' ' + str(record.birth_date().hour) + ':' + str(
                record.birth_date().minute) + ':' + str(record.birth_date().second)
        except AttributeError as e:
            birth_from_note = str(None)
        try:
            death_from_note = str(record.death_date().year) + '-' + str(record.death_date().month) + '-' + str(
                record.death_date().day) + ' ' + str(record.death_date().hour) + ':' + str(
                record.death_date().minute) + ':' + str(record.death_date().second)
        except AttributeError as e:
            death_from_note = str(None)
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
        wikipedia_field = record.wikipedia856()
        wikidata_source_field = record.source670('wikidata')
        wikipedia_source_field = record.source670('wikipedia')
        wikidata_from_nkcr = ''
        wikipedia_from_nkcr = ''
        last_name = str(record.last_name())
        narozen = str(record.birth())
        zemrel = str(record.death())
        popis = str(record.note())
        status = str(record.status())
        okres = str(record.okres())
        mesto = str(record.mesto())

        if (orcid_field == 'None'):
            orcid_field = ''

        if (first_name == 'None'):
            first_name = ''

        if (last_name == 'None'):
            last_name = ''

        if (wikidata_source_field != None and wikipedia_source_field != None):
            print(wikidata_source_field)
            print(wikipedia_source_field)

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

        mydata.append(
            [nkcr_aut, name, first_name, last_name, narozen, zemrel, okres, popis, exist_quid, birth_from_note,
             death_from_note, birth_note_precision, death_note_precision, birth_wd, death_wd, type,
             new, updated, orcid_field, wikidata_from_nkcr, wikilang_from_nkcr, wikiarticle_from_nkcr, wikiproject_from_nkcr, wikilink_from_nkcr])
        if (count % 10 == 0):
            cursor.executemany(query, mydata)
            db.commit()
            return True
        # cursor.executemany(query, mydata)
        # db.commit()
        # cursor.close()
        # print(r.name())
        # print(aut)
        return False

data = nkcrlib.get_nkcr_aut_in_db(new_only=True, column_to_return=['nkcr_aut'], withoutEmptyNames=False, typeOfReturn='set')

def get_my_data():
    return []

# mydata = get_my_data()
data = get_my_data()
count = 0


# map_xml(insert_into_nkcr_db, 'aut.xml')
# map_xml(insert_into_nkcr_db, 'vyreznew.xml')

def reconcileByReconciler():
    from reconciler import reconcile
    import pandas as pd

    data = nkcrlib.get_nkcr_aut_in_db(new_only=True, column_to_return=['first_name', 'surname'], withoutEmptyNames=True, typeOfReturn='list', limit='20', index_column='nkcr_aut')


    # data_frame = pd.DataFrame()


    # A DataFrame with a column you want to reconcile.
    test_df = pd.DataFrame(
        {
            "people_name": data['data'],
            "nkcr_aut": data['index'],
        }
    )
    # print(test_df)
    # test_df.set_index('nkcr_aut', drop=True, inplace=True)
    print(test_df)
    # Reconcile against type city (Q515), getting the best match for each item.
    reconciled = reconcile(test_df, type_id="Q5", top_res='all')
    assert isinstance(reconciled, pd.DataFrame)
    # reconciled.insert(5, 'sloup', data['index'])
    print(reconciled.to_string())

# reconcileByReconciler()


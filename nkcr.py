#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv
import json
import re
import sys
from urllib.parse import unquote

import lxml.etree
import requests
import unicodecsv
from pymarc import marcxml

import pywikibot
from logger import Logger
from pywikibot.data import sparql


class excel_semicolon(unicodecsv.Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = unicodecsv.QUOTE_MINIMAL


def cleanup(url):
    try:
        return unquote(url, errors='strict')
    except UnicodeDecodeError:
        return unquote(url, encoding='latin-1')

def get_wd():
    count = 0
    with open('clanky.csv', 'rt') as f:

        reader = csv.DictReader(f, delimiter=';')

        langs = []
        for line in reader:
            count = count + 1
            if line['lang'] not in langs:
                langs.append(line['lang'])
    print('celkem: ' + str(count))
    sites = {}
    for lang in langs:
        sites[lang] = pywikibot.Site(lang, 'wikipedia')

    position = 0
    with open('clafnky.csv', 'rt') as f:
        wdup = open('wd_k_uprave.csv', 'a')
        wdup.close()
        reader = csv.DictReader(f, delimiter=';')
        langs = []
        for line in reader:
            position = position + 1
            if (position < 14800):
                continue
            if (position % 100 == 0):
                print(str(position) + ' z ' + str(count))
            page = pywikibot.Page(sites[line['lang']],line['article'])
            if page.isRedirectPage():
                page = page.getRedirectTarget()
            try:
                item = page.data_item()

                if not u'P691' in item.claims:
                    wdup = open('wd_k_uprave.csv', 'a')
                    wdup.write(line['nkcr'])
                    wdup.write(';')
                    wdup.write(line['lang'])
                    wdup.write(';')
                    wdup.write(line['article'])
                    wdup.write(';')
                    wdup.write(item.title())
                    wdup.write('\n')
                    wdup.close()
            except pywikibot.exceptions.NoPage as e:
                print('not_exist_wd_page: ' + line['lang'] + ':' + line['article'])


# get_wd()

def create_csv():
    # tree = lxml.etree.parse('vyrez_xml.xml')
    tree = lxml.etree.parse('aut_exp.xml')
    root = tree.getroot()
    # f = open('clanky_test.csv', 'w')
    f = open('clanky.csv', 'w')

    for record in tree.findall('//*[@code="u"]'):
        # print()
        regex = u"wikipedia"
        match = re.search(regex, record.text, re.IGNORECASE)
        # match = re.search('[Nn]áměstí', street_name)
        if match:
            regex = u"http:\/\/([a-z]+)\.wikipedia\.org\/wiki\/(.*)"
            # print(html.unescape('&pound;682m'))
            test_str = record.text

            # Out[10]: 'Gotterdammerung'
            matches = re.search(regex, test_str, re.MULTILINE)
            if (matches):
                groups = matches.groups()
                # print(groups[1])
                # vys = re.search(reg,groups[1])
                # if (vys):
                #     print(vys.groups())
                f.write(record.getparent().getparent().find('*[@tag="001"]').text)
                f.write(';')
                f.write(groups[0])
                f.write(';')
                f.write(cleanup(groups[1]))
                f.write(';')
                f.write(record.text)
                f.write('\n')

        # print(record.text)

    f.close()
    # for neco in root:
    #     print(neco)
    # sys.exit()
    # for record in records:
    #     with open('response.xml', 'w') as fp:
    #         fp.write(record.raw)
    #     # print(record.header.identifier)
    #     # assert isinstance(xml, etree.Element)
    #     # rec2 = sickle.GetRecord(identifier=record.header.identifier, metadataPrefix='marc21')
    #     # print("fds")
    #     f = open('response.xml')
    #     marc = marcxml.parse_xml_to_array('response.xml')
    #
    #     zaznam = marc[0]
    #     assert isinstance(zaznam, marcxml.Record)
    #     print(zaznam.title())
    #     print(zaznam.isbn())
    #     print(zaznam.uniformtitle())
    #     print(zaznam.series())
    #     print(zaznam.author())
    #     print(zaznam.subjects())
    #     print(zaznam.addedentries())
    #     print(zaznam.location())
    #     print(zaznam.notes())
    #     print(zaznam.physicaldescription())
    #     print(zaznam.publisher())
    #     print(zaznam.pubyear())
    #     dict_zaznam = zaznam.as_dict()
    #     print(dict_zaznam)
    #
    #
    #


        # data = dict(record)


    print('fds')

def checkPersonWD():
    query = '''select distinct ?item ?itemLabel ?nkcr (year(xsd:dateTime(?naro)) as ?birth) (year(xsd:dateTime(?umrt)) as ?death) where {

?item wdt:P31 wd:Q5.
  ?item wdt:P106 wd:Q36180.
  ?item wdt:P27 wd:Q213
  MINUS {?item wdt:P691 ?nkcr .}
    OPTIONAL {?item wdt:P569 ?naro}
    OPTIONAL {?item wdt:P570 ?umrt}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "cs,en". }  
}

                                     '''
    import MySQLdb
    f = open('spisovatel_cs.csv', 'w')
    f.write('NKČR')
    f.write(';')
    f.write('WD')
    f.write(';')
    f.write('NKCR name')
    f.write(';')
    f.write('WD name')
    f.write(';')
    f.write('NKCR birth')
    f.write(';')
    f.write('WD birth')
    f.write(';')
    f.write('NKCR death')
    f.write(';')
    f.write('WD death')
    f.write(';')
    f.write('NKCR desc')
    f.write(';')
    f.write('status 1 pravdepodobne, 0 mene pravdepodobne')
    f.write('\n')


    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="nkcr")
    cursor = db.cursor()

    query_object = sparql.SparqlQuery()
    data = query_object.select(query, full_data=True)
    for line in data:
        where = []
        where.append('MATCH (`name`) AGAINST ("'+str(line['itemLabel'])+'")')
        if (line['birth'] is not None):
            where.append('birth = "'+str(line['birth'])+'"')

        if (line['death'] is not None):
            where.append('death = "'+str(line['death'])+'"')

        limit = " LIMIT 50"
        sql_select = "SELECT * FROM `nkcr` WHERE 1 = 1 "
        for w in where:
            sql_select = sql_select + ' AND ' + w
        sql_select = sql_select + limit
        cursor = db.cursor()
        cursor.execute(sql_select)
        record = cursor.fetchone()
        status = 1
        if (record is None):
            where = []
            where.append('MATCH (`name`) AGAINST ("' + str(line['itemLabel']) + '")')
            # if (line['birth'] is not None):
            #     where.append('birth = "' + str(line['birth']) + '"')

            # if (line['death'] is not None):
            #     where.append('death = "' + str(line['death']) + '"')

            limit = " LIMIT 50"
            sql_select = "SELECT * FROM `nkcr` WHERE 1 = 1 "
            for w in where:
                sql_select = sql_select + ' AND ' + w
            sql_select = sql_select + limit
            cursor = db.cursor()
            cursor.execute(sql_select)
            record = cursor.fetchone()
            status = 0
        print(record)
        if (record is not None):
            f.write(record[1])
            f.write(';')
            f.write(str(line['item']))
            f.write(';')
            f.write(record[2])
            f.write(';')
            f.write(str(line['itemLabel']))
            f.write(';')
            f.write(record[3])
            f.write(';')
            f.write(str(line['birth']))
            f.write(';')
            f.write(record[4])
            f.write(';')
            f.write(str(line['death']))
            f.write(';')
            f.write(record[5])
            f.write(';')
            f.write(str(status))
            f.write('\n')
        cursor.close()
    f.close()

def checkCityWD():
    query = '''SELECT DISTINCT ?item ?itemLabel ?okresLabel
WHERE
{
    ?item wdt:P31 wd:Q5153359 .
    ?item wdt:P131 ?okres .
    
  MINUS { ?item wdt:P691 [] } .
 OPTIONAL { ?sitelink schema:about ?item . ?sitelink schema:inLanguage "cs" } 
    SERVICE wikibase:label { bd:serviceParam wikibase:language "cs"}
}


                                     '''
    import MySQLdb
    f = open('cities_cs.csv', 'w')
    f.write('NKČR')
    f.write(';')
    f.write('WD')
    f.write(';')
    f.write('NKCR name')
    f.write(';')
    f.write('WD name')
    f.write(';')
    f.write('NKCR okres')
    f.write(';')
    f.write('WD okres')
    f.write(';')
    f.write('NKCR desc')
    f.write(';')
    f.write('status 1 pravdepodobne, 0 mene pravdepodobne')
    f.write('\n')


    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="nkcr")
    cursor = db.cursor()

    query_object = sparql.SparqlQuery()
    data = query_object.select(query, full_data=True)
    for line in data:
        where = []
        # where.append('MATCH (`name`) AGAINST ("'+str(line['itemLabel'])+' '+str(line['okresLabel'])+'")')
        regex = "okres (.*)"
        matches = re.search(regex, str(line['okresLabel']), re.IGNORECASE)
        try:
            groups = matches.groups()
            okres = groups[0]
        except AttributeError as e:
            okres = ""


        where.append('name = "'+str(line['itemLabel'])+'"')
        where.append('okres = "'+str(okres)+'"')
        # if (line['birth'] is not None):
        #     where.append('birth = "'+str(line['birth'])+'"')

        # if (line['death'] is not None):
        #     where.append('death = "'+str(line['death'])+'"')

        limit = " LIMIT 50"
        sql_select = "SELECT * FROM `nkcr2` WHERE 1 = 1 "
        for w in where:
            sql_select = sql_select + ' AND ' + w
        sql_select = sql_select + limit
        cursor = db.cursor()
        cursor.execute(sql_select)
        record = cursor.fetchone()
        status = 1
        if (record is None):
            status = 0
        print(record)
        if (record is not None):
            f.write(record[1])
            f.write(';')
            f.write(str(line['item']))
            f.write(';')
            f.write(record[2])
            f.write(';')
            f.write(str(line['itemLabel']))
            f.write(';')
            f.write(record[5])
            f.write(';')
            f.write(str(line['okresLabel']))
            f.write(';')
            f.write(record[6])
            f.write(';')
            f.write(str(status))
            f.write('\n')
        cursor.close()
    f.close()


def saveMixFromNKCRandWikiData():
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")

    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    sql_years = ''' 
        select distinct birth from people_new 
    '''
    cursor.execute(sql_years)
    record = cursor.fetchall()
    years = []
    for line in record:
        if (line['birth'] > 500):
            years.append(str(line['birth']))

    cursor.close()

    f = open('birth_years_wd_nkcr_mix_v2.csv', 'w+')
    f.write('WD_label')
    f.write(';')
    f.write('WD_first_name')
    f.write(';')
    f.write('WD_surname')
    f.write(';')
    f.write('WD_QID')
    f.write(';')
    f.write('WD_birth')
    f.write(';')
    f.write('WD_death')
    f.write(';')
    f.write('NKCR_AUT')
    f.write(';')
    f.write('NKCR_label')
    f.write(';')
    f.write('NKCR_first_name')
    f.write(';')
    f.write('NKCR_surname')
    f.write(';')
    f.write('NKCR_birth')
    f.write(';')
    f.write('NKCR_death')
    f.write('\n')

    for year in years:

        # year = "15"
        print(year)
        sql_select = '''
        
        SELECT p.label as wd_label, p.first_name as wd_first_name, p.surname as wd_surname, p.people_q as wd_qid, p.birth as wd_birth, p.death as wd_death, 
    q.nkcr_aut as nkcr_aut, q.name as nkcr_label, q.first_name as nkcr_first_name, q.surname as nkcr_surname, q.birth as nkcr_birth, q.death as nkcr_death
    FROM people_new as p
    left join (select * from nkcr2_new as n where n.birth = ''' + year + ''') as q on p.birth = q.birth and q.surname = p.surname and q.first_name = p.first_name
    where p.birth = ''' + year + ''' and nkcr_aut is not null and exist_quid = ''
        
        '''

        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(sql_select)
        record = cursor.fetchall()
        for line in record:
            print(line)
            if (record is not None):
                f.write(line['wd_label'])
                f.write(';')
                f.write(line['wd_first_name'])
                f.write(';')
                f.write(line['wd_surname'])
                f.write(';')
                f.write(line['wd_qid'])
                f.write(';')
                f.write(str(line['wd_birth']))
                f.write(';')
                f.write(str(line['wd_death']))
                f.write(';')
                f.write(line['nkcr_aut'])
                f.write(';')
                f.write(line['nkcr_label'])
                f.write(';')
                f.write(line['nkcr_first_name'])
                f.write(';')
                f.write(line['nkcr_surname'])
                f.write(';')
                f.write(str(line['nkcr_birth']))
                f.write(';')
                f.write(str(line['nkcr_death']))
                f.write('\n')
        cursor.close()
    f.close()


def add_to_db():
    import MySQLdb

    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="nkcr")
    cursor = db.cursor()

    query = 'INSERT INTO nkcr(nkcr_aut,name,birth,death,okres,description) VALUES( %s, %s, %s, %s, %s, %s)'
    mydata = []





    # tree = lxml.etree.parse('test.xml')
    tree = lxml.etree.parse('aut_exp.xml')
    root = tree.getroot()
    # f = open('clanky_test.csv', 'w')
    f = open('clanky.csv', 'w')

    count = 0
    for record in tree.findall('//{http://www.loc.gov/MARC21/slim}record'):
        # print()
        # count = count + 1
        nkcr_aut_field = record.find('.//*[@tag="001"]')
        name_field = record.find('.//*[@tag="100"]/*[@code="a"]')
        narozen_field = record.find('.//*[@tag="046"]/*[@code="f"]')
        zemrel_field = record.find('.//*[@tag="046"]/*[@code="g"]')
        popis_field = record.find('.//*[@tag="678"]/*[@code="a"]')

        status_field = record.find('.//*[@tag="950"]/*[@code="a"]')

        okres_field = record.find('.//*[@tag="951"]/*[@code="d"]')
        mesto_field = record.find('.//*[@tag="951"]/*[@code="e"]')

        try:
            nkcr_aut = nkcr_aut_field.text
        except AttributeError as e:
            nkcr_aut = ""

        try:
            okres = okres_field.text
        except AttributeError as e:
            okres = ""

        try:
            status = status_field.text
        except AttributeError as e:
            status = ""

        try:
            mesto = mesto_field.text
        except AttributeError as e:
            mesto = ""

        try:
            name = name_field.text
        except AttributeError as e:
            name = ""

        try:
            narozen = narozen_field.text
        except AttributeError as e:
            narozen = ""

        try:
            zemrel = zemrel_field.text
        except AttributeError as e:
            zemrel = ""

        try:
            popis = popis_field.text
        except AttributeError as e:
            popis = ""

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


        if (status == 'správní celek'):
            mydata.append([nkcr_aut, name, narozen, zemrel, okres, popis])
            count = count + 1
            if (count % 10 == 0):
                cursor.executemany(query, mydata)
                mydata = []
                db.commit()
    cursor.executemany(query, mydata)
    mydata = []
    db.commit()
    cursor.close()


    f.close()
    # for neco in root:
    #     print(neco)
    sys.exit()
    for record in records:
        with open('response.xml', 'w') as fp:
            fp.write(record.raw)
        # print(record.header.identifier)
        # assert isinstance(xml, etree.Element)
        # rec2 = sickle.GetRecord(identifier=record.header.identifier, metadataPrefix='marc21')
        # print("fds")
        f = open('response.xml')
        marc = marcxml.parse_xml_to_array('response.xml')

        zaznam = marc[0]
        assert isinstance(zaznam, marcxml.Record)
        print(zaznam.title())
        print(zaznam.isbn())
        print(zaznam.uniformtitle())
        print(zaznam.series())
        print(zaznam.author())
        print(zaznam.subjects())
        print(zaznam.addedentries())
        print(zaznam.location())
        print(zaznam.notes())
        print(zaznam.physicaldescription())
        print(zaznam.publisher())
        print(zaznam.pubyear())
        dict_zaznam = zaznam.as_dict()
        print(dict_zaznam)





        # data = dict(record)


    print('fds')


def addNewNKCRaut():
    with open('birth_years_wd_nkcr_mix_v2.csv', 'rb') as f:
        unicodecsv.register_dialect('excel_semicolon', excel_semicolon)
        reader = unicodecsv.reader(f, encoding='utf-8', dialect=excel_semicolon)
        # headers = next(reader)
        csv = list(reader)
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    logger_name = 'nkcr_aut_new'
    logger = Logger(logger_name + u'Fill', 'saved')
    iter = 0
    for line in csv:

        if iter == 0:
            iter = iter + 1
            continue
        iter = iter + 1

        qid = line[3]
        if not (logger.isCompleteFile(qid)):
            try:
                autorita = line[6]
                di = []
                data = {}
                nkcraut = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P691",
                        "datavalue": {
                            "value": autorita,
                            "type": "string",
                        }},
                    "type": "statement",
                    "rank": "normal",
                    "references": [
                        {
                            "snaks": {
                                "P248": [
                                    {
                                        "snaktype": "value",
                                        "property": "P248",
                                        "datavalue": {
                                            "value": {
                                                "entity-type": "item",
                                                "numeric-id": 13550863,
                                                "id": "Q13550863"
                                            },
                                            "type": "wikibase-entityid"
                                        },
                                        "datatype": "wikibase-item"
                                    }
                                ]
                            }
                        }
                    ]
                }
                di.append(nkcraut)

                data['claims'] = di
                item = pywikibot.ItemPage(repo, qid)
                item.editEntity(data)

            except pywikibot.OtherPageSaveError as e:
                pass

            logger.logComplete(qid)

def checkDuplicatesNKCR():
    with open('vyrez_z_birth_years_wd_nkcr_mix_v2.csv', 'rb') as f:
        unicodecsv.register_dialect('excel_semicolon', excel_semicolon)
        reader = unicodecsv.reader(f, encoding='utf-8', dialect=excel_semicolon)
        # headers = next(reader)
        csv = list(reader)
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    logger_name = 'nkcr_aut_new'
    logger = Logger(logger_name + u'Fill', 'saved')
    iter = 0
    pseudonymy = getPseudonymy()
    for line in csv:
        if iter == 0:
            iter = iter + 1
            continue
        iter = iter + 1

        qid = line[3]
        try:
            item = pywikibot.ItemPage(repo, qid)
            data = item.get()
            autority = data['claims']['P691']
            if len(autority) > 1:
                try:
                    for aut in autority:
                        assert isinstance(aut, pywikibot.Claim)
                        if len(aut.qualifiers):
                            pass
                        else:

                            try:
                                pseudonym = pseudonymy[aut.getTarget()]
                                addPseudonymToItem(item, pseudonym, repo)
                                print(pseudonym)
                                print('https://www.wikidata.org/wiki/' + qid)
                            except Exception as e:
                                pass

                            break
                except KeyError as e:
                    pass
        except pywikibot.IsRedirectPage as e:
            pass
        except KeyError as e:
            pass
        except pywikibot.exceptions.NoPage as e:
            pass


def cleanLastComma(string: str) -> str:
    if string.endswith(','):
        return string[:-1]
    return string

def getPeopleFromDbByNKCRAut(nkcr_aut:str, site:pywikibot.site.DataSite):
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")

    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    sql_years = ''' 
            select * from nkcr2_new where nkcr_aut = "''' + nkcr_aut + '''" 
        '''
    cursor.execute(sql_years)
    record = cursor.fetchone()
    if record == None:

        url = "https://tools.wmflabs.org/hub/P691:" + nkcr_aut + "?lang=cs&format=json"
        response = requests.get(url)
        jsontext = response.text
        data = json.loads(jsontext)
        try:
            qid = data['origin']['qid']
            mess = data['message']
            print(mess)
        except pywikibot.exceptions.OtherPageSaveError:
            pass
        except KeyError:
            qid = ""
            pass
        except json.decoder.JSONDecodeError:
            pass
        except BaseException:
            pass

    else:
        qid = record['exist_quid']
        if (qid == ""):
            url = "https://tools.wmflabs.org/hub/P691:" + nkcr_aut + "?lang=cs&format=json"
            response = requests.get(url)
            jsontext = response.text
            data = json.loads(jsontext)
            try:
                qid = data['origin']['qid']
                # mess = data['message']
                # print(mess)
            except pywikibot.exceptions.OtherPageSaveError:
                pass
            except KeyError:
                pass
            except json.decoder.JSONDecodeError:
                pass
            except BaseException:
                pass

    cursor.close()
    return qid

def cleanOrg():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    pseudonymy = getOrganizations()
    for aut, pseudonym in pseudonymy.items():
        if (pseudonym['name_org'] != ''):
            qid = getPeopleFromDbByNKCRAut(aut, site)
            if (qid == ''):
                if pseudonym['name'] == '':
                    pseudonym_name = pseudonym['name_org']
                else:
                    pseudonym_name = pseudonym['name']
                # print("not exist on wd: " + pseudonym_name + " - " + aut)
                continue
            item = pywikibot.ItemPage(site, qid)
            data = item.get()
            clean_this = {}
            processed_nkcr = []
            for pseud in pseudonym['pseudo']:
                if pseud['name'] == '':
                    pseudonym_name = pseud['name_oth']
                else:
                    pseudonym_name = pseud['name']
                clean_this[pseud['aut']] = pseud['aut']
            claims_to_delete = []
            try:
                autority = data['claims']['P691']
                if (len(autority)):
                    for aut in autority:
                        target = aut.getTarget()
                        if (target in clean_this):
                            claims_to_delete.append(aut)
                if (len(claims_to_delete)):
                    item.removeClaims(claims_to_delete)
                    print(claims_to_delete)
            except Exception as e:
                print(e)
                pass

def cleanLidi():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    pseudonymy = getOrganizations()
    for aut, pseudonym in pseudonymy.items():
        if (pseudonym['name'] != ''):
            qid = getPeopleFromDbByNKCRAut(aut, site)
            if (qid == ''):
                if pseudonym['name'] == '':
                    pseudonym_name = pseudonym['name_org']
                else:
                    pseudonym_name = pseudonym['name']
                # print("not exist on wd: " + pseudonym_name + " - " + aut)
                continue
            try:
                item = pywikibot.ItemPage(site, qid)
                data = item.get()
            except pywikibot.IsRedirectPage as e:
                continue
            clean_this = {}
            processed_nkcr = []
            for pseud in pseudonym['pseudo_org']:
                if pseud['name'] == '':
                    pseudonym_name = pseud['name_org']
                else:
                    pseudonym_name = pseud['name']
                clean_this[pseud['aut']] = pseud['aut']
            claims_to_delete = []
            try:
                autority = data['claims']['P691']
                if (len(autority)):
                    for aut in autority:
                        target = aut.getTarget()
                        if (target in clean_this):
                            claims_to_delete.append(aut)
                if (len(claims_to_delete)):
                    item.removeClaims(claims_to_delete)
                    print(claims_to_delete)
            except Exception as e:
                print(e)
                pass

def cleanLidi():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    pseudonymy = getOrganizations()
    for aut, pseudonym in pseudonymy.items():
        if (pseudonym['name'] != ''):
            qid = getPeopleFromDbByNKCRAut(aut, site)
            if (qid == ''):
                if pseudonym['name'] == '':
                    pseudonym_name = pseudonym['name_org']
                else:
                    pseudonym_name = pseudonym['name']
                # print("not exist on wd: " + pseudonym_name + " - " + aut)
                continue
            try:
                item = pywikibot.ItemPage(site, qid)
                data = item.get()
            except pywikibot.IsRedirectPage as e:
                continue
            clean_this = {}
            processed_nkcr = []
            for pseud in pseudonym['pseudo_org']:
                if pseud['name'] == '':
                    pseudonym_name = pseud['name_org']
                else:
                    pseudonym_name = pseud['name']
                clean_this[pseud['aut']] = pseud['aut']
            claims_to_delete = []
            try:
                autority = data['claims']['P691']
                if (len(autority)):
                    for aut in autority:
                        target = aut.getTarget()
                        if (target in clean_this):
                            claims_to_delete.append(aut)
                if (len(claims_to_delete)):
                    item.removeClaims(claims_to_delete)
                    print(claims_to_delete)
            except Exception as e:
                print(e)
                pass

def cleanPseudonymy():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    pseudonymy = getPseudonymy()
    for aut, pseudonym in pseudonymy.items():
        if (pseudonym['name'] != ''):
            qid = getPeopleFromDbByNKCRAut(aut, site)
            if (qid == ''):
                if pseudonym['name'] == '':
                    pseudonym_name = pseudonym['name_org']
                else:
                    pseudonym_name = pseudonym['name']
                # print("not exist on wd: " + pseudonym_name + " - " + aut)
                continue
            try:
                item = pywikibot.ItemPage(site, qid)
                data = item.get()
            except pywikibot.IsRedirectPage as e:
                continue
            clean_this = {}
            processed_nkcr = []
            for pseud in pseudonym['pseudo_org']:
                if pseud['name'] == '':
                    pseudonym_name = pseud['name_org']
                else:
                    pseudonym_name = pseud['name']
                clean_this[pseud['aut']] = pseud['aut']
            claims_to_delete = []
            try:
                autority = data['claims']['P691']
                if (len(autority)):
                    for aut in autority:
                        target = aut.getTarget()
                        if (target in clean_this):
                            claims_to_delete.append(aut)
                if (len(claims_to_delete)):
                    item.removeClaims(claims_to_delete)
                    print(claims_to_delete)
            except Exception as e:
                print(e)
                pass


def runPseudonymy():
    site = pywikibot.Site('wikidata', 'wikidata')
    repo = site.data_repository()
    pseudonymy = getPseudonymy()

    for aut,pseudonym in pseudonymy.items():
        try:
            qid = getPeopleFromDbByNKCRAut(aut, site)
            if (qid == ''):
                if pseudonym['name'] == '':
                    pseudonym_name = pseudonym['name_oth']
                else:
                    pseudonym_name = pseudonym['name']
                # print("not exist on wd: " + pseudonym_name + " - " + aut)
                continue
            item = pywikibot.ItemPage(site, qid)
            data = item.get()
            vys = {}
            processed_nkcr = []
            for pseud in pseudonym['pseudo']:
                if pseud['name'] == '':
                    pseudonym_name = pseud['name_oth']
                else:
                    pseudonym_name = pseud['name']
                vys[pseud['aut']] = cleanLastComma(pseudonym_name)

            if pseudonym['name'] == '':
                pseudonym_name = pseudonym['name_oth']
            else:
                pseudonym_name = pseudonym['name']

            vys[pseudonym['id']] = cleanLastComma(pseudonym_name)
            try:
                autority = data['claims']['P691']
                if (len(autority)):
                    for aut in autority:
                        target = aut.getTarget()
                        pseudonym_text = vys[target]
                        addPseudonymToQualifier(aut, pseudonym_text, repo)
                        processed_nkcr.append(target)
            except Exception as e:
                print(e)
                pass

            for key,value in vys.items():
                if (key in processed_nkcr):
                    pass
                else:
                    #add new
                    try:
                        addNewPseudonym(item, key, vys[key], repo)
                    except pywikibot.data.api.APIError as e:
                        print(e)
        except pywikibot.IsRedirectPage as e:
            pass


def addPseudonymToQualifier(nkcr_claim:pywikibot.Claim, pseudonym:str, repo:pywikibot.site.DataSite)->None:
    qualifiers = nkcr_claim.qualifiers
    add = True
    if "P1810" in qualifiers:
        if (len(qualifiers['P1810'])):
            for qualifier in qualifiers['P1810']:
                if (qualifier.getTarget() == pseudonym):
                    add = False
    if add:
        uveden_jako = pywikibot.Claim(repo, 'P1810')
        uveden_jako.setTarget(pseudonym)
        objekt_v_roli = pywikibot.Claim(repo, 'P3831')
        objekt_v_roli.setTarget(pywikibot.ItemPage(repo, 'Q61002'))
        nkcr_claim.addQualifier(uveden_jako)
        nkcr_claim.addQualifier(objekt_v_roli)
        sources = []

        source = pywikibot.Claim(repo, 'P248')
        source.setTarget(pywikibot.ItemPage(repo, 'Q13550863'))

        datumsource = pywikibot.Claim(repo, 'P813')
        datumsource.setTarget(pywikibot.WbTime(year=2019,month=11,day=24))

        sources.append(source)
        sources.append(datumsource)
        nkcr_claim.addSources(sources)
        print("add wd: " + pseudonym)




def addNewPseudonym(item:pywikibot.ItemPage, nkcr_aut:str ,pseudonym:str, repo:pywikibot.site.DataSite)->None:
    nkcr_aut_claim = pywikibot.Claim(repo, 'P691')

    uveden_jako = pywikibot.Claim(repo, 'P1810')
    uveden_jako.setTarget(pseudonym)
    objekt_v_roli = pywikibot.Claim(repo, 'P3831')
    objekt_v_roli.setTarget(pywikibot.ItemPage(repo, 'Q61002'))

    nkcr_aut_claim.setTarget(nkcr_aut)
    item.addClaim(nkcr_aut_claim)
    nkcr_aut_claim.addQualifier(uveden_jako)
    nkcr_aut_claim.addQualifier(objekt_v_roli)
    sources = []

    source = pywikibot.Claim(repo, 'P248')
    source.setTarget(pywikibot.ItemPage(repo, 'Q13550863'))

    datumsource = pywikibot.Claim(repo, 'P813')
    datumsource.setTarget(pywikibot.WbTime(year=2019, month=11, day=24))

    sources.append(source)
    sources.append(datumsource)
    nkcr_aut_claim.addSources(sources)
    print("add wd new: " + pseudonym)


def addPseudonymToItem(item:pywikibot.ItemPage, pseudonymy:dict, repo:pywikibot.site.DataSite)->None:
    try:
        vys = {}
        for pseudonym in pseudonymy['pseudo']:
            if pseudonym['name'] == '':
                pseudonym_name = pseudonym['name_oth']
            else:
                pseudonym_name = pseudonym['name']
            vys[pseudonym['aut']] = cleanLastComma(pseudonym_name)

        if pseudonymy['name'] == '':
            pseudonym_name = pseudonymy['name_oth']
        else:
            pseudonym_name = pseudonymy['name']

        vys[pseudonymy['id']] = cleanLastComma(pseudonym_name)

        data = item.get()
        autority = data['claims']['P691']
        try:
            for aut in autority:
                assert isinstance(aut, pywikibot.Claim)
                if len(aut.qualifiers):
                    pass
                else:
                    uveden_jako = pywikibot.Claim(repo, 'P1810')
                    uveden_jako.setTarget(vys[aut.getTarget()])
                    aut.addQualifier(uveden_jako)
                    print(aut.getTarget())
                    print(vys[aut.getTarget()])
        except KeyError as e:
            pass
    except pywikibot.IsRedirectPage as e:
        pass
    except KeyError as e:
        pass
    except pywikibot.exceptions.NoPage as e:
        pass


def getPseudonymy()->dict:
    name = "export-pseudo"
    json_file_path = name + ".json"

    fp = open(json_file_path, 'r')
    json_value = fp.read()
    raw_data = json.loads(json_value)

    data_to_be_processed = raw_data

    processed_data = []
    header = []
    line = {}
    for item in data_to_be_processed:
        id = item['id']
        try:
            name = item['name']
        except KeyError as e:
            name = ''

        try:
            name_oth = item['name_oth']
        except KeyError as e:
            name_oth = ''
        final = {}
        pseudo = []
        for ps in item['pseudo']:
            arr = {}
            arr['name'] = ps[0]
            arr['aut'] = ps[1]
            pseudo.append(arr)
        final['pseudo'] = pseudo
        final['name'] = name
        final['name_oth'] = name_oth
        final['id'] = id
        line[id] = final
    return line

def pseudonymyToCSV():
    pseudo = getPseudonymy()
    import csv
    longest = 0
    for k, v in pseudo.items():
        if len(v['pseudo']) > longest:
            longest = len(v['pseudo'])

    print(longest)
    with open('pseudonymy_vojta.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=";",quotechar="'",quoting=csv.QUOTE_ALL)
        writer.writerow(['name'] + ['name_other'] + ['nkcr_aut'] + ['pseudo'] * longest)
        for k, v in pseudo.items():
            arr = []
            for ps in v['pseudo']:
                text = ps['name'][:-1] + ':' + ps['aut']
                arr.append(text)
            writer.writerow([v['name'][:-1]] + [v['name_oth'][:-1]] + [v['id']] + arr)




def getOrganizations()->dict:
    name = "aut_exp_org"
    json_file_path = name + ".json"

    fp = open(json_file_path, 'r')
    json_value = fp.read()
    raw_data = json.loads(json_value)

    data_to_be_processed = raw_data

    processed_data = []
    header = []
    line = {}
    for item in data_to_be_processed:
        id = item['id']
        try:
            name = item['name']
        except KeyError as e:
            name = ''

        try:
            name_oth = item['name_org']
        except KeyError as e:
            name_oth = ''
        final = {}
        pseudo = []
        pseudo_org = []
        if ('pseudo' in item):
            for ps in item['pseudo']:
                arr = {}
                if (ps[0] == 's'):
                    if (len(ps) == 3):
                        arr['name'] = ps[1]
                        arr['aut'] = ps[2]
                    else:
                        arr['name'] = ps[1]
                        arr['aut'] = ps[3]
                else:
                    if (len(ps) == 2):
                        arr['name'] = ps[0]
                        arr['aut'] = ps[1]
                    else:
                        arr['name'] = ps[0]
                        arr['aut'] = ps[2]

                pseudo.append(arr)
        if ('pseudo_org' in item):
            for ps in item['pseudo_org']:
                arr = {}
                if (ps[0] == 'b' or ps[0] == 'a'):
                    if (len(ps) == 2):
                        arr['aut'] = ''
                        arr['name'] = ps[1]
                    else:
                        arr['name'] = ps[1]
                        arr['aut'] = ps[2]
                else:
                    arr['name'] = ps[0]
                    arr['aut'] = ps[1]
                pseudo_org.append(arr)
        final['pseudo'] = pseudo
        final['pseudo_org'] = pseudo_org
        final['name'] = name
        final['name_org'] = name_oth
        final['id'] = id

        if (final['name_org'] == '' and len(pseudo_org) > 0):
            line[id] = final
    return line

def loadViafFromFile():
    file = open("wd-nkcr-links.txt", "r")
    vysledek = {}
    for line in file:
        try:
            regex = r"http:\/\/viaf\.org\/viaf\/(\d+)\W+(\w+)\|(.+)"
            matches = re.search(regex, line)
            groups = matches.groups()
            try:
                vysledek[groups[0]][groups[1]] = groups[2]
            except Exception as e:
                vysledek[groups[0]] = {}
                vysledek[groups[0]][groups[1]] = groups[2]

        except Exception as e:
            pass
    return vysledek


def prepareNKCRVIAF():
    viafquery = """
    select ?pers ?viaf where {
        ?pers wdt:P31 wd:Q5.
        ?pers wdt:P214 ?viaf
        MINUS{?pers wdt:P691 ?nkcr}
    } 
    OFFSET %d
    LIMIT %d
    """
    file_data = loadViafFromFile()
    repo = pywikibot.Site().data_repository()
    step = 1000
    limit = 1000
    for i in range(505000, 2000000, step):
        query = viafquery % (i, limit)
        print(query)
        # print(query)
        sq = pywikibot.data.sparql.SparqlQuery()
        queryresult = sq.select(query)
        count = 0
        for res in queryresult:
            if count % 200 == 0:
                print("pocet: " + str(count))
            count = count + 1
            viaf = res['viaf']
            write_to_file = {}
            has_nkcr = False
            try:
                viaf_offline = file_data[viaf]
                if ("NKC" in viaf_offline.keys()):
                    has_nkcr = True
                    nkcr = viaf_offline['NKC']
            except Exception as e:
                url = "http://www.viaf.org/viaf/" + viaf + "/justlinks.json"
                import csv

                nkcrpage = requests.get(url)
                if not nkcrpage.status_code == 200:
                    pywikibot.output(u'Viaf %s points to broken NKC url: %s' % ('', url,))
                    # brokenlinks = brokenlinks + 1
                    # continue

                validviaffound = False

                if viaf in nkcrpage.text:
                    validviaffound = True
                    # pywikibot.output(
                    #     u'Adding NKČR for Author Names ID %s claim to %s (based on bidirectional viaf<->nkcr links)' % (
                    #     nkcr, item.title(),))
                    # summary = u'based on VIAF %s (with bidirectional viaf<->nkcr links)' % (viafid,)
                    try:
                        data = json.loads(nkcrpage.text)
                        try:
                            nkcr = data.get('NKC')
                            if (nkcr != None):
                                nkcr = nkcr[0]
                                has_nkcr = True
                        except Exception as e:
                            pass
                    except json.decoder.JSONDecodeError as d:
                        pass
            if has_nkcr:
                qid = res.get('pers').replace(u'http://www.wikidata.org/entity/', u'')
                with open('nkcr-from-viaf-december2019.csv', mode='a') as employee_file:
                    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    employee_writer.writerow([viaf, nkcr, qid])




def getNKCRFromWikidata():
    viafquery = """
    select ?pers ?nkcr where {
        
        ?pers wdt:P691 ?nkcr
    } 
    ORDER BY ?nkcr
    OFFSET %d
    LIMIT %d
    """
    # file_data = loadViafFromFile()
    repo = pywikibot.Site().data_repository()
    step = 1000
    limit = 1000
    for i in range(265000, 300000, step):
        query = viafquery % (i, limit)
        print(query)
        # print(query)
        sq = pywikibot.data.sparql.SparqlQuery()
        queryresult = sq.select(query)
        count = 0
        for res in queryresult:
            if count % 200 == 0:
                print("pocet: " + str(count))
            count = count + 1
            nkcr = res['nkcr']
            qid = res.get('pers').replace(u'http://www.wikidata.org/entity/', u'')
            with open('nkcr-from-wd-december2019-all-12_12_2019.csv', mode='a') as employee_file:
                employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                employee_writer.writerow([nkcr, qid])

def actualizationNkcrQidInDb():
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")
    query = 'UPDATE nkcr2_new SET exist_quid = %s where nkcr_aut = %s'
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    file = open("nkcr-from-wd-december2019-all-12_12_2019.csv", "r")
    vysledek = {}
    mydata = []
    count = 0
    for line in file:
        try:
            cols = line.rstrip('\n').split(',')
            # print(cols)

            mydata.append([cols[1], cols[0]])
            count = count + 1
            if (count % 10 == 0):
                cursor.executemany(query, mydata)
                mydata = []
                db.commit()
            if (count % 200 == 0):
                print(count)
        except Exception as e:
            print(e)
            pass
    return vysledek

    cursor.executemany(query, mydata)
    db.commit()
    cursor.close()

    f.close()
    # for neco in root:
    #     print(neco)
    sys.exit()

def actualizationNkcrBirthDeathinDb(type):
    import MySQLdb

    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")
    if (type == 'birth'):
        query = 'UPDATE nkcr2_new SET birth_from_note = %s, birth_note_precision = %s where nkcr_aut = %s'
        file = open("narozeni_z_nkcr.csv", "r")
    elif (type == 'death'):
        query = 'UPDATE nkcr2_new SET death_from_note = %s, death_note_precision = %s where nkcr_aut = %s'
        file = open("umrti_z_nkcr.csv", "r")
    elif (type == 'birth_vojta'):
        query = 'UPDATE nkcr2_new SET birth_from_note = %s, birth_note_precision = %s where nkcr_aut = %s'
        file = open("narozeni_roku_v_roce_zeny_pro_vojtu.csv", "r")
    else:
        sys.exit()

    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    vysledek = {}
    mydata = []
    count = 0
    for line in file:
        try:
            cols = line.rstrip('\n').lstrip('\ufeff').split(';')
            nkcr = cols[0]

            regex = r"\+(\d+)\-(\d+)\-(\d+)T(\d+):(\d+):(\d+)Z\/(\d+)"
            if (type == "birth_vojta"):
                matches = re.search(regex, cols[4])
            else:
                matches = re.search(regex, cols[1])
            groups = matches.groups()
            year = groups[0]
            month = groups[1]
            day = groups[2]
            hour = groups[3]
            minute = groups[4]
            second = groups[5]
            precision = groups[6]
            datetime = year+'-'+month+'-'+day+'-'+hour+'-'+minute+'-'+second
            mydata.append([datetime, precision, nkcr])
            count = count + 1
            if (count % 10 == 0):
                cursor.executemany(query, mydata)
                mydata = []
                db.commit()
            if (count % 200 == 0):
                print(count)
        except Exception as e:
            print(e)
            pass
    return vysledek

    # cursor.executemany(query, mydata)
    # db.commit()
    # cursor.close()

    f.close()
    # for neco in root:
    #     print(neco)
    sys.exit()

def org_names_to_db():
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")
    query = 'UPDATE nkcr2_new SET name = %s where nkcr_aut = %s'
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    name = "events"
    json_file_path = name + ".json"

    fp = open(json_file_path, 'r')
    json_value = fp.read()
    raw_data = json.loads(json_value)

    data_to_be_processed = raw_data

    processed_data = []
    header = []
    line = {}
    count = 0
    mydata = []
    for item in data_to_be_processed:
        print(item['org_nkcr'])
        print(item['org_name'])
        count = count + 1
        mydata.append([item['org_name'], item['org_nkcr']])
        count = count + 1
        if (count % 10 == 0):
            cursor.executemany(query, mydata)
            mydata = []
            db.commit()
        if (count % 200 == 0):
            print(count)

def types_to_db():
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")
    query = 'UPDATE nkcr2_new SET type = %s where nkcr_aut = %s'
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    name = "typy"
    json_file_path = name + ".json"

    fp = open(json_file_path, 'r')
    json_value = fp.read()
    raw_data = json.loads(json_value)

    data_to_be_processed = raw_data

    processed_data = []
    header = []
    line = {}
    count = 0
    mydata = []
    for item in data_to_be_processed:
        print(item['id'])
        print(item['typ'])
        count = count + 1
        typ = 0
        if (item['typ'] == 'clovek'):
            typ = 1
        elif (item['typ'] == 'org'):
            typ = 2
        elif(item['typ'] == 'akce'):
            typ = 3

        mydata.append([typ, item['id']])
        count = count + 1
        if (count % 10 == 0):
            cursor.executemany(query, mydata)
            mydata = []
            db.commit()
        if (count % 200 == 0):
            print(count)

def article_days():
    file = open("quarry.csv", "r")
    count = 0
    day_of_years = {}
    day_of_weeks = {}
    hours_in_day = {}
    mins_in_day = {}
    day_months = {}
    day_months_txt = {}
    f = open('article_year_2019.csv', 'w')

    for line in file:
        try:
            if count == 0:
                count = count + 1
                continue
            cols = line.rstrip('\n').split(',')
            # print(cols)
            import datetime
            timestamp = cols[5]
            year = timestamp[0:4]
            if int(year) == 2019:
                month = timestamp[4:6]
                day = timestamp[6:8]
                hour = timestamp[8:10]
                min = timestamp[10:12]
                sec = timestamp[12:14]
                date = datetime.date(int(year), int(month), int(day))
                date = datetime.datetime(int(year), int(month), int(day), int(hour), int(min), int(sec))
                day_of_year = date.timetuple().tm_yday
                day_of_week = date.timetuple().tm_wday
                hour_in_day = date.timetuple().tm_hour
                min_in_day = date.timetuple().tm_min
                if day_of_week in day_of_weeks.keys():
                    day_of_weeks[day_of_week] = day_of_weeks[day_of_week] + 1
                else:
                    day_of_weeks[day_of_week] = 1

                if hour_in_day in hours_in_day.keys():
                    hours_in_day[hour_in_day] = hours_in_day[hour_in_day] + 1
                else:
                    hours_in_day[hour_in_day] = 1

                if min_in_day in mins_in_day.keys():
                    mins_in_day[min_in_day] = mins_in_day[min_in_day] + 1
                else:
                    mins_in_day[min_in_day] = 1

                if day_of_year in day_of_years.keys():
                    day_of_years[day_of_year] = day_of_years[day_of_year] + 1
                else:
                    day_of_years[day_of_year] = 1
                if int(month) in day_months.keys():
                    if (int(day) in day_months[int(month)].keys()):
                        day_months[int(month)][int(day)] = day_months[int(month)][int(day)] + 1
                        day_months_txt[str(int(month))+'_'+str(int(day))] = day_months_txt[str(int(month))+'_'+str(int(day))] + 1
                    else:
                        day_months[int(month)][int(day)] = 1
                        day_months_txt[str(int(month)) + '_' + str(int(day))] = 1
                else:
                    day_months[int(month)] = {}
                count = count + 1
            # print(day_months)
        except Exception as e:
            print(e)
            pass
    for key in day_months_txt:
        f.write(key)
        f.write(';')
        f.write(str(day_months_txt[key]))
        f.write('\n')
    print(day_months_txt)
    print(count)
    print(day_of_weeks)
    print(hours_in_day)
    print(mins_in_day)



def updateQIDandBirthDateWD():
    import MySQLdb

    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")
    query = 'UPDATE nkcr2_new SET birth_wd = %s, death_wd = %s, exist_quid = %s where nkcr_aut = %s'
    file = open("wd_birth_death.csv", "r")

    cursor = db.cursor(MySQLdb.cursors.DictCursor)

    vysledek = {}
    mydata = []
    count = 0
    for line in file:
        try:
            if (count == 0):
                count = count + 1
                continue
            cols = line.rstrip('\n').lstrip('\ufeff').split(',')
            nkcr = cols[1]

            regex = r"http://www.wikidata.org/entity/(Q[0-9]+)"
            matches = re.search(regex, cols[0])
            group_qid = matches.groups()
            qid = group_qid[0]

            regex = r"(\d+)\-(\d+)\-(\d+)T(\d+):(\d+):(\d+)Z"
            birth = re.search(regex, cols[2])
            death = re.search(regex, cols[3])
            if death is None:
                death_datetime = '0000-00-00-00-00-00'
            else:
                groups_death = death.groups()
                death_year = groups_death[0]
                death_month = groups_death[1]
                death_day = groups_death[2]
                death_hour = groups_death[3]
                death_minute = groups_death[4]
                death_second = groups_death[5]
                # death_precision = groups_death[6]
                death_datetime = death_year + '-' + death_month + '-' + death_day + '-' + death_hour + '-' + death_minute + '-' + death_second

            if birth is None:
                birth_datetime = '0000-00-00-00-00-00'
            else:
                groups_birth = birth.groups()

                birth_year = groups_birth[0]
                birth_month = groups_birth[1]
                birth_day = groups_birth[2]
                birth_hour = groups_birth[3]
                birth_minute = groups_birth[4]
                birth_second = groups_birth[5]
                # birth_precision = groups_birth[6]

                birth_datetime = birth_year + '-' + birth_month + '-' + birth_day + '-' + birth_hour + '-' + birth_minute + '-' + birth_second



            mydata.append([birth_datetime, death_datetime,qid , nkcr])
            count = count + 1
            if (count % 10 == 0):
                cursor.executemany(query, mydata)
                mydata = []
                db.commit()
            if (count % 200 == 0):
                print(count)
        except Exception as e:
            print(e)
            pass
    return vysledek

    # cursor.executemany(query, mydata)
    # db.commit()
    # cursor.close()

    f.close()
    # for neco in root:
    #     print(neco)
    sys.exit()

def richDataFromMySQL():
    import MySQLdb

    csvfile = open('vojta_rich_data_nkcr.csv', 'w', newline='')
    writer = csv.writer(csvfile, delimiter=";",quotechar="'",quoting=csv.QUOTE_ALL)
    writer.writerow(['nkcr_aut'] + ['name'] + ['first_name'] +
                    ['surname'] + ['birth'] + ['death'] +
                    ['description'] + ['birth_from_note'] + ['birth_note_precision'] +
                    ['death_from_note'] + ['death_note_precision'] + ['type'])


    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")
    query = 'SELECT * FROM nkcr2_new where nkcr_aut = "%s"'
    # cursor = db.cursor(MySQLdb.cursors.DictCursor)
    file = open("Autority-bez-QID-a-s-datem-narozeni-na-den.csv", "r")
    count = 0
    for line in file:
        try:
            cols = line.rstrip('\n').lstrip('\ufeff').split(',')
            # print(cols)
            nkcr = cols[0]
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query % (nkcr))
            record = cursor.fetchone()

            if record['birth_from_note'] is not None:
                birth = record['birth_from_note'].isoformat()
            else:
                birth = ''

            if record['death_from_note'] is not None:
                death = record['death_from_note'].isoformat()
            else:
                death = ''

            writer.writerow([record['nkcr_aut']] + [record['name']] + [record['first_name']] +
                            [record['surname']] + [record['birth']] + [record['death']] +
                            [record['description']] + [birth] + [record['birth_note_precision']] +
                            [death] + [record['death_note_precision']] + [record['type']])


        except Exception as e:
            print(e)
            pass
    return None

    cursor.executemany(query, mydata)
    db.commit()
    cursor.close()

    f.close()
    # for neco in root:
    #     print(neco)
    sys.exit()




# add_to_db()
# checkCityWD()

# create_csv()
# get_wd()
#saveMixFromNKCRandWikiData()

# addNewNKCRaut()
# checkDuplicatesNKCR()
# getPseudonymy()
# runPseudonymy()
# cleanOrg()
# cleanLidi()
# cleanPseudonymy()
#runPseudonymy()
# prepareNKCRVIAF()
# loadViafFromFile()

# getNKCRFromWikidata()
# actualizationNkcrQidInDb()
# article_days()
updateQIDandBirthDateWD()
# actualizationNkcrBirthDeathinDb('birth')
# actualizationNkcrBirthDeathinDb('birth_vojta')
# org_names_to_db()
# types_to_db()

# pseudonymyToCSV()
# richDataFromMySQL()
#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

import pywikibot
import MySQLdb


class importWikibaseAutority:

    def create_item_for_page(self, data=None, summary='creating NKCR aut', repo=None, name=''):
        self.iter = self.iter + 1
        self.countInMinute = self.countInMinute + 1
        curr_datetime = datetime.now()
        actual_minute = curr_datetime.minute
        if (actual_minute != self.minute):
            pywikibot.output('Iteration: ' + str(self.iter))
            pywikibot.output('Created in last minute: ' + str(self.countInMinute))
            average = 60/self.countInMinute
            pywikibot.output('Creating time average: ' + str(average) + ' sec')
            self.minute = actual_minute
            self.countInMinute = 0

        item = pywikibot.ItemPage(repo)
        result = self.user_edit_entity(item, data, summary=summary)
        if result:
            return item
        else:
            return None

    def user_edit_entity(self, item, data=None, summary=None):
        return self._save_page(item, item.editEntity, data)

    def _save_page(self, page, func, *args):
        func(*args)
        return True

    def importAutority(self):
        self.iter = 0
        self.countInMinute = 0
        curr_datetime = datetime.now()
        self.minute = curr_datetime.minute
        db = MySQLdb.connect(host="localhost",
                             user="root",
                             passwd="root",
                             db="wikidata_lidi")

        site = pywikibot.Site('autority', 'autority')
        ver = site.version()
        botusers = site.botusers()
        repo = site.data_repository()

        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        sql_years = '''
            select * from nkcr2_new where new = 1 and nkcr_aut NOT LIKE 'aun%'
        '''
        cursor.execute(sql_years)
        record = cursor.fetchall()

        for line in record:
            data = {}

            data.setdefault('labels', {}).update({
                'en': {
                    'language': 'en',
                    'value': line['name'].strip()
                },
                'cs': {
                    'language': 'cs',
                    'value': line['name'].strip()
                },
            })

            data.setdefault('descriptions', {}).update({
                'en': {
                    'language': 'en',
                    'value': 'person in NKČR authority database (' + line['nkcr_aut'] + ')'
                },
                'cs': {
                    'language': 'cs',
                    'value': 'osoba v databázi autorit NK ČR (' + line['nkcr_aut'] + ')'
                },
            })

            di = []
            if (line['name'] != ''):
                name = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P1",
                        "datavalue": {
                            "value": line['name'].strip(),
                            "type": "string",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(name)

            if (line['birth'] > 0):
                date = pywikibot.WbTime(year=line['birth'], precision=9)
                narozeni = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P2",
                        "datavalue": {
                            "value": {'time': date.toTimestr(),
                                      'precision': 9,
                                      'after': date.after,
                                      'before': date.before,
                                      'timezone': date.timezone,
                                      'calendarmodel': date.calendarmodel
                                      },
                            "type": "time",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(narozeni)

            if (line['death'] > 0):
                date = pywikibot.WbTime(year=line['death'], precision=9)
                umrti = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P3",
                        "datavalue": {
                            "value": {'time': date.toTimestr(),
                                      'precision': 9,
                                      'after': date.after,
                                      'before': date.before,
                                      'timezone': date.timezone,
                                      'calendarmodel': date.calendarmodel
                                      },
                            "type": "time",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(umrti)

            if (line['birth_from_note'] is not None):
                precision = line['birth_note_precision']
                db_time = line['birth_from_note']
                date = pywikibot.WbTime(year=db_time.year, month=db_time.month, day=db_time.day, precision=precision)
                narozeni_from_note = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P15",
                        "datavalue": {
                            "value": {'time': date.toTimestr(),
                                      'precision': precision,
                                      'after': date.after,
                                      'before': date.before,
                                      'timezone': date.timezone,
                                      'calendarmodel': date.calendarmodel
                                      },
                            "type": "time",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(narozeni_from_note)

            if (line['death_from_note'] is not None):
                precision = line['death_note_precision']
                db_time = line['death_from_note']
                date = pywikibot.WbTime(year=db_time.year, month=db_time.month, day=db_time.day, precision=precision)
                umrti_from_note = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P16",
                        "datavalue": {
                            "value": {'time': date.toTimestr(),
                                      'precision': precision,
                                      'after': date.after,
                                      'before': date.before,
                                      'timezone': date.timezone,
                                      'calendarmodel': date.calendarmodel
                                      },
                            "type": "time",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(umrti_from_note)

            if (line['first_name'] != ''):
                first_name = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P13",
                        "datavalue": {
                            "value": line['first_name'].strip(),
                            "type": "string",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(first_name)

            if (line['surname'] != ''):
                surname = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P14",
                        "datavalue": {
                            "value": line['surname'].strip(),
                            "type": "string",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(surname)

            if (line['type'] > 0):
                type = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P17",
                        "datavalue": {
                            "value": {
                                "entity-type":"item",
                                "id":"Q33655",
                                "numeric-id": 33655
                                },
                            "type": "wikibase-entityid",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(type)

            nkcraut = {
                "mainsnak": {
                    "snaktype": "value",
                    "property": "P4",
                    "datavalue": {
                        "value": line['nkcr_aut'],
                        "type": "string",
                    }},
                "type": "statement",
                "rank": "normal",
                "references": [
                    {
                        "snaks": {
                            "P12": [
                                {
                                    "snaktype": "value",
                                    "property": "P12",
                                    "datavalue": {
                                        "value": {
                                            "entity-type": "item",
                                            "numeric-id": 33635,
                                            "id": "Q33635"
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

            if line['exist_quid'] != '':
                wikidata = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P9",
                        "datavalue": {
                            "value": line['exist_quid'],
                            "type": "string",
                        }},
                    "type": "statement",
                    "rank": "normal"
                }
                di.append(wikidata)

            if line['description'] != '':
                note = {
                    "mainsnak": {
                        "snaktype": "value",
                        "property": "P10",
                        "datavalue": {
                            "value": line['description'][:399].strip(),
                            "type": "string",
                        }},
                    "type": "statement",
                    "rank": "normal",
                }
                di.append(note)
            data['claims'] = di
            if (line['name'] == ''):
                data['labels']['en']['value'] = line['nkcr_aut']
                data['labels']['cs']['value'] = line['nkcr_aut']
            try:
                item = self.create_item_for_page(data, 'Creating NKČR auth - ' + line['nkcr_aut'], repo, line['name'])
            except pywikibot.exceptions.OtherPageSaveError as e:
                pywikibot.output(e.message)
                pywikibot.output(line['nkcr_aut'])

        cursor.close()

    def delete_aun(self):
        site = pywikibot.Site('autority', 'autority')
        repo = site.data_repository()

        with open('aun_nkcr.csv') as fh:
            for line in fh:
                p = pywikibot.Page(source=repo, ns=120, title=line.strip())
                if site.user() is None:
                    site.login()
                if (p.text.strip() == ''):
                    continue
                p.delete(reason='deleted aun authority', prompt=False, quit=True)
                print(line.strip())

    def prepare_json_dump(self):
        import ujson
        import csv

        properties = ['P1', 'P2', 'P13', 'P14']

        with open('exp.json') as f:
            data = ujson.load(f)
            with open('new_nkcr.csv', mode='w') as wf:
                wf_writer = csv.writer(wf, delimiter=';', quotechar='"',
                                       quoting=csv.QUOTE_MINIMAL)
                for line in data:
                    if (line['type'] != 'property'):
                        qid = line['id']
                        arr_to_csv = [qid]
                        for property in properties:
                            if property in line['claims']:
                                val = line['claims'][property][0]['mainsnak']['datavalue']['value']
                                if 'time' in val:
                                    val = val['time']
                                arr_to_csv.append(val)
                        wf_writer.writerow(arr_to_csv)

    def load_to_dict(self):
        import csv
        dicti = {}
        with open('new_nkcr.csv', mode='r') as employee_file:
            employee_writer = csv.reader(employee_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for line in employee_writer:
                dicti[line[1]] = line[0]
        return dicti

    def delete_non_person(self):
        site = pywikibot.Site('autority', 'autority')
        repo = site.data_repository()
        conv = self.load_to_dict()
        db = MySQLdb.connect(host="localhost",
                             user="root",
                             passwd="root",
                             db="wikidata_lidi")

        site = pywikibot.Site('autority', 'autority')
        repo = site.data_repository()

        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        sql_years = '''
                    select nkcr_aut from nkcr2_new where new = 1 and nkcr_aut NOT LIKE 'aun%' and first_name = '' and surname = ''
                '''
        cursor.execute(sql_years)
        record = cursor.fetchall()
        for l in record:
            if l['nkcr_aut'] in conv:
                qid = conv[l['nkcr_aut']]
                p = pywikibot.Page(source=repo, ns=120, title=qid.strip())
                if site.user() is None:
                    site.login()
                if (p.text.strip() == ''):
                    continue
                print(l['nkcr_aut'])
                p.delete(reason='deleted non personal authority', prompt=False, quit=True)

c = importWikibaseAutority()
c.prepare_json_dump()

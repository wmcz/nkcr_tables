#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

from pywikibot import pagegenerators
import pywikibot.data.sparql
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

        # pywikibot.output('Creating item ' + str(self.iter) + ' (' + name + ')')
        item = pywikibot.ItemPage(repo)

        result = self.user_edit_entity(item, data, summary=summary)
        if result:
            return item
        else:
            return None


    def user_edit_entity(self, item, data=None, summary=None):
        """
        Edit entity with data provided, with user confirmation as required.

        @param item: page to be edited
        @type item: ItemPage
        @param data: data to be saved, or None if the diff should be created
          automatically
        @kwarg summary: revision comment, passed to ItemPage.editEntity
        @type summary: str
        @kwarg show_diff: show changes between oldtext and newtext (default:
          True)
        @type show_diff: bool
        @kwarg ignore_server_errors: if True, server errors will be reported
          and ignored (default: False)
        @type ignore_server_errors: bool
        @kwarg ignore_save_related_errors: if True, errors related to
          page save will be reported and ignored (default: False)
        @type ignore_save_related_errors: bool
        @return: whether the item was saved successfully
        @rtype: bool
        """
        return self._save_page(item, item.editEntity, data)


    def _save_page(self, page, func, *args):
        """
        Helper function to handle page save-related option error handling.

        @param page: currently edited page
        @param func: the function to call
        @param args: passed to the function
        @param kwargs: passed to the function
        @kwarg ignore_server_errors: if True, server errors will be reported
          and ignored (default: False)
        @kwtype ignore_server_errors: bool
        @kwarg ignore_save_related_errors: if True, errors related to
        page save will be reported and ignored (default: False)
        @kwtype ignore_save_related_errors: bool
        @return: whether the page was saved successfully
        @rtype: bool
        """
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
            select * from nkcr2_new where type = 1 and nkcr_aut IN (
"jk01082604",
"jk01032488",
"jk01120440",
"jk01141433",
"jk01142319",
"jk01142533",
"jz8600001",
"jz8000053",
"jz8600049",
"jz8000120",
"jz8000219",
"jz8000233",
"jz8600229",
"jz8600273",
"jz8600275",
"jz8000462",
"jz8600377",
"jz8600383",
"jz8600418",
"jz8600436",
"jz8600492",
"jz8000644",
"jz8600651",
"jz8600665",
"jz8600692",
"jz8600694",
"jz8000880",
"jz8000935",
"jz8600815",
"jz8001039",
"jz8600881",
"jz8600886",
"jz8600888",
"jz8600963",
"jz8601003",
"jz8601005",
"jz8001225",
"jz8001226",
"jz8001387",
"jn19992000348",
"jn19992000349",
"jn19990003867",
"jn19990006198",
"nlk20010099470",
"js20020115007",
"jn20020723139",
"ntka172643",
"ntka173553",
"jo2006219803",
"jo2004232816",
"js20040503006",
"xx0022822",
"xx0005141",
"mzk2004258451",
"jx20050627002",
"jx20050926013",
"mzk2005312976",
"mzk2006322668",
"jo2006325085",
"js20060205004",
"jo2009330686",
"mzk2006355950",
"mzk2006356129",
"xx0050248",
"js20061006029",
"mzk2006377289",
"mzk2006377290",
"mzk2006377291",
"xx0058124",
"js20070119017",
"js2007382449",
"xx0059271",
"jx20070402002",
"jx20070410014",
"jx20070615028",
"mzk2007408585",
"mzk2007408589",
"mzk2007411188",
"xx0068771",
"xx0069051",
"mzk2007423888",
"jx20071212003",
"vut2011439979",
"vut2011439980",
"xx0075805",
"xx0076887",
"jx20080409028",
"jx20080422007",
"js20080427005",
"mzk2008453545",
"ola2008460002",
"jo2008464735",
"pna2008467260",
"mzk2008468961",
"mzk2008472947",
"xx0088706",
"hka2009498656",
"xx0090907",
"xx0091081",
"mzk2009502498",
"xx0092827",
"ola2009507562",
"mzk2009511238",
"mzk2009512364",
"xx0095978",
"mzk2009517350",
"mzk2009517423",
"mzk2009521605",
"jx20090930011",
"xx0104261",
"xx0106793",
"xx0106854",
"xx0107114",
"ola2010588889",
"xx0122028",
"jo2010596917",
"mzk2010598155",
"mzk2010609087",
"xx0129698",
"xx0129995",
"vut2011621924",
"xx0133190",
"ola2011643728",
"xx0138071",
"vut2011651641",
"xx0139552",
"mub2011668134",
"jx20120109016",
"jx20120214024",
"jx20120228045",
"vut2012702081",
"xx0155308",
"xx0161230",
"mzk2013743986",
"js2013747886",
"jo2013750187",
"mzk2013789043",
"jcu2013793345",
"xx0180268",
"mzk2013798910",
"uk2015885324",
"vut2015867840",
"js2015863584",
"xx0202437",
"xx0199416",
"jo2016932770",
"ntk2017945205",
"ntk2017951838",
"ntk2017957991",
"ntk2017965378",
"jo2017966594",
"ntk2017966622",
"xx0219388",
"jo2017975115",
"jo2018984147",
"jo2018984240",
"xx0223310",
"ntk2018997415",
"ntk2018997775",
"jo2018998219",
"jo20181002244",
"ntk20181004542",
"ntk20181005587",
"ntk20181005817",
"jo20181005885",
"jo20181006920",
"xx0227396",
"ntk20181008538",
"ntk20181012377",
"jo20181012600",
"jo20181013294",
"ntk20181015465",
"ntk20181018842",
"aun20181019181",
"ntk20191020145",
"ntk20191033494",
"ntk20191032957",
"jo20191032546",
"ntk20191032008",
"ntk20191028658",
"ntk20191027861",
"ntk20191025228",
"xx0232011",
"ntk20191022088")     
        '''
        cursor.execute(sql_years)
        record = cursor.fetchall()

        years = []
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

            # data.setdefault('claims', {}).update(di)

            # {"claims": [{"mainsnak": {"snaktype": "value", "property": "P56",
            #                           "datavalue": {"value": "ExampleString", "type": "string"}}, "type": "statement",
            #              "rank": "normal"}]}
            # if (line[2] != ''):
            #     item = pywikibot.ItemPage(repo, line[2])
            #     data = None
            # else:
            # page = None
            # item = create_item_for_page(page=gendata, data=data, repo=repo, summary='Creating czech company')

            # sources = []

            # source = pywikibot.Claim(repo, 'P248')
            # source.setTarget(pywikibot.ItemPage(repo, 'Q8182488'))

            # instance = pywikibot.Claim(repo, 'P31')
            # instance.setTarget(pywikibot.ItemPage(repo, 'Q4830453'))
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
                # narozeni = pywikibot.Claim(repo, 'P2')
                # narozeni.setTarget(date)

            if (line['death'] > 0):
                # umrti = pywikibot.Claim(repo, 'P3')
                # date = pywikibot.WbTime(year=line['death'], precision=9)
                # umrti.setTarget(date)
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
                f = '%Y-%m-%d %H:%M:%S'
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
                # narozeni = pywikibot.Claim(repo, 'P2')
                # narozeni.setTarget(date)

            if (line['death_from_note'] is not None):
                precision = line['death_note_precision']
                f = '%Y-%m-%d %H:%M:%S'
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

            # nkcraut = pywikibot.Claim(repo, 'P4')
            # nkcraut.setTarget(line['nkcr_aut'])

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
                # wikidata = pywikibot.Claim(repo, 'P9')
                # wikidata.setTarget(line['exist_quid'])

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
                # note = pywikibot.Claim(repo, 'P10')
                # note.setTarget(line['description'])
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



c = importWikibaseAutority()
c.importAutority()
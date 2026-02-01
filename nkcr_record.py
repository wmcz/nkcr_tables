from autrecord import AutRecord
import nkcrlib
from datetime import datetime
import re

class nkcr_record:

    def __init__(self, record):
        assert isinstance(record, AutRecord)
        self.record = record
        self.aut = self.record.aut()
        self.birth_from_note = nkcrlib.resolve_birth_from_note(self.record)
        self.death_from_note = nkcrlib.resolve_death_from_note(self.record)
        self.name = self.record.name()
        self.aliases = self.record.aliases()
        self.geographicNameWithoutBrackets = self.record.geographic_name_without_brackets()
        self.first_name = self.record.first_name()
        self.wikidata_field = self.record.wikidata024('wikidata')
        self.orcid_field = self.record.wikidata024('orcid')
        self.wikipedia_field = self.record.wikipedia856()
        self.wikidata_source_field = self.record.source670('wikidata')
        self.wikipedia_source_field = self.record.source670('wikipedia')
        self.last_name = record.last_name()
        self.birth = record.birth()
        self.death = record.death()
        self.description = record.note()
        self.status = record.status()
        self.county = record.okres()
        self.city = record.mesto()
        self.gender = record.gender()
        self.human = self.gender is not None

        self.birth_wd = ''
        self.death_wd = ''
        self.birth_note_precision = '0'
        self.death_note_precision = '0'
        self.new = 1
        self.type = 1

        self.wikidata_from_nkcr = None
        self.wikiproject_from_nkcr = ''
        self.wikilang_from_nkcr = ''
        self.wikiarticle_from_nkcr = ''
        self.wikilink_from_nkcr = ''

        self.birth_to_quickstatements = None
        self.death_to_quickstatements = None

        self.get_updated_time()
        self.resolve_wikidata_from_nkcr()
        self.resolve_wikipedia_from_nkcr()
        self.resolve_name()
        self.resolve_quickstatements_dates()

    def get_updated_time(self):
        self.updatedraw = datetime.now()
        self.updated = str(self.updatedraw.year) + '-' + str(self.updatedraw.month) + '-' + str(
            self.updatedraw.day) + ' ' + str(self.updatedraw.hour) + ':' + str(self.updatedraw.minute) + ':' + str(
            self.updatedraw.second)
        return self.updated

    def resolve_wikidata_from_nkcr(self):
        if (self.wikidata_source_field != None and self.wikidata_field == None):
            self.wikidata_from_nkcr = self.wikidata_source_field['article']
        elif (self.wikidata_field != None):
            self.wikidata_from_nkcr = self.wikidata_field
        else:
            self.wikidata_from_nkcr = None

    def resolve_wikipedia_from_nkcr(self):
        if (self.wikipedia_source_field != None and self.wikipedia_field == None):
            self.wikiproject_from_nkcr = self.wikipedia_source_field['project']
            self.wikilang_from_nkcr = self.wikipedia_source_field['lang']
            self.wikiarticle_from_nkcr = self.wikipedia_source_field['article']
            self.wikilink_from_nkcr = self.wikipedia_source_field['link']
        elif (self.wikipedia_field != None):
            self.wikiproject_from_nkcr = self.wikipedia_field['project']
            self.wikilang_from_nkcr = self.wikipedia_field['lang']
            self.wikiarticle_from_nkcr = self.wikipedia_field['article']
            self.wikilink_from_nkcr = self.wikipedia_field['link']
        else:
            self.wikiproject_from_nkcr = ''
            self.wikilang_from_nkcr = ''
            self.wikiarticle_from_nkcr = ''
            self.wikilink_from_nkcr = ''

    def resolve_name(self):
        if (self.status == 'správní celek'):
            self.name = self.city

            regex = r"(.*) : okres"
            matches = re.search(regex, self.county, re.IGNORECASE)
            try:
                groups = matches.groups()
                self.county = groups[0]
            except AttributeError:
                self.county = ""

    def resolve_quickstatements_dates(self):
        self.birth_to_quickstatements = self.birth_from_note if self.birth_from_note is not None else self.birth
        self.death_to_quickstatements = self.death_from_note if self.death_from_note is not None else self.death

from pymarc.marcxml import XmlHandler
from pymarc import Field, unicodedata
from autrecord import AutRecord
MARC_XML_NS = "http://www.loc.gov/MARC21/slim"
# SKIPPED = 990000
SKIPPED_MODULO = 10000
SKIPPED = 0
class AutXmlHandler(XmlHandler):

    """
    You can subclass XmlHandler and add your own process_record
    method that'll be passed a pymarc.Record as it becomes
    available. This could be useful if you want to stream the
    records elsewhere (like to a rdbms) without having to store
    them all in memory.
    """

    count = 0

    mydata = []

    def startElementNS(self, name, qname, attrs):
        if self._strict and name[0] != MARC_XML_NS:
            return

        element = name[1]
        self._text = []

        if element == 'record':
            self.count = self.count + 1
            if self.count <= SKIPPED:
                if (self.count % SKIPPED_MODULO == 0):
                    print(self.count)
                return
            if (self.count == SKIPPED):
                print('milion')
            self._record = AutRecord()
        elif element == 'controlfield':
            tag = attrs.getValue((None, 'tag'))
            self._field = Field(tag)
        elif element == 'datafield':
            tag = attrs.getValue((None, 'tag'))
            ind1 = attrs.get((None, 'ind1'), ' ')
            ind2 = attrs.get((None, 'ind2'), ' ')
            self._field = Field(tag, [ind1, ind2])
        elif element == 'subfield':
            self._subfield_code = attrs[(None, 'code')]

    def endElementNS(self, name, qname):
        if self._strict and name[0] != MARC_XML_NS:
            return

        if self.count <= SKIPPED:
            if (self.count % SKIPPED_MODULO == 0):
                print(self.count)
            return

        element = name[1]
        if self.normalize_form is not None:
            text = unicodedata.normalize(self.normalize_form, u''.join(self._text))
        else:
            text = u''.join(self._text)

        if element == 'record':

            clear = self.process_record(self._record, self.count, self.mydata)
            if (clear == True):
                self.mydata = []
            self._record = None
        elif element == 'leader':
            self._record.leader = text
        elif element == 'controlfield':
            self._field.data = text
            self._record.add_field(self._field)
            self._field = None
        elif element == 'datafield':
            self._record.add_field(self._field)
            self._field = None
        elif element == "subfield":
            self._field.add_subfield(self._subfield_code, text)
            self._subfield_code = None

        self._text = []
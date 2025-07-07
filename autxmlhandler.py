from pymarc.marcxml import XmlHandler
from pymarc import Field, unicodedata
from autrecord import AutRecord
from typing import List, Any, Optional

MARC_XML_NS: str = "http://www.loc.gov/MARC21/slim"
# SKIPPED = 990000
SKIPPED_MODULO: int = 10000
SKIPPED: int = 0

class AutXmlHandler(XmlHandler):
    """
    Custom XML handler for parsing MARCXML records, extending pymarc.marcxml.XmlHandler.
    This handler processes MARCXML elements and constructs `AutRecord` objects.
    It includes functionality to skip a certain number of records and to pass
    processed records to a `process_record` method.
    """

    count: int = 0
    mydata: List[Any] = []

    def startElementNS(self, name: Any, qname: Any, attrs: Any) -> None:
        """
        Handles the start of an XML element in a namespace-aware way.
        Overrides the method from XmlHandler to specifically handle MARCXML records
        and initialize `AutRecord` objects.

        Args:
            name: A tuple of (namespace URI, localname) or (None, qname) if no namespace.
            qname: The qualified name of the element.
            attrs: A SAX Attributes object containing the attributes of the element.
        """
        if self._strict and name[0] != MARC_XML_NS:
            return

        element = name[1]
        self._text = []

        if element == 'record':
            self.count += 1
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

    def endElementNS(self, name: Any, qname: Any) -> None:
        """
        Handles the end of an XML element in a namespace-aware way.
        Overrides the method from XmlHandler to finalize MARCXML fields and records,
        and to call the `process_record` method when a full record is parsed.

        Args:
            name: A tuple of (namespace URI, localname) or (None, qname) if no namespace.
            qname: The qualified name of the element.
        """
        if self._strict and name[0] != MARC_XML_NS:
            return

        if self.count <= SKIPPED:
            if (self.count % SKIPPED_MODULO == 0):
                print(self.count)
            return

        element = name[1]
        if self.normalize_form is not None:
            text = unicodedata.normalize(self.normalize_form, ''.join(self._text))
        else:
            text = ''.join(self._text)

        if element == 'record':
            # Assuming process_record is a callable attribute set by the user
            clear = self.process_record(self._record, self.count, self.mydata)
            if clear:
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

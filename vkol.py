from sickle import Sickle
from sickle.iterator import OAIResponseIterator
from pymarc import marcxml
from lxml import etree
sickle = Sickle('http://aleph.vkol.cz/OAI', iterator=OAIResponseIterator)
# sickle = Sickle('http://aleph.vkol.cz/OAI')
records = sickle.ListRecords(metadataPrefix='marc21')
# sets = sickle.ListSets()
# for set in sets:
#     print(set)

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

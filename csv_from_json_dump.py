#!/usr/bin/python
# -*- coding: utf-8 -*-

# def load_with_bigjson():
#     import bigjson
#
#     with open('dump.json', 'rb') as f:
#         j = bigjson.load(f)
#         for line in j:
#             print(line['type'])
#             print(line['id'])

def header(properties, time_properties, wf_writer):
    properties_names = {
        'qid': 'AUTORITY-QID',
        'P1': 'NKČR AUT name',
        'P2': 'birth-NKCR',
        'P2-prec': 'birth-NKCR-precision',
        'P3': 'death-NKCR',
        'P3-prec': 'death-NKCR-precision',
        'P4': 'NKCR-AUT',
        'P5': 'place-of-birth-NKCR',
        'P6': 'place-of-death-NKCR',
        'P7': 'place-of-birth-WD',
        'P8': 'place-of-death-WD',
        'P9': 'QID',
        'P10': 'note-NKCR',
        'P13': 'first-name',
        'P14': 'surname',
        'P15': 'birth-from-note',
        'P15-prec': 'birth-from-note-precision',
        'P16': 'death-from-note',
        'P16-prec': 'death-from-note-precision',
        'P17': 'type-of-record',
    }

    arr_to_csv = ['qid']
    for prop in properties:
        if prop in time_properties:
            arr_to_csv.append(prop)
            arr_to_csv.append(prop + '-prec')
        else:
            arr_to_csv.append(prop)
    final_arr_to_csv = []
    for cell in arr_to_csv:
        final_arr_to_csv.append(properties_names.get(cell, ''))
    wf_writer.writerow(final_arr_to_csv)


def prepare_json_dump():
    # import ujson
    import bigjson
    import csv

    properties = ['P1', 'P2', 'P3', 'P15', 'P16', 'P13', 'P14']

    time_properties = ['P2', 'P3', 'P15', 'P16']

    with open('exp_short.json', 'rb') as f:
        print('start')
        # data = ujson.load(f)
        data = bigjson.load(f)
        print('loaded json')

        with open('new_nkcr.csv', mode='w') as wf:
            wf_writer = csv.writer(wf, dialect='unix')
            count = 0

            header(properties, time_properties, wf_writer)

            for line in data:
                count = count + 1
                if count % 1000 == 0:
                    print(count)
                if line['type'] != 'property':
                    qid = line['id']
                    arr_to_csv = {'qid': qid}

                    precisions = []
                    for prop in properties:

                        if prop in line['claims']:
                            val = line['claims'][prop][0]['mainsnak']['datavalue']['value']

                            try:
                                try:
                                    valitem = val.to_python()
                                    if 'time' in valitem.keys():
                                        whole_val = val
                                        val = whole_val['time']
                                        precisions.append(whole_val['precision'])
                                        arr_to_csv[prop] = val
                                        arr_to_csv[prop + '-prec'] = whole_val['precision']
                                    else:
                                        arr_to_csv[prop] = val
                                except Exception:
                                    arr_to_csv[prop] = val



                            except Exception:
                                pass
                        else:
                            if prop in time_properties:
                                arr_to_csv[prop] = ''
                                arr_to_csv[prop + '-prec'] = ''
                            else:
                                arr_to_csv[prop] = ''

                    try:
                        final_arr_to_csv = []
                        for cell in arr_to_csv.items():
                            final_arr_to_csv.append(cell[1])

                        wf_writer.writerow(final_arr_to_csv)
                    except UnicodeEncodeError as e:
                        print(e)
                        print('unicode encode error u polozky: ' + qid)


prepare_json_dump()
# test_big_json()

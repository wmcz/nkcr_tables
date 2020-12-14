#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import csv

y2017 = {}
with open('cswiki_201701-12.all.views.poradi') as f:
    csv.field_size_limit(1000000)
    reader = csv.DictReader(f, delimiter=';')
    for line in reader:
        y2017[line['article']] = {'article' : line['article'], 'poradi' : line['poradi'], 'views' : line['views']}

    # print(y2017)

y2018 = {}
with open('cswiki_20180101-1219.all.views.poradi') as f:
    csv.field_size_limit(1000000)
    reader = csv.DictReader(f, delimiter=';')
    for line in reader:
        y2018[line['article']] = {'article' : line['article'], 'poradi' : line['poradi'], 'views' : line['views']}

    # print(y2018)

vys = []
poc = 0
for key, art in y2018.items():
    poc = poc + 1
    # if poc <= 100:
    try:
        if y2017[art['article']]:
            year_prev = y2017[art['article']]
            if (year_prev['views'] == ''):
                print(art['article'])
            if (art['views'] == ''):
                print(art['article'])
            try:
                vys.append({
                    'article' : art['article'],
                    'poradi2018' : art['poradi'],
                    'views2018' : art['views'],
                    'poradi2017': year_prev['poradi'],
                    'views2017': year_prev['views'],
                    'rozdil_poradi': int(year_prev['poradi'])-int(art['poradi']),
                    'rozdil_views': int(art['views'])-int(year_prev['views']),
                })
            except ValueError as e:
                print(art)
                print(year_prev)
                sys.exit()
    except KeyError as e:
        pass

from operator import itemgetter
sorted_by_poradi = sorted(vys, key=itemgetter('rozdil_poradi'))
sorted_by_views = sorted(vys, key=itemgetter('rozdil_views'), reverse=True)

# porplus = open('rozdil_poradi_plus.txt', 'w')
# for por in sorted_by_poradi:
#     if (por['rozdil_poradi']>0):
#         porplus.write(str(por['article']) + " > " + str(por['rozdil_poradi']) + " (2017: " + por['poradi2017'] + ", 2018: " + por['poradi2018'] + ")")
#         porplus.write('\n')
# porplus.close()
#
# porminus = open('rozdil_poradi_minus.txt', 'w')
# for por in sorted_by_poradi:
#     if (por['rozdil_poradi']<0):
#         porminus.write(str(por['article']) + " > " + str(por['rozdil_poradi']) + " (2017: " + por['poradi2017'] + ", 2018: " + por['poradi2018'] + ")")
#         porminus.write('\n')
# porminus.close()
#
# porstejne = open('rozdil_poradi_stejne.txt', 'w')
# for por in sorted_by_poradi:
#     if (por['rozdil_poradi']==0):
#         porstejne.write(str(por['article']) + " > " + str(por['rozdil_poradi']) + " (2017: " + por['poradi2017'] + ", 2018: " + por['poradi2018'] + ")")
#         porstejne.write('\n')
# porstejne.close()

viewplus = open('rozdil_views_plus.txt', 'w')
for por in sorted_by_views:
    if (por['rozdil_views']>0):
        viewplus.write(str(por['article']) + " > " + str(por['rozdil_views']) + " (2017: " + por['views2017'] + ", 2018: " + por['views2018'] + ")")
        viewplus.write('\n')
viewplus.close()

viewminus = open('rozdil_views_minus.txt', 'w')
for por in sorted_by_views:
    if (por['rozdil_views']<0):
        viewminus.write(str(por['article']) + " > " + str(por['rozdil_views']) + " (2017: " + por['views2017'] + ", 2018: " + por['views2018'] + ")")
        viewminus.write('\n')
viewminus.close()

viewstejne = open('rozdil_views_stejne.txt', 'w')
for por in sorted_by_views:
    if (por['rozdil_views']==0):
        viewstejne.write(str(por['article']) + " > " + str(por['rozdil_views']) + " (2017: " + por['views2017'] + ", 2018: " + por['views2018'] + ")")
        viewstejne.write('\n')
viewstejne.close()
# print(vys)
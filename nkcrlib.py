# import MySQLdb
from autxmlhandler import AutXmlHandler
from pymarc.marcxml import parse_xml
import datetime
from quickstatements import quickstatements

write_allowed = False

def get_nkcr_aut_in_db(new_only = False, column_to_return = [], withoutEmptyNames = True, typeOfReturn = 'set', limit = None, index_column = None):

    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="wikidata_lidi")

    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    if (len(column_to_return) > 0):
        columns = ''
        for column in column_to_return:
            if (columns == ''):
                columns = columns + ' ' + column
            else:
                columns = columns + ', ' + column
    if (index_column is not None):
        index_column_to_sql = ',' + index_column
    else:
        index_column_to_sql = ''
    sql = "SELECT " + columns + index_column_to_sql + " from nkcr2_new WHERE 1=1"
    if (new_only == True):
        sql = sql + ' AND new = 1'
    if (withoutEmptyNames == True):
        sql = sql + ' AND first_name != ""'
    if (limit is not None):
        sql = sql + ' LIMIT ' + limit
    cursor.execute(sql)
    record = cursor.fetchall()
    dataFinal = set()
    if (typeOfReturn == 'list'):
        data = []
        dataFinal = []
        indexes = []
    for line in record:
        retline = ''
        for column in column_to_return:
            if (retline == ''):
                retline = line[column]
            else:
                retline = retline + ' ' + line[column]
        if (index_column is not None):
            index_data = line[index_column]
        if (typeOfReturn == 'list'):
            data.append(retline)
            indexes.append(index_data)


        else:
            dataFinal.add(retline)

    if (typeOfReturn == 'list'):
        ret = {'data': data, 'index': indexes}
        dataFinal = ret

    return dataFinal

import io

def map_xml(function, *files):
    """
    map a function onto the file, so that for each record that is
    parsed the function will get called with the extracted record

    def do_it(r):
      print(r)

    map_xml(do_it, 'marc.xml')
    """
    handler = AutXmlHandler()
    handler.process_record = function
    for xml_file in files:
        with open(xml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace('\002', '-')
        parse_xml(io.StringIO(content), handler)

def get_week_num_to_download(force_week = None):
    if (force_week is not None):
        return force_week
    actual_week_num_obj = datetime.datetime.now()
    actual_week_num = actual_week_num_obj.isocalendar()[1]
    year = actual_week_num_obj.year
    if year == 2025:
        week_num_to_download = actual_week_num - 2
        if (actual_week_num == 1):
            week_num_to_download = 51

    else:
        week_num_to_download = actual_week_num - 1
        if (week_num_to_download == 0):
            week_num_to_download = 52
    return week_num_to_download

def get_year_actual():

    actual_week_num_obj = datetime.datetime.now()
    actual_week_num = actual_week_num_obj.isocalendar()[1]
    year = actual_week_num_obj.year
    if year == 2025:
        week_num_to_download = actual_week_num - 2
    else:
        week_num_to_download = actual_week_num - 1
        if (week_num_to_download == 0):
            year = year-1
    return year

def download_actual_file_from_nkcr(force = None):
    import ftputil
    week_num_to_download = get_week_num_to_download(force)

    with ftputil.FTPHost("ftp.nkp.cz", "wikimedia", "wikid4t4369") as ftp_host:
        names = ftp_host.listdir(ftp_host.curdir)
        for name in names:
            # regex = r"wnew_m_(\d+)\.xml"
            # matches = re.search(regex, name, re.IGNORECASE)
            # try:
            #     groups = matches.groups()
            #     week_num = groups[0]
            #     print(name)
            #     print(week_num)
            # except AttributeError as e:
            #     week_num = 0
            week_num_to_download = str(week_num_to_download).zfill(2)
            # print(name)
            file_name_to_download = 'wnew_m_' + week_num_to_download + '.xml'
            # print(file_name_to_download)
            # print(name)
            if (name == file_name_to_download):
                if ftp_host.path.isfile(name):
                    info = ftp_host.stat(name)
                    mtime = info.st_mtime
                    dt_object = datetime.datetime.fromtimestamp(int(mtime))
                    new_name = str(dt_object.year) + '-' + name
                    ftp_host.download(name, new_name)  # remote, local
                    return new_name

        return False

def resolve_death_from_note(record):
    try:
        # death_from_note = str(record.death_date().year) + '-' + str(record.death_date().month) + '-' + str(
        #     record.death_date().day) + ' ' + str(record.death_date().hour) + ':' + str(
        #     record.death_date().minute) + ':' + str(record.death_date().second)
        death_from_note = record.death_date()
    except AttributeError:
        death_from_note = None

    return death_from_note

def resolve_birth_from_note(record):
    try:
        # birth_from_note = str(record.birth_date().year) + '-' + str(record.birth_date().month) + '-' + str(
        #     record.birth_date().day) + ' ' + str(record.birth_date().hour) + ':' + str(
        #     record.birth_date().minute) + ':' + str(record.birth_date().second)
        birth_from_note = record.birth_date()
    except AttributeError:
        birth_from_note = None

    return birth_from_note

def create_search_link(name):
    link = "<span style='border: 1px solid black; padding: 5px; border-radius: 2px; background-color: #b9f5b3; background-image: none;'>[https://www.wikidata.org/w/index.php?search=" + str(name).replace(' ', '+').replace('"','+').replace('+,Czechia', '') + " 🔎&nbsp;WD]</span>"
    return link

def create_wd_link(qid):
    link = ' ([https://www.wikidata.org/wiki/' + qid + ' ' + qid + '])'
    return link

def create_nkcr_link(nkcr_aut):
    link = ' ([https://aleph.nkp.cz/F/?func=find-c&local_base=aut&ccl_term=ica=' + nkcr_aut + ' ' + nkcr_aut + '])'
    return link

def create_quickstatements_link(record_in_nkcr, force_qid = None, quickstatement_line_only = False):
    link = quickstatements()
    link.reset()
    create_new = False
    if (record_in_nkcr.wikidata_from_nkcr is not None):
        which_wd_item = record_in_nkcr.wikidata_from_nkcr
    elif (force_qid is not None):
        which_wd_item = force_qid
    else:
        create_new = True
        which_wd_item = link.LAST_DEFINE
        link.create()


    link.set_record(record_in_nkcr)
    link.set_item_to_add(which_wd_item)
    if create_new:
        try:
            link.set_label(record_in_nkcr.first_name + " " + record_in_nkcr.last_name)
            link.set_label(record_in_nkcr.first_name + " " + record_in_nkcr.last_name, 'en')
            link.set_label(record_in_nkcr.first_name + " " + record_in_nkcr.last_name, 'de')
        except TypeError:
            link.set_label(record_in_nkcr.name)
            # link.set_label(record_in_nkcr.name, 'en')
            # link.set_label(record_in_nkcr.name, 'de')
        if (record_in_nkcr.human):
            link.set_gender(record_in_nkcr.aut, record_in_nkcr.name, record_in_nkcr.gender)
            link.set_human(record_in_nkcr.aut, record_in_nkcr.name, record_in_nkcr.human)
            link.set_description(record_in_nkcr.description)
        elif record_in_nkcr.aut.startswith("ph"):
            link.set_label(record_in_nkcr.name)
            link.set_description(record_in_nkcr.description)
        else:
            link.set_label(record_in_nkcr.geographicNameWithoutBrackets)
            link.set_label(record_in_nkcr.geographicNameWithoutBrackets, 'en')
            link.set_label(record_in_nkcr.geographicNameWithoutBrackets, 'de')

    link.set_nkcr(record_in_nkcr.aut, record_in_nkcr.name)
    link.set_aliases(record_in_nkcr.aliases)
    link.set_date(record_in_nkcr.aut, link.BIRTH, record_in_nkcr.birth_to_quickstatements)
    link.set_date(record_in_nkcr.aut, link.DEATH, record_in_nkcr.death_to_quickstatements)

    get_link = link.get_link()
    if (quickstatement_line_only):
        return link.get_line()
    if (record_in_nkcr.wikidata_from_nkcr is not None):
        quickstatement_link = "<span style='border: 1px solid black; padding: 5px; border-radius: 2px; background-color: #b9f5b3; background-image: none;'>[" + link.get_link() + " ➕&nbsp;Doplnit&nbsp;do&nbsp;" + record_in_nkcr.wikidata_from_nkcr + "]</span>"
    elif (force_qid is not None):
        quickstatement_link = "<span style='border: 1px solid black; padding: 5px; border-radius: 2px; background-color: #b9f5b3; background-image: none;'>[" + link.get_link() + " ➕&nbsp;Doplnit&nbsp;do&nbsp;" + force_qid + "]</span>"
    else:
        quickstatement_link = "<span style='border: 1px solid black; padding: 5px; border-radius: 2px; background-color: #b9f5b3; background-image: none;'>[" + link.get_link() + " ➕&nbsp;Vytvořit]</span>"
    return quickstatement_link

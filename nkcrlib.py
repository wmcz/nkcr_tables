import MySQLdb
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
        parse_xml(xml_file, handler)

def get_week_num_to_download(force_week = None):
    if (force_week is not None):
        return force_week
    actual_week_num_obj = datetime.datetime.now()
    actual_week_num = actual_week_num_obj.isocalendar()[1]
    week_num_to_download = actual_week_num - 2
    return week_num_to_download

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

            # print(name)
            file_name_to_download = 'wnew_m_' + str(week_num_to_download) + '.xml'
            # print(file_name_to_download)
            # print(name)
            if (name == file_name_to_download):
                if ftp_host.path.isfile(name):
                    ftp_host.download(name, name)  # remote, local
                    return name

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
    link = "[https://www.wikidata.org/w/index.php?search=" + str(name).replace(' ', '+') + " Prohledat Wikidata]"
    return link

def create_nkcr_link(nkcr_aut):
    link = '([https://aleph.nkp.cz/F/?func=find-c&local_base=aut&ccl_term=ica=' + nkcr_aut + ' ' + nkcr_aut + '])'
    return link

def create_quickstatements_link(record_in_nkcr):
    link = quickstatements()
    link.reset()
    if (record_in_nkcr.wikidata_from_nkcr is not None):
        which_wd_item = record_in_nkcr.wikidata_from_nkcr
    else:
        which_wd_item = link.LAST_DEFINE
        link.create()


    link.set_record(record_in_nkcr)
    link.set_item_to_add(which_wd_item)
    try:
        link.set_label(record_in_nkcr.first_name + " " + record_in_nkcr.last_name)
        link.set_label(record_in_nkcr.first_name + " " + record_in_nkcr.last_name, 'en')
        link.set_label(record_in_nkcr.first_name + " " + record_in_nkcr.last_name, 'de')
    except TypeError:
        link.set_label(record_in_nkcr.name)
        link.set_label(record_in_nkcr.name, 'en')
        link.set_label(record_in_nkcr.name, 'de')
    link.set_description(record_in_nkcr.description)
    link.set_nkcr(record_in_nkcr.aut, record_in_nkcr.name)
    link.set_date(record_in_nkcr.aut, link.BIRTH, record_in_nkcr.birth_to_quickstatements)
    link.set_date(record_in_nkcr.aut, link.DEATH, record_in_nkcr.death_to_quickstatements)

    if (record_in_nkcr.wikidata_from_nkcr is not None):
        quickstatement_link = "[" + link.get_link() + " Přidat přes QuickStatements]"
    else:
        quickstatement_link = "[" + link.get_link() + " Vytvořit přes QuickStatements]"
    return quickstatement_link

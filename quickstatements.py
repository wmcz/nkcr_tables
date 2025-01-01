from datetime import datetime
import urllib

class quickstatements:

    quickstatements_command = list()

    record = None

    QUICKSTATEMENTS_LINK = 'https://tools.wmflabs.org/quickstatements/#v1='

    END_LINE = '||'
    SEPARATOR = '|'
    ENCLOSURE = '"'
    CREATE_DEFINE = 'CREATE'
    LAST_DEFINE = 'LAST'
    LABEL = 'L'
    ALIAS = 'A'
    DESCRIPTION = 'D'

    BIRTH = 'BIRTH'
    DEATH = 'DEATH'

    def reset(self):
        self.quickstatements_command = list()

    def add_command(self, command):
        self.quickstatements_command.append(command)

    def create(self):
        self.add_command(self.CREATE_DEFINE + self.END_LINE)

    def set_record(self, record):
        self.record = record

    def set_item_to_add(self, which_item):
        self.which_item = which_item

    def set_label(self, value, lang = 'cs'):
        try:
            value = self.ENCLOSURE + value + self.ENCLOSURE
        except TypeError:
            value = ''
        self.add_command(self.which_item + self.SEPARATOR + self.LABEL + lang + self.SEPARATOR + value + self.END_LINE)

    def set_alias(self, value, lang = 'cs'):
        value = self.ENCLOSURE + value + self.ENCLOSURE
        self.add_command(self.which_item + self.SEPARATOR + self.ALIAS + lang + self.SEPARATOR + value + self.END_LINE)

    def set_description(self, value, lang = 'cs'):
        try:
            if (len(value) > 250):
                value = value[ 0 : 250 ]
            value = self.ENCLOSURE + value + self.ENCLOSURE
        except TypeError as e:
            value = ''
        self.add_command(self.which_item + self.SEPARATOR + self.DESCRIPTION + lang + self.SEPARATOR + value + self.END_LINE)

    def get_link(self):
        link = ''.join(self.quickstatements_command)
        return self.QUICKSTATEMENTS_LINK + urllib.parse.quote(link, safe="")

    def get_line(self):
        line = ''.join(self.quickstatements_command)
        return line

    def set_date(self, nkcr_aut, birth_or_death, value):
        if (birth_or_death == self.BIRTH):
            property = 'P569'
        elif (birth_or_death == self.DEATH):
            property = 'P570'
        else:
            return None

        if (value is None):
            return None
        nkcr_aut = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        now_dt_string = self.now_time()

        dt_string = ''
        if (len(str(value)) == 4):
            precision = '9'
            try:
                dt = datetime(int(value), 1, 1)
                dt_string = dt.strftime("+%Y-%m-%dT%H:%M:%SZ/"+precision)
            except ValueError as e:
                dt_string = ''
        elif (type(value) is datetime):
            try:
                precision = '11'
                dt_string = value.strftime("+%Y-%m-%dT%H:%M:%SZ/" + precision)
            except ValueError as e:
                dt_string = ''

        if (dt_string != ''):
            cmd = self.which_item + self.SEPARATOR + property + self.SEPARATOR + dt_string + self.SEPARATOR + "S248" + self.SEPARATOR + "Q13550863" + self.SEPARATOR + "S691" + self.SEPARATOR + nkcr_aut + self.SEPARATOR + "S813" + self.SEPARATOR + now_dt_string + self.END_LINE
            self.add_command(cmd)


    def now_time(self):
        # "+2017-10-04T00:00:00Z/11"

        now = datetime.now()
        dt_string = now.strftime("+%Y-%m-%dT00:00:00Z/11")
        return dt_string

    def set_nkcr(self, nkcr_aut, name_in_nkcr):
        #Q95168516|P691|"nk123456"|P1810|"Matla Patla"|S248|Q13550863|S691|"nk123456"|S813|+2017-10-04T00:00:00Z/11

        nkcr_aut = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        try:
            name_in_nkcr = self.ENCLOSURE + name_in_nkcr + self.ENCLOSURE
        except TypeError:
            name_in_nkcr = ''

        dt_string = self.now_time()
        cmd = self.which_item + self.SEPARATOR + "P691" + self.SEPARATOR + nkcr_aut + self.SEPARATOR + "P1810" + self.SEPARATOR + name_in_nkcr + self.SEPARATOR + "S248" + self.SEPARATOR + "Q13550863" + self.SEPARATOR + "S691" + self.SEPARATOR + nkcr_aut + self.SEPARATOR + "S813" + self.SEPARATOR + dt_string + self.END_LINE
        # cmd = which + self.SEPARATOR + "P691" + self.SEPARATOR + nkcr_aut + self.END_LINE
        self.add_command(cmd)

    def set_gender(self, nkcr_aut, name_in_nkcr, gender):
        #Q95168516|P691|"nk123456"|P1810|"Matla Patla"|S248|Q13550863|S691|"nk123456"|S813|+2017-10-04T00:00:00Z/11

        nkcr_aut = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        try:
            name_in_nkcr = self.ENCLOSURE + name_in_nkcr + self.ENCLOSURE
        except TypeError:
            name_in_nkcr = ''

        try:
            if (gender == 'man'):
                gender_qid = "Q6581097"
            elif gender == 'woman':
                gender_qid = "Q6581072"
            else:
                return None
        except TypeError:
            gender_string = ''

        dt_string = self.now_time()
        cmd = self.which_item + self.SEPARATOR + "P21" + self.SEPARATOR + gender_qid + self.SEPARATOR + "S248" + self.SEPARATOR + "Q13550863" + self.SEPARATOR + "S691" + self.SEPARATOR + nkcr_aut + self.SEPARATOR + "S813" + self.SEPARATOR + dt_string + self.END_LINE
        # cmd = which + self.SEPARATOR + "P691" + self.SEPARATOR + nkcr_aut + self.END_LINE
        self.add_command(cmd)

    def set_human(self, nkcr_aut, name_in_nkcr, human):
        # Q95168516|P691|"nk123456"|P1810|"Matla Patla"|S248|Q13550863|S691|"nk123456"|S813|+2017-10-04T00:00:00Z/11

        nkcr_aut = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        try:
            name_in_nkcr = self.ENCLOSURE + name_in_nkcr + self.ENCLOSURE
        except TypeError:
            name_in_nkcr = ''

        try:
            if (human == True):
                human_qid = 'Q5'
            else:
                return None
        except TypeError:
            gender_string = ''

        dt_string = self.now_time()
        cmd = self.which_item + self.SEPARATOR + "P31" + self.SEPARATOR + human_qid + self.SEPARATOR + "S248" + self.SEPARATOR + "Q13550863" + self.SEPARATOR + "S691" + self.SEPARATOR + nkcr_aut + self.SEPARATOR + "S813" + self.SEPARATOR + dt_string + self.END_LINE
        # cmd = which + self.SEPARATOR + "P691" + self.SEPARATOR + nkcr_aut + self.END_LINE
        self.add_command(cmd)

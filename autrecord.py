from pymarc import Record
import re
import datetime
class AutRecord(Record):
    def name(self):
        """
        Returns the title of the record (245 $a an $b).
        """
        name = None
        try:
            name = self['100']['a']

        except TypeError:
            try:
                prep = self['110']
                name = prep['t']
                if (name is None):
                    raise(TypeError('err'))
            except TypeError:
                try:
                    name = self['110']['a']
                    try:
                        second_name = self['110']['b']
                    except TypeError:
                        second_name = None
                    if second_name is not None:
                        name = name + ' ' + second_name
                except TypeError:
                    try:
                        name = self['111']['a']
                    except TypeError:
                        try:
                            name = self['150']['a']
                        except TypeError:
                            try:
                                name = self['151']['a']
                            except TypeError:
                                name = None
        last_character = str(name)[-1]
        if (str(last_character) == ','):
            name = name[:-1]
        return name

    def aut(self):
        """
        Returns the title of the record (245 $a an $b).
        """
        try:
            # name = self['100']['7']
            name = self['001'].data
        except TypeError:
            name = None
        except AttributeError:
            name = None

        return name

    def birth_death(self):
        """
                Returns the title of the record (245 $a an $b).
                """
        try:
            name = self['100']['d']
        except TypeError:
            name = None

        return name

    def birth(self):
        """
                Returns the birth of the record (46f $a an $b).
                """
        try:
            name = str(self['46']['f'])
        except TypeError:
            try:
                name = self['046']['f']
                if (name is not None):
                    name = str(name)
            except TypeError:
                name = None

        return name

    def death(self):
        """
                Returns the death of the record (46g $a an $b).
                """
        try:
            name = str(self['46']['g'])
        except TypeError:
            try:
                name = self['046']['g']
                if name is not None:
                    name = str(name)
            except TypeError:
                name = None

        return name

    def note(self):
        """
                Returns the title of the record (678a $a an $b).
                """
        try:
            name = self['678']['a']
        except TypeError:
            name = None

        return name

    def wikidata024(self, type_of_link='wikidata'):
        '''
        <datafield tag="024" ind1="7" ind2=" ">
            <subfield code="a">Q98804556</subfield>
            <subfield code="2">wikidata</subfield>
        </datafield>

        :return:
        '''
        name = None
        name_to_return = None
        try:
            isexist = self['024']
            if isexist is not None:
                ex = self.get_fields('024')
                for line in ex:
                    # print(line)
                    name = line['a']
                    typ = line['2']

                    if (str(typ) == type_of_link):
                        name_to_return = name
        except TypeError:
            name = None

        return name_to_return

    def wikipedia856(self):
        '''
        <datafield tag="856" ind1="4" ind2="2">
            <subfield code="u">https://sv.wikipedia.org/wiki/Brigitte_Mral</subfield>
            <subfield code="4">N</subfield>
        </datafield>

        :return:
        '''
        link = None
        try:
            isexist = self['856']
            if isexist is not None:
                ex = self.get_fields('856')
                for line in ex:
                    # print(line)
                    name = line['u']
                    typ = line['4']

                    import re

                    regex = r"(http|https):\/\/([a-z]+)\.(wikipedia|wikisource)\.org\/wiki\/(.*)"

                    matches = re.search(regex, name, re.IGNORECASE)
                    link = None
                    try:
                        groups = matches.groups()
                        lang = groups[1]
                        wikiproject = groups[2]
                        article = groups[3]
                        ret_dict = {
                            'lang' : lang,
                            'project' : wikiproject,
                            'article' : article,
                            'link' : name
                        }
                        link = ret_dict
                    except AttributeError as e:
                        link = None
                    except ValueError as e:
                        link = None
        except TypeError:
            link = None

        return link

    def source670(self, type_of_source='wikidata'):
        '''
        <datafield tag="670" ind1=" " ind2=" ">
            <subfield code="a">www(Wikidata, Gabriel Chesneau), cit. 9. 6. 2020</subfield>
            <subfield code="b">biografické údaje</subfield>
            <subfield code="u">https://www.wikidata.org/wiki/Q15971728</subfield>
        </datafield>

        :return:
        '''
        link = None
        try:
            isexist = self['670']
            if isexist is not None:
                ex = self.get_fields('670')

                for line in ex:
                    # print(line)
                    name = line['u']
                    if (name is None):
                        name = ''

                    import re

                    if (type_of_source == 'wikidata'):
                        regex = r"(http|https):\/\/([a-z]+)\.(wikidata)\.org\/wiki\/(.*)"
                    else:
                        regex = r"(http|https):\/\/([a-z]+)\.(wikipedia)\.org\/wiki\/(.*)"

                    matches = re.search(regex, name, re.IGNORECASE)
                    link = None
                    try:
                        groups = matches.groups()
                        lang = groups[1]
                        wikiproject = groups[2]
                        article = groups[3]
                        ret_dict = {
                            'lang' : lang,
                            'project' : wikiproject,
                            'article' : article,
                            'link' : name
                        }
                        # link = ret_dict
                        return ret_dict
                    except AttributeError as e:
                        link = None
                    except ValueError as e:
                        link = None
        except TypeError:
            link = None

        return link

    def birth_date(self)->datetime:
        """
                Returns the title of the record (245 $a an $b).
                """
        try:
            note = self['678']['a']
            import re

            mapping = {' ledna': '1.', ' února': '2.', ' března': '3.', ' dubna': '4.',
                       ' května': '5.', ' června': '6.', ' července': '7.', ' srpna': '8.',
                       ' září': '9.', ' října': '10.', ' listopadu': '11.', ' prosince': '12.'}
            for k, v in mapping.items():
                note = note.replace(k, v)


            regex = r"(Narozen|Narozena|narozen|narozena) (\d+)\.\D*(\d+)\.\D*(\d+).*"

            matches = re.search(regex, note, re.IGNORECASE)
            bdate = None
            try:
                groups = matches.groups()
                x = datetime.datetime(int(groups[3]), int(groups[2]), int(groups[1]))
                bdate = x
            except AttributeError as e:
                bdate = None
            except ValueError as e:
                bdate = None
        except TypeError as e:
            # print(e)
            bdate = None

        return bdate

    def death_date(self)->datetime:
        """
                Returns the title of the record (245 $a an $b).
                """
        try:
            note = self['678']['a']
            import re

            mapping = {' ledna': '1.', ' února': '2.', ' března': '3.', ' dubna': '4.',
                       ' května': '5.', ' června': '6.', ' července': '7.', ' srpna': '8.',
                       ' září': '9.', ' října': '10.', ' listopadu': '11.', ' prosince': '12.'}
            for k, v in mapping.items():
                note = note.replace(k, v)

            regex = r"(Zemřel|Zemřela|zemřel|zemřela) (\d+)\.\D*(\d+)\.\D*(\d+).*"

            matches = re.search(regex, note, re.IGNORECASE)
            bdate = None
            try:
                groups = matches.groups()
                x = datetime.datetime(int(groups[3]), int(groups[2]), int(groups[1]))
                bdate = x
            except AttributeError as e:
                bdate = None
            except ValueError as e:
                bdate = None
        except TypeError:
            bdate = None

        return bdate

    def first_name(self):
        """
                Returns the title of the record (245 $a an $b).
                """
        try:
            name = self['100']['a']
            assert isinstance(name, str)
            splits = name.replace(',','').split(' ')
            length = len(splits)
            ret = splits[len(splits)-1]

            import re
            regex = r"(.*),\W+([\w‘ \.]*)(,*)"
            matches = re.search(regex, name, re.IGNORECASE)
            try:
                groups = matches.groups()
                name = groups[1]
            except AttributeError as e:
                name = ret
            except ValueError as e:
                name = ret
        except TypeError:
            name = None

        return name

    def last_name(self):
        """
                Returns the title of the record (245 $a an $b).
                """
        try:
            name = self['100']['a']
            assert isinstance(name, str)
            splits = name.replace(',', '').split(' ')
            length = len(splits)
            ret = splits[0]

            import re
            regex = r"(.*),\W+([\w‘ \.]*)(,*)"
            matches = re.search(regex, name, re.IGNORECASE)
            try:
                groups = matches.groups()
                name = groups[0]
            except AttributeError as e:
                name = ret
            except ValueError as e:
                name = ret
        except TypeError:
            name = None

        return name

    def status(self):
        """
                        Returns the title of the record (245 $a an $b).
                        """
        try:
            name = self['950']['a']
        except TypeError:
            name = None

        return name

    def okres(self):
        """
                        Returns the title of the record (245 $a an $b).
                        """
        try:
            name = self['751']['a']
        except TypeError:
            try:
                name = self['151']['a']
            except TypeError:
                name = None

        return name

    def mesto(self):
        """
                        Returns the title of the record (245 $a an $b).
                        """
        try:
            name = self['751']['a']
        except TypeError:
            try:
                name = self['151']['a']
            except TypeError:
                name = None

        return name

    def gender(self):
        """
                        Returns the title of the record (245 $a an $b).
                        """
        try:
            gender = self['375']['a']
            if (gender == 'muž'):
                return "man"
            elif (gender == 'žena'):
                return "woman"
            else:
                return None
        except TypeError:
            gender = None

        return gender
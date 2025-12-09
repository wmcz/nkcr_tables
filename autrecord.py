from pymarc import Record
import re
import datetime
from typing import Optional, Dict, Any, List


class AutRecord(Record):
    """
    A subclass of pymarc.Record to provide methods for accessing specific
    fields in an authority record.
    """

    def name(self) -> Optional[str]:
        """
        Returns the name of the record from various fields.
        Searches fields 100, 110, 111, 150, 151, 130, and 240 for the name.
        """
        for tag in ['100', '110', '111', '150', '151', '130', '240']:
            if tag in self:
                if 'a' in self[tag]:
                    name = self[tag]['a']
                    if name:
                        if name.endswith(','):
                            return name[:-1]
                        if name.endswith('.') and 'b' in self[tag]:
                            return name[:-1] + ', ' + self[tag]['b']
                        return name
                if 't' in self[tag]:
                    name = self[tag]['t']
                    if name:
                        return name
        return None

    def aliases(self) -> Optional[List[str]]:
        """
        Returns the name of the record from various fields.
        Searches fields 400 for the alias.
        """
        start = ''
        aliases = []
        for tag in self.get_fields('400'):
            if 'a' in tag:
                alias = tag['a']
                if alias:
                    if alias.endswith(','):
                        alias = alias[:-1]
                    # Pokud má alias čárku, otočit pořadí slov
                    if ',' in alias:
                        parts = alias.split(',', 1)
                        if len(parts) == 2 or len(parts) == 3 or len(parts) == 4:
                            alias = parts[1].strip() + ' ' + parts[0].strip()

                    aliases.append(alias)
            # if 't' in tag:
            #     alias = tag['t']
            #     if alias:
            #         # Pokud má alias čárku, otočit pořadí slov
            #         if ',' in alias:
            #             parts = alias.split(',', 1)
            #             if len(parts) == 2 or len(parts) == 3 or len(parts) == 4:
            #                 alias = parts[1].strip() + ' ' + parts[0].strip()
            #         aliases.append(alias)
        if (len(aliases) > 0):
            return aliases
        return None

    def aut(self) -> Optional[str]:
        """
        Returns the authority record identifier from field 001.
        """
        if '001' in self:
            return self['001'].data
        return None

    def birth_death(self) -> Optional[str]:
        """
        Returns the birth and death dates from field 100, subfield 'd'.
        """
        if '100' in self and 'd' in self['100']:
            return self['100']['d']
        return None

    def birth(self) -> Optional[str]:
        """
        Returns the birth date from field 046, subfield 'f'.
        """
        if '046' in self and 'f' in self['046']:
            return self['046']['f']
        return None

    def death(self) -> Optional[str]:
        """
        Returns the death date from field 046, subfield 'g'.
        """
        if '046' in self and 'g' in self['046']:
            return self['046']['g']
        return None

    def note(self) -> Optional[str]:
        """
        Returns the note from field 678, subfield 'a'.
        """
        if '678' in self and 'a' in self['678']:
            return self['678']['a']
        return None

    def wikidata024(self, type_of_link: str = 'wikidata') -> Optional[str]:
        """
        Returns the identifier from field 024 for a given type of link.
        """
        for field in self.get_fields('024'):
            if field['2'] == type_of_link:
                return field['a']
        return None

    def wikipedia856(self) -> Optional[Dict[str, str]]:
        """
        Parses field 856 to find a Wikipedia link and returns its components.
        """
        for field in self.get_fields('856'):
            if 'u' in field:
                match = re.search(r"https://([a-z]+)\.(wikipedia|wikisource)\.org/wiki/(.*)", field['u'], re.IGNORECASE)
                if match:
                    return {
                        'lang': match.group(1),
                        'project': match.group(2),
                        'article': match.group(3),
                        'link': field['u']
                    }
        return None

    def source670(self, type_of_source: str = 'wikidata') -> Optional[Dict[str, str]]:
        """
        Parses field 670 to find a source link and returns its components.
        """
        for field in self.get_fields('670'):
            if 'u' in field:
                if type_of_source == 'wikidata':
                    regex = r"https://([a-z]+)\.wikidata\.org/wiki/(.*)"
                else:
                    regex = r"https://([a-z]+)\.(wikipedia|wikisource)\.org/wiki/(.*)"

                match = re.search(regex, field['u'], re.IGNORECASE)
                if match:
                    groups = match.groups()
                    return {
                        'lang': groups[0] if type_of_source != 'wikidata' else None,
                        'project': 'wikidata' if type_of_source == 'wikidata' else groups[1],
                        'article': groups[1] if type_of_source == 'wikidata' else groups[2],
                        'link': field['u']
                    }
        return None

    def birth_date(self) -> Optional[datetime.datetime]:
        """
        Parses the birth date from the note field (678).
        """
        note = self.note()
        if not note:
            return None

        mapping = {' ledna': '.1.', ' února': '.2.', ' března': '.3.', ' dubna': '.4.',
                   ' května': '.5.', ' června': '.6.', ' července': '.7.', ' srpna': '.8.',
                   ' září': '.9.', ' října': '.10.', ' listopadu': '.11.', ' prosince': '.12.'}
        for k, v in mapping.items():
            note = note.replace(k, v)

        match = re.search(r"(?:Narozen|Narozena|narozen|narozena) (\d+)\.(\d+)\.(\d+)", note, re.IGNORECASE)
        if match:
            try:
                return datetime.datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            except ValueError:
                return None
        return None

    def death_date(self) -> Optional[datetime.datetime]:
        """
        Parses the death date from the note field (678).
        """
        note = self.note()
        if not note:
            return None

        mapping = {' ledna': '.1.', ' února': '.2.', ' března': '.3.', ' dubna': '.4.',
                   ' května': '.5.', ' června': '.6.', ' července': '.7.', ' srpna': '.8.',
                   ' září': '.9.', ' října': '.10.', ' listopadu': '.11.', ' prosince': '.12.'}
        for k, v in mapping.items():
            note = note.replace(k, v)

        match = re.search(r"(?:Zemřel|Zemřela|zemřel|zemřela) (\d+)\.(\d+)\.(\d+)", note, re.IGNORECASE)
        if match:
            try:
                return datetime.datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
            except ValueError:
                return None
        return None

    def first_name(self) -> Optional[str]:
        """
        Extracts the first name from field 100, subfield 'a'.
        """
        if '100' in self and 'a' in self['100']:
            name = self['100']['a']
            if ',' in name:
                return name.split(',')[1].strip()
        return None

    def last_name(self) -> Optional[str]:
        """
        Extracts the last name from field 100, subfield 'a'.
        """
        if '100' in self and 'a' in self['100']:
            name = self['100']['a']
            if ',' in name:
                return name.split(',')[0].strip()
        return None

    def status(self) -> Optional[str]:
        """
        Returns the status from field 950, subfield 'a'.
        """
        if '950' in self and 'a' in self['950']:
            return self['950']['a']
        return None

    def okres(self) -> Optional[str]:
        """
        Returns the district from field 751 or 151, subfield 'a'.
        """
        for tag in ['751', '151']:
            if tag in self and 'a' in self[tag]:
                return self[tag]['a']
        return None

    def mesto(self) -> Optional[str]:
        """
        Returns the city from field 751 or 151, subfield 'a'.
        """
        for tag in ['751', '151']:
            if tag in self and 'a' in self[tag]:
                return self[tag]['a']
        return None

    def gender(self) -> Optional[str]:
        """
        Returns the gender from field 375, subfield 'a'.
        Maps Czech gender terms to 'man' or 'woman'.
        """
        if '375' in self and 'a' in self['375']:
            gender = self['375']['a'].lower()
            if gender == 'muž':
                return 'man'
            elif gender == 'žena':
                return 'woman'
        return None

    def geographic_name_without_brackets(self) -> Optional[str]:
        """
        Returns the geographic name without brackets and 'Czechia'.
        """
        name = self.name()
        if name:
            return re.sub(r"[\(\[].*?[\)\]]", "", name).replace('Czechia', '').strip()
        return None

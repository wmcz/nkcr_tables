from datetime import datetime
import urllib.parse
from typing import List, Optional, Union

class quickstatements:
    """
    A class to generate QuickStatements commands for Wikidata.

    This class provides methods to construct various QuickStatements commands
    such as creating new items, setting labels, aliases, descriptions,
    dates (birth/death), NKCR authority IDs, gender, and human instance.
    """

    quickstatements_command: List[str] = []
    record: Optional[str] = None
    which_item: str = ""

    QUICKSTATEMENTS_LINK: str = 'https://tools.wmflabs.org/quickstatements/#v1='

    END_LINE: str = '||'
    SEPARATOR: str = '|'
    ENCLOSURE: str = '"'
    CREATE_DEFINE: str = 'CREATE'
    LAST_DEFINE: str = 'LAST'
    LABEL: str = 'L'
    ALIAS: str = 'A'
    DESCRIPTION: str = 'D'

    BIRTH: str = 'BIRTH'
    DEATH: str = 'DEATH'

    def reset(self) -> None:
        """
        Resets the list of QuickStatements commands.
        """
        self.quickstatements_command = []

    def add_command(self, command: str) -> None:
        """
        Adds a single QuickStatements command string to the list.

        Args:
            command: The QuickStatements command string.
        """
        self.quickstatements_command.append(command)

    def create(self) -> None:
        """
        Adds a 'CREATE' command to start a new item creation.
        """
        self.add_command(self.CREATE_DEFINE + self.END_LINE)

    def set_record(self, record: str) -> None:
        """
        Sets a record identifier. (Currently not directly used in command generation).

        Args:
            record: The record identifier.
        """
        self.record = record

    def set_item_to_add(self, which_item: str) -> None:
        """
        Sets the target item for subsequent commands.

        Args:
            which_item: The QID of the item (e.g., 'Q123', or 'LAST' for the last created item).
        """
        self.which_item = which_item

    def set_label(self, value: str, lang: str = 'cs') -> None:
        """
        Sets the label for the current item in a specified language.

        Args:
            value: The label string.
            lang: The language code (e.g., 'cs', 'en'). Defaults to 'cs'.
        """
        try:
            value = self.ENCLOSURE + value + self.ENCLOSURE
        except TypeError:
            value = ''
        self.add_command(self.which_item + self.SEPARATOR + self.LABEL + lang + self.SEPARATOR + value + self.END_LINE)

    def set_alias(self, value: str, lang: str = 'cs') -> None:
        """
        Sets an alias for the current item in a specified language.

        Args:
            value: The alias string.
            lang: The language code (e.g., 'cs', 'en'). Defaults to 'cs'.
        """
        value = self.ENCLOSURE + value + self.ENCLOSURE
        self.add_command(self.which_item + self.SEPARATOR + self.ALIAS + lang + self.SEPARATOR + value + self.END_LINE)

    def set_description(self, value: str, lang: str = 'cs') -> None:
        """
        Sets the description for the current item in a specified language.
        The description will be truncated to 250 characters if longer.

        Args:
            value: The description string.
            lang: The language code (e.g., 'cs', 'en'). Defaults to 'cs'.
        """
        try:
            if (len(value) > 250):
                value = value[0:250]
            value = self.ENCLOSURE + value + self.ENCLOSURE
        except TypeError:
            value = ''
        self.add_command(self.which_item + self.SEPARATOR + self.DESCRIPTION + lang + self.SEPARATOR + value + self.END_LINE)

    def get_link(self) -> str:
        """
        Generates the full QuickStatements URL with all added commands.

        Returns:
            The QuickStatements URL.
        """
        link = ''.join(self.quickstatements_command)
        return self.QUICKSTATEMENTS_LINK + urllib.parse.quote(link, safe="")

    def get_line(self) -> str:
        """
        Returns all accumulated QuickStatements commands as a single string.

        Returns:
            A string containing all QuickStatements commands.
        """
        line = ''.join(self.quickstatements_command)
        return line

    def set_date(self, nkcr_aut: str, birth_or_death: str, value: Optional[Union[int, datetime]]) -> None:
        """
        Sets a birth (P569) or death (P570) date for the current item.
        Includes references to NKCR authority and current timestamp.

        Args:
            nkcr_aut: The NKCR authority ID.
            birth_or_death: Specifies 'BIRTH' or 'DEATH'.
            value: The year (int) or a datetime object for the date.
        """
        if birth_or_death == self.BIRTH:
            prop = 'P569'
        elif birth_or_death == self.DEATH:
            prop = 'P570'
        else:
            return None

        if value is None:
            return None

        nkcr_aut_enclosed = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        now_dt_string = self.now_time()

        dt_string: str = ''
        if isinstance(value, int) and len(str(value)) == 4:
            precision = '9'  # Year precision
            try:
                dt = datetime(value, 1, 1)
                dt_string = dt.strftime(f"+%Y-%m-%dT%H:%M:%SZ/{precision}")
            except ValueError:
                dt_string = ''
        elif isinstance(value, datetime):
            precision = '11'  # Day precision
            try:
                dt_string = value.strftime(f"+%Y-%m-%dT%H:%M:%SZ/{precision}")
            except ValueError:
                dt_string = ''

        if dt_string:
            cmd = (
                f"{self.which_item}{self.SEPARATOR}{prop}{self.SEPARATOR}{dt_string}{self.SEPARATOR}"
                f"S248{self.SEPARATOR}Q13550863{self.SEPARATOR}S691{self.SEPARATOR}{nkcr_aut_enclosed}{self.SEPARATOR}"
                f"S813{self.SEPARATOR}{now_dt_string}{self.END_LINE}"
            )
            self.add_command(cmd)

    def now_time(self) -> str:
        """
        Generates a timestamp string in QuickStatements format for the current date.

        Returns:
            A string representing the current date and time in QuickStatements format.
        """
        now = datetime.now()
        dt_string = now.strftime("+%Y-%m-%dT00:00:00Z/11")
        return dt_string

    def set_nkcr(self, nkcr_aut: str, name_in_nkcr: str) -> None:
        """
        Sets the NKCR authority ID (P691) for the current item,
        including the name as it appears in NKCR (P1810) as a qualifier.
        Includes references to NKCR authority and current timestamp.

        Args:
            nkcr_aut: The NKCR authority ID.
            name_in_nkcr: The name string as it appears in NKCR.
        """
        nkcr_aut_enclosed = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        try:
            name_in_nkcr_enclosed = self.ENCLOSURE + name_in_nkcr + self.ENCLOSURE
        except TypeError:
            name_in_nkcr_enclosed = ''

        dt_string = self.now_time()
        cmd = (
            f"{self.which_item}{self.SEPARATOR}P691{self.SEPARATOR}{nkcr_aut_enclosed}{self.SEPARATOR}"
            f"P1810{self.SEPARATOR}{name_in_nkcr_enclosed}{self.SEPARATOR}"
            f"S248{self.SEPARATOR}Q13550863{self.SEPARATOR}S691{self.SEPARATOR}{nkcr_aut_enclosed}{self.SEPARATOR}"
            f"S813{self.SEPARATOR}{dt_string}{self.END_LINE}"
        )
        self.add_command(cmd)

    def set_gender(self, nkcr_aut: str, name_in_nkcr: str, gender: str) -> None:
        """
        Sets the gender (P21) for the current item.
        Includes references to NKCR authority and current timestamp.

        Args:
            nkcr_aut: The NKCR authority ID.
            name_in_nkcr: The name string as it appears in NKCR (used for reference, not directly in statement).
            gender: 'man' or 'woman'.
        """
        nkcr_aut_enclosed = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        try:
            # name_in_nkcr is not directly used in the command, but kept for consistency with other methods
            _ = self.ENCLOSURE + name_in_nkcr + self.ENCLOSURE
        except TypeError:
            _ = ''

        gender_qid: Optional[str] = None
        try:
            if gender == 'man':
                gender_qid = "Q6581097"  # male
            elif gender == 'woman':
                gender_qid = "Q6581072"  # female
        except TypeError:
            pass

        if gender_qid:
            dt_string = self.now_time()
            cmd = (
                f"{self.which_item}{self.SEPARATOR}P21{self.SEPARATOR}{gender_qid}{self.SEPARATOR}"
                f"S248{self.SEPARATOR}Q13550863{self.SEPARATOR}S691{self.SEPARATOR}{nkcr_aut_enclosed}{self.SEPARATOR}"
                f"S813{self.SEPARATOR}{dt_string}{self.END_LINE}"
            )
            self.add_command(cmd)

    def set_human(self, nkcr_aut: str, name_in_nkcr: str, human: bool) -> None:
        """
        Sets the instance of (P31) to human (Q5) for the current item.
        Includes references to NKCR authority and current timestamp.

        Args:
            nkcr_aut: The NKCR authority ID.
            name_in_nkcr: The name string as it appears in NKCR (used for reference, not directly in statement).
            human: Boolean, should be True to set as human.
        """
        nkcr_aut_enclosed = self.ENCLOSURE + nkcr_aut + self.ENCLOSURE
        try:
            # name_in_nkcr is not directly used in the command, but kept for consistency with other methods
            _ = self.ENCLOSURE + name_in_nkcr + self.ENCLOSURE
        except TypeError:
            _ = ''

        human_qid: Optional[str] = None
        try:
            if human:
                human_qid = 'Q5'  # human
        except TypeError:
            pass

        if human_qid:
            dt_string = self.now_time()
            cmd = (
                f"{self.which_item}{self.SEPARATOR}P31{self.SEPARATOR}{human_qid}{self.SEPARATOR}"
                f"S248{self.SEPARATOR}Q13550863{self.SEPARATOR}S691{self.SEPARATOR}{nkcr_aut_enclosed}{self.SEPARATOR}"
                f"S813{self.SEPARATOR}{dt_string}{self.END_LINE}"
            )
            self.add_command(cmd)
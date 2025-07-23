from jinja2 import Template
from typing import List


class WikiTable:
    """A class to generate a wikitext table."""

    template_text = '''
<div style="display: flex; justify-content: space-between;">
<div>[[Wikidata:WikiProject Czech Republic/New authorities/{{ previous_year }}/{{ previous_week }}|Předchozí]]</div>
<div>[[Wikidata:WikiProject Czech Republic/New authorities/{{ next_year }}/{{ next_week }}|Následující]]</div>
</div>
{{'{'}}| class="{{ class_name }}"
|+ {{ caption }}
|-
! {% for column in header_columns %} {% if loop.index > 1 %}!!{% endif %} {{ column }} {% endfor %}
{% for line in lines %}|-
| {% for col in line %}{% if loop.index > 1 %}||{% endif %} {{col}} {% endfor %}
{% endfor %}
|{{'}'}}
    '''

    def __init__(self, caption: str = '', class_name: str = 'wikitable sortable'):
        """
        Initializes the Wikitable object.

        :param caption: The caption of the table.
        :param class_name: The CSS class of the table.
        """
        self.caption: str = caption
        self.class_name: str = class_name
        self.header_columns: List[str] = []
        self.lines: List[List[str]] = []
        self.year: int
        self.week_num: int

    def set_caption(self, caption: str):
        """Sets the caption of the table."""
        self.caption = caption

    def set_week_num(self, week_num: int):
        self.week_num = week_num

    def set_year(self, year: int):
        self.year = year

    def set_class(self, class_name: str):
        """Sets the CSS class of the table."""
        self.class_name = class_name

    def add_header_column(self, col_name: str):
        """Adds a column to the table header."""
        self.header_columns.append(col_name)

    def add_line(self, line: List[str]):
        """Adds a line (row) to the table."""
        self.lines.append(line)

    def print_table(self):
        """Prints the table."""
        self.render()

    def render(self) -> str:
        """Renders the table to wikitext."""
        previous_year = self.year
        previous_week = self.week_num - 1
        if previous_week < 0:
            previous_week = 51
            previous_year -= 1

        next_year = self.year
        next_week = self.week_num + 1
        if next_week == 53:
            next_week = 0
            next_year += 1
            
        template = Template(self.template_text)
        return template.render(
            caption=self.caption,
            class_name=self.class_name,
            header_columns=self.header_columns,
            lines=self.lines,
            previous_year=previous_year,
            previous_week=previous_week,
            next_year=next_year,
            next_week=next_week
        )

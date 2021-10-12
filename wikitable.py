from jinja2 import Template

class wikitable:

    caption = ''
    class_name = 'wikitable'
    header_columns = []
    lines = []
    template_text = '''
{{'{'}}| class="{{ class_name }}"
|+ {{ caption }}
|-
! {% for column in header_columns %} {% if loop.index >= 1 %}!!{% endif %} {{ column }} {% endfor %}
{% for line in lines %}|-
| {% for col in line %}{% if loop.index >= 1 %}||{% endif %} {{col}} {% endfor %}
{% endfor %}
|{{'}'}}
    '''

    def set_caption(self, caption):
        self.caption = caption

    def set_class(self, class_name):
        self.class_name = class_name

    def add_header_column(self, col_name):
        self.header_columns.append(col_name)

    def add_line(self, line):
        self.lines.append(line)

    def print_table(self):
        template = Template(self.template_text)
        return template.render(caption=self.caption, class_name=self.class_name, header_columns=self.header_columns, lines=self.lines)

    def __init__(self):
        self.caption = ''
        self.class_name = 'wikitable'
        self.header_columns = []
        self.lines = []
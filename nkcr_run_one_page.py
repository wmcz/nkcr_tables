import create_nkcr_table
import nkcrlib

c = create_nkcr_table.create_table()
c.update_main_page = False

c.quick_lines = []
c.run(11, 2026)
c.table = []

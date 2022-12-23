#run every 10 minutes
import create_nkcr_table

c = create_nkcr_table.create_table()
c.run(quiet=True)
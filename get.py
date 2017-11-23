import sqlite3

db = sqlite3.connect("admin.db")
c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")

#eal_number = raw_input("Enter an EAL euipment number you want to retrieve: ",)

#c.execute('''SELECT equipment.eal_number, equipment_type, cal_comp, cal_date, cal_overview.created_at FROM equipment INNER JOIN cal_overview ON equipment.eal_number == cal_overview.eal_number''')

c.execute('''SELECT equipment.eal_number, equipment_type, serial_number cal_expiry, log_to FROM equipment INNER JOIN cal_overview ON equipment.eal_number == cal_overview.eal_number INNER JOIN log_overview ON equipment.eal_number == log_overview.eal_number''')





#c.execute("CREATE VIEW cal_overview AS SELECT t1.* FROM calibration t1 WHERE t1.cal_id = (SELECT t2.cal_id FROM calibration t2 WHERE t2.eal_number = t1.eal_number ORDER BY t2.cal_id DESC LIMIT 1)")

#c.execute("CREATE VIEW log_overview AS SELECT t1.* FROM logbook t1 WHERE t1.log_id = (SELECT t2.log_id FROM logbook t2 WHERE t2.eal_number = t1.eal_number ORDER BY t2.log_id DESC LIMIT 1)")

#c.execute("""SELECT eal_number FROM cal_overview""" )

#c.execute('SELECT * FROM calibration ')
#c.execute("SELECT eal_number, max(created_at) FROM calibration GROUP BY eal_number")

print(c.fetchall())

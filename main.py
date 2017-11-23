import sqlite3
from datetime import date, datetime

file = "admin.db"

db = sqlite3.connect(file, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

c = db.cursor()

c.execute("""PRAGMA foreign_keys = 1""")

c.execute('''CREATE TABLE IF NOT EXISTS equipment 
    (created_at timestamp NOT NULL,
    eal_number TEXT PRIMARY KEY NOT NULL UNIQUE,   
    equipment_type TEXT, 
    manufacturer TEXT, 
    model TEXT, 
    serial_number TEXT)''')

print("Table equipment opened")

c.execute('''CREATE TABLE IF NOT EXISTS logbook 
    (log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    eal_number TEXT,
    created_at timestamp NOT NULL,
    log_date DATE,
    log_from TEXT,
    log_to TEXT, 
    procedure TEXT,
    message TEXT,
    FOREIGN KEY(eal_number) REFERENCES equipment(eal_number))''')

print("Table logbook opened")

c.execute('''CREATE TABLE IF NOT EXISTS calibration 
    (cal_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    eal_number TEXT, 
    created_at timestamp NOT NULL, 
    cal_comp TEXT,
    cal_type TEXT,
    cal_date DATE,
    cal_recall DATE,
    cal_expiry DATE,
    cal_cert TEXT,
    FOREIGN KEY(eal_number) REFERENCES equipment(eal_number))''')

print ("Table calibration opened")

c.execute('''CREATE TABLE IF NOT EXISTS procedures
    (doc_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    created_at timestamp NOT NULL,
    date DATE,
    doc_ref TEXT,
    doc_issue INT,
    doc_name TEXT,  
    doc_reason TEXT,
    doc_path TEXT,
    equipment_used TEXT)''')

db.commit()

db.close()
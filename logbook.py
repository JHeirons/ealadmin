import sqlite3
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

db = sqlite3.connect("equipment.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")




def validate(date_text):
    try:
        datetime.strptime(date_text, '%d/%m/%Y')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def cal_date():
    select_cal_date = raw_input("Enter the date of calibration in dd/mm/yyyy format: ")
    validate(select_cal_date)
    cal_date = datetime.strptime(select_cal_date, "%d/%m/%Y").date()
    return cal_date


def cal_recall(cal_type, cal_date):
    if (cal_type == "internal"):
        cal_recall_date = cal_date + relativedelta(months=5)
        cal_recall = cal_recall_date
    elif(cal_type == "external"):
        cal_recall_date = cal_date + relativedelta(months=11)
        cal_recall = cal_recall_date
    else:
        print("Warning message")
    
    return cal_recall

def cal_expiry(cal_recall):
    cal_expiry = cal_recall + relativedelta(months=1)
    return cal_expiry



def log_entry():
    
    print ("Enter the following information about the equipment you want to update.")
    now = datetime.now()
    eal_number = raw_input("EAL Number: ")
    location = raw_input("Location: ")
    cal_typ = raw_input("Please type in either external or internal: ")

    cal_dat = cal_date()
    cal_recal = cal_recall(cal_typ, cal_dat)
    cal_expir = cal_expiry(cal_recal)
    print (cal_typ, cal_dat, cal_recal, cal_expir)
    cal_cert = raw_input("File path: ")
    message = raw_input("Enter message about this log update: ")
    

    
    c.execute("""INSERT INTO logbook (created_at,eal_number,location,cal_type,cal_date,cal_recall,cal_expiry,cal_cert,message) VALUES (?,?,?,?,?,?,?,?,?)""", (now, eal_number, location, cal_typ, cal_dat, cal_recal, cal_expir, cal_cert, message))
    
    db.commit()


while True:
    new_entry = raw_input("\nDo you want to update the log book of an equipment? (Y/N)")
    
    if new_entry == "Y":
        log_entry()
    
    elif new_entry == "N":
        print ("Closing Database")
        db.close()
        break
        

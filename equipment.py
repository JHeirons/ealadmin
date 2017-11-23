import sqlite3
import csv
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

db = sqlite3.connect("admin.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")

def equipment_entry():
    
    
    print ("Enter the following information about the equipment you want to add to the database.")
    now = datetime.now()
    with open ('equipment.csv', 'r') as f:
        data = csv.DictReader(f)
        to_db = [(now, i['EAL_Number'], i['Type'], i['Manufacturer'], i['Model'], i['Serial_Number']) for i in data]
    
    c.executemany("INSERT INTO equipment (created_at, eal_number, equipment_type, manufacturer, model, serial_number) VALUES (?,?,?,?,?,?);", (to_db))
    
    db.commit()

def calibration_entry():
    
    
    print ("Enter the following information about the calibration you want to add to the database.")
    now = datetime.now()
    
    def cal_date(date):
        select_cal_date = date
        cal_date = datetime.strptime(select_cal_date, "%d/%m/%Y").date()
        return cal_date


    def cal_recall(cal_type, cal_date):
        if (cal_type == "internal"):
            cal_recall_date = cal_date+relativedelta(months=5)
            cal_recall = cal_recall_date
        elif(cal_type == "external"):
            cal_recall_date = cal_date+relativedelta(months=11)
            cal_recall = cal_recall_date
        else:
            print("Warning message")

        return cal_recall

    def cal_expiry(cal_recall):
        cal_expiry = cal_recall+relativedelta(months=1)
        return cal_expiry

    with open ('calibration.csv', 'r') as f:
        data = csv.DictReader(f)
        for i in data:
            cali_date = cal_date(i['Calibration_Date'])
            cali_recall_d = cal_recall(i['Calibration_Type'], cali_date)
            cali_expiry_d = cal_expiry(cali_recall_d)

            to_db = (now, i['EAL_Number'], i['Calibration_Type'], cali_date, cali_recall_d, cali_expiry_d, i["Company"], i["Certificate"])
            c.execute("INSERT INTO calibration (created_at, eal_number, cal_type, cal_date, cal_recall, cal_expiry, cal_comp, cal_cert) VALUES (?,?,?,?,?,?,?,?);", (to_db))
    print (to_db)
    
    

    db.commit()

def log_entry():


    print ("Enter the following information about the equipment you want to add to the database.")
    now = datetime.now()

    def log_date(date):
        select_cal_date = date
        cal_date = datetime.strptime(select_cal_date, "%d/%m/%Y").date()
        return cal_date
    
    with open ('calibration.csv', 'r') as f:
        data = csv.DictReader(f)
        for i in data:
            log_date = log_date(i['Log_Date'])
            to_db = (now, i['EAL_Number'], log_date, i['Location_From'], i['Location_To'], i['Procedure'], i['Message'])

            c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (to_db))


    db.commit()
    
def procedure_entry():
    
    
    print ("Enter the following information about the equipment you want to add to the database.")
    now = datetime.now()
    with open ('Master.csv', 'r') as f:
        data = csv.DictReader(f)
        to_db = [(now, i['Date'], i['Ref'], i['Issue'], i['Name'], i['Reason']) for i in data]
    
    c.executemany("INSERT INTO procedures (created_at, date, doc_ref, doc_issue, doc_name, doc_reason) VALUES (?,?,?,?,?,?);", (to_db))
    
    db.commit()

while True:
    new_entry = raw_input("\nDo you want to add a new piece of equipment to the database? (Y/N)")
    
    if new_entry == "Y":
        equipment_entry()
    
    elif new_entry == "N":
        print ("Closing Database")
        db.close()
        break


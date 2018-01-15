import mysql.connector
import numpy as np
from datetime import date
from GUI_Widgets import Confirm

class Store:
    def __init__(self, dbConfig):
        self.dbConfig = dbConfig
        
    def get(self, query):
        conn = mysql.connector.connect(**self.dbConfig)
        curr = conn.cursor()
        curr.execute(query) 
        items = curr.fetchall()
        curr.close()
        conn.close()
        return items
    
    def build(self, s, items):
        store = s
        store.clear()
        for item in items:
            row = list(item)
            for i in range(len(row)):
                if isinstance(row[i], date) == True:
                    row[i] = row[i].strftime("%d/%m/%Y")
            store.append(row)
    
    def compare(self, current, new):
        x = np.array(current)
        y = np.array(new)
        z = np.array_equal(x, y)
        return z

class Queries:
    def __init__(self, dbConfig):
        self.equipment = {"insert" : "INSERT INTO equipment (created_at, eal_number, equipment_type, manufacturer, model, pressure, serial_number) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                          "update" : "UPDATE equipment SET created_at = %s WHERE eal_number = %s",
                          "select" : "SELECT eal_number, equipment_type, manufacturer, model, pressure, serial_number FROM equipment"}
        
        self.calibration = {"insert" : "INSERT INTO calibration (eal_number, created_at, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                          "select" : "SELECT eal_number, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert FROM calibration"}
        
        self.logbook = {"insert" : "INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);",
                          "select" : "SELECT eal_number, log_date, log_location, log_procedure, message FROM logbook ORDER BY eal_number"}
        
        self.cleanliness = {"insert" : "INSERT INTO clean (eal_number, created_at, pco_number, dew_number, procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                          "select" : "SELECT eal_number, pco_number, dew_number, clean_procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate FROM clean"}
        
        self.proof = {"insert" : "INSERT INTO proof (eal_number, created_at, proof_pressure, proof_duration, pt_number, procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                          "update" : "UPDATE equipment SET equipment_type = %s WHERE eal_number = %s;",
                          "select" : "SELECT eal_number, proof_pressure, proof_duration, pt_number, proof_procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate FROM proof"}
        
        self.overview = {"select" : "SELECT equipment.eal_number, equipment_type, serial_number, cal_expiry, log_location FROM equipment INNER JOIN cal_overview ON equipment.eal_number = cal_overview.eal_number INNER JOIN log_overview ON equipment.eal_number = log_overview.eal_number"}
        
        self.documents = {"insert" : "INSERT INTO procedures (doc_name, doc_ref, doc_client, doc_issue, doc_reason, date, doc_path) VALUES (%s,%s,%s,%s,%s,%s, %s);",
                          "select" : "SELECT doc_name, doc_ref, doc_client, doc_issue, doc_reason, date, doc_path FROM procedures"}
        
        self.completion = {"select" : "to_do"}
        self.conn = mysql.connector.connect(**dbConfig)
    
    def query(self, query, values):
        curr = self.conn.cursor()
        curr.execute(query, values)
        self.conn.commit()
        curr.close()
        
    def log_query(self, query, values):
        curr = self.conn.cursor()
        curr.execute(query, values)
        self.conn.commit()
        curr.close()
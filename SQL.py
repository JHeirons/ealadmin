import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
import mysql.connector
import numpy as np
from datetime import date

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
        return store
    
    def item(self, s, items, equiptype):
        store = s
        for item in items:
            row = list(item)
            
            if row[1] == equiptype:
                x = [row[0]]
                store.append(x)
    
    def compare(self, current, new):
        x = np.array(current)
        y = np.array(new)
        z = np.array_equal(x, y)
        return z

class Queries:
    def __init__(self, dbConfig):
        self.equipment = {"insert" : "INSERT INTO equipment (created_at, eal_number, equipment_type, manufacturer, model, pressure, serial_number) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                          "update" : "UPDATE equipment SET created_at=%s, equipment_type=%s, manufacturer=%s, model=%s, pressure=%s, serial_number=%s WHERE eal_number = %s",
                          "select" : "SELECT eal_number, equipment_type, manufacturer, model, pressure, serial_number FROM equipment"}
        
        self.calibration = {"insert" : "INSERT INTO calibration (created_at, eal_number, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                            "update" : "UPDATE calibration SET created_at=%s, cal_comp=%s, cal_type=%s, cal_date=%s, cal_recall=%s, cal_expiry=%s, cal_cert=%s WHERE eal_number = %s",
                            "select" : "SELECT eal_number, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert FROM calibration"}
        
        self.logbook = {"insert" : "INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);",
                          "select" : "SELECT eal_number, log_date, log_location, log_procedure, message FROM logbook ORDER BY eal_number"}
        
        self.cleanliness = {"insert" : "INSERT INTO clean (created_at, eal_number, pco_number, dew_number, clean_procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                            "update" : "UPDATE clean SET created_at=%s, pco_number=%s, dew_number=%s, clean_procedure=%s, clean_date=%s, clean_recall=%s, clean_expiry=%s, clean_location=%s, clean_result=%s, clean_certificate=%s WHERE eal_number = %s",
                            "select" : "SELECT eal_number, pco_number, dew_number, clean_procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate FROM clean"}
        
        self.proof = {"insert" : "INSERT INTO proof (created_at, eal_number, proof_pressure, proof_duration, pt_number, proof_procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                          "update" : "UPDATE proof SET created_at=%s, proof_pressure=%s, proof_duration=%s, pt_number=%s, proof_procedure=%s, proof_date=%s, proof_recall=%s, proof_expiry=%s, proof_location=%s, proof_result=%s, proof_certificate=%s WHERE eal_number = %s",
                          "select" : "SELECT eal_number, proof_pressure, proof_duration, pt_number, proof_procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate FROM proof"}
        
        self.overview = {"select" : "SELECT e.eal_number, e.model, e.serial_number, c.cal_expiry, p.proof_expiry, cd.clean_expiry, l.log_location FROM equipment e INNER JOIN log_overview l ON e.eal_number = l.eal_number LEFT JOIN calibration c ON e.eal_number = c.eal_number LEFT JOIN proof p ON e.eal_number = p.eal_number LEFT JOIN clean cd ON e.eal_number = cd.eal_number WHERE c.cal_expiry or p.proof_expiry and cd.clean_expiry is NOT NULL"}
        
        
        self.documents = {"insert" : "INSERT INTO procedures (created_at, doc_client, doc_ref, doc_name, doc_issue, doc_reason, date, doc_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);",
                          "update" : "UPDATE procedures SET created_at=%s, doc_client=%s, doc_name=%s, doc_issue=%s, doc_reason=%s, date=%s, doc_path=%s WHERE doc_ref = %s",
                          "select" : "SELECT doc_client, doc_ref, doc_name, doc_issue, doc_reason, date, doc_path FROM procedures"}
        
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
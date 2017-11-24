import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sqlite3

db = sqlite3.connect("admin.db")
#db = sqlite3.connect("http://ealserver/Jonathan Folder/admin.db")
c = db.cursor()

class Store():
    def __init__(self):
        self.equipment = self.Equipment()
        self.calibration = self.Calibration()
        self.logbook = self.Logbook()
        self.procedures = self.Procedures()
        self.cleanliness = self.Cleanliness()
        self.proof = self.Proof()
        
    def Equipment(self):
        equipment_store = Gtk.ListStore(str, str, str, str, str, str)
        items = c.execute('SELECT eal_number, equipment_type, manufacturer, model, pressure, serial_number FROM equipment') 
        for item in items:
            equipment_store.append(list(item))
        return equipment_store
    
    def Calibration(self):
        calibration_store = Gtk.ListStore(str, str, str, str, str, str, str)
        items = c.execute('SELECT eal_number, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert FROM calibration') 
        for item in items:
            calibration_store.append(list(item))
        return calibration_store
    
    def Logbook(self):
        log_store = Gtk.ListStore(str, str, str, str, str, str)
        items = c.execute('SELECT eal_number, log_date, log_from, log_to, procedure, message FROM logbook ORDER BY eal_number') 
        for item in items:
            log_store.append(list(item))
        return log_store
    
    def Procedures(self):
        procedure_store = Gtk.ListStore(str)
        items = c.execute('SELECT doc_ref FROM procedures') 
        for item in items:
            procedure_store.append(list(item))
        return procedure_store
    
    def Cleanliness(self):
        cleanliness_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str)
        items = c.execute('SELECT eal_number, pco_number, dew_number, procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate FROM clean') 
        for item in items:
            cleanliness_store.append(list(item))
        return cleanliness_store
    
    def Proof(self):
        proof_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str)
        items = c.execute('SELECT eal_number, proof_pressure, proof_duration, pt_number, procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate FROM proof') 
        for item in items:
            proof_store.append(list(item))
        return proof_store
    
    def Overview(self):
        overview_store = Gtk.ListStore(str, str, str, str, str)
        items = c.execute('''SELECT equipment.eal_number, equipment_type, serial_number, cal_expiry, log_to FROM equipment INNER JOIN cal_overview ON equipment.eal_number == cal_overview.eal_number INNER JOIN log_overview ON equipment.eal_number == log_overview.eal_number''')
        
        for item in item:
            overview_store.append(list(item))
        return overview_store
    
    def Completion(self, field, table):
        completion_store = Gtk.ListStore(str)
        query = 'SELECT DISTINCT ' + field + ' FROM '+ table
        items = c.execute(query) 
        for item in items:
            completion_store.append(list(item))
        return completion_store




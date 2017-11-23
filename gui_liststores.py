import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sqlite3

db = sqlite3.connect("admin.db")
#db = sqlite3.connect("http://ealserver/Jonathan Folder/admin.db")
c = db.cursor()


class EquipmentStore:
    def __init__(self):
        self.full_equipment_store = self.FullEquipmentStore()
        self.type_equipment_store = self.TypeEquipmentStore()
        self.manufacturer_equipment_store = self.ManufacturerEquipmentStore()
        self.model_equipment_store = self.ModelEquipmentStore()
        
    def FullEquipmentStore(self):
        full_equipment_store = Gtk.ListStore(str, str, str, str, str, str)
        full_store = c.execute('SELECT eal_number, equipment_type, manufacturer, model, pressure, serial_number FROM equipment') 
        for item in full_store:
            full_equipment_store.append(list(item))
        return full_equipment_store
    
    def TypeEquipmentStore(self):
        type_equipment_store = Gtk.ListStore(str)
        type_store = c.execute('SELECT DISTINCT equipment_type FROM equipment ') 
        for item in type_store:
            type_equipment_store.append(list(item))
        return type_equipment_store
    
    def ManufacturerEquipmentStore(self):
        manufacturer_equipment_store = Gtk.ListStore(str)
        manufacturer_store = c.execute('SELECT DISTINCT manufacturer FROM equipment ') 
        for item in manufacturer_store:
            manufacturer_equipment_store.append(list(item))
        return manufacturer_equipment_store
    
    def ModelEquipmentStore(self):
        model_equipment_store = Gtk.ListStore(str)
        model_store = c.execute('SELECT DISTINCT model FROM equipment ') 
        for item in model_store:
            model_equipment_store.append(list(item))
        return model_equipment_store

class CalibrationStore:
    def __init__(self):
        self.full_calibration_store = self.FullCalibrationStore()
        self.company_calibration_store = self.CompanyCalibrationStore()
        
    def FullCalibrationStore(self):
        full_calibration_store = Gtk.ListStore(str, str, str, str, str, str, str)
        full_store = c.execute('SELECT eal_number, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert FROM calibration') 
        for item in full_store:
            full_calibration_store.append(list(item))
        return full_calibration_store
    
    def CompanyCalibrationStore(self):
        company_calibration_store = Gtk.ListStore(str)
        company_store = c.execute('SELECT DISTINCT cal_comp FROM calibration ') 
        for item in company_store:
            company_calibration_store.append(list(item))
        return company_calibration_store
    
class OverviewStore:
    def __init__(self):
        self.overview_store = self.OverviewStore()
        
    def OverviewStore(self):
        overview_store = Gtk.ListStore(str, str, str, str, str)
        store = c.execute('''SELECT equipment.eal_number, equipment_type, serial_number, cal_expiry, log_to FROM equipment INNER JOIN cal_overview ON equipment.eal_number == cal_overview.eal_number INNER JOIN log_overview ON equipment.eal_number == log_overview.eal_number''')
        
        for item in store:
            overview_store.append(list(item))
        return overview_store

class LogStore:
    def __init__(self):
        self.full_log_store = self.FullLogStore()
        
    def FullLogStore(self):
        full_log_store = Gtk.ListStore(str, str, str, str, str, str)
        full_store = c.execute('SELECT eal_number, log_date, log_from, log_to, procedure, message FROM logbook ORDER BY eal_number') 
        for item in full_store:
            full_log_store.append(list(item))
        return full_log_store
    
    
class ProcedureStore:
    def __init__(self):
        self.procedure_store = self.ProcedureStore()
        
    def ProcedureStore(self):
        procedure_store = Gtk.ListStore(str)
        store = c.execute('SELECT doc_ref FROM procedures') 
        for item in store:
            procedure_store.append(list(item))
        return procedure_store
    
class ProofStore:
    def __init__(self):
        self.full_proof_store = self.FullProofStore()
        
        
    def FullProofStore(self):
        full_proof_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str)
        full_store = c.execute('SELECT eal_number, proof_pressure, proof_duration, pt_number, procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate FROM proof') 
        for item in full_store:
            full_proof_store.append(list(item))
        return full_proof_store

class CleanlinessStore:
    def __init__(self):
        self.full_clean_store = self.FullCleanStore()
        
        
    def FullCleanStore(self):
        full_clean_store = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str)
        full_store = c.execute('SELECT eal_number, pco_number, dew_number, procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate FROM clean') 
        for item in full_store:
            full_clean_store.append(list(item))
        return full_clean_store
    
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_liststores import ProofStore, EquipmentStore, ProcedureStore
from datetime import date, datetime, timedelta
from gui_functions import Function
import sqlite3
import shutil
import os

db = sqlite3.connect("admin.db")
c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")

class EquipmentProofPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_proof.glade")
        self.builder.connect_signals(self)
        self.go = self.builder.get_object
        self.page = self.go("equipment_proof_page")
        self.proof_scroll = self.go("equipment_proof_scroll_window")
        
        self.store = ProofStore()
        self.equipment_store = EquipmentStore()
        self.procedure_store = ProcedureStore()
        
        self.current_proof_filter = None
        
        self.proof_filter = self.store.full_proof_store.filter_new()
        self.proof_filter.set_visible_func(self.proof_filter_func)
    
        self.proof_treeview = Gtk.TreeView.new_with_model(self.proof_filter)
        self.proof_scroll.add(self.proof_treeview)
        
        self.entries = {"eal_number":"equipment_proof_entry_eal", "proof_pressure":"equipment_proof_entry_bar", "proof_duration":"equipment_proof_entry_duration", "pt_number":"equipment_proof_entry_pt", "procedure":"equipment_proof_entry_procedure", "proof_location":"equipment_proof_entry_location"}
        
        
        self.type = "Pass"
        
        for i, column_title in enumerate(["EAL Number", "Test Pressure", "Test Duration", "Transducer Number", "Procedure", "Proof Date", "Proof Recall", "Proof Expiry", "Test Location", "Result", "Proof Certificate"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            
            self.proof_treeview.append_column(self.column)
        
        self.select = self.proof_treeview.get_selection()
        self.select.connect("changed", self.on_equipment_proof_tree_selection_changed)
        self.completions()
    
        
    def completions(self):
        Function.entry_completion(self, self.equipment_store.full_equipment_store, "equipment_proof_entry_eal", 0)
        Function.entry_completion(self, self.procedure_store.procedure_store, "equipment_proof_entry_procedure", 0)
        #Function.entry_completion(self, self.store.company_calibration_store, "equipment_calibration_entry_company", 0)
        
    
    def treeview_refresh(self):
        self.store.full_proof_store.clear()
        self.store = ProofStore()
        self.proof_treeview.set_model(model=self.store.full_proof_store)
        self.completions()
        print("Refresh")
        
    def date(self):
        calendar = self.go("equipment_proof_calendar_date")
        get_date = calendar.get_date()
        month = get_date.month + 1
        date = str(get_date.day) + '/' + str(month) + '/' + str(get_date.year)
        select_cal_date = date
        proof_date = datetime.strptime(select_cal_date, "%d/%m/%Y").date()
        return proof_date

    def recall(self, proof_date):
        proof_recall_date = proof_date+timedelta(days=323)
        proof_recall = proof_recall_date
        return proof_recall

    def expiry(self, proof_recall):
        proof_expiry = proof_recall+timedelta(days=42)
        return proof_expiry
    
    def on_equipment_proof_tree_selection_changed(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        selected = []
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.eal_number = model.get_value(tree_iter,0)
            selected.append(self.eal_number)
            
            self.proof_pressure = model.get_value(tree_iter,1)
            selected.append(self.proof_pressure)
            
            self.proof_duration = model.get_value(tree_iter,2)
            selected.append(self.proof_duration)
            
            self.pt_number = model.get_value(tree_iter,3)
            selected.append(self.pt_number)
            
            self.procedure = model.get_value(tree_iter,4)
            selected.append(self.procedure)
            
            self.proof_date = model.get_value(tree_iter,5)
            self.proof_recall = model.get_value(tree_iter,6)
            self.proof_expiry = model.get_value(tree_iter,7)
            
            self.proof_location = model.get_value(tree_iter,8)
            selected.append(self.proof_location)
            
            self.proof_result = model.get_value(tree_iter,9)
            
            self.proof_certificate = model.get_value(tree_iter,10)
            selected.append(self.proof_certificate)
            
            Function.set_entries(self, self.entries, selected)
        
        
    
    def on_equipment_proof_radio_pass_toggled(self, equipment_proof_radio_pass):
        self.type = "Pass"
    
    def on_equipment_proof_radio_fail_toggled(self, equipment_proof_radio_fail):
        self.type = "Fail"
    
    def on_equipment_proof_button_enter_clicked(self, equipment_proof_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        result_type = self.type
        proof_date = self.date()
        proof_recall = self.recall(proof_date)
        proof_expiry = self.expiry(proof_recall)
        
        if not os.path.exists('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"]):
            os.mkdir('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"])
            
        certificate_location = '/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"] + '/' + text["eal_number"] + '_Proof_Cert-' + str(proof_date) + '.pdf'
        shutil.copy(self.file, certificate_location)
        proof_certificate = certificate_location
        now = datetime.now()
        
       # print (text["eal_number"], text["calibration_company"], calibration_type, calibration_certificate, calibration_date, calibration_recall, calibration_expiry)
        
        proof_message = "Proof certificate added."
        
        c.execute("INSERT INTO proof (eal_number, created_at, proof_pressure, proof_duration, pt_number, procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);", (text["eal_number"], now, text["proof_pressure"], text["proof_duration"], text["pt_number"], text["procedure"], proof_date, proof_recall, proof_expiry, text["proof_location"], result_type, proof_certificate))
        
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, text['eal_number'], now, text["proof_location"], text["proof_location"], text["procedure"], proof_message))
    
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
    
    def on_equipment_proof_button_clear_clicked(self, equipment_proof_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_proof_filter = None
        print ("Clear")
        
    def on_equipment_proof_file_certificate_file_set(self, equipment_proof_file_certificate):
        print ("Test")
        self.file = equipment_proof_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_proof_entry_eal_changed(self, equipment_proof_entry_eal):
        search = equipment_proof_entry_eal.get_text()
        self.current_proof_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_proof_filter)
        self.proof_filter.refilter()
        
    def proof_filter_func(self, model, iter, data):
        if self.current_proof_filter is None or self.current_proof_filter == "":
            return True
        elif self.current_proof_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
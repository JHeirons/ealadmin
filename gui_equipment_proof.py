import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from store import Store
from datetime import date, datetime, timedelta
from gui_functions import Function, Cal_Date, Db
import shutil
import os
import mysql.connector

conn = Db.conn()

class EquipmentProofPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_proof.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("equipment_proof_page")
        self.scroll = self.builder.get_object("equipment_proof_scroll_window")
        
        self.store = Store()
        
        self.current_filter = None
        
        self.filter = self.store.proof.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        self.entries = {"eal_number":"equipment_proof_entry_eal", "proof_pressure":"equipment_proof_entry_bar", "proof_duration":"equipment_proof_entry_duration", "pt_number":"equipment_proof_entry_pt", "procedure":"equipment_proof_entry_procedure", "proof_location":"equipment_proof_entry_location"}
        
        
        self.type = "Pass"
        
        for i, column_title in enumerate(["EAL Number", "Test Pressure", "Test Duration", "Transducer Number", "Procedure", "Proof Date", "Proof Recall", "Proof Expiry", "Test Location", "Result", "Proof Certificate"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            
            self.treeview.append_column(self.column)
        
        self.select = self.treeview.get_selection()
        self.select.connect("changed", self.on_equipment_proof_tree_selection_changed)
        self.completions()
    
        
    def completions(self):
        Function.entry_completion(self, self.store.equipment, "equipment_proof_entry_eal", 0)
        Function.entry_completion(self, self.store.procedures, "equipment_proof_entry_procedure", 0)
        #Function.entry_completion(self, self.store.company_calibration_store, "equipment_calibration_entry_company", 0)
        
    
    def treeview_refresh(self):
        self.store.proof.clear()
        self.store = Store()
        self.treeview.set_model(model=self.store.proof)
        self.completions()
        print("Refresh")
        
   
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
        proof_date = Cal_Date.date(self, "equipment_proof_calendar_date")
        proof_recall = Cal_Date.expiry(self, calibration_date, 12)
        proof_expiry = Cal_Date.recall(self, calibration_expiry)
        
        if not os.path.exists('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"]):
            os.mkdir('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"])
            
        certificate_location = '/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"] + '/' + text["eal_number"] + '_Proof_Cert-' + str(proof_date) + '.pdf'
        shutil.copy(self.file, certificate_location)
        proof_certificate = certificate_location
        now = datetime.now()
        
       # print (text["eal_number"], text["calibration_company"], calibration_type, calibration_certificate, calibration_date, calibration_recall, calibration_expiry)
        
        proof_message = "Proof certificate added."
        curr = conn.cursor()
        
        proof_query = ("INSERT INTO proof (eal_number, created_at, proof_pressure, proof_duration, pt_number, procedure, proof_date, proof_recall, proof_expiry, proof_location, proof_result, proof_certificate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);") 
        proof_values = (text["eal_number"], now, text["proof_pressure"], text["proof_duration"], text["pt_number"], text["procedure"], proof_date, proof_recall, proof_expiry, text["proof_location"], result_type, proof_certificate)
        
        curr.execute(proof_query, proof_values)
    
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, text['eal_number'], log_date, text["proof_location"], text["procedure"], proof_message)
        
        curr.execute(log_query, log_values)
    
        conn.commit()
        curr.close()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
    
    def on_equipment_proof_button_clear_clicked(self, equipment_proof_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_proof_file_certificate_file_set(self, equipment_proof_file_certificate):
        print ("Test")
        self.file = equipment_proof_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_proof_entry_eal_changed(self, equipment_proof_entry_eal):
        search = equipment_proof_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from store import Store
from datetime import date, datetime, timedelta
from gui_functions import Function, Cal_Date
import sqlite3
import shutil
import os

db = sqlite3.connect("admin.db")
c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")

class EquipmentCleanlinessPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_cleanliness.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("equipment_cleanliness_page")
        self.scroll = self.builder.get_object("equipment_cleanliness_scroll_window")
        self.store = Store()
        
        self.current_filter = None
        
        self.filter = self.store.cleanliness.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        self.entries = {"eal_number":"equipment_cleanliness_entry_eal", "pco_number":"equipment_cleanliness_entry_pco", "dew_number":"equipment_cleanliness_entry_dew", "procedure":"equipment_cleanliness_entry_procedure", "clean_location":"equipment_cleanliness_entry_location"}
        
        
        self.type = "Pass"
        
        for i, column_title in enumerate(["EAL Number", "Particle Counter Number", "Dew Point Meter", "Procedure", "Cleanliness & Dryness Date", "Cleanliness & Dryness Recall", "Cleanliness & Dryness Expiry", "Test Location", "Result", "Proof Certificate"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            
            self.treeview.append_column(self.column)
        
        self.select = self.treeview.get_selection()
        self.select.connect("changed", self.on_equipment_clean_tree_selection_changed)
        self.completions()
    
        
    def completions(self):
        Function.entry_completion(self, self.store.cleanliness, "equipment_cleanliness_entry_eal", 0)
        #procedure, dew and pco completions

    
    def treeview_refresh(self):
        self.store.cleanliness.clear()
        self.store = Store()
        self.treeview.set_model(model=self.store.cleanliness)
        self.completions()
        print("Refresh")
        
    
    def on_equipment_clean_tree_selection_changed(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        selected = []
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.eal_number = model.get_value(tree_iter,0)
            selected.append(self.eal_number)
            
            self.clean_pressure = model.get_value(tree_iter,1)
            selected.append(self.clean_pressure)
            
            self.clean_duration = model.get_value(tree_iter,2)
            selected.append(self.clean_duration)
            
            self.procedure = model.get_value(tree_iter,3)
            selected.append(self.procedure)
            
            self.proof_date = model.get_value(tree_iter,4)
            self.proof_recall = model.get_value(tree_iter,5)
            self.proof_expiry = model.get_value(tree_iter,6)
            
            self.proof_location = model.get_value(tree_iter,7)
            selected.append(self.proof_location)
            
            self.proof_result = model.get_value(tree_iter,8)
            
            self.proof_certificate = model.get_value(tree_iter,9)
            selected.append(self.proof_certificate)
            
            Function.set_entries(self, self.entries, selected)
        
        
    
    def on_equipment_cleanliness_radio_pass_toggled(self, equipment_cleanliness_radio_pass):
        self.type = "Pass"
    
    def on_equipment_cleanliness_radio_fail_toggled(self, equipment_cleanliness_radio_fail):
        self.type = "Fail"
    
    def on_equipment_cleanliness_button_enter_clicked(self, equipment_cleanliness_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        result_type = self.type
        clean_date = Cal_Date.date(self, "equipment_cleanliness_calendar_date")
        clean_expiry = Cal_Date.expiry(self, calibration_date, length)
        clean_recall = Cal_Date.recall(self, calibration_expiry)
        
        print(clean_date, clean_expiry, clean_recall)
        
        if not os.path.exists('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"]):
            os.mkdir('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"])
            
        certificate_location = '/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"] + '/' + text["eal_number"] + '_Clean_and_Dry_Cert-' + str(clean_date) + '.pdf'
        shutil.copy(self.file, certificate_location)
        clean_certificate = certificate_location
        now = datetime.now()
        
       # print (text["eal_number"], text["calibration_company"], calibration_type, calibration_certificate, calibration_date, calibration_recall, calibration_expiry)
        
        clean_message = "Cleanliness & Dryness certificate added."
        
        c.execute("INSERT INTO clean (eal_number, created_at, pco_number, dew_number, procedure, clean_date, clean_recall, clean_expiry, clean_location, clean_result, clean_certificate) VALUES (?,?,?,?,?,?,?,?,?,?,?);", (text["eal_number"], now, text["pco_number"], text["dew_number"], text["procedure"], clean_date, clean_recall, clean_expiry, text["clean_location"], result_type, clean_certificate))
        
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, text['eal_number'], now, text["clean_location"], text["clean_location"], text["procedure"], clean_message))
    
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
    
    def on_equipment_cleanliness_button_clear_clicked(self, equipment_cleanliness_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_cleanliness_file_certificate_file_set(self, equipment_cleanliness_file_certificate):
        print ("Test")
        self.file = equipment_cleanliness_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_cleanliness_entry_eal_changed(self, equipment_cleanliness_entry_eal):
        search = equipment_cleanliness_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
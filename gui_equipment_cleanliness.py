import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_liststores import CleanlinessStore, ProcedureStore, EquipmentStore
from datetime import date, datetime, timedelta
from gui_functions import Function
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
        self.go = self.builder.get_object
        self.page = self.go("equipment_cleanliness_page")
        self.clean_scroll = self.go("equipment_cleanliness_scroll_window")
        
        self.store = CleanlinessStore()
        self.equipment_store = EquipmentStore()
        self.procedure_store = ProcedureStore()
        
        self.current_cleanliness_filter = None
        
        self.clean_filter = self.store.full_clean_store.filter_new()
        self.clean_filter.set_visible_func(self.clean_filter_func)
    
        self.clean_treeview = Gtk.TreeView.new_with_model(self.clean_filter)
        self.clean_scroll.add(self.clean_treeview)
        
        self.entries = {"eal_number":"equipment_cleanliness_entry_eal", "pco_number":"equipment_cleanliness_entry_pco", "dew_number":"equipment_cleanliness_entry_dew", "procedure":"equipment_cleanliness_entry_procedure", "clean_location":"equipment_cleanliness_entry_location"}
        
        
        self.type = "Pass"
        
        for i, column_title in enumerate(["EAL Number", "Particle Counter Number", "Dew Point Meter", "Procedure", "Cleanliness & Dryness Date", "Cleanliness & Dryness Recall", "Cleanliness & Dryness Expiry", "Test Location", "Result", "Proof Certificate"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            
            self.clean_treeview.append_column(self.column)
        
        self.select = self.clean_treeview.get_selection()
        self.select.connect("changed", self.on_equipment_clean_tree_selection_changed)
        self.completions()
    
        
    def completions(self):
        Function.entry_completion(self, self.equipment_store.full_equipment_store, "equipment_cleanliness_entry_eal", 0)
        #Function.entry_completion(self, self.procedure_store.procedure_store, "equipment_clanliness_entry_procedure", 0)
        #Function.entry_completion(self, self.store.company_calibration_store, "equipment_calibration_entry_company", 0)
        
    
    def treeview_refresh(self):
        self.store.full_clean_store.clear()
        self.store = CleanlinessStore()
        self.clean_treeview.set_model(model=self.store.full_clean_store)
        self.completions()
        print("Refresh")
        
    def date(self):
        calendar = self.go("equipment_cleanliness_calendar_date")
        get_date = calendar.get_date()
        month = get_date.month + 1
        date = str(get_date.day) + '/' + str(month) + '/' + str(get_date.year)
        select_cal_date = date
        clean_date = datetime.strptime(select_cal_date, "%d/%m/%Y").date()
        return clean_date

    def recall(self, clean_date):
        clean_recall_date = clean_date+timedelta(days=323)
        clean_recall = clean_recall_date
        return clean_recall

    def expiry(self, clean_recall):
        clean_expiry = clean_recall+timedelta(days=42)
        return clean_expiry
    
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
        clean_date = self.date()
        clean_recall = self.recall(clean_date)
        clean_expiry = self.expiry(clean_recall)
        
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
        self.current_cleanliness_filter = None
        print ("Clear")
        
    def on_equipment_cleanliness_file_certificate_file_set(self, equipment_cleanliness_file_certificate):
        print ("Test")
        self.file = equipment_cleanliness_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_cleanliness_entry_eal_changed(self, equipment_cleanliness_entry_eal):
        search = equipment_cleanliness_entry_eal.get_text()
        self.current_cleanliness_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_cleanliness_filter)
        self.cleanliness_filter.refilter()
        
    def clean_filter_func(self, model, iter, data):
        if self.current_cleanliness_filter is None or self.current_cleanliness_filter == "":
            return True
        elif self.current_cleanliness_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
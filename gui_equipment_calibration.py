import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from store import Store
from datetime import date, datetime, timedelta
from gui_functions import Function, Cal_Date, Db
import mysql.connector
import shutil
import os



class EquipmentCalibrationPage:
    def __init__(self, conn):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_calibration.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("equipment_calibration_page")
        self.scroll = self.builder.get_object("equipment_calibration_scroll_window")
        self.store = Store.Calibration(self, conn)
        self.conn = conn
        self.current_filter = None
        
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        self.entries = {"eal_number":"equipment_calibration_entry_eal", "calibration_company":"equipment_calibration_entry_company"}
        
        self.type = "External"
        
        for i, column_title in enumerate(["EAL Number", "Calibration Company", "Calibration Type", "Calibration Date", "Calibration Recall", "Calibration Expiry", "Calibration Certificate"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            
            self.treeview.append_column(self.column)
        
        self.select = self.treeview.get_selection()
        self.select.connect("changed", self.on_equipment_calibration_tree_selection_changed)
        self.completions()
        
    def completions(self):
        Function.entry_completion(self, self.store, "equipment_calibration_entry_eal", 0)
        self.store_company = Store.Completion(self, self.conn, "cal_comp", "calibration")
        Function.entry_completion(self, self.store_company, "equipment_calibration_entry_company", 0)
    
    def treeview_refresh(self):
        self.store.clear()
        self.store = Store.Calibration(self, self.conn)
        self.treeview.set_model(model=self.store)
        self.completions()
        print("Refresh")
    
    def on_equipment_calibration_tree_selection_changed(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        self.selected = []
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.eal_number = model.get_value(tree_iter,0)
            self.selected.append(self.eal_number)
            self.calibration_company = model.get_value(tree_iter,1)
            self.selected.append(self.calibration_company)
            self.calibration_type = model.get_value(tree_iter,2)
            self.calibration_date = model.get_value(tree_iter,3)
            self.calibration_recall = model.get_value(tree_iter,4)
            self.calibration_expiry = model.get_value(tree_iter,5)
            self.calibration_certificate = model.get_value(tree_iter,6)
            self.selected.append(self.calibration_certificate)
            Function.set_entries(self, self.entries, self.selected)
        
    def on_equipment_calibration_radio_external_toggled(self, equipment_calibration_radio_external):
        self.type = "External"
    
    def on_equipment_calibration_radio_internal_toggled(self, equipment_calibration_radio_internal):
        self.type = "Internal"
    
    def on_equipment_calibration_button_enter_clicked(self, equipment_calibration_button_enter):
        curr = self.conn.cursor()
        
        entries = self.entries
        text = Function.get_entries(self, entries)
        calibration_type = self.type
        if (calibration_type == "External"):
            length = 12
        elif (calibration_type == "Internal"):
            length = 6
        else:
            length = 12
            
        print(length)
        
        calibration_date = Cal_Date.date(self, "equipment_calibration_calendar_date")
        print(calibration_date)
        calibration_expiry = Cal_Date.expiry(self, calibration_date, length)
        print(calibration_expiry)
        calibration_recall = Cal_Date.recall(self, calibration_expiry)
        print(calibration_recall)
        
        print(calibration_date, calibration_expiry, calibration_recall)
        
        folder_path = '//EALSERVER/Jonathan Folder/Admin_Test/'
        if not os.path.exists(folder_path + text["eal_number"]):
            os.mkdir(folder_path + text["eal_number"])
            
        certificate_location = folder_path + text["eal_number"] + '/' + text["eal_number"] + '_Cal_Cert-' + str(calibration_date) + '.pdf'
        shutil.copy(self.file, certificate_location)
        calibration_certificate = certificate_location
        now = datetime.now()
        
        print (text["eal_number"], text["calibration_company"], calibration_type, calibration_certificate, calibration_date, calibration_recall, calibration_expiry)
        
        message = "Calibration certificate added."
        location = "Westcott"
        procedure = "N/A"
        
        cal_query = ("INSERT INTO calibration (eal_number, created_at, cal_comp, cal_type, cal_date, cal_recall, cal_expiry, cal_cert) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);") 
        cal_values = (text["eal_number"], now, text["calibration_company"], calibration_type, calibration_date, calibration_recall, calibration_expiry, calibration_certificate)
        curr.execute(cal_query, cal_values)
        
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, text['eal_number'], now, location, procedure, message)
        
        curr.execute(log_query, log_values)
        self.conn.commit()
        
        
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
        curr.close()
    
    def on_equipment_calibration_button_clear_clicked(self, equipment_calibration_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_calibration_file_certificate_file_set(self, equipment_calibration_file_certificate):
        print ("Test")
        self.file = equipment_calibration_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_calibration_entry_eal_changed(self, equipment_calibration_entry_eal):
        search = equipment_calibration_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
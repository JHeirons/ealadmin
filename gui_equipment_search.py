import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from time import sleep
from gui_liststores import OverviewStore
import sqlite3
import csv 

db = sqlite3.connect("admin.db")
c = db.cursor()


class EquipmentSearchPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_search.glade")
        self.builder.connect_signals(self)
        self.go = self.builder.get_object
        self.page = self.go("equipment_search_page")
        self.store = OverviewStore()
        self.treeview = self.go("equipment_search_tree_view")
        #self.current_filter = None
        #self.filter = self.store.overview_store.filter_new()
        #self.filter.set_visible_func(self.filter_func)
        
        self.treeview.set_model(model=self.store.overview_store)
        #self.treeview = self.get_treeview.new_with_model(self.language_filter)
        
        for i, column_title in enumerate(["EAL Number", "Equipment Type", "Serial Number", "Calibration Expiry", "Current Location"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.column.set_sort_column_id(i)
            self.treeview.append_column(self.column)
        
    
        
    def test(self):
        print("test")
        
    
    
    def on_equipment_search_button_export_clicked(self, equipment_search_button_export):
        with open('overview.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for row in c.execute('''SELECT equipment.eal_number, equipment_type, serial_number, cal_expiry, log_to FROM equipment INNER JOIN cal_overview ON equipment.eal_number == cal_overview.eal_number INNER JOIN log_overview ON equipment.eal_number == log_overview.eal_number'''):
                data = ",".join([str(i) for i in row])
                print(data)
                writer.writerow(data)
        
    def treeview_refresh(self):
        
        self.store.overview_store.clear()
        self.store = OverviewStore()
        self.treeview.set_model(model=self.store.overview_store)
        
        #self.completions()
        print("Refresh")
    
    def on_equipment_search_tree_selection_changed(self, equipment_search_tree_selection):
        (model, pathlist) = equipment_search_tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.eal_number = model.get_value(tree_iter,0)
            
            print(self.eal_number)
    
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "None":
            return True
        else:
            entry_to_get = self.go("entry")
            entry_text = entry_to_get.get_text()
            return model[iter][2] == self.current_filter_language
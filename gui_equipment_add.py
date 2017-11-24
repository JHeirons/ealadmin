import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
from gui_liststores import EquipmentStore
from gui_functions import Function
import sqlite3

db = sqlite3.connect("admin.db")
#db = sqlite3.connect("http://ealserver/Jonathan Folder/admin.db")
c = db.cursor()


class EquipmentAddPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_add.glade")
        self.builder.connect_signals(self)
        self.go = self.builder.get_object
        self.page = self.go("equipment_add_page")
        self.scroll = self.go("equipment_add_scroll_window")
        self.store = EquipmentStore()
        
        self.current_filter = None
        
        self.filter = self.store.full_equipment_store.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        self.entries = {"eal_number":"equipment_add_entry_eal", "equipment_type":"equipment_add_entry_type", "manufacturer":"equipment_add_entry_manufacturer", "model":"equipment_add_entry_model", "pressure":"equipment_add_entry_pressure", "serial_number":"equipment_add_entry_serial"}
        
        column_headings = ["EAL Number", "Equipment Type", "Manufacturer", "Model", "Pressure", "Serial Number"]
        for i, column_title in enumerate(column_headings):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(self.column)
        
        self.select = self.treeview.get_selection()
        self.select.connect("changed", self.on_equipment_add_tree_selection_changed)
        
        self.completions()  
        
            
    def treeview_refresh(self):
        self.store.full_equipment_store.clear()
        self.store = EquipmentStore()
        self.treeview.set_model(model=self.store.full_equipment_store)
        self.completions()
        
        print("Refresh")
        
    def completions(self):
        Function.entry_completion(self, self.store.full_equipment_store, "equipment_add_entry_eal", 0)
        Function.entry_completion(self, self.store.type_equipment_store, "equipment_add_entry_type", 0)
        Function.entry_completion(self, self.store.manufacturer_equipment_store, "equipment_add_entry_manufacturer", 0)
        Function.entry_completion(self, self.store.model_equipment_store, "equipment_add_entry_model", 0)
    
    def on_equipment_add_tree_selection_changed(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        self.selected = {}
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.selected['eal_number'] = model.get_value(tree_iter,0)
            self.selected['equipment_type'] = model.get_value(tree_iter,1)
            self.selected['manufacturer'] = model.get_value(tree_iter,2)
            self.selected['model'] = model.get_value(tree_iter,3)
            self.selected['pressure'] = model.get_value(tree_iter,4)
            self.selected['serial_number'] = model.get_value(tree_iter,5)
            selected_values = list(self.selected.values())
            Function.set_entries(self, self.entries, selected_values)
        
    def on_equipment_add_button_add_clicked(self, equipment_add_button_add):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        
        print (entered_text['eal_number'], entered_text["equipment_type"], entered_text["manufacturer"], entered_text["model"], entered_text["serial_number"])
        now = datetime.now()
        
        c.execute("INSERT INTO equipment (created_at, eal_number, equipment_type, manufacturer, model, pressure, serial_number) VALUES (?,?,?,?,?,?,?);", (now, entered_text['eal_number'], entered_text["equipment_type"], entered_text["manufacturer"], entered_text["model"], entered_text["pressure"], entered_text["serial_number"]))
        
        location = 'Westcott'
        procedure = 'N/A'
        calibration_message = entered_text['eal_number'] + ' added to equipment store'
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, entered_text['eal_number'], now, location, location, procedure, calibration_message))
    
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
        
    def on_equipment_add_button_remove_clicked(self, equipment_add_button_remove):
        
        c.execute("DELETE FROM equipment WHERE eal_number = ?", (self.selected["eal_number"],))
        
        now = datetime.now()
        location = 'Westcott'
        procedure = 'N/A'
        calibration_message = self.eal_number + ' removed from equipment store'
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, self.selected["eal_number"], now, location, location, procedure, calibration_message))
        
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Remove")
        
        
    def on_equipment_add_button_update_clicked(self, equipment_add_button_update):
        
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        now = datetime.now()
        
        c.execute("UPDATE equipment SET created_at = ? WHERE eal_number = ?", (now, entered_text['eal_number'],))
        c.execute("UPDATE equipment SET equipment_type = ? WHERE eal_number = ?", (entered_text['equipment_type'], entered_text['eal_number'],))
        c.execute("UPDATE equipment SET manufacturer = ? WHERE eal_number = ?", (entered_text['manufacturer'], entered_text['eal_number'],))
        c.execute("UPDATE equipment SET model = ? WHERE eal_number = ?", (entered_text['model'], entered_text['eal_number'],))
        c.execute("UPDATE equipment SET pressure = ? WHERE eal_number = ?", (entered_text['pressure'], entered_text['eal_number'],))
        c.execute("UPDATE equipment SET serial_number = ? WHERE eal_number = ?", (entered_text['serial_number'], entered_text['eal_number'],))
        
        location = 'Westcott'
        procedure = 'N/A'
        calibration_message = entered_text['eal_number'] + ' updated info'
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, entered_text['eal_number'], now, location, location, procedure, calibration_message))
    
        db.commit()
        Function.clear_entries(self, entries)
        self.treeview_refresh()
    
    def on_equipment_add_button_clear_clicked(self, equipment_add_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_add_filter = None
        
        print ("Clear")
    
    def on_equipment_add_entry_eal_changed(self, equipment_add_entry_eal):
        search = equipment_add_entry_eal.get_text() 
        self.current_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_filter)
        self.filter.refilter()
        
    def on_equipment_add_entry_type_changed(self, equipment_add_entry_type):
        search = equipment_add_entry_type.get_text()
        self.current_filter = search 
        self.current_filter_column = 1
        print(self.current_filter)
        self.filter.refilter()
        
    def on_equipment_add_entry_manufacturer_changed(self, equipment_add_entry_manufacturer):
        search = equipment_add_entry_manufacturer.get_text()
        self.current_filter = search 
        self.current_filter_column = 2
        print(self.current_filter)
        self.filter.refilter()
    
    def on_equipment_add_entry_model_changed(self, equipment_add_entry_model):
        search = equipment_add_entry_model.get_text()
        self.current_filter = search
        self.current_filter_column = 3
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
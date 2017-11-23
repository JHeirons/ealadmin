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
        self.add_scroll = self.go("equipment_add_scroll_window")
        self.store = EquipmentStore()
        
        self.current_add_filter = None
        
        self.add_filter = self.store.full_equipment_store.filter_new()
        self.add_filter.set_visible_func(self.add_filter_func)
    
        self.add_treeview = Gtk.TreeView.new_with_model(self.add_filter)
        self.add_scroll.add(self.add_treeview)
        
        self.entries = {"EAL Number":"equipment_add_entry_eal", "Equipment Type":"equipment_add_entry_type", "Manufacturer":"equipment_add_entry_manufacturer", "Model":"equipment_add_entry_model", "Pressure":"equipment_add_entry_pressure", "Serial Number":"equipment_add_entry_serial"}
        
        
        for i, column_title in enumerate(["EAL Number", "Equipment Type", "Manufacturer", "Model", "Pressure", "Serial Number"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.add_treeview.append_column(self.column)
        
        self.select = self.add_treeview.get_selection()
        self.select.connect("changed", self.on_equipment_add_tree_selection_changed)
        
        self.completions()  
        
            
    def treeview_refresh(self):
        self.store.full_equipment_store.clear()
        self.store = EquipmentStore()
        self.add_treeview.set_model(model=self.store.full_equipment_store)
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
            self.eal_number = model.get_value(tree_iter,0)
            self.selected['EAL Number'] = self.eal_number
            self.equip_type = model.get_value(tree_iter,1)
            self.selected['Equipment Type'] = self.equip_type
            self.manufacturer = model.get_value(tree_iter,2)
            self.selected['Manufacturer'] = self.manufacturer
            self.model = model.get_value(tree_iter,3)
            self.selected['Model'] = self.model
            self.pressure = model.get_value(tree_iter,4)
            self.selected['Pressure'] = self.pressure
            self.serial_number = model.get_value(tree_iter,5)
            self.selected['Serial Number'] = self.serial_number
            selected_values = list(self.selected.values())
            Function.set_entries(self, self.entries, selected_values)
        
    def on_equipment_add_button_add_clicked(self, equipment_add_button_add):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        
        #context_id = self.status_bar.get_context_id("Added")
        status = "Added: {eal_number} - {equip_type}, {manu}, {model}, {serial}".format(eal_number = entered_text['EAL Number'], equip_type = entered_text["Equipment Type"], manu = entered_text["Manufacturer"], model = entered_text["Model"], serial = entered_text["Serial Number"])
        
        #Function.push_item(self, status, context_id)
        
        print (entered_text['EAL Number'], entered_text["Equipment Type"], entered_text["Manufacturer"], entered_text["Model"], entered_text["Serial Number"])
        now = datetime.now()
        
        c.execute("INSERT INTO equipment (created_at, eal_number, equipment_type, manufacturer, model, pressure, serial_number) VALUES (?,?,?,?,?,?,?);", (now, entered_text['EAL Number'], entered_text["Equipment Type"], entered_text["Manufacturer"], entered_text["Model"], entered_text["Pressure"], entered_text["Serial Number"]))
        
        location = 'Westcott'
        procedure = 'N/A'
        calibration_message = entered_text['EAL Number'] + ' added to equipment store'
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, entered_text['EAL Number'], now, location, location, procedure, calibration_message))
    
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
        
    def on_equipment_add_button_remove_clicked(self, equipment_add_button_remove):
        entries = self.entries
        
        context_id = self.status_bar.get_context_id("Delete")
        status = "Deleted: {eal_number}".format(eal_number = self.eal_number)
        #Function.push_item(self, status, context_id)
        
        c.execute("DELETE FROM equipment WHERE eal_number = ?", (self.eal_number,))
        
        now = datetime.now()
        location = 'Westcott'
        procedure = 'N/A'
        calibration_message = self.eal_number + ' removed from equipment store'
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, self.eal_number, now, location, location, procedure, calibration_message))
        
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Remove")
        
        
    def on_equipment_add_button_update_clicked(self, equipment_add_button_update):
        
        entries = self.entries
        text = Function.get_entries(self, entries)
        print (text)
        now = datetime.now()
        
        context_id = self.status_bar.get_context_id("Update")
        
        new_list = list(text.values())
        old_list = list(self.selected.values())
        
        changed = [a for a in new_list + old_list if (a not in new_list) or (a not in old_list)]
        print (changed)
        status = "Updated: {eal_number} - ".format(eal_number = text['EAL Number'])
        for key in text:
            for item in changed:
                if text[key] == item:
                    name = str(key)
                    value = str(text[key])
                    status = status + name + ' with ' + value + ', '
                    
        
        status = status[:-2]
        
        #Function.push_item(self, status, context_id)
        
        c.execute("UPDATE equipment SET created_at = ? WHERE eal_number = ?", (now, text['EAL Number'],))
        c.execute("UPDATE equipment SET equipment_type = ? WHERE eal_number = ?", (text['Equipment Type'], text['EAL Number'],))
        c.execute("UPDATE equipment SET manufacturer = ? WHERE eal_number = ?", (text['Manufacturer'], text['EAL Number'],))
        c.execute("UPDATE equipment SET model = ? WHERE eal_number = ?", (text['Model'], text['EAL Number'],))
        c.execute("UPDATE equipment SET pressure = ? WHERE eal_number = ?", (text['Pressure'], text['EAL Number'],))
        c.execute("UPDATE equipment SET serial_number = ? WHERE eal_number = ?", (text['Serial Number'], text['EAL Number'],))
        
        location = 'Westcott'
        procedure = 'N/A'
        calibration_message = text['EAL Number'] + ' updated info'
        
        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, text['EAL Number'], now, location, location, procedure, calibration_message))
    
        db.commit()
        Function.clear_entries(self, entries)
        self.treeview_refresh()
        
    def test(self):
        print("testing")
    
    def on_equipment_add_button_clear_clicked(self, equipment_add_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_add_filter = None
        
        print ("Clear")
    
    def on_equipment_add_entry_eal_changed(self, equipment_add_entry_eal):
        search = equipment_add_entry_eal.get_text() 
        self.current_add_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_add_filter)
        self.add_filter.refilter()
        
    def on_equipment_add_entry_type_changed(self, equipment_add_entry_type):
        search = equipment_add_entry_type.get_text()
        self.current_add_filter = search 
        self.current_filter_column = 1
        print(self.current_add_filter)
        self.add_filter.refilter()
        
    def on_equipment_add_entry_manufacturer_changed(self, equipment_add_entry_manufacturer):
        search = equipment_add_entry_manufacturer.get_text()
        self.current_add_filter = search 
        self.current_filter_column = 2
        print(self.current_add_filter)
        self.add_filter.refilter()
    
    def on_equipment_add_entry_model_changed(self, equipment_add_entry_model):
        search = equipment_add_entry_model.get_text()
        self.current_add_filter = search
        self.current_filter_column = 3
        print(self.current_add_filter)
        self.add_filter.refilter()
        
    def add_filter_func(self, model, iter, data):
        if self.current_add_filter is None or self.current_add_filter == "":
            return True
        elif self.current_add_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
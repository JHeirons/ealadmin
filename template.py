import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
import Store
import mysql_con


class <PageName>:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/<page>.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("<page id>")
        self.scroll = self.builder.get_object("<page scrollwindow>")
        self.store = Store()
        
        self.current_filter = None
        
        self.filter = self.store.<store>.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        self.entries = {<page entries>}
        
        
        for i, column_title in enumerate([treeview column headers]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(self.column)
        
        self.select = self.treeview.get_selection()
        self.select.connect("changed", self.on_equipment_add_tree_selection_changed)
        
        self.completions()  
        
    def treeview_refresh(self):
        self.store.<store>.clear()
        self.store = Store()
        self.treeview.set_model(model=self.store.<store>)
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
        self.current_filter = None
        
        print ("Clear")
    
    def on_equipment_add_entry_eal_changed(self, equipment_add_entry_eal):
        search = equipment_add_entry_eal.get_text() 
        self.current_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_filter)
        self.filter.refilter()
        
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
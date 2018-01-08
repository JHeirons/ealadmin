import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
from gui_functions import Function, Db
from store import Store
import mysql.connector

class EquipmentAddPage():
    def __init__(self, conn):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_add.glade")
        self.builder.connect_signals(self)
        self.go = self.builder.get_object
        self.page = self.go("equipment_add_page")
        self.scroll = self.go("equipment_add_scroll_window")
        self.conn = conn
        self.store = Store.Equipment(self, conn)
        
        self.current_filter = None
        
        self.filter = self.store.filter_new()
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
        self.store.clear()
        self.store = Store.Equipment(self, self.conn)
        self.treeview.set_model(model=self.store)
        self.completions()
        
        print("Refresh")
        
    def completions(self):
        Function.entry_completion(self, self.store, "equipment_add_entry_eal", 0)
        
        self.store_type = Store.Completion(self, self.conn, "equipment_type", "equipment")
        Function.entry_completion(self, self.store_type, "equipment_add_entry_type", 0)
        
        self.store_manufacturer = Store.Completion(self, self.conn, "manufacturer", "equipment")
        Function.entry_completion(self, self.store_manufacturer, "equipment_add_entry_manufacturer", 0)
        
        self.store_model = Store.Completion(self, self.conn, "model", "equipment")
        Function.entry_completion(self, self.store_model, "equipment_add_entry_model", 0)
    
    def on_equipment_add_tree_selection_changed(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        self.selected = {}
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.selected['eal_number'] = model.get_value(tree_iter,0)
            self.selected['equipment_type'] = model.get_value(tree_iter,1)
            self.selected['manufacturer'] = model.get_value(tree_iter,2)
            self.selected['model'] = model.get_value(tree_iter,3)
            self.selected['pressure'] = str(model.get_value(tree_iter,4))
            self.selected['serial_number'] = model.get_value(tree_iter,5)
            selected_values = list(self.selected.values())
            Function.set_entries(self, self.entries, selected_values)
        
    def on_equipment_add_button_add_clicked(self, equipment_add_button_add):
        curr = self.conn.cursor()
        
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        
        print (entered_text['eal_number'], entered_text["equipment_type"], entered_text["manufacturer"], entered_text["model"], entered_text["serial_number"])
        now = datetime.now()
        
        equip_query = ("INSERT INTO equipment (created_at, eal_number, equipment_type, manufacturer, model, pressure, serial_number) VALUES (%s,%s,%s,%s,%s,%s,%s);")
        equip_values = (now, entered_text['eal_number'], entered_text["equipment_type"], entered_text["manufacturer"], entered_text["model"], entered_text["pressure"], entered_text["serial_number"])
        
        curr.execute(equip_query, equip_values)
        
        location = 'Westcott'
        procedure = 'N/A'
        message = entered_text['eal_number'] + ' added to equipment store'
        
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, entered_text['eal_number'], now, location, procedure, message)
        
        curr.execute(log_query, log_values)
        self.conn.commit()
        curr.close()
        
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Add")
        
    def on_equipment_add_button_remove_clicked(self, equipment_add_button_remove):
        curr = self.conn.cursor()
        
        del_query = ("DELETE FROM equipment WHERE eal_number = %s") 
        del_values = (self.selected["eal_number"],)
        
        curr.execute(del_query, del_values)
        
        now = datetime.now()
        location = 'Westcott'
        procedure = 'N/A'
        message = self.eal_number + ' removed from equipment store'
        
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, entered_text['eal_number'], now, location, procedure, message)
        
        curr.execute(log_query, log_values)
        self.conn.commit()
        curr.close()
        
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print ("Remove")
        
        
    def on_equipment_add_button_update_clicked(self, equipment_add_button_update):
        curr = self.conn.cursor()
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        now = datetime.now()
        
        update1 = ("UPDATE equipment SET created_at = %s WHERE eal_number = %s") 
        values1 = (now, entered_text['eal_number'],)
        update2 = ("UPDATE equipment SET equipment_type = %s WHERE eal_number = %s") 
        values2 = (entered_text['equipment_type'], entered_text['eal_number'],)
        update3 = ("UPDATE equipment SET manufacturer = %s WHERE eal_number = %s") 
        values3 = (entered_text['manufacturer'], entered_text['eal_number'],)
        update4 = ("UPDATE equipment SET model = %s WHERE eal_number = %s") 
        values4 =(entered_text['model'], entered_text['eal_number'],)
        update5 = ("UPDATE equipment SET pressure = %s WHERE eal_number = %s") 
        values5 =(entered_text['pressure'], entered_text['eal_number'],)
        update6 = ("UPDATE equipment SET serial_number = %s WHERE eal_number = %s") 
        values6 = (entered_text['serial_number'], entered_text['eal_number'],)
        
        curr.execute(update1, values1)
        curr.execute(update2, values2)
        curr.execute(update3, values3)
        curr.execute(update4, values4)
        curr.execute(update5, values5)
        curr.execute(update6, values6)
        
        location = 'Westcott'
        procedure = 'N/A'
        message = entered_text['eal_number'] + ' updated info'
        
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, entered_text['eal_number'], now, location, procedure, message)
        
        curr.execute(log_query, log_values)
        self.conn.commit()
        curr.close()
        
        Function.clear_entries(self, entries)
        self.treeview_refresh()
    
    def on_equipment_add_button_clear_clicked(self, equipment_add_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        self.select.unselect_all()
        self.current_add_filter = None
        
        print ("Clear")
    
    def on_equipment_add_entry_eal_changed(self, entry):
        search = entry.get_text() 
        self.current_filter = search.upper()
        self.current_filter_column = 0
        print(self.current_filter_column)
        print(self.current_filter)
        self.filter.refilter()
        
    def on_equipment_add_entry_type_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search 
        self.current_filter_column = 1
        print(self.current_filter_column)
        print(self.current_filter)
        self.filter.refilter()
        
    def on_equipment_add_entry_manufacturer_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search 
        self.current_filter_column = 2
        print(self.current_filter_column)
        print(self.current_filter)
        self.filter.refilter()
    
    def on_equipment_add_entry_model_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search
        self.current_filter_column = 3
        print(self.current_filter_column)
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
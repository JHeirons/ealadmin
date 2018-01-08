import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
from store import Store
from gui_functions import Function, Cal_Date, Db
import mysql.connector

class EquipmentLogPage:
    def __init__(self, conn):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_log.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("equipment_log_page")
        self.scroll = self.builder.get_object("equipment_log_scroll_window")
        self.conn = conn
        self.store = Store.Logbook(self, conn)
        
        self.entries = {"eal_number":"equipment_log_entry_eal", "log_location":"equipment_log_entry_from", "procedure":"equipment_log_entry_procedure", "message":"equipment_log_entry_message"}
        
        
        self.current_filter = None
        
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        
        for i, column_title in enumerate(["EAL Number", "Log Date", "Location", "Procedure", "Message"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(self.column)
        
        select = self.treeview.get_selection()
        select.connect("changed", self.on_equipment_log_tree_selection_changed)
        
        Function.entry_completion(self, Store.Equipment(self, self.conn), "equipment_log_entry_eal", 0)
        Function.entry_completion(self, Store.Procedures(self, self.conn), "equipment_log_entry_procedure", 0)
        
    def on_equipment_log_button_enter_clicked(self, equipment_log_button_enter):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        log_date = Cal_Date.date(self, "equipment_log_calendar_date")
        now = datetime.now()
        curr = self.conn.cursor()
    
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, entered_text['eal_number'], log_date, entered_text["log_from"], entered_text["procedure"], entered_text["message"])
        
        curr.execute(log_query, log_values)
    
        self.conn.commit()
        curr.close()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        
    def on_equipment_log_button_clear_clicked(self, equipment_log_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        print("Clear")
        
    
    def on_equipment_log_tree_selection_changed(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        self.selected = {}
        for path in pathlist :
            tree_iter = model.get_iter(path)
            self.eal_number = model.get_value(tree_iter,0)
            self.selected['EAL Number'] = self.eal_number
            self.log_date = model.get_value(tree_iter,1)
            self.selected['Log Date'] = self.log_date
            self.going_from = model.get_value(tree_iter,2)
            self.selected['Location'] = self.going_from
            self.procedure = model.get_value(tree_iter,3)
            self.selected['Procedure'] = self.procedure
            self.message = model.get_value(tree_iter,4)
            self.selected['Message'] = self.message
            selected_values = list(self.selected.values())
            Function.set_entries(self, self.entries, selected_values)
            
    
    def treeview_refresh(self):
        self.store.clear()
        self.store = Store.Logbook(self, self.conn)
        self.treeview.set_model(model=self.store)
        #self.completions()
        print("Refresh")
    
    def on_equipment_log_entry_eal_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        self.current_column = 0
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_column]:
            return model[iter][self.current_column]
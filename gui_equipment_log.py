import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
from store import Store
from gui_functions import Function, Cal_Date, Db
import mysql.connector

conn = Db.conn()


class EquipmentLogPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_log.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("equipment_log_page")
        self.scroll = self.builder.get_object("equipment_log_scroll_window")
        
        self.store = Store()
        
        self.entries = {"eal_number":"equipment_log_entry_eal", "log_from":"equipment_log_entry_from", "log_to":"equipment_log_entry_to", "procedure":"equipment_log_entry_procedure", "message":"equipment_log_entry_message"}
        
        
        self.current_filter = None
        
        self.filter = self.store.logbook.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        
        for i, column_title in enumerate(["EAL Number", "Log Date", "Location", "Procedure", "Message"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(self.column)
        
        select = self.treeview.get_selection()
        select.connect("changed", self.on_equipment_log_tree_selection_changed)
        
        Function.entry_completion(self, self.store.equipment, "equipment_log_entry_eal", 0)
        Function.entry_completion(self, self.store.procedures, "equipment_log_entry_procedure", 0)
        
    def on_equipment_log_button_enter_clicked(self, equipment_log_button_enter):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        log_date = Cal_Date.date(self, "equipment_log_calendar_date")
        now = datetime.now()
        curr = conn.cursor()
    
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, entered_text['eal_number'], log_date, entered_text["log_from"], entered_text["procedure"], entered_text["message"])
        
        curr.execute(log_query, log_values)
    
        conn.commit()
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
            self.going_from = model.get_value(tree_iter,2)
            self.selected['Going From'] = self.going_from
            self.going_to = model.get_value(tree_iter,3)
            self.selected['Going To'] = self.going_to
            self.procedure = model.get_value(tree_iter,4)
            self.selected['Procedure'] = self.procedure
            self.message = model.get_value(tree_iter,5)
            self.selected['Message'] = self.message
            selected_values = list(self.selected.values())
            Function.set_entries(self, self.entries, selected_values)
            
    
    def treeview_refresh(self):
        self.store.logbook.clear()
        self.store = Store()
        self.treeview.set_model(model=self.store.logbook)
        #self.completions()
        print("Refresh")
    
    def on_equipment_log_entry_eal_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][0]:
            return model[iter][0]
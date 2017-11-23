import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
from gui_liststores import LogStore, EquipmentStore, ProcedureStore
from gui_functions import Function
import sqlite3

db = sqlite3.connect("admin.db")
c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")


class EquipmentLogPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/equipment_log.glade")
        self.builder.connect_signals(self)
        self.go = self.builder.get_object
        self.page = self.go("equipment_log_page")
        self.log_scroll = self.go("equipment_log_scroll_window")
        self.store = LogStore()
        self.equipment = EquipmentStore()
        self.procedure = ProcedureStore()
        
        self.entries = {"eal_number":"equipment_log_entry_eal", "log_from":"equipment_log_entry_from", "log_to":"equipment_log_entry_to", "procedure":"equipment_log_entry_procedure", "message":"equipment_log_entry_message"}
        
        
        self.current_log_filter = None
        
        self.log_filter = self.store.full_log_store.filter_new()
        self.log_filter.set_visible_func(self.log_filter_func)
    
        self.log_treeview = Gtk.TreeView.new_with_model(self.log_filter)
        self.log_scroll.add(self.log_treeview)
        
        
        for i, column_title in enumerate(["EAL Number", "Log Date", "Going From", "Going To", "Procedure", "Message"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.log_treeview.append_column(self.column)
        
        select = self.log_treeview.get_selection()
        select.connect("changed", self.on_equipment_log_tree_selection_changed)
        
        Function.entry_completion(self, self.equipment.full_equipment_store, "equipment_log_entry_eal", 0)
        Function.entry_completion(self, self.procedure.procedure_store, "equipment_log_entry_procedure", 0)
        
    def on_equipment_log_button_enter_clicked(self, equipment_log_button_enter):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        log_date = self.log_date()
        now = datetime.now()

        c.execute("INSERT INTO logbook (created_at, eal_number, log_date, log_from, log_to, procedure, message) VALUES (?,?,?,?,?,?,?);", (now, entered_text['eal_number'], log_date, entered_text["log_from"], entered_text["log_to"], entered_text["procedure"], entered_text["message"]))
    
        db.commit()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print(text)
        
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
            
    def log_date(self):
        calendar = self.go("equipment_log_calendar_date")
        get_date = calendar.get_date()
        print (get_date.month)
        date = str(get_date.day) + '/' + str(get_date.month) + '/' + str(get_date.year)
        select_log_date = date
        log_date = datetime.strptime(select_log_date, "%d/%m/%Y").date()
        return log_date
    
    def treeview_refresh(self):
        self.store.full_log_store.clear()
        self.store = LogStore()
        self.log_treeview.set_model(model=self.store.full_log_store)
        #self.completions()
        print("Refresh")
    
    def on_equipment_log_entry_eal_changed(self, entry):
        search = entry.get_text()
        self.current_log_filter = search.upper()
        print(self.current_log_filter)
        self.log_filter.refilter()
        
    def log_filter_func(self, model, iter, data):
        if self.current_log_filter is None or self.current_log_filter == "":
            return True
        elif self.current_log_filter in model[iter][0]:
            return model[iter][0]
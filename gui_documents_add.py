import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from datetime import date, datetime
from gui_functions import Function, Cal_Date, Db
from store import Store
import mysql.connector

conn = Db.conn()

class DocumentsAddPage:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/documents.glade")
        self.builder.connect_signals(self)
        self.page = self.builder.get_object("documents_add_page")
        self.scroll = self.builder.get_object("documents_add_scroll_window")
        self.store = Store()

        self.current_filter = None
        
        self.filter = self.store.procedures.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        self.entries = {"doc_for":"documents_add_entry_for", "doc_ref":"documents_add_entry_ref", "doc_name":"documents_add_entry_name", "doc_issue":"documents_add_entry_issue", "issue_reason":"documents_add_entry_reason"}
        
        
        for i, column_title in enumerate(["Name", "Reference", "Client", "Issue", "Reason for Issue", "Date", "File"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(self.column)
        
        select = self.treeview.get_selection()
        
        select.connect("changed", self.on_documents_add_tree_selection_changed)
        
        
        
    def on_documents_add_button_enter_clicked(self, documents_add_button_enter):
        curr = conn.cursor()
        entries = self.entries
        text = Function.get_entries(self, entries)
        date = Cal_Date.date(self, "documents_add_calendar_date")
        now = datetime.now()
        
        log_query = ("INSERT INTO logbook (created_at, eal_number, log_date, log_location, log_procedure, message) VALUES (%s,%s,%s,%s,%s,%s);")
        log_values = (now, entered_text['eal_number'], log_date, entered_text["log_to"], entered_text["procedure"], entered_text["message"])
        
        curr.execute(log_query, log_values)
        conn.commit()
        curr.close()
        self.treeview_refresh()
        Function.clear_entries(self, entries)
        print(text)
        
    def on_documents_add_button_clear_clicked(self, documents_add_button_clear):
        entries = self.entries
        Function.clear_entries(self, entries)
        print("Clear")
        
    
    def on_documents_add_tree_selection_changed(self, selection):
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
        self.store.procedures.clear()
        self.store = Store()
        self.treeview.set_model(model=self.store.procedures)
        #self.completions()
        print("Refresh")
    
    def on_documents_add_entry_eal_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][0]:
            return model[iter][0]
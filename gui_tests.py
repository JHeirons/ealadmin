import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui_liststores import CalibrationStore
from datetime import date, datetime, timedelta
from gui_functions import Function
import sqlite3
import shutil
import os


db = sqlite3.connect("admin.db")
c = db.cursor()
c.execute("""PRAGMA foreign_keys = 1""")

class Main:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/test.glade")
        self.builder.connect_signals(self)
        self.go = self.builder.get_object
        self.window = self.go("test")
        self.calibration_treeview = self.go("treeview")
        self.scroll = self.go("scroll")
        self.entry_to_get = self.go("entry")
        #self.treeview = self.go("treeview")
        self.store = CalibrationStore()
        self.liststore = self.store.full_calibration_store
        self.current_filter = None
        
        self.filter = self.liststore.filter_new()
        self.filter.set_visible_func(self.filter_func)
    
        self.treeview = Gtk.TreeView.new_with_model(self.filter)
        self.scroll.add(self.treeview)
        
        for i, column_title in enumerate(["EAL Number", "Calibration Company", "Calibration Type", "Calibration Date", "Calibration Recall", "Calibration Expiry", "Calibration Certificate"]):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            
            self.treeview.append_column(self.column)
            self.column.set_sort_column_id(i)
        
        
        self.window.show_all()
        
    
    def on_test_delete_event(self, *args):
        Gtk.main_quit(*args)
        
    
    def on_entry_search_changed(self, entry):
        self.current_filter = entry.get_text()
        print(self.current_filter)
        self.filter.refilter()
        
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][0]:
            return model[iter][0]

if __name__ == "__main__":
    main = Main()
    Gtk.main()
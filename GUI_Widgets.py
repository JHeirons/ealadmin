import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

import mysql.connector
import numpy as np

dbConfig = {

    'user' : '',
    'password' : '',
    'host' : '',
    'database' : 'eal_admin'
}

class Store:
    def get(query):
        conn = mysql.connector.connect(**dbConfig)
        curr = conn.cursor()
        curr.execute(query) 
        items = curr.fetchall()
        curr.close()
        conn.close()
        return items
    
    def build(s, items):
        store = s
        store.clear()
        for item in items:
            store.append(list(item))
    
    def compare(current, new):
        x = np.array(current)
        y = np.array(new)
        z = np.array_equal(x, y)
        return z

class Queries:
    def __init__(self):
        self.equipment = {"insert" : "INSERT INTO equipment (eal_number, equipment_type) VALUES (%s,%s);",
                          "update" : "UPDATE equipment SET equipment_type = %s WHERE eal_number = %s;",
                          "select" : "SELECT eal_number, equipment_type, manufacturer, model, pressure, serial_number FROM equipment"}
        self.conn = mysql.connector.connect(**dbConfig)
    
    def query(self, query, values):
        curr = self.conn.cursor()
        curr.execute(query, values)
        self.conn.commit()
        curr.close()

class Widget:
    def __init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)
        self.widget = self.builder.get_object(widget_id)
        self.scroll = self.builder.get_object(widget_scroll_id)
        
        self.current_items = None
        self.current_filter = None
        self.query = timer_query
        
        self.store = store_setup #Gtk.ListStore(str)
        self.columns = column_numbers
        
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filter_func)
        self.filter_view = Gtk.TreeModel.sort_new_with_model(self.filter)
        self.treeview = Gtk.TreeView.new_with_model(self.filter_view)
        self.tree_selection = self.treeview.get_selection()
        self.tree_selection.connect("changed", self.onSelectionChanged)
        self.scroll.add(self.treeview)
        
        for i, column_title in enumerate(column_headings):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.column.set_sort_column_id(i)
            self.treeview.append_column(self.column)
            
        self.widget.show_all()
        
    def timer(self):
        GObject.timeout_add(1000, self.timer_func)
        
    def timer_func(self):
        s = self.store
        #query = self.queries.equipment["select"]
        new_items = Store.get(self.query)
        
        comparison = Store.compare(self.current_items, new_items)
        
        if comparison == False:
            Store.build(s, new_items)
        self.current_items = new_items
        
        return True
    
    def onSelectionChanged(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            c = self.columns
            self.row = []
            for i in c:
                value = model.get_value(tree_iter,c[i])
                self.row.append(value)
            print(self.row)
            
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
        
class Test(Widget):
    def __init__(self, queries):
        glade_file = "Glade/mysql_test.glade"
        widget_id = "window1"
        widget_scroll_id = "scrolledwindow1"
        timer_query = queries.equipment["select"]
        store_setup = Gtk.ListStore(str, str, str, str, int, str)
        column_numbers = (0,1,2,3,4,5)
        column_headings = ["EAL Number", "Equipment Type", "Manufacturer", "Model", "Pressure", "Serial Number"]
        
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings)
        self.queries = queries
        
    def on_button1_clicked(self, button1):
        name = self.get_entry("entry1")
        model = 'test'
        query = self.queries.equipment["insert"]
        values = (name, name)
        self.queries.query(query, values)
        
    def on_button2_clicked(self, button2):
        name = self.get_entry("entry1")
        model = 'update test'
        query = self.queries.equipment["update"]
        values = (model, name)
        self.queries.query(query, values)
        
    def on_entry1_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search
        self.current_filter_column = 0
        self.filter.refilter()
        
    def get_entry(self, entry):
        entry_to_get = self.builder.get_object(entry)
        entry_text = entry_to_get.get_text()
        return entry_text
    
    def on_window1_delete_event(self, *args):
        Gtk.main_quit(*args)
        
if __name__ == "__main__":
    queries = Queries()
    main = Test(queries)
    main.timer()
    
    Gtk.main()
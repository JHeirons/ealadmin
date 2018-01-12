import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import mysql.connector
import numpy as np

dbConfig = {
    'user' : 'root',
    'password' : 'Password',
    'host' : '127.0.0.1',
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
        


class Main:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/mysql_test.glade")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.scroll = self.builder.get_object("scrolledwindow1")
        self.current_items = 'test'
        self.conn = mysql.connector.connect(**dbConfig)
        self.queries = Queries()
        self.current_filter = None
        
        self.store = Gtk.ListStore(str, str, str, str, int, str)
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filter_func)
        self.filter_view = Gtk.TreeModel.sort_new_with_model(self.filter)
        self.treeview = Gtk.TreeView.new_with_model(self.filter_view)
        self.tree_selection = self.treeview.get_selection()
        self.tree_selection.connect("changed", self.onSelectionChanged)
        self.scroll.add(self.treeview)
        
        column_headings = ["EAL Number", "Equipment Type", "Manufacturer", "Model", "Pressure", "Serial Number"]
        for i, column_title in enumerate(column_headings):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.column.set_sort_column_id(i)
            self.treeview.append_column(self.column)
            
        self.window.show_all()
        
    def timer(self):
        GObject.timeout_add(1000, self.build)
        
    def build(self):
        s = self.store
        query = self.queries.equipment["select"]
        new_items = Store.get(query)
        
        comparison = Store.compare(self.current_items, new_items)
        
        if comparison == False:
            Store.build(s, new_items)
        self.current_items = new_items
        
        return True
    
    def onSelectionChanged(self, tree_selection):
        (model, pathlist) = tree_selection.get_selected_rows()
        for path in pathlist :
            tree_iter = model.get_iter(path)
            value = model.get(tree_iter,0,1,2,3,4,5)
            print (value)
        
    def on_button1_clicked(self, button1):
        name = self.get_entry("entry1")
        model = 'test'
        cquery = self.queries.equipment["insert"]
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
    
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
    
    def on_window1_delete_event(self, *args):
        self.conn.close()
        Gtk.main_quit(*args)

if __name__ == "__main__":
    
    main = Main()
    main.timer()
    
    
    Gtk.main()
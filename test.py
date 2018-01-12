import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import mysql.connector

dbConfig = {
    'user' : 'jonathan',
    'password' : 'HP224AZ',
    'host' : '192.168.0.103',
    'database' : 'eal_test'
}


class Store:
    def q():
        query = "SELECT name, model FROM equipment"
        return query
    
    def build(s, q):
        conn = mysql.connector.connect(**dbConfig)
        print("Build Store")
        curr = conn.cursor()
        store = s
        store.clear()
        curr.execute(q) 
        items = curr.fetchall()
        for item in items:
            store.append(list(item))
        curr.close()
        conn.close()
        return store
    
    def insert(name, model):
        conn = mysql.connector.connect(**dbConfig)
        curr = conn.cursor()
        print("Button Clicked")
        query = ("INSERT INTO equipment (name, model) VALUES (%s,%s);")
        values = (name, model)
        
        curr.execute(query, values)
        conn.commit()
        curr.close()

class Main:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/mysql_test.glade")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.scroll = self.builder.get_object("scrolledwindow1")
        
        self.current_filter = None
        s = Gtk.ListStore(str, str)
        self.store = Gtk.ListStore(str, str)
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filter_func)
        self.filter_view = Gtk.TreeModel.sort_new_with_model(self.filter)
        self.treeview = Gtk.TreeView.new_with_model(self.filter_view)
        self.scroll.add(self.treeview)
        
        column_headings = ["EAL Number", "Equipment Type"]
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
        q = Store.q()
        Store.build(s, q)
        return True
        
    def on_button1_clicked(self, button1):
        name = self.get_entry("entry1")
        model = 'test'
        print(name, model)
        Store.insert(name, model)
        
    def on_button2_clicked(self, button2):
        print("button 2")
        
        
    def on_entry1_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search
        self.current_filter_column = 0
        print(self.current_filter_column)
        print(self.current_filter)
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
    
    def on_window1_delete_event(self, *args):s
        Gtk.main_quit(*args)

if __name__ == "__main__":
    
    #while Gtk.events_pending():
        #Gtk.main_iteration()
    
    main = Main()
    main.timer()
    
    Gtk.main()
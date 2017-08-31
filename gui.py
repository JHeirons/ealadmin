import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class EquipmentEntry(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self, title="Equipment Entry")
        self.set_border_width(20)
        
        grid = Gtk.Grid()
        self.add(grid)
        
        label = Gtk.Label()
        label.set_text("Enter New EAL Number: ")
        
        self.entry = Gtk.Entry()
        self.entry.set_text("Enter EAL Number Here")
        
        self.button = Gtk.Button(label="Enter")
        self.button.connect("clicked", self.on_button_clicked)
        
        label2 = Gtk.Label()
        label2.set_text("Enter Equiment Type")
        
        self.name_store = Gtk.ListStore(int, str)
        self.name_store.append([1, "Moisture Meter"])
        self.name_store.append([2, "Partical Counter"])
        self.name_store.append([3, "Tourqe Meter"])
        self.name_store.append([4, "Digital Pressure Indicator"])
        
        type_combo = Gtk.ComboBox.new_with_model_and_entry(self.name_store)
        type_combo.connect("changed", self.on_type_combo_changed)
        type_combo.set_entry_text_column(1)
        
        self.button2 = Gtk.Button(label="Enter")
        self.button2.connect("clicked", self.on_button2_clicked)
        
        grid.add(label)
        grid.attach(self.entry, 1, 0, 3, 1)
        grid.attach_next_to(self.button, self.entry, Gtk.PositionType.RIGHT, 1, 1)
        grid.attach(label2, 0, 1, 1, 1)
        grid.attach(type_combo, 1, 1, 3, 1)
        grid.attach_next_to(self.button2, type_combo, Gtk.PositionType.RIGHT, 1, 1)
        
        
        
    def on_button_clicked(self, widget):
        ealNumber = self.entry.get_text()
        print(ealNumber)
    
    def on_type_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            row_id, name = model[tree_iter][:2]
            self.equip_type = name
        else:
            entry = combo.get_child()
            self.equip_type = entry.get_text()
        
    
    def on_button2_clicked(self, combo):
        print(self.equip_type)
    

win = EquipmentEntry()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
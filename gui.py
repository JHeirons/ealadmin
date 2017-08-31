import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")

        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

        self.label = Gtk.Label()
        self.label.set_text("Enter New EAL Number")
        self.box.pack_start(self.label, True, True, 0)
        
        self.entry = Gtk.Entry()
        self.entry.set_text("Hello World")
        self.box.pack_start(self.entry, True, True, 0)

        self.button2 = Gtk.Button(label="Enter")
        self.button2.connect("clicked", self.on_button2_clicked)
        self.box.pack_start(self.button2, True, True, 0)

    

    def on_button2_clicked(self, widget):
        ealNumber = self.entry.get_text()
        print(ealNumber)

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
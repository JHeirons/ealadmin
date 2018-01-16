import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from time import sleep
from GUI_Widgets import DocAdd, Log, EquipAdd, EquipCal, EquipClean, EquipProof, EquipSearch, Confirm
from SQL import Store, Queries
import mysql.connector
from gui_functions import Function, Cal_Date

dbConfig = {
            'user' : '',
            'password' : '',
            'host' : '192.168.0.103',
            'database' : 'eal_admin'
            }
        
class Main:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/main.glade")
        self.builder.connect_signals(self)
        self.main = self.builder.get_object("main")
        
        self.notebook = self.builder.get_object("main_tabs")
        self.equipment = self.builder.get_object("equipment_tabs")
        self.equip_add = self.builder.get_object("equipment_add_box")
        self.equip_search = self.builder.get_object("equipment_search_box")
        self.equip_calibration = self.builder.get_object("equipment_calibration_box")
        self.equip_proof = self.builder.get_object("equipment_proof_box")
        self.equip_cleanliness = self.builder.get_object("equipment_cleanliness_box")
        self.log = self.builder.get_object("log_box")
        self.docs_add = self.builder.get_object("documents_add_box")
        self.notebook.set_current_page(0)
        
        self.login = self.builder.get_object("login")
        
        self.login.show()
        
    def on_login_button_clicked (self, login_button):
        user = Function.get_entry(self, "login_username")
        p_word = Function.get_entry(self, "login_password")
        error = self.builder.get_object("warning_label")
        dbConfig['user'] = user
        dbConfig['password'] = p_word
        
        try:
            self.conn = mysql.connector.connect(**dbConfig)
            self.store_func = Store(dbConfig)
            self.queries = Queries(dbConfig)
            self.pages()
            self.login.destroy()
            self.main.show_all()
            
        except mysql.connector.Error as err:
            error.set_label("Error occured: {}".format(err))
            
    def pages(self):
        self.equip_add_page = EquipAdd(self.queries, self.store_func, self.main)
        self.equip_search_page = EquipSearch(self.queries, self.store_func, self.main)
        self.equip_calibration_page = EquipCal(self.queries, self.store_func, self.main)
        self.equip_proof_page = EquipProof(self.queries, self.store_func, self.main)
        self.equip_cleanliness_page = EquipClean(self.queries, self.store_func, self.main)
        self.log_page = Log(self.queries, self.store_func, self.main)
        self.docs_add_page = DocAdd(self.queries, self.store_func, self.main)
        
        self.equip_add.add(self.equip_add_page.widget)
        self.equip_search.add(self.equip_search_page.widget)
        self.equip_calibration.add(self.equip_calibration_page.widget)
        self.equip_proof.add(self.equip_proof_page.widget)
        self.equip_cleanliness.add(self.equip_cleanliness_page.widget)
        self.log.add(self.log_page.widget)
        self.docs_add.add(self.docs_add_page.widget)
    
    def on_login_username_changed(self, login_username):
        error = self.builder.get_object("warning_label")
        error.set_label(" ")
        
    def on_login_password_changed(self, login_password):
        error = self.builder.get_object("warning_label")
        error.set_label(" ")
    
    def on_cancel_button_clicked(self, cancel_button):
        Gtk.main_quit()
    
    def on_login_delete_event(self, *args):
        Gtk.main_quit(*args)
        
    def on_main_delete_event(self, *args):
        
        self.conn.close()
        Gtk.main_quit(*args)

        
if __name__ == "__main__":
    main = Main()
    
    Gtk.main()
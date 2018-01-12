import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from gui_equipment_add import EquipmentAddPage
from gui_equipment_search import EquipmentSearchPage
from gui_equipment_calibration import EquipmentCalibrationPage
from gui_equipment_proof import EquipmentProofPage
from gui_equipment_cleanliness import EquipmentCleanlinessPage
from gui_equipment_log import EquipmentLogPage
from gui_functions import Function
from gui_documents_add import DocumentsAddPage
from time import sleep
import mysql.connector

dbConfig = {
    'user' : 'test_user',
    'password' : 'eal123',
    'host' : '192.168.0.103',
    'database' : 'eal_admin'
}
           
class Main:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/main.glade")
        self.builder.connect_signals(self)
        self.main = self.builder.get_object("main")
        self.login = self.builder.get_object("login")
        self.login.show()
        
        Gdk.EventMask.BUTTON_PRESS_MASK
        
        self.notebook = self.builder.get_object("main_tabs")
        self.equipment = self.builder.get_object("equipment_tabs")
        self.page_equipment_add = self.builder.get_object("equipment_add_box")
        self.page_equipment_search = self.builder.get_object("equipment_search_box")
        self.page_equipment_calibration = self.builder.get_object("equipment_calibration_box")
        self.page_equipment_proof = self.builder.get_object("equipment_proof_box")
        self.page_equipment_cleanliness = self.builder.get_object("equipment_cleanliness_box")
        self.page_log = self.builder.get_object("log_box")
        
        self.page_documents_add = self.builder.get_object("documents_add_box")
        
        
       
        
        self.notebook.set_current_page(0)
        
    def on_login_button_clicked (self, login_button):
        user = Function.get_entry(self, "login_username")
        p_word = Function.get_entry(self, "login_password")
        error = self.builder.get_object("warning_label")
        dbConfig['user'] = user
        dbConfig['password'] = p_word
        
        try:
            self.conn = mysql.connector.connect(**dbConfig)
            self.page_connections(self.conn)
            self.login.destroy()
            sleep(1)
            self.main.show_all()
            
        except mysql.connector.Error as err:
            error.set_label("Error occured: {}".format(err))
        
        
    
    def page_connections(self, conn):
        self.equipment_add_page = EquipmentAddPage(conn)
        self.equipment_search_page = EquipmentSearchPage(conn)
        self.equipment_calibration_page = EquipmentCalibrationPage(conn)
        self.equipment_proof_page = EquipmentProofPage(conn)
        self.equipment_cleanliness_page = EquipmentCleanlinessPage(conn)
        
        self.log_page = EquipmentLogPage(conn)
        
        self.documents_add_page = DocumentsAddPage(conn)
        
        self.page_equipment_add.add(self.equipment_add_page.page)
        self.page_equipment_search.add(self.equipment_search_page.page)
        self.page_equipment_calibration.add(self.equipment_calibration_page.page)
        self.page_equipment_proof.add(self.equipment_proof_page.page)
        self.page_equipment_cleanliness.add(self.equipment_cleanliness_page.page)
        
        self.page_log.add(self.log_page.page)
        
        self.page_documents_add.add(self.documents_add_page.page)
    
    def on_login_username_changed(self, login_username):
        error = self.builder.get_object("warning_label")
        error.set_label(" ")
        
    def on_login_password_changed(self, login_password):
        error = self.builder.get_object("warning_label")
        error.set_label(" ")

    
    def on_equipment_tabs_switch_page(self, equipment_tabs, page, page_num):
        print(page)
        print(page_num)
        self.equipment_search_page.treeview_refresh()
        self.equipment_add_page.treeview_refresh()
        self.equipment_calibration_page.treeview_refresh()
        #self.equipment_log_page.treeview_refresh()
    
    def on_cancel_button_clicked(self, cancel_button):
        Gtk.main_quit()
    
    def on_login_delete_event(self, *args):
        Gtk.main_quit(*args)

    def on_main_delete_event(self, *args):
        self.conn.close()
        Gtk.main_quit(*args)
        
if __name__ == "__main__":
    
    #while Gtk.events_pending():
        #Gtk.main_iteration()
    
    main = Main()
    
    Gtk.main()
    
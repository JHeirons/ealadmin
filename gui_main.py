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



class Main:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/main.glade")
        self.builder.connect_signals(self)
        self.go_main = self.builder.get_object
        self.window = self.go_main("main")
        
        Gdk.EventMask.BUTTON_PRESS_MASK
        
        self.notebook = self.go_main("main_tabs")
        self.equipment = self.go_main("equipment_tabs")
        self.page_equipment_add = self.go_main("equipment_add_box")
        self.page_equipment_search = self.go_main("equipment_search_box")
        self.page_equipment_calibration = self.go_main("equipment_calibration_box")
        self.page_equipment_proof = self.go_main("equipment_proof_box")
        self.page_equipment_cleanliness = self.go_main("equipment_cleanliness_box")
        self.page_log = self.go_main("log_box")
        
        self.page_documents_add = self.go_main("documents_add_box")
        
        self.equipment_add_page = EquipmentAddPage()
        self.equipment_search_page = EquipmentSearchPage()
        self.equipment_calibration_page = EquipmentCalibrationPage()
        self.equipment_proof_page = EquipmentProofPage()
        self.equipment_cleanliness_page = EquipmentCleanlinessPage()
        
        self.log_page = EquipmentLogPage()
        
        self.documents_add_page = DocumentsAddPage()
        
        self.page_equipment_add.add(self.equipment_add_page.page)
        self.page_equipment_search.add(self.equipment_search_page.page)
        self.page_equipment_calibration.add(self.equipment_calibration_page.page)
        self.page_equipment_proof.add(self.equipment_proof_page.page)
        self.page_equipment_cleanliness.add(self.equipment_cleanliness_page.page)
        
        self.page_log.add(self.log_page.page)
        
        self.page_documents_add.add(self.documents_add_page.page)
        
        self.window.show_all()
        self.notebook.set_current_page(0)
        
    
    def on_equipment_tabs_switch_page(self, equipment_tabs, page, page_num):
        print(page)
        print(page_num)
        self.equipment_search_page.treeview_refresh()
        self.equipment_add_page.treeview_refresh()
        self.equipment_calibration_page.treeview_refresh()
        #self.equipment_log_page.treeview_refresh()
    
    def on_main_delete_event(self, *args):
        Gtk.main_quit(*args)
        
if __name__ == "__main__":
    main = Main()
    Gtk.main()

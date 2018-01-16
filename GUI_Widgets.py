import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from gui_functions import Function, Cal_Date
import shutil
from datetime import date, datetime, timedelta
#from GUI_Admin import Main

class Widget:
    def __init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)
        self.widget = self.builder.get_object(widget_id)
        self.scroll = self.builder.get_object(widget_scroll_id)
        self.confirm = Confirm(parent)
        
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
        self.store_func = store_func
        #self.entries = entries
        self.timer()
        
    def timer(self):
        GObject.timeout_add(1000, self.timer_func)
        
    def timer_func(self):
        s = self.store
        #query = self.queries.equipment["select"]
        new_items = self.store_func.get(self.query)
        
        comparison = self.store_func.compare(self.current_items, new_items)
        
        if comparison == False:
            self.store_func.build(s, new_items)
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
                self.row.append(str(value))
            print(self.row)
            Function.set_entries(self, self.entries, self.row)
            tree_selection.unselect_all()
            
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
        
        
class DocAdd(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/documents.glade"
        widget_id = "documents_add_page"
        widget_scroll_id = "documents_add_scroll_window"
        timer_query = queries.documents["select"]
        store_setup = Gtk.ListStore(str, str, str, int, str, str, str)
        column_numbers = (0,1,2,3,4,5,6)
        column_headings = ["Name", "Reference", "Client", "Issue", "Reason for Issue", "Date", "File"]
        store_func = store_func
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        self.entries = {"doc_for":"documents_add_entry_for", "doc_ref":"documents_add_entry_ref", "doc_name":"documents_add_entry_name", "doc_issue":"documents_add_entry_issue", "issue_reason":"documents_add_entry_reason"}
        
    def on_documents_add_button_enter_clicked(self, documents_add_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        date = Cal_Date.date(self, "documents_add_calendar_date")
        now = datetime.now()
        
        query = self.queries.documents["insert"]
        values = (now, entered_text['eal_number'], log_date, entered_text["log_to"], entered_text["procedure"], entered_text["message"])
        Confirm(self.queries, query, values)
        
        log_query = self.queries.logbook["insert"]
        log_values = (now, text['eal_number'], date, text["log_to"], text["procedure"], text["message"])
        
        Function.clear_entries(self, entries)
        print(text)
        
    def on_documents_add_button_clear_clicked(self, documents_add_button_clear):
        self.tree_selection.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        
    def on_documents_add_entry_eal_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
    
    def on_documents_add_page_delete_event(self, *args):
        
        Gtk.main_quit(*args)

class Log(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/equipment_log.glade"
        widget_id = "equipment_log_page"
        widget_scroll_id = "equipment_log_scroll_window"
        timer_query = queries.logbook["select"]
        store_setup = Gtk.ListStore(str, str, str, str, str)
        column_numbers = (0,1,2,3,4)
        column_headings = ["EAL Number", "Log Date", "Location", "Procedure", "Message"]
        store_func = store_func
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        self.entries = {"equipment_log_entry_eal" : 0, "equipment_log_entry_from" : 2, "equipment_log_entry_procedure" : 3, "equipment_log_entry_message" : 4} 
        
        
    def on_equipment_log_button_enter_clicked(self, equipment_log_button_enter):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        log_date = Cal_Date.date(self, "equipment_log_calendar_date")
        now = datetime.now()

        log_values = (now, entered_text['eal_number'], log_date, entered_text["log_from"], entered_text["procedure"], entered_text["message"])
        
        log_query = self.queries.logbook["insert"]
        Confirm(self.queries, query, values)
        
        Function.clear_entries(self, entries)
        
    def on_equipment_log_button_clear_clicked(self, equipment_log_button_clear):
        self.tree_selection.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        
    def on_equipment_log_entry_eal_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()  
        
    def on_equipment_log_page_delete_event(self, *args):
        
        Gtk.main_quit(*args)
    
#Do Remove/Update and Completions
class EquipAdd(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/equipment_add.glade"
        widget_id = "equipment_add_page"
        widget_scroll_id = "equipment_add_scroll_window"
        timer_query = queries.equipment["select"]
        store_setup = Gtk.ListStore(str, str, str, str, int, str)
        column_numbers = (0,1,2,3,4,5)
        column_headings = ["EAL Number", "Equipment Type", "Manufacturer", "Model", "Pressure", "Serial Number"]
        store_func = store_func
        self.entries = {"equipment_add_entry_eal" : 0, "equipment_add_entry_type" : 1, "equipment_add_entry_manufacturer" : 2, "equipment_add_entry_model" : 3, "equipment_add_entry_pressure" : 4, "equipment_add_entry_serial" : 5}   
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        
        self.eal_number_comp = Function.entry_completion(self, self.store, "equipment_add_entry_eal", 0)
        Function.entry_completion(self, self.store, "equipment_add_entry_type", 1)
        Function.entry_completion(self, self.store, "equipment_add_entry_manufacturer", 2)
        Function.entry_completion(self, self.store, "equipment_add_entry_model", 3)
        #Function.entry_completion(self, self.store, "equipment_add_entry_pressure", 4)
        #Function.entry_completion(self, self.store, "equipment_add_entry_serial", 5)
        
    def on_equipment_add_button_add_clicked(self, equipment_add_button_add):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
    
        now = datetime.now()
        
        values = (now, entered_text['eal_number'], entered_text["equipment_type"], entered_text["manufacturer"], entered_text["model"], entered_text["pressure"], entered_text["serial_number"])
        
        location = 'Westcott'
        procedure = 'N/A'
        message = entered_text['eal_number'] + ' added to equipment store'
        
        log_query = self.queries.logbook["insert"]
        log_values = (now, entered_text['eal_number'], now, location, procedure, message)
        
        query = self.queries.equipment["insert"]
        #self.queries.query(query, values)
        self.confirm.confirm_message(self.queries, query, values, log_query, log_values)
        
        
        
        Function.clear_entries(self, entries)
        
    def on_equipment_add_button_remove_clicked(self, equipment_add_button_remove):
        now = datetime.now()
        location = 'Westcott'
        procedure = 'N/A'
        message = self.eal_number + ' removed from equipment store'
        
        Function.clear_entries(self, entries)
        
        
    def on_equipment_add_button_update_clicked(self, equipment_add_button_update):
        entries = self.entries
        entered_text = Function.get_entries(self, entries)
        now = datetime.now()
        
        Function.clear_entries(self, entries)
        self.treeview_refresh()
    
    def on_equipment_add_button_clear_clicked(self, equipment_add_button_clear):
        self.tree_selection.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        
        self.current_filter = None
    
    def on_equipment_add_entry_eal_changed(self, entry):
        self.tree_selection.unselect_all()
        search = entry.get_text() 
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_add_entry_type_changed(self, entry):
        self.tree_selection.unselect_all()
        search = entry.get_text()
        self.current_filter = search 
        self.current_filter_column = 1
        self.filter.refilter()
        
    def on_equipment_add_entry_manufacturer_changed(self, entry):
        self.tree_selection.unselect_all()
        search = entry.get_text()
        '''self.current_filter = search 
        self.current_filter_column = 2
        self.filter.refilter()'''
    
    def on_equipment_add_entry_model_changed(self, entry):
        self.tree_selection.unselect_all()
        search = entry.get_text()
        '''self.current_filter = search
        self.current_filter_column = 3
        self.filter.refilter()'''  
        
        
    def on_equipment_add_page_delete_event(self, *args):
        
        Gtk.main_quit(*args)
        
#Do completions
class EquipCal(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/equipment_calibration.glade"
        widget_id = "equipment_calibration_page"
        widget_scroll_id = "equipment_calibration_scroll_window"
        timer_query = queries.calibration["select"]
        store_setup = Gtk.ListStore(str, str, str, str, str, str, str)
        column_numbers = (0,1,2,3,4,5,6)
        column_headings = ["EAL Number", "Calibration Company", "Calibration Type", "Calibration Date", "Calibration Recall", "Calibration Expiry", "Calibration Certificate"]
        store_func = store_func
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        self.type = "External"
        self.entries = {"equipment_calibration_entry_eal" : 0, "equipment_calibration_entry_company" : 1}  
        
        #Function.entry_completion2(self, self.completion, "equipment_calibration_entry_eal")
        
    def on_equipment_calibration_radio_external_toggled(self, equipment_calibration_radio_external):
        self.type = "External"
    
    def on_equipment_calibration_radio_internal_toggled(self, equipment_calibration_radio_internal):
        self.type = "Internal"
    
    def on_equipment_calibration_button_enter_clicked(self, equipment_calibration_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        print(text)
        calibration_type = self.type
        if (calibration_type == "External"):
            length = 12
        elif (calibration_type == "Internal"):
            length = 6
        else:
            length = 12
        
        calibration_date = Cal_Date.date(self, "equipment_calibration_calendar_date")
        calibration_expiry = Cal_Date.expiry(self, calibration_date, length)
        calibration_recall = Cal_Date.recall(self, calibration_expiry)
        
        file_name = text[0] + '_Cal_Cert-' + str(calibration_date)
        certificate_location = Function.file_path(self, 'QA_Calibration_Certificates', text[0], file_name, 'pdf')
        shutil.copy(self.file, certificate_location)
        calibration_certificate = certificate_location
        
        now = datetime.now()
        
        message = "Calibration certificate added."
        location = Function.get_entry(self, "equipment_calibration_entry_location")
        procedure = "N/A"
        
        values = (text[0], now, text[1], calibration_type, calibration_date, calibration_recall, calibration_expiry, calibration_certificate)
    
        log_values = (now, text[0], now, location, procedure, message)
        
        query = self.queries.calibration["insert"]
        
        
        log_query = self.queries.logbook["insert"]
        self.confirm.confirm_message(self.queries, query, values, log_query, log_values)
        
        Function.clear_entries(self, entries)
    
    def on_equipment_calibration_button_clear_clicked(self, equipment_calibration_button_clear):
        self.tree_selection.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_calibration_file_certificate_file_set(self, equipment_calibration_file_certificate):
        self.file = equipment_calibration_file_certificate.get_filename()
    
    def on_equipment_calibration_entry_eal_changed(self, equipment_calibration_entry_eal):
        search = equipment_calibration_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_calibration_page_delete_event(self, *args):
        
        Gtk.main_quit(*args)    
        
#Do compltions
class EquipClean(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/equipment_cleanliness.glade"
        widget_id = "equipment_cleanliness_page"
        widget_scroll_id = "equipment_cleanliness_scroll_window"
        timer_query = queries.cleanliness["select"]
        store_setup = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str)
        column_numbers = (0,1,2,3,4,5,6,7,8,9)
        column_headings = ["EAL Number", "Particle Counter Number", "Dew Point Meter", "Procedure", "Cleanliness & Dryness Date", "Cleanliness & Dryness Recall", "Cleanliness & Dryness Expiry", "Test Location", "Result", "Proof Certificate"]
        store_func = store_func
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        self.entries = {"equipment_cleanliness_entry_eal" : 0, "equipment_cleanliness_entry_pco" : 1, "equipment_cleanliness_entry_dew" : 2, "equipment_cleanliness_entry_procedure" : 3, "equipment_cleanliness_entry_location" : 7} 
        
    def on_equipment_cleanliness_radio_pass_toggled(self, equipment_cleanliness_radio_pass):
        self.type = "Pass"
    
    def on_equipment_cleanliness_radio_fail_toggled(self, equipment_cleanliness_radio_fail):
        self.type = "Fail"
    
    def on_equipment_cleanliness_button_enter_clicked(self, equipment_cleanliness_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        result_type = self.type
        clean_date = Cal_Date.date(self, "equipment_cleanliness_calendar_date")
        clean_expiry = Cal_Date.expiry(self, calibration_date, length)
        clean_recall = Cal_Date.recall(self, calibration_expiry)
        
        print(clean_date, clean_expiry, clean_recall)
        
        if not os.path.exists('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"]):
            os.mkdir('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"])
            
        certificate_location = '/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"] + '/' + text["eal_number"] + '_Clean_and_Dry_Cert-' + str(clean_date) + '.pdf'
        shutil.copy(self.file, certificate_location)
        clean_certificate = certificate_location
        now = datetime.now()
        
        message = "Cleanliness & Dryness certificate added."
        
        values = (text["eal_number"], now, text["pco_number"], text["dew_number"], text["procedure"], clean_date, clean_recall, clean_expiry, text["clean_location"], result_type, clean_certificate)
        
        log_values = (now, entered_text['eal_number'], now, location, procedure, message)
        query = self.queries.clean["insert"]
        Confirm(self.queries, query, values)
        
        log_query = self.queries.logbook["insert"]
        self.queries.log_query(log_query, log_values)
        
        Function.clear_entries(self, entries)
    
    def on_equipment_cleanliness_button_clear_clicked(self, equipment_cleanliness_button_clear):
        self.tree_selection.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_cleanliness_file_certificate_file_set(self, equipment_cleanliness_file_certificate):
        self.file = equipment_cleanliness_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_cleanliness_entry_eal_changed(self, equipment_cleanliness_entry_eal):
        search = equipment_cleanliness_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_cleanliness_page_delete_event(self, *args):
        
        Gtk.main_quit(*args) 
        
#Do completions
class EquipProof(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/equipment_proof.glade"
        widget_id = "equipment_proof_page"
        widget_scroll_id = "equipment_proof_scroll_window"
        timer_query = queries.proof["select"]
        store_setup = Gtk.ListStore(str, str, str, str, str, str, str, str, str, str, str)
        column_numbers = (0,1,2,3,4,5,6,7,8,9,10)
        column_headings = ["EAL Number", "Test Pressure", "Test Duration", "Transducer Number", "Procedure", "Proof Date", "Proof Recall", "Proof Expiry", "Test Location", "Result", "Proof Certificate"]
        store_func = store_func
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        self.entries = {"equipment_proof_entry_eal" : 0, "equipment_proof_entry_bar" : 1, "equipment_proof_entry_duration" : 2, "equipment_proof_entry_pt" : 3, "equipment_proof_entry_procedure" : 4, "equipment_proof_entry_location" : 8} 
        
        
    def on_equipment_proof_radio_pass_toggled(self, equipment_proof_radio_pass):
        self.type = "Pass"
    
    def on_equipment_proof_radio_fail_toggled(self, equipment_proof_radio_fail):
        self.type = "Fail"
    
    def on_equipment_proof_button_enter_clicked(self, equipment_proof_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        result_type = self.type
        proof_date = Cal_Date.date(self, "equipment_proof_calendar_date")
        proof_recall = Cal_Date.expiry(self, calibration_date, 12)
        proof_expiry = Cal_Date.recall(self, calibration_expiry)
        
        if not os.path.exists('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"]):
            os.mkdir('/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"])
            
        certificate_location = '/Users/Home/Documents/Cal_Cert_Test/' + text["eal_number"] + '/' + text["eal_number"] + '_Proof_Cert-' + str(proof_date) + '.pdf'
        shutil.copy(self.file, certificate_location)
        proof_certificate = certificate_location
        now = datetime.now()
        
       # print (text["eal_number"], text["calibration_company"], calibration_type, calibration_certificate, calibration_date, calibration_recall, calibration_expiry)
        
        proof_message = "Proof certificate added."
        values = (text["eal_number"], now, text["proof_pressure"], text["proof_duration"], text["pt_number"], text["procedure"], proof_date, proof_recall, proof_expiry, text["proof_location"], result_type, proof_certificate)
        
        log_values = (now, text['eal_number'], log_date, text["proof_location"], text["procedure"], proof_message)
        
        query = self.queries.proof["insert"]
        Confirm(self.queries, query, values)
        
        log_query = self.queries.logbook["insert"]
        self.queries.log_query(log_query, log_values)
        
        Function.clear_entries(self, entries)
        print ("Add")
    
    def on_equipment_proof_button_clear_clicked(self, equipment_proof_button_clear):
        self.tree_selection.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_proof_file_certificate_file_set(self, equipment_proof_file_certificate):
        self.file = equipment_proof_file_certificate.get_filename()
        print(self.file)
    
    def on_equipment_proof_entry_eal_changed(self, equipment_proof_entry_eal):
        search = equipment_proof_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_proof_page_delete_event(self, *args):
        
        Gtk.main_quit(*args)    
#Entry for filter
class EquipSearch(Widget):
    def __init__(self, queries, store_func, parent):
        glade_file = "Glade/equipment_search.glade"
        widget_id = "equipment_search_page"
        widget_scroll_id = "equipment_search_scroll_window"
        timer_query = queries.overview["select"]
        store_setup = Gtk.ListStore(str, str, str, str, str)
        column_numbers = (0,1,2,3,4)
        column_headings = ["EAL Number", "Equipment Type", "Serial Number", "Calibration Expiry", "Current Location"]
        store_func = store_func
        Widget.__init__(self, glade_file, widget_id, widget_scroll_id, timer_query, store_setup, column_numbers, column_headings, store_func, parent)
        self.queries = queries
        self.entries = {"equipment_search_entry_search" : 0}
        
    def on_equipment_search_entry_search_changed(self, equipment_search_entry_search):
        search = equipment_search_entry_search.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
    
    
    def on_equipment_search_button_export_clicked(self, equipment_search_button_export):
        with open('overview.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            rows = self.current_items
            for row in rows:
                writer.writerow(row)
        
    def on_equipment_search_page_delete_event(self, *args):
        
        Gtk.main_quit(*args)

class Confirm:
    def __init__(self, parent):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade/confirm.glade")
        self.builder.connect_signals(self)
        self.confirm = self.builder.get_object("confirm")
        self.msg = self.builder.get_object("confirm_label")
        self.confirm.set_transient_for(parent)
        #self.confirm.show()
        
        
    def confirm_message(self, queries, query, values, log_query, log_values):
        self.confirm.show()
        self.queries = queries
        self.query = query
        self.values = values
        self.log_query = log_query
        self.log_values = log_values
        
        self.msg.set_label("You are about to add {}".format(self.values))
        
    def on_confirm_button_clicked(self, confirm_button):
        self.queries.query(self.query, self.values)
        self.queries.log_query(self.log_query, self.log_values)
        self.confirm.destroy()
        
    def on_confirm_cancel_button_clicked(self, confirm_cancel_button):
        self.confirm.destroy()
    
    def on_confirm_delete_event(self, *args):
        self.confirm.destroy()
        
    
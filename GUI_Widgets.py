import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gio
from gui_functions import Function, Cal_Date
import shutil
from datetime import date, datetime, timedelta
from SQL import Queries, Store
#from GUI_Admin import Main

class Widget:
    def __init__(self, store_func, parent, queries, **setup):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(setup["glade_file"])
        self.builder.connect_signals(self)
        self.widget = self.builder.get_object(setup["widget_id"])
        self.scroll = self.builder.get_object(setup["widget_scroll_id"])
        if setup["widget_calander_id"] != None:
            self.calander = self.builder.get_object(setup["widget_calander_id"])
        else:
            self.calander = None
        self.parent = parent
        self.queries = queries
        
        self.current_items = None
        self.current_filter = None
        self.file = None
        if setup["file_chooser"] != None:
            self.file_chooser = self.builder.get_object(setup["file_chooser"])
        else:
            self.file_chooser = None
        self.query = setup["timer_query"]
        
        self.store = setup["store_setup"] #Gtk.ListStore(str)
        self.columns = setup["column_numbers"]
        self.column_headings = setup["column_headings"]
        self.entries = setup["entries"]
        
        self.filter = self.store.filter_new()
        self.filter.set_visible_func(self.filter_func)
        self.filter_view = Gtk.TreeModel.sort_new_with_model(self.filter)
        self.treeview = Gtk.TreeView.new_with_model(self.filter_view)
        self.tree_selection = self.treeview.get_selection()
        self.tree_selection.connect("changed", self.onSelectionChanged)
        self.scroll.add(self.treeview)
        
        for i, column_title in enumerate(self.column_headings):
            renderer = Gtk.CellRendererText()
            self.column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.column.set_sort_column_id(i)
            self.treeview.append_column(self.column)
            
        self.widget.show_all()
        self.store_func = store_func
        self.timer()
        
    def timer(self):
        GObject.timeout_add(1000, self.timer_func)
        
    def timer_func(self):
        s = self.store
        new_items = self.store_func.get(self.query)
        comparison = self.store_func.compare(self.current_items, new_items)
        if comparison == False:
            x = self.store_func.build(s, new_items)
        self.current_items = new_items
        
        return True
    
    def filter_func(self, model, iter, data):
        if self.current_filter is None or self.current_filter == "":
            return True
        elif self.current_filter in model[iter][self.current_filter_column]:
            return model[iter][self.current_filter_column]
        
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
            
            if self.calander != None:
                for j in range(len(self.column_headings)):
                    if self.column_headings[j].endswith("Expiry") == True:
                        date_to_set = self.row[j]
                        Cal_Date.set_date(self,  calander_object=self.calander, date=date_to_set)
                    elif self.column_headings[j].endswith("Date") == True:
                        date_to_set = self.row[j]
                        Cal_Date.set_date(self,  calander_object=self.calander, date=date_to_set)
                    
            if self.file_chooser != None:
                for k in range(len(self.column_headings)):
                    if self.column_headings[k].endswith("Certificate") == True:
                        f = Gio.File.new_for_path(self.row[k])
                        self.file_chooser.set_file(f)
                        
                    elif self.column_headings[k].endswith("File") == True:
                        f = Gio.File.new_for_path(self.row[k])
                        self.file_chooser.set_file(f)
                        
            
    def confirm_init(self):
        self.builder.add_from_file("Glade/confirm.glade")
        self.builder.connect_signals(self)
        self.confirm = self.builder.get_object("confirm")
        self.log = False
        self.msg_label = self.builder.get_object("title")
        self.confirm.set_transient_for(self.parent)
        self.f_labels = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11"]
        self.v_labels = ["v11", "v10", "v9", "v8", "v7", "v6", "v5", "v4", "v3", "v2", "v1"]
    
    def insert(self, query, values, log_query, log_values):
        self.confirm_init()
        self.q = query
        self.v = values
        self.lq = log_query
        self.lv = log_values
        table = "equipment"
        self.msg = ("You are about to add the following {} to the database".format(table))
        self.heading_labels = self.column_headings
        self.label_values = list(values)[1:]
        self.show_message()
        
    def log_insert(self, log_query, log_values):
        self.confirm_init()
        self.lq = log_query
        self.lv = log_values
        table = "logbook"
        self.msg = ("You are about to add the following {} to the database".format(table))
        self.heading_labels = self.column_headings
        self.label_values = list(log_values)[1:]
        self.log = True
        self.show_message()
        
    def update(self, query, values, log_query, log_values):
        self.confirm_init()
        columns = list(self.column_headings)[1:]
        current_values = self.row[1:]
        new_values = list(values)[1:-1]
        self.q = query
        self.v = values
        self.lq = log_query
        self.lv = log_values
        self.heading_labels = []
        self.label_values = []
        self.msg = ("You are about to update the following fields with: ")
        for i in range(len(new_values)):
            if new_values[i] != current_values[i]:
                self.heading_labels.append(columns[i])
                self.label_values.append(new_values[i])
        
        self.show_message()                
            
    def show_message(self):
        self.msg_label.set_label(self.msg)
        for i in range(len(self.heading_labels)):
            field_label = self.builder.get_object(self.f_labels[i])
            value_label = self.builder.get_object(self.v_labels[i])
            field_label.set_label(self.heading_labels[i])
            value_label.set_label(str(self.label_values[i]))
        self.confirm.show()
        
    def on_confirm_button_clicked(self, confirm_button):
        if self.log == False:
            self.queries.query(self.q, self.v)
            self.queries.log_query(self.lq, self.lv)
            self.confirm.destroy()
        elif self.log == True:
            self.queries.log_query(self.lq, self.lv)
            self.confirm.destroy()
        
        
    def on_confirm_cancel_button_clicked(self, confirm_cancel_button):
        self.confirm.destroy()
    
    def on_confirm_delete_event(self, *args):
        self.confirm.destroy()

#Do Remove/Update and Completions
class EquipAdd(Widget):
    def __init__(self, queries, store_func, parent):
        self.entries = {"equipment_add_entry_eal" : 0, "equipment_add_entry_type" : 1, "equipment_add_entry_manufacturer" : 2, "equipment_add_entry_model" : 3, "equipment_add_entry_pressure" : 4, "equipment_add_entry_serial" : 5}
        self.queries = queries
        
        setup = {"glade_file" : "Glade/equipment_add.glade", 
                 "widget_id" :  "equipment_add_page",
                 "widget_scroll_id" : "equipment_add_scroll_window", 
                 "widget_calander_id" : None, 
                 "timer_query" : queries.equipment["select"],
                 "store_setup" : Gtk.ListStore(str, str, str, str, int, str), 
                 "column_numbers" : (0, 1, 2, 3, 4, 5),
                 "column_headings" : ["EAL Number", "Equipment Type", "Manufacturer", "Model", "Pressure", "Serial Number"],
                 "entries" : self.entries,
                 "file_chooser" : None}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
        
        Function.entry_completion(self, self.store, "equipment_add_entry_eal", 0)
        Function.entry_completion(self, self.store, "equipment_add_entry_type", 1)
        Function.entry_completion(self, self.store, "equipment_add_entry_manufacturer", 2)
        Function.entry_completion(self, self.store, "equipment_add_entry_model", 3)
        #Function.entry_completion(self, self.store, "equipment_add_entry_pressure", 4)
        #Function.entry_completion(self, self.store, "equipment_add_entry_serial", 5)
        
    def on_equipment_add_button_add_clicked(self, equipment_add_button_add):
        entries = self.entries
        text = Function.get_entries(self, entries)
        now = datetime.now()
        for item in self.current_items:
            row = list(item)
            if row[0] != text[0]:
                match = False
                
            elif row[0] == text[0]:
                match = True
                
        if match == True:
            query = self.queries.equipment["update"]
            utext = text[1:]
            utext.append(text[0])
            values = (now, utext[0], utext[1], utext[2], utext[3], utext[4], utext[5])
            location = 'Westcott'
            procedure = 'N/A'
            message = text[0] + ' updated field'
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[0], now, location, procedure, message)
            self.update(query, values, log_query, log_values)
        elif match == False:
            values = (now, text[0], text[1], text[2], text[3], text[4], text[5])
            location = 'Westcott'
            procedure = 'N/A'
            message = text[0] + ' added to equipment store'
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[0], now, location, procedure, message)
            query = self.queries.equipment["insert"]
            self.insert(query, values, log_query, log_values)
        
        Function.clear_entries(self, entries)
        
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
    
    def on_equipment_add_entry_model_changed(self, entry):
        self.tree_selection.unselect_all()
        search = entry.get_text() 
        
    def on_equipment_add_page_delete_event(self, *args):
        Gtk.main_quit(*args)

class EquipCal(Widget):
    def __init__(self, queries, store_func, parent, com_store):
        
        self.queries = queries
        self.type = "External"
        self.entries = {"equipment_calibration_entry_eal" : 0, "equipment_calibration_entry_company" : 1}
        
        setup = {"glade_file" : "Glade/equipment_calibration.glade", 
                 "widget_id" :  "equipment_calibration_page",
                 "widget_scroll_id" : "equipment_calibration_scroll_window", 
                 "widget_calander_id" : "equipment_calibration_calendar_date", 
                 "timer_query" : queries.calibration["select"],
                 "store_setup" : Gtk.ListStore(str, str, str, str, str, str, str), 
                 "column_numbers" : (0,1,2,3,4,5,6),
                 "column_headings" : ["EAL Number", "Calibration Company", "Calibration Type", "Calibration Date", "Calibration Recall", "Calibration Expiry", "Calibration Certificate"],
                 "entries" : self.entries,
                 "file_chooser" : "equipment_calibration_file_certificate"}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
        Function.entry_completion(self, com_store, "equipment_calibration_entry_eal", 0)
        
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
        calibration_certificate = ''
        if self.file != None:
            file_name = text[0] + '_Cal_Cert-' + str(calibration_date)
            calibration_certificate = Function.file_path(self, 'Calibration Certificates', text[0], file_name, 'pdf')
            shutil.copy(self.file, calibration_certificate)
            self.file_chooser.unselect_all()
        else:
            calibration_certificate = "Not Uploaded"
        
        
        now = datetime.now()
        location = Function.get_entry(self, "equipment_calibration_entry_location")
        
        for item in self.current_items:
            row = list(item)
            if row[0] != text[0]:
                match = False
                
            elif row[0] == text[0]:
                match = True
                
        if match == True:
            query = self.queries.calibration["update"]
            utext = text[1:]
            utext.append(text[0])
            values = (now, utext[0], calibration_type, calibration_date, calibration_recall, calibration_expiry, calibration_certificate, utext[1])
            procedure = 'N/A'
            message = text[0] + ' updated field'
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[0], now, location, procedure, message)
            self.update(query, values, log_query, log_values)
            
        elif match == False:
            message = "Calibration certificate added."
            procedure = "N/A"
            values = (now, text[0], text[1], calibration_type, calibration_date, calibration_recall, calibration_expiry, calibration_certificate)
            log_values = (now, text[0], now, location, procedure, message)
            query = self.queries.calibration["insert"]
            log_query = self.queries.logbook["insert"]
            self.insert(query, values, log_query, log_values)
        
        Function.clear_entries(self, entries)
    
    def on_equipment_calibration_button_clear_clicked(self, equipment_calibration_button_clear):
        self.tree_selection.unselect_all()
        self.file_chooser.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_calibration_file_certificate_file_set(self, equipment_calibration_file_certificate):
        self.file_chooser = equipment_calibration_file_certificate
        self.file = self.file_chooser.get_filename()
    
    def on_equipment_calibration_entry_eal_changed(self, equipment_calibration_entry_eal):
        search = equipment_calibration_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_calibration_page_delete_event(self, *args):
        Gtk.main_quit(*args)  
        
class EquipProof(Widget):
    def __init__(self, queries, store_func, parent, com_store, proc_store):
        self.queries = queries
        self.entries = {"equipment_proof_entry_eal" : 0, "equipment_proof_entry_bar" : 1, "equipment_proof_entry_duration" : 2, "equipment_proof_entry_pt" : 3, "equipment_proof_entry_procedure" : 4, "equipment_proof_entry_location" : 8} 
        self.result = "Pass"
        
        setup = {"glade_file" : "Glade/equipment_proof.glade", 
                 "widget_id" :  "equipment_proof_page",
                 "widget_scroll_id" : "equipment_proof_scroll_window", 
                 "widget_calander_id" : "equipment_proof_calendar_date", 
                 "timer_query" : queries.proof["select"],
                 "store_setup" : Gtk.ListStore(str, int, int, str, str, str, str, str, str, str, str), 
                 "column_numbers" : (0,1,2,3,4,5,6,7,8,9,10),
                 "column_headings" : ["EAL Number", "Test Pressure", "Test Duration", "Transducer Number", "Procedure", "Proof Date", "Proof Recall", "Proof Expiry", "Test Location", "Result", "Proof Certificate"],
                 "entries" : self.entries, 
                 "file_chooser" : "equipment_proof_file_certificate"}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
        Function.entry_completion(self, com_store, "equipment_proof_entry_eal", 0)
        Function.entry_completion(self, com_store, "equipment_proof_entry_pt", 0)
        Function.entry_completion(self, proc_store, "equipment_proof_entry_procedure", 2)
        
    def on_equipment_proof_radio_pass_toggled(self, equipment_proof_radio_pass):
        self.result = "Pass"
    
    def on_equipment_proof_radio_fail_toggled(self, equipment_proof_radio_fail):
        self.result = "Fail"
    
    def on_equipment_proof_button_enter_clicked(self, equipment_proof_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        proof_date = Cal_Date.date(self, "equipment_proof_calendar_date")
        proof_expiry = Cal_Date.expiry(self, proof_date, 12)
        proof_recall = Cal_Date.recall(self, proof_expiry)
        
        proof_certificate = ''
        if self.file != None:
            file_name = text[0] + '_Proof_Cert-' + str(proof_date)
            proof_certificate = Function.file_path(self, 'Proof Certificates', text[0], file_name, 'pdf')
            shutil.copy(self.file, proof_certificate)
            self.file_chooser.unselect_all()
        else:
            proof_certificate = "Not Uploaded"
            
        now = datetime.now()
        
        for item in self.current_items:
            row = list(item)
            if row[0] != text[0]:
                match = False
                
            elif row[0] == text[0]:
                match = True
                
        if match == True:
            query = self.queries.proof["update"]
            utext = text[1:]
            utext.append(text[0])
            values = (now, utext[0], utext[1], utext[2], utext[3], proof_date, proof_recall, proof_expiry, utext[4], self.result, proof_certificate, utext[5])
            procedure = 'N/A'
            message = text[0] + ' updated field'
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[0], now, text[5], text[4], message)
            self.update(query, values, log_query, log_values)
            
        elif match == False:
            proof_message = "Proof certificate added."
            values = (now, text[0], text[1], text[2], text[3], text[4], proof_date, proof_recall, proof_expiry, text[5], self.result, proof_certificate)
            log_values = (now, text[0], now, text[5], text[4], proof_message)

            query = self.queries.proof["insert"]
            log_query = self.queries.logbook["insert"]
            self.insert(query, values, log_query, log_values)
        
        Function.clear_entries(self, entries)
        print ("Add")
    
    def on_equipment_proof_button_clear_clicked(self, equipment_proof_button_clear):
        self.tree_selection.unselect_all()
        self.file_chooser.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        
    def on_equipment_proof_file_certificate_file_set(self, equipment_proof_file_certificate):
        self.file_chooser = equipment_proof_file_certificate
        self.file = self.file_chooser.get_filename()
    
    def on_equipment_proof_entry_eal_changed(self, equipment_proof_entry_eal):
        search = equipment_proof_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_proof_page_delete_event(self, *args):
        Gtk.main_quit(*args)    
        
class EquipClean(Widget):
    def __init__(self, queries, store_func, parent, com_store, proc_store):
        self.queries = queries
        self.entries = {"equipment_cleanliness_entry_eal" : 0, "equipment_cleanliness_entry_pco" : 1, "equipment_cleanliness_entry_dew" : 2, "equipment_cleanliness_entry_procedure" : 3, "equipment_cleanliness_entry_location" : 7} 
        self.result = "Pass"
        
        setup = {"glade_file" : "Glade/equipment_cleanliness.glade", 
                 "widget_id" :  "equipment_cleanliness_page",
                 "widget_scroll_id" : "equipment_cleanliness_scroll_window", 
                 "widget_calander_id" : "equipment_cleanliness_calendar_date", 
                 "timer_query" : queries.cleanliness["select"],
                 "store_setup" : Gtk.ListStore(str, str, str, str, str, str, str, str, str, str), 
                 "column_numbers" : (0,1,2,3,4,5,6,7,8,9),
                 "column_headings" : ["EAL Number", "Particle Counter Number", "Dew Point Meter", "Procedure", "Cleanliness & Dryness Date", "Cleanliness & Dryness Recall", "Cleanliness & Dryness Expiry", "Test Location", "Result", "Proof Certificate"],
                 "entries" : self.entries, 
                 "file_chooser" : "equipment_cleanliness_file_certificate"}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
        Function.entry_completion(self, com_store, "equipment_cleanliness_entry_eal", 0)
        Function.entry_completion(self, com_store, "equipment_cleanliness_entry_pco", 0)
        Function.entry_completion(self, com_store, "equipment_cleanliness_entry_dew", 0)
        Function.entry_completion(self, proc_store, "equipment_cleanliness_entry_procedure", 2)
        
        
    def on_equipment_cleanliness_radio_pass_toggled(self, equipment_cleanliness_radio_pass):
        self.result = "Pass"
    
    def on_equipment_cleanliness_radio_fail_toggled(self, equipment_cleanliness_radio_fail):
        self.result = "Fail"
    
    def on_equipment_cleanliness_button_enter_clicked(self, equipment_cleanliness_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        clean_date = Cal_Date.date(self, "equipment_cleanliness_calendar_date")
        clean_expiry = Cal_Date.expiry(self, clean_date, 12)
        clean_recall = Cal_Date.recall(self, clean_expiry)
        
        clean_certificate = ''
        if self.file != None:
            file_name = text[0] + '_C&D_Cert-' + str(clean_date)
            clean_certificate = Function.file_path(self, 'Cleanliness & Dryness Certificates', text[0], file_name, 'pdf')
            shutil.copy(self.file, clean_certificate)
            self.file_chooser.unselect_all()
        else:
            clean_certificate = "Not Uploaded"
            
        now = datetime.now()
        for item in self.current_items:
            row = list(item)
            if row[0] != text[0]:
                match = False
                
            elif row[0] == text[0]:
                match = True
                
        if match == True:
            query = self.queries.cleanliness["update"]
            utext = text[1:]
            utext.append(text[0])
            values = (now, utext[0], utext[1], utext[2], clean_date, clean_recall, clean_expiry, utext[3], self.result, clean_certificate, utext[4])
            procedure = 'N/A'
            message = text[0] + ' updated field'
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[0], now, text[4], text[3], message)
            self.update(query, values, log_query, log_values)
            
        elif match == False:
            message = "Cleanliness & Dryness certificate added."
        
            values = (now, text[0], text[1], text[2], text[3], clean_date, clean_recall, clean_expiry, text[4], self.result, clean_certificate)
        
            log_values = (now, text[0], now, text[4], text[3], message)
            query = self.queries.cleanliness["insert"]
        
            log_query = self.queries.logbook["insert"]
            self.insert(query, values, log_query, log_values)
        
        Function.clear_entries(self, entries)
    
    def on_equipment_cleanliness_button_clear_clicked(self, equipment_cleanliness_button_clear):
        self.tree_selection.unselect_all()
        self.file_chooser.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        print ("Clear")
        
    def on_equipment_cleanliness_file_certificate_file_set(self, equipment_cleanliness_file_certificate):
        self.file_chooser = equipment_cleanliness_file_certificate
        self.file = self.file_chooser.get_filename()
    
    def on_equipment_cleanliness_entry_eal_changed(self, equipment_cleanliness_entry_eal):
        search = equipment_cleanliness_entry_eal.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
        
    def on_equipment_cleanliness_page_delete_event(self, *args):
        Gtk.main_quit(*args) 
        
class EquipSearch(Widget):
    def __init__(self, queries, store_func, parent):
        self.queries = queries
        self.entries = {"equipment_search_entry_search" : 0}
        
        setup = {"glade_file" : "Glade/equipment_search.glade", 
                 "widget_id" :  "equipment_search_page",
                 "widget_scroll_id" : "equipment_search_scroll_window", 
                 "widget_calander_id" : None, 
                 "timer_query" : queries.overview["select"],
                 "store_setup" : Gtk.ListStore(str, str, str, str, str, str, str), 
                 "column_numbers" : (0,1,2,3,4,5,6),
                 "column_headings" : ["EAL Number", "Equipment Type", "Serial Number", "Calibration Expiry", "Proof Expiry", "Cleanliness Expiry", "Current Location"],
                 "entries" : self.entries, 
                 "file_chooser" : None}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
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
        
class Log(Widget):
    def __init__(self, queries, store_func, parent, com_store, proc_store):
        self.queries = queries
        self.entries = {"equipment_log_entry_eal" : 0, "equipment_log_entry_from" : 2, "equipment_log_entry_procedure" : 3, "equipment_log_entry_message" : 4} 
        
        setup = {"glade_file" : "Glade/equipment_log.glade", 
                 "widget_id" :  "equipment_log_page",
                 "widget_scroll_id" : "equipment_log_scroll_window", 
                 "widget_calander_id" : "equipment_log_calendar_date", 
                 "timer_query" : queries.logbook["select"],
                 "store_setup" : Gtk.ListStore(str, str, str, str, str), 
                 "column_numbers" : (0,1,2,3,4),
                 "column_headings" : ["EAL Number", "Log Date", "Location", "Documents", "Message"],
                 "entries" : self.entries, 
                 "file_chooser" : None}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
        Function.entry_completion(self, com_store, "equipment_log_entry_eal", 0)
        Function.entry_completion(self, proc_store, "equipment_log_entry_procedure", 2)
        
    def on_equipment_log_button_enter_clicked(self, equipment_log_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        log_date = Cal_Date.date(self, "equipment_log_calendar_date")
        now = datetime.now()
        log_values = (now, text[0], log_date, text[1], text[2], text[3])
        log_query = self.queries.logbook["insert"]
        self.log_insert(log_query, log_values)
        
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
        
class DocAdd(Widget):
    def __init__(self, queries, store_func, parent):
        self.queries = queries
        self.entries = {"documents_add_entry_for" : 0, "documents_add_entry_ref" : 1, "documents_add_entry_name" : 2, "documents_add_entry_issue" : 3, "documents_add_entry_reason" : 4}
        
        setup = {"glade_file" : "Glade/documents.glade", 
                 "widget_id" :  "documents_add_page",
                 "widget_scroll_id" : "documents_add_scroll_window", 
                 "widget_calander_id" : "documents_add_calendar_date", 
                 "timer_query" : queries.documents["select"],
                 "store_setup" : Gtk.ListStore(str, str, str, int, str, str, str), 
                 "column_numbers" : (0,1,2,3,4,5,6),
                 "column_headings" : ["Client", "Reference", "Name", "Issue", "Reason for Issue", "Date", "File"],
                 "entries" : self.entries, 
                 "file_chooser" : "documents_add_file_path"}
        
        Widget.__init__(self, store_func, parent, queries, **setup)
        
        Function.entry_completion(self, self.store, "documents_add_entry_for", 0)
        Function.entry_completion(self, self.store, "documents_add_entry_ref", 1)
        Function.entry_completion(self, self.store, "documents_add_entry_name", 2)
        
    def on_documents_add_button_enter_clicked(self, documents_add_button_enter):
        entries = self.entries
        text = Function.get_entries(self, entries)
        date = Cal_Date.date(self, "documents_add_calendar_date")
        
        doc = ''
        if self.file != None:
            file_name = text[2]
            doc = Function.file_path(self, 'Documents', text[0], file_name, 'pdf')
            shutil.copy(self.file, doc)
            self.file_chooser.unselect_all()
        else:
            doc = "Not Uploaded"
            
        now = datetime.now()
        for item in self.current_items:
            row = list(item)
            if row[1] != text[1]:
                match = False
                
            elif row[1] == text[1]:
                match = True
                
        if match == True:
            query = self.queries.documents["update"]
            values = (now, text[0], text[2], text[3], text[4], date, doc, text[1])
            procedure = 'N/A'
            message = text[1] + ' updated field'
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[0], now, text[4], text[3], message)
            self.update(query, values, log_query, log_values)
            
        elif match == False:
            query = self.queries.documents["insert"]
            values = (now, text[0], text[1], text[2], text[3], text[4], date, doc)
            log_query = self.queries.logbook["insert"]
            log_values = (now, text[1], date, "N/A", text[2], text[4])
            self.insert(query, values, log_query, log_values)
        Function.clear_entries(self, entries)
        
    def on_documents_add_button_clear_clicked(self, documents_add_button_clear):
        self.tree_selection.unselect_all()
        self.file_chooser.unselect_all()
        entries = self.entries
        Function.clear_entries(self, entries)
        self.current_filter = None
        
    def on_documents_add_file_path_file_set(self, documents_add_file_path):
        self.file_chooser = documents_add_file_path
        self.file = self.file_chooser.get_filename()
        
    def on_documents_add_entry_ref_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 1
        self.filter.refilter()
        
    def on_documents_add_entry_for_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 0
        self.filter.refilter()
    
    def on_documents_add_entry_name_changed(self, entry):
        search = entry.get_text()
        self.current_filter = search.upper()
        self.current_filter_column = 2
        self.filter.refilter()
        
        on_documents_add_entry_name_changed
    
    def on_documents_add_page_delete_event(self, *args):
        Gtk.main_quit(*args)
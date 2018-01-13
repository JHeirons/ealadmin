import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from dateutil.relativedelta import *
from datetime import *
import mysql.connector

import os


class Function:
    def __init__(self):
        self.builder = Gtk.Builder()
        
    def get_entry(self, entry):
        entry_to_get = self.builder.get_object(entry)
        entry_text = entry_to_get.get_text()
        print(entry_text)
        return entry_text
    
    def get_entries(self, entries):
        entered_text = {}
        for entry in entries:
            #name = entry
            entered_text[entry] = Function.get_entry(self, entries[entry])
        
        return entered_text
    
    def set_entry(self, entry, text):
        entry_to_set = self.builder.get_object(entry)
        set_text = entry_to_set.set_text(text)
        return text
        
    def set_entries(self, entries, text):
        set_entries = {}
        for i, entry in enumerate(entries):
            set_entries[entry] = Function.set_entry(self, entries[entry], text[i])
        return set_entries
    
    def clear_entries(self, entries):
        entries_to_clear = entries
        text = ['']*len(entries_to_clear)
        Function.set_entries(self, entries_to_clear, text)
    
    
    def entry_completion(self, model, entry, column):
        entry_to_complete = self.builder.get_object(entry)
        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        entry_to_complete.set_completion(completion)
        completion.set_text_column(column)
        
    def push_item(self, text, data):
        buff = text
        self.status_bar.push(data, buff)
        return

    def pop_item(self, data):
        self.status_bar.pop(data)
        return
    
    def file_path(self, dept_folder, sub_folder, name, file_format):
        slash = '/'
        dot = '.'
        #path_root = '//EALSERVER/Jonathan Folder/Admin_Test/'
        path_root = "Documents/Programming/Brackets/ealadmin/"
        #check path existance
        dept_folder_path = path_root + dept_folder 
        folder_path = dept_folder_path + slash + sub_folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        full_path = folder_path + slash + name + dot + file_format
        
        return full_path

class Cal_Date:
    def __init__(self):
        self.builder = Gtk.Builder()
        
    def date(self, calender_object):
        print ("cal function")
        calender = self.builder.get_object(calender_object)
        test_date = calender.get_date()
        month = test_date.month + 1
        date_str = str(test_date.day) + '/' + str(month) + '/' + str(test_date.year)
       
        cal_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        return cal_date
        
        
    def expiry(self, initial_date, length):
        expiry_date = initial_date + relativedelta(months=+length)
        return expiry_date
    
    def recall(self, expiry_date):
        recall_date = expiry_date - relativedelta(months=+1)
        return recall_date

    
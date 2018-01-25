import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from dateutil.relativedelta import *
from datetime import datetime, date

import os


class Function:
    def __init__(self):
        self.builder = Gtk.Builder()
        
    def get_entry(self, entry):
        entry_to_get = self.builder.get_object(entry)
        entry_text = entry_to_get.get_text()
        return entry_text
    
    def get_entries(self, entries):
        text = []
        for i in range(len(entries)):
            values = Function.get_entry(self, entries[i])
            text.append(str(values))
        return text
    
    def set_entry(self, entry, text):
        entry_to_set = self.builder.get_object(entry)
        set_text = str(entry_to_set.set_text(text))
        return text
        
    def set_entries(self, entries, text):
        for entry in entries:
            t = str(text[entries[entry]])
            Function.set_entry(self, entry, t)
    
    def clear_entries(self, entries):
        for entry in entries:
            Function.set_entry(self, entry, '')
        
    def entry_completion(self, model, entry, column):
        entry_to_complete = self.builder.get_object(entry)
        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(column)
        entry_to_complete.set_completion(completion)
        
    def file_path(self, dept_folder, sub_folder, name, file_format):
        #slash = '\\'
        slash = '/'
        dot = '.'
        #path_root = '\\\\EALSERVER\\Jonathan Folder\\Admin_Test\\'
        path_root = "Documents/Programming/Brackets/ealadmin/"
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
        calender = self.builder.get_object(calender_object)
        test_date = calender.get_date()
        month = test_date.month + 1
        date_str = str(test_date.day) + '/' + str(month) + '/' + str(test_date.year)
       
        cal_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        return cal_date
    
    def set_date(self, calander_object, date):
        day = int(date[0:2])
        month = int(date[3:5])-1
        year = int(date[6:10])
        calender = calander_object
        calender.select_day(day)
        calender.select_month(month, year)
        
        
    def expiry(self, initial_date, length):
        expiry_date = initial_date + relativedelta(months=+length)
        return expiry_date
    
    def recall(self, expiry_date):
        recall_date = expiry_date - relativedelta(months=+1)
        return recall_date

    
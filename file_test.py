from dateutil.relativedelta import *
from datetime import datetime, date
import os
import shutil

root = '/Volumes/Jonathan Folder/Admin_Test'
file_loc = '/Users/Home/Documents/Programming/Brackets/ealadmin/file.pdf'

new_name = "/test.pdf"

new_loc = root + '/sub_folder1/subfolder2'



if not os.path.exists(new_loc):
    print("make folders")
    os.makedirs(new_loc)
    
new_file = new_loc + new_name    
shutil.copy(file_loc, new_file)
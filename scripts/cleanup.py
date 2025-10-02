import os
import shutil

def cleanup():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(parent_dir, "data")
    diff_dir = os.path.join(data_dir, "diff")


    if os.path.exists(diff_dir):
        for filename in os.listdir(diff_dir):
            file_path = os.path.join(diff_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    
    

    
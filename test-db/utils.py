# Utilities functions
import uuid
import os

def create_bug_folder():
    folder_name = "bug_" + uuid.uuid4().hex

    folder_path = "./bugs/" + folder_name

    os.makedirs(folder_path)
    
    return folder_path

def write_file(path, filename, content):
    with open(os.path.join(path, filename), "w") as f:
        f.write(content)
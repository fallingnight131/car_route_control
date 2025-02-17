import os
import ast
import json

def save_track_data(file_path, track_outer, track_inner, check_line):
    data = {
        "track_outer": track_outer,
        "track_inner": track_inner,
        "check_line": check_line
    }
    
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load_track_data(file_path):
    if not os.path.exists(file_path):
        return [], [], []
    
    with open(file_path, "r") as f:
        data = json.load(f)
    
    return data.get("track_outer", []), data.get("track_inner", []), data.get("check_line", [])
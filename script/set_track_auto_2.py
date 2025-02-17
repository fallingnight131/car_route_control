import os
import sys
# 添加根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.util.track_file_util import save_track_data

track_outer = [(150, 150), (650, 150), (700, 250), (700, 300), (600, 400), (500, 450), 
               (400, 500), (300, 450), (200, 400), (100, 300), (100, 200)]
track_inner = [(200, 200), (600, 200), (650, 250), (600, 350), (500, 400), (400, 450), 
               (300, 400), (200, 350), (150, 250), (200, 200)]
check_line = []

save_track_data("src/config/track_info/auto_2.json", track_outer, track_inner, check_line)
print("Track data saved to src/config/track_info/auto_2.json")

# src/data_core.py
import json, os
import win32gui
from datetime import datetime, timedelta
from .config import DATA_FILE

class DataCore:
    def __init__(self):
        self.data = self._load()
        self.today = datetime.now().strftime("%Y-%m-%d")
        self._init_today()

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f)

    def _init_today(self):
        if self.today not in self.data:
            self.data[self.today] = {
                "mouse": {"l":0, "r":0, "dist":0},
                "key_count": 0,
                "regret": 0,      # 后悔率
                "copy_paste": 0,  # 灵魂指标
                "keys": {},
                "apps": {},
                "timeline": [0]*24,
                "trajectory": []
            }

    def update_mouse(self, key, val=1):
        self.data[self.today]["mouse"][key] += val
    
    def update_dist(self, val, x, y):
        self.data[self.today]["mouse"]["dist"] += val
        try:
            s_w, s_h = win32gui.GetWindowRect(win32gui.GetDesktopWindow())[2:]
            if s_w > 0 and s_h > 0:
                norm_x, norm_y = round(x/s_w, 3), round(y/s_h, 3)
                traj = self.data[self.today]["trajectory"]
                traj.append([norm_x, norm_y])
                if len(traj) > 2000: traj.pop(0)
        except: pass

    def update_key(self, key):
        self.data[self.today]["key_count"] += 1
        k = str(key).upper()
        self.data[self.today]["keys"][k] = self.data[self.today]["keys"].get(k, 0) + 1
        
        h = datetime.now().hour
        if "timeline" not in self.data[self.today]: 
            self.data[self.today]["timeline"] = [0]*24
        self.data[self.today]["timeline"][h] += 1

    def update_special(self, type_name):
        self.data[self.today][type_name] = self.data[self.today].get(type_name, 0) + 1

    def log_app(self, app_name):
        self.data[self.today]["apps"][app_name] = self.data[self.today]["apps"].get(app_name, 0) + 1

    def get_stats(self, mode):
        res = {"mouse":{"l":0,"r":0,"dist":0}, "key_count":0, "regret":0, "copy_paste":0, "keys":{}, "apps":{}, "timeline":[0]*24, "trajectory":[]}
        dates = [self.today]
        if mode == 1: # Weekly
             start = datetime.now() - timedelta(days=datetime.now().weekday())
             dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        
        for d in dates:
            if d in self.data:
                src = self.data[d]
                for k in ["l","r","dist"]: res["mouse"][k] += src["mouse"].get(k,0)
                res["key_count"] += src.get("key_count",0)
                res["regret"] += src.get("regret",0)
                res["copy_paste"] += src.get("copy_paste",0)
                for k,v in src.get("keys",{}).items(): res["keys"][k] = res["keys"].get(k,0)+v
                for k,v in src.get("apps",{}).items(): res["apps"][k] = res["apps"].get(k,0)+v
                for i in range(24): res["timeline"][i] += src.get("timeline",[0]*24)[i]
                if d == self.today: res["trajectory"] = src.get("trajectory", [])
        return res
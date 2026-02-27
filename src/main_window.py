# src/main_window.py
import math, time, psutil
import win32gui
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pynput import mouse, keyboard

from .config import THEME, STYLESHEET
from .data_core import DataCore
from .components import TrajectoryCanvas, BioClockWidget, MiniWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.core = DataCore()
        self.last_pos = (0,0)
        self.apm_q = deque(maxlen=60)
        self.net_io = psutil.net_io_counters()
        self.ctrl_pressed = False
        self.mode = 0 
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1200, 800)
        
        self.mini = MiniWindow(); self.mini.restore.connect(self.restore_win)
        self.init_tray()
        self.setup_ui()
        self.start_listeners()
        
        self.timer = QTimer(); self.timer.timeout.connect(self.tick); self.timer.start(1000)

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        p = QPixmap(16,16); p.fill(QColor(THEME['cyan'])); self.tray.setIcon(QIcon(p))
        m = QMenu(); m.addAction("Open", self.restore_win); m.addAction("Exit", self.close_app)
        self.tray.setContextMenu(m); self.tray.show()
        self.tray.activated.connect(lambda r: self.restore_win() if r==QSystemTrayIcon.DoubleClick else None)

    def setup_ui(self):
        w = QWidget(); self.setCentralWidget(w)
        lay = QHBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)

        # Sidebar
        side = QFrame(); side.setStyleSheet(f"background:#08080a; border-right:1px solid {THEME['border']};")
        side.setFixedWidth(220)
        sv = QVBoxLayout(side); sv.setContentsMargins(15,40,15,20); sv.setSpacing(10)
        
        logo = QLabel("GOD MODE"); logo.setStyleSheet(f"color:{THEME['cyan']}; font-size:24px; font-weight:900; letter-spacing:2px;")
        sv.addWidget(logo); sv.addSpacing(40)
        
        self.bg = QButtonGroup()
        for i,t in enumerate(["DASHBOARD", "WEEKLY", "YEARLY"]):
            b = QPushButton(t); b.setObjectName("TabBtn"); b.setCheckable(True)
            if i==0: b.setChecked(True)
            b.clicked.connect(lambda _,x=i: self.set_mode(x))
            self.bg.addButton(b); sv.addWidget(b)
        sv.addStretch()
        
        # Sys Info
        sys_f = QFrame(); sys_f.setStyleSheet(f"background:#101012; border-radius:8px; padding:15px; border:1px solid {THEME['border']};")
        sl = QVBoxLayout(sys_f)
        self.l_cpu = QLabel("CPU: 0%"); self.l_cpu.setStyleSheet("color:#888; font-size:13px; font-weight:bold;")
        self.l_ram = QLabel("RAM: 0%"); self.l_ram.setStyleSheet("color:#888; font-size:13px; font-weight:bold;")
        sl.addWidget(self.l_cpu); sl.addWidget(self.l_ram); sv.addWidget(sys_f)
        
        min_b = QPushButton("MINIMIZE (悬浮)"); min_b.setObjectName("TabBtn"); min_b.clicked.connect(self.to_mini); sv.addWidget(min_b)
        exit_b = QPushButton("EXIT"); exit_b.setObjectName("TabBtn"); exit_b.setStyleSheet(f"color:{THEME['pink']}"); exit_b.clicked.connect(self.close_app); sv.addWidget(exit_b)
        lay.addWidget(side)

        # Content
        cont = QWidget(); cont.setStyleSheet(f"background:{THEME['bg']};")
        cv = QVBoxLayout(cont); cv.setContentsMargins(30,30,30,30); cv.setSpacing(20)
        
        # Row 1: Key Metrics
        r1 = QGridLayout(); r1.setSpacing(15)
        self.cards = {}
        metrics = [
            ("l", "LEFT CLICK", "Value", ""), ("r", "RIGHT CLICK", "Value", ""),
            ("k", "TOTAL KEYS", "ValCyan", "presses"), ("d", "DISTANCE", "Value", "meters"),
            ("regret", "REGRET RATE", "ValPink", "backspaces"), ("cp", "COPY / PASTE", "ValYellow", "times")
        ]
        for idx, (k, t, s, u) in enumerate(metrics):
            f = QFrame(); f.setObjectName("Panel"); f.setFixedHeight(110)
            v = QVBoxLayout(f); v.setContentsMargins(20,15,20,15)
            v.addWidget(QLabel(t, objectName="Title"))
            val = QLabel("0", objectName=s); v.addWidget(val)
            if u: v.addWidget(QLabel(u, objectName="Unit"), alignment=Qt.AlignRight)
            r1.addWidget(f, idx//3, idx%3)
            self.cards[k] = val
        cv.addLayout(r1)

        # Row 2: Visuals
        r2 = QHBoxLayout(); r2.setSpacing(15)
        
        # Apps
        app_f = QFrame(); app_f.setObjectName("Panel"); app_f.setFixedWidth(260)
        av = QVBoxLayout(app_f)
        av.addWidget(QLabel("ACTIVE APPS", objectName="Title"))
        self.app_list = QListWidget(); av.addWidget(self.app_list)
        r2.addWidget(app_f)
        
        # Canvas
        traj_f = QFrame(); traj_f.setObjectName("Panel")
        tv = QVBoxLayout(traj_f); tv.setContentsMargins(1,1,1,1)
        self.canvas = TrajectoryCanvas(); tv.addWidget(self.canvas)
        r2.addWidget(traj_f, stretch=1)
        
        # Bio
        bio_f = QFrame(); bio_f.setObjectName("Panel"); bio_f.setFixedWidth(260)
        bv = QVBoxLayout(bio_f)
        bv.addWidget(QLabel("BIO RHYTHM (24H)", objectName="Title"))
        self.bio_chart = BioClockWidget(); bv.addWidget(self.bio_chart)
        self.l_net = QLabel("↓ 0KB/s", styleSheet=f"color:{THEME['cyan']}; font-weight:bold; font-size:16px; margin-top:15px;")
        bv.addWidget(self.l_net, alignment=Qt.AlignCenter)
        r2.addWidget(bio_f)
        
        cv.addLayout(r2, stretch=1)

        # Row 3: Keyboard
        kb_f = QFrame(); kb_f.setObjectName("Panel"); kb_f.setFixedHeight(240)
        kv = QVBoxLayout(kb_f)
        kv.addWidget(QLabel("MECHANICAL HEATMAP", objectName="Title"))
        self.kb_widgets = {}
        grid = QGridLayout(); grid.setSpacing(5)
        keys_ly = [
            ["ESC","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","DEL"],
            ["`","1","2","3","4","5","6","7","8","9","0","-","=","BACK"],
            ["TAB","Q","W","E","R","T","Y","U","I","O","P","[","]","\\"],
            ["CAPS","A","S","D","F","G","H","J","K","L",";","'","ENTER"],
            ["SHIFT","Z","X","C","V","B","N","M",",",".","/","SHIFT"],
            ["CTRL","WIN","ALT","SPACE","ALT","FN","CTRL"]
        ]
        for r, row in enumerate(keys_ly):
            for c, k in enumerate(row):
                lbl = QLabel(f"{k}"); lbl.setObjectName("KeyBox")
                w = 48
                if k in ["BACK","TAB","CAPS","ENTER","SHIFT"]: w = 75
                if k == "SPACE": w = 240
                lbl.setFixedSize(w, 32)
                grid.addWidget(lbl, r, c); self.kb_widgets[k] = lbl
        kv.addLayout(grid)
        cv.addWidget(kb_f)
        lay.addWidget(cont)
        self.setStyleSheet(STYLESHEET)

    def set_mode(self, x): self.mode=x; self.refresh()

    def start_listeners(self):
        def on_c(x,y,b,p):
            if p: 
                self.apm_q.append(time.time()); self.core.update_mouse("l" if b==mouse.Button.left else "r")
        def on_m(x,y):
            d = math.hypot(x-self.last_pos[0], y-self.last_pos[1])
            self.core.update_dist(d*0.00026, x, y); self.last_pos = (x,y)
        def on_k(k):
            self.apm_q.append(time.time())
            try: char = k.char.upper()
            except: char = str(k).replace("Key.","").upper()
            
            if "CTRL" in char: self.ctrl_pressed = True
            if "BACKSPACE" in char: char = "BACK"; self.core.update_special("regret")
            if "DELETE" in char: char = "DEL"; self.core.update_special("regret")
            
            if self.ctrl_pressed and char in ['C', 'V']: 
                self.core.update_special("copy_paste")
            
            if "ENTER" in char: char = "ENTER"
            if "SHIFT" in char: char = "SHIFT"
            if "ALT" in char: char = "ALT"
            
            self.core.update_key(char)

        def on_kr(k):
             try: 
                 if "ctrl" in str(k).lower(): self.ctrl_pressed = False
             except: pass

        self.ml = mouse.Listener(on_click=on_c, on_move=on_m)
        self.kl = keyboard.Listener(on_press=on_k, on_release=on_kr)
        self.ml.start(); self.kl.start()

    def tick(self):
        cpu = psutil.cpu_percent(); ram = psutil.virtual_memory().percent
        self.l_cpu.setText(f"CPU: {cpu}%"); self.l_ram.setText(f"RAM: {ram}%")
        
        nn = psutil.net_io_counters(); s=(nn.bytes_sent-self.net_io.bytes_sent)/1024; r=(nn.bytes_recv-self.net_io.bytes_recv)/1024
        self.net_io = nn; net_str = f"↓{r:.0f}K  ↑{s:.0f}K"
        self.l_net.setText(net_str)
        
        try:
            h = win32gui.GetForegroundWindow(); a = win32gui.GetWindowText(h).split("-")[-1].strip()
            if a: self.core.log_app(a)
        except: pass

        now = time.time()
        while self.apm_q and now - self.apm_q[0] > 60: self.apm_q.popleft()
        apm = len(self.apm_q)

        self.core.save(); self.refresh()
        if self.mini.isVisible(): self.mini.update_s(f"NET: {net_str} | APM: {apm}")

    def refresh(self):
        d = self.core.get_stats(self.mode)
        self.cards['l'].setText(f"{d['mouse']['l']:,}")
        self.cards['r'].setText(f"{d['mouse']['r']:,}")
        self.cards['d'].setText(f"{d['mouse']['dist']:.1f}")
        self.cards['k'].setText(f"{d['key_count']:,}")
        
        self.cards['regret'].setText(f"{d['regret']:,}")
        self.cards['cp'].setText(f"{d['copy_paste']:,}")

        self.app_list.clear()
        for a,v in sorted(d['apps'].items(), key=lambda x:x[1], reverse=True)[:8]:
            if len(a)>1: self.app_list.addItem(f"{a} ({v})")

        self.canvas.set_points(d['trajectory'])
        self.bio_chart.set_data(d['timeline'])

        max_k = max(d['keys'].values()) if d['keys'] else 1
        for k, lbl in self.kb_widgets.items():
            val = d['keys'].get(k, 0)
            if val > 0:
                alpha = int((val/max_k)*200) + 40
                lbl.setStyleSheet(f"background-color: rgba(0, 243, 255, {alpha/255}); color:#000; border-radius:6px;")
            else:
                lbl.setStyleSheet(f"background-color: #1a1a1d; color:{THEME['dim']}; border-radius:6px;")

    def to_mini(self):
        self.hide(); sg = QApplication.primaryScreen().availableGeometry()
        self.mini.move(sg.width()-240, sg.height()-120); self.mini.show()
    def restore_win(self): self.mini.hide(); self.showNormal(); self.activateWindow()
    def close_app(self): self.core.save(); QApplication.quit()
    def mousePressEvent(self, e): 
        if e.button()==Qt.LeftButton: self.dp=e.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e): 
        if e.buttons()==Qt.LeftButton: self.move(e.globalPos()-self.dp)
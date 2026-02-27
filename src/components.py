# src/components.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .config import THEME

class TrajectoryCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []
    
    def set_points(self, points):
        self.points = points
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        p.fillRect(self.rect(), QColor("#08080a"))
        pen_grid = QPen(QColor("#1a1a1d")); pen_grid.setStyle(Qt.DotLine)
        p.setPen(pen_grid)
        w, h = self.width(), self.height()
        for i in range(0, w, 40): p.drawLine(i, 0, i, h)
        for i in range(0, h, 40): p.drawLine(0, i, w, i)

        if not self.points: return

        path = QPainterPath()
        start = self.points[0]
        path.moveTo(start[0]*w, start[1]*h)
        for pt in self.points[1:]:
            path.lineTo(pt[0]*w, pt[1]*h)
        
        glow_pen = QPen(QColor(THEME['cyan'])); glow_pen.setWidth(4); glow_pen.setJoinStyle(Qt.RoundJoin)
        glow_pen.setColor(QColor(0, 243, 255, 50))
        p.setPen(glow_pen); p.drawPath(path)
        
        core_pen = QPen(QColor(THEME['cyan'])); core_pen.setWidth(1)
        p.setPen(core_pen); p.drawPath(path)

class BioClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = [0]*24
    
    def set_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bar_w = w / 24
        max_v = max(self.data) if max(self.data) > 0 else 1
        
        for i, val in enumerate(self.data):
            bar_h = (val / max_v) * (h - 20)
            x = i * bar_w
            y = h - bar_h
            
            color = QColor(THEME['cyan'])
            if val > max_v * 0.7: color = QColor(THEME['pink'])
            elif val > max_v * 0.4: color = QColor("#bd00ff")
            
            p.fillRect(QRectF(x+2, y, bar_w-4, bar_h), color)
            
            if i % 6 == 0:
                p.setPen(QColor(THEME['dim']))
                p.drawText(QRectF(x, h-15, 30, 15), Qt.AlignCenter, f"{i}:00")

class MiniWindow(QWidget):
    restore = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setObjectName("MiniWidget")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(200, 45)
        l = QHBoxLayout(self); l.setContentsMargins(15,0,15,0)
        l.addWidget(QLabel("●", styleSheet=f"color:{THEME['cyan']}; font-size:14px;")) 
        self.lbl = QLabel("Monitoring...", objectName="MiniText"); self.lbl.setAlignment(Qt.AlignCenter)
        l.addWidget(self.lbl)

    def update_s(self, txt): self.lbl.setText(txt)
    def mouseDoubleClickEvent(self, e): self.restore.emit()
    def mousePressEvent(self, e): 
        if e.button()==Qt.LeftButton: self.dp=e.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self, e): 
        if e.buttons()==Qt.LeftButton: self.move(e.globalPos()-self.dp)
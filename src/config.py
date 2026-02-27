# src/config.py
import os

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
DATA_FILE = os.path.join(DATA_DIR, "godmode_data.json")

# 配色方案 (Cyberpunk Neon)
THEME = {
    "bg": "#050505", 
    "panel": "#101012", 
    "border": "#27272a",
    "cyan": "#00f3ff",  # 赛博蓝
    "pink": "#ff0055",  # 霓虹粉
    "yellow": "#fcee0a",# 警告黄
    "text": "#ffffff",
    "dim": "#888888"
}

# 样式表
STYLESHEET = f"""
QMainWindow {{ background: {THEME['bg']}; }}
QToolTip {{ background: {THEME['panel']}; color: {THEME['text']}; border: 1px solid {THEME['cyan']}; }}

/* 悬浮窗 */
#MiniWidget {{
    background: rgba(16, 16, 18, 240);
    border: 2px solid {THEME['cyan']};
    border-radius: 20px;
}}
#MiniText {{ color: {THEME['cyan']}; font-weight: bold; font-family: 'Segoe UI'; font-size: 14px; }}

/* 通用面板 */
QFrame#Panel {{ 
    background: {THEME['panel']}; 
    border-radius: 12px; 
    border: 1px solid {THEME['border']}; 
}}
QFrame#Panel:hover {{ border: 1px solid {THEME['cyan']}; }}

/* 字体放大区 */
QLabel#Title {{ color: {THEME['dim']}; font-size: 12px; font-weight: bold; letter-spacing: 1px; }}
QLabel#Value {{ color: {THEME['text']}; font-size: 28px; font-weight: bold; font-family: 'Consolas'; }}
QLabel#Unit {{ color: {THEME['dim']}; font-size: 12px; margin-bottom: 5px; }}

QLabel#ValCyan {{ color: {THEME['cyan']}; font-size: 28px; font-weight: bold; font-family: 'Consolas'; }}
QLabel#ValPink {{ color: {THEME['pink']}; font-size: 28px; font-weight: bold; font-family: 'Consolas'; }}
QLabel#ValYellow {{ color: {THEME['yellow']}; font-size: 28px; font-weight: bold; font-family: 'Consolas'; }}

/* 键盘按键 */
QLabel#KeyBox {{
    background-color: #1a1a1d;
    border-radius: 6px;
    color: {THEME['dim']};
    font-size: 11px;
    font-weight: bold;
    qproperty-alignment: AlignCenter;
}}

/* 侧边栏按钮 */
QPushButton#TabBtn {{
    background: transparent; border: none; color: {THEME['dim']}; text-align: left;
    padding: 15px 20px; border-radius: 8px; font-weight: bold; font-family: 'Segoe UI'; font-size: 14px;
}}
QPushButton#TabBtn:hover {{ background: #1a1a1d; color: {THEME['text']}; }}
QPushButton#TabBtn:checked {{ background: rgba(0, 243, 255, 0.1); color: {THEME['cyan']}; border-left: 4px solid {THEME['cyan']}; }}

QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{ color: {THEME['text']}; padding: 8px; border-bottom: 1px solid #1a1a1d; font-size: 13px; }}
"""
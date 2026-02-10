import sys
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QWidget, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame, QSpinBox)
from PyQt6.QtCore import Qt, QTimer

# --- 配置 ---
STORAGE_FILE = "notes.json"
DEFAULT_LOCK_HOURS = 5  # 默认锁定时间
DOCK_WIDTH = 15         
EXPAND_WIDTH = 380      
HEIGHT = 600            
# -----------

class VibeNote(QWidget):
    def __init__(self):
        super().__init__()
        self.lock_hours = DEFAULT_LOCK_HOURS # 将常量变为变量
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width()//2 - 150, screen.height()//2 - 200, 300, 400)
        print("窗口已启动...")
        
        QTimer.singleShot(500, self.dock)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.container = QWidget()
        self.container.setObjectName("MainBox")
        self.container.setStyleSheet("""
            #MainBox {
                background-color: rgba(25, 25, 25, 245);
                border-left: 5px solid #00bcd4;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        self.inner_layout = QVBoxLayout(self.container)
        
        # --- 新增：设置/调整板块 ---
        self.settings_layout = QHBoxLayout()
        self.lbl_setting = QLabel("锁定时长 (h):")
        self.lbl_setting.setStyleSheet("color: #666; font-size: 11px;")
        
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 720) # 最高支持30天
        self.hour_spin.setValue(self.lock_hours)
        self.hour_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons) # 极简外观
        self.hour_spin.setStyleSheet("""
            QSpinBox {
                background: rgba(255,255,255,15);
                color: #00bcd4;
                border: none;
                border-radius: 3px;
                padding: 0 5px;
                font-size: 11px;
                width: 30px;
            }
        """)
        self.hour_spin.valueChanged.connect(self.update_lock_hours)
        
        self.settings_layout.addWidget(self.lbl_setting)
        self.settings_layout.addWidget(self.hour_spin)
        self.settings_layout.addStretch()
        self.inner_layout.addLayout(self.settings_layout)
        # ------------------------

        self.lbl_info = QLabel("✍️ 记录灵感 (Ctrl+Enter 存入)")
        self.lbl_info.setStyleSheet("color: #00bcd4; font-weight: bold; font-size: 12px;")
        self.inner_layout.addWidget(self.lbl_info)
        
        self.editor = QTextEdit()
        self.editor.setFixedHeight(80)
        self.editor.setPlaceholderText(f"想法将在锁定时间后解锁...")
        self.editor.setStyleSheet("background: rgba(255,255,255,10); color: white; border: none; border-radius: 5px; padding: 5px; font-size: 13px;")
        self.inner_layout.addWidget(self.editor)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #444; margin-top: 10px; margin-bottom: 10px;")
        self.inner_layout.addWidget(line)

        self.lbl_list = QLabel("🔓 已解锁的想法")
        self.lbl_list.setStyleSheet("color: #888; font-size: 11px;")
        self.inner_layout.addWidget(self.lbl_list)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.list_widget)
        self.inner_layout.addWidget(self.scroll)
        
        self.main_layout.addWidget(self.container)

    # --- 新增功能：更新锁定时间 ---
    def update_lock_hours(self, value):
        self.lock_hours = value
        self.refresh_list() # 调整时间后，列表会实时根据新规则刷新
    # ---------------------------

    def dock(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - DOCK_WIDTH, (screen.height() - HEIGHT)//2, DOCK_WIDTH, HEIGHT)
        
        self.lbl_info.hide()
        self.editor.hide()
        self.lbl_list.hide()
        self.scroll.hide()
        # 隐藏新增的设置板块
        self.lbl_setting.hide()
        self.hour_spin.hide()
        
        self.editor.clearFocus()
        self.is_expanded = False

    def expand(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - EXPAND_WIDTH, (screen.height() - HEIGHT)//2, EXPAND_WIDTH, HEIGHT)
        
        self.lbl_info.show()
        self.editor.show()
        self.lbl_list.show()
        self.scroll.show()
        # 显示新增的设置板块
        self.lbl_setting.show()
        self.hour_spin.show()
        
        self.refresh_list()
        self.editor.setFocus()
        self.is_expanded = True

    def refresh_list(self):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not os.path.exists(STORAGE_FILE): return

        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                notes = json.load(f)
            
            now = datetime.now()
            for i in range(len(notes) - 1, -1, -1):
                note = notes[i]
                note_time = datetime.strptime(note['time'], "%Y-%m-%d %H:%M:%S")
                
                # 使用动态的 self.lock_hours
                if now - note_time > timedelta(hours=self.lock_hours):
                    self.add_note_card(note, i)
                        
        except Exception as e:
            print(f"读取错误: {e}")

    def add_note_card(self, note_data, real_index):
        card = QFrame()
        card.setStyleSheet("background: rgba(255,255,255,5); border-radius: 6px; margin-bottom: 8px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)

        header = QHBoxLayout()
        time_lbl = QLabel(note_data['time'])
        time_lbl.setStyleSheet("color: #666; font-size: 10px;")
        
        btn_del = QPushButton("×")
        btn_del.setFixedSize(20, 20)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("color: #d32f2f; background: transparent; font-weight: bold; border: none;")
        btn_del.clicked.connect(lambda _, idx=real_index: self.delete_note(idx))
        
        header.addWidget(time_lbl)
        header.addStretch()
        header.addWidget(btn_del)
        layout.addLayout(header)

        txt_edit = QTextEdit(note_data['content'])
        txt_edit.setStyleSheet("background: transparent; color: #ddd; border: none; font-size: 13px;")
        txt_edit.setFixedHeight(60)
        txt_edit.textChanged.connect(lambda: self.update_note(real_index, txt_edit.toPlainText()))
        
        layout.addWidget(txt_edit)
        self.list_layout.addWidget(card)

    def update_note(self, index, content):
        self.modify_json(index, "update", content)

    def delete_note(self, index):
        self.modify_json(index, "delete")
        self.refresh_list()

    def modify_json(self, index, action, content=None):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if action == "delete":
                data.pop(index)
            elif action == "update":
                data[index]['content'] = content
                
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except: pass

    def enterEvent(self, event):
        if not self.is_expanded: self.expand()

    def leaveEvent(self, event):
        QTimer.singleShot(100, self.check_hide)

    def check_hide(self):
        if not self.underMouse() and not self.isActiveWindow():
            self.dock()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.save_new_note()
        if event.key() == Qt.Key.Key_Q and (event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            QApplication.quit()

    def save_new_note(self):
        text = self.editor.toPlainText().strip()
        if text:
            entry = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "content": text}
            try:
                data = []
                if os.path.exists(STORAGE_FILE):
                    with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                data.append(entry)
                with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except: pass
            
            self.editor.clear()
            self.dock()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VibeNote()
    window.show()
    sys.exit(app.exec())
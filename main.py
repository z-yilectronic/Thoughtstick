import sys
import json
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QWidget, QTextEdit, QVBoxLayout, 
                             QHBoxLayout, QLabel, QScrollArea, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer

# --- 配置 ---
STORAGE_FILE = "notes.json"
LOCK_HOURS = 5          # 设定锁定时间（小时）
DOCK_WIDTH = 15         # 稍微加宽一点，防止看不见
EXPAND_WIDTH = 380      # 展开后的宽度
HEIGHT = 600            # 加高一点以便查看列表
# -----------

class VibeNote(QWidget):
    def __init__(self):
        super().__init__()
        # 窗口属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.init_ui()
        
        # --- 修复“消失”问题：启动动画 ---
        # 先让窗口在屏幕中间显示一下，确保它是活着的
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width()//2 - 150, screen.height()//2 - 200, 300, 400)
        print("窗口已启动...")
        
        # 500毫秒后自动飞到侧边停靠
        QTimer.singleShot(500, self.dock)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # 主背景容器
        self.container = QWidget()
        self.container.setObjectName("MainBox")
        self.container.setStyleSheet("""
            #MainBox {
                background-color: rgba(25, 25, 25, 245);
                border-left: 5px solid #00bcd4; /* 显眼的青色把手 */
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
        """)
        self.inner_layout = QVBoxLayout(self.container)
        
        # --- 上部：输入区 ---
        self.lbl_info = QLabel("✍️ 记录灵感 (Ctrl+Enter 存入)")
        self.lbl_info.setStyleSheet("color: #00bcd4; font-weight: bold; font-size: 12px;")
        self.inner_layout.addWidget(self.lbl_info)
        
        self.editor = QTextEdit()
        self.editor.setFixedHeight(80)
        self.editor.setPlaceholderText(f"想法将在 {LOCK_HOURS} 小时后解锁...")
        self.editor.setStyleSheet("background: rgba(255,255,255,10); color: white; border: none; border-radius: 5px; padding: 5px; font-size: 13px;")
        self.inner_layout.addWidget(self.editor)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #444; margin-top: 10px; margin-bottom: 10px;")
        self.inner_layout.addWidget(line)

        # --- 下部：历史列表区 ---
        self.lbl_list = QLabel("🔓 已解锁的想法 (直接编辑 / 点×删除)")
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

    def dock(self):
        """停靠模式"""
        screen = QApplication.primaryScreen().geometry()
        # 定位到右侧，高度居中
        self.setGeometry(screen.width() - DOCK_WIDTH, (screen.height() - HEIGHT)//2, DOCK_WIDTH, HEIGHT)
        
        # 隐藏内部元素，只保留 container 背景色作为把手
        self.lbl_info.hide()
        self.editor.hide()
        self.lbl_list.hide()
        self.scroll.hide()
        
        self.editor.clearFocus()
        self.is_expanded = False

    def expand(self):
        """展开模式"""
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - EXPAND_WIDTH, (screen.height() - HEIGHT)//2, EXPAND_WIDTH, HEIGHT)
        
        # 显示内部元素
        self.lbl_info.show()
        self.editor.show()
        self.lbl_list.show()
        self.scroll.show()
        
        self.refresh_list() # 展开时刷新列表
        self.editor.setFocus()
        self.is_expanded = True

    def refresh_list(self):
        """读取并显示已解锁的想法"""
        # 清空旧列表
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not os.path.exists(STORAGE_FILE): return

        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                notes = json.load(f)
            
            now = datetime.now()
            # 倒序显示（最新的在上面）
            for i in range(len(notes) - 1, -1, -1):
                note = notes[i]
                note_time = datetime.strptime(note['time'], "%Y-%m-%d %H:%M:%S")
                
                # 核心逻辑：只显示超过锁定时间的
                if now - note_time > timedelta(hours=LOCK_HOURS):
                    self.add_note_card(note, i)
                    
        except Exception as e:
            print(f"读取错误: {e}")

    def add_note_card(self, note_data, real_index):
        """添加一个卡片"""
        card = QFrame()
        card.setStyleSheet("background: rgba(255,255,255,5); border-radius: 6px; margin-bottom: 8px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)

        # 头部：时间和删除按钮
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

        # 内容编辑区
        txt_edit = QTextEdit(note_data['content'])
        txt_edit.setStyleSheet("background: transparent; color: #ddd; border: none; font-size: 13px;")
        txt_edit.setFixedHeight(60)
        txt_edit.textChanged.connect(lambda: self.update_note(real_index, txt_edit.toPlainText()))
        
        layout.addWidget(txt_edit)
        self.list_layout.addWidget(card)

    def update_note(self, index, content):
        """实时保存修改"""
        self.modify_json(index, "update", content)

    def delete_note(self, index):
        """删除想法"""
        self.modify_json(index, "delete")
        self.refresh_list() # 刷新界面

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

    # --- 事件处理 ---
    def enterEvent(self, event):
        if not self.is_expanded: self.expand()

    def leaveEvent(self, event):
        # 智能隐藏：只有当鼠标离开 且 没有在编辑时才缩回
        # 使用延时检查防止鼠标抖动导致闪烁
        QTimer.singleShot(100, self.check_hide)

    def check_hide(self):
        # 如果鼠标不在窗口范围内 且 窗口不是当前焦点窗口
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
            self.dock() # 保存后缩回

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VibeNote()
    window.show()
    sys.exit(app.exec())



print("PROGRAM STARTED")


import tkinter as tk

root = tk.Tk()
root.title("Sticky Thoughts")

# 窗口大小
root.geometry("300x200")

# 置顶
root.attributes("-topmost", True)

# 简单文本框
text = tk.Text(root, wrap="word")
text.pack(expand=True, fill="both")

root.mainloop()


from tkinter import simpledialog
import time

class StickyNote:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vibe Note")
        self.root.geometry("300x200")
        self.text = tk.Text(self.root, wrap="word")
        self.text.pack(expand=True, fill="both")
        
        self.locked = False
        self.lock_time = None
        
        # 锁按钮
        lock_btn = tk.Button(self.root, text="锁定/设置解锁时间", command=self.lock_note)
        lock_btn.pack(side="bottom")
        
        self.update_content()
        self.root.mainloop()
        
    def lock_note(self):
        if not self.locked:
            # 弹窗获取锁定小时数
            hours = simpledialog.askfloat("设置解锁时间", "输入锁定小时数：")
            if hours is not None:
                self.locked = True
                self.lock_time = time.time() + hours * 3600
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, "[内容已锁定]")
        else:
            tk.messagebox.showinfo("信息", "便笺已锁定，等待解锁时间")
            
    def update_content(self):
        if self.locked and time.time() >= self.lock_time:
            self.locked = False
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, "[内容解锁，可以编辑]")
        # 每秒检查一次
        self.root.after(1000, self.update_content)

StickyNote()
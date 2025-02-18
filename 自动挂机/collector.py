import tkinter as tk
from tkinter import scrolledtext
import pyautogui
import os


class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("鼠标位置跟踪器")

        self.label = tk.Label(root, text="鼠标位置: X=0, Y=0", font=("Helvetica", 14))
        self.label.pack(pady=20)

        self.record_label = tk.Label(root, text="记录的位置:", font=("Helvetica", 12))
        self.record_label.pack()

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=15, font=("Helvetica", 10))
        self.text_area.pack(padx=20, pady=20)

        self.recording = False
        self.counter = 0

        self.x = 0
        self.y = 0
        self.update_mouse_position()
        # 绑定 Ctrl+S 快捷键
        root.bind("<Control-s>", self.toggle_recording)
        # 检查文件是否存在，如果不存在则创建文件
        if not os.path.exists("collected_positions.txt"):
            with open("collected_positions.txt", "w") as file:
                pass

    def update_mouse_position(self):
        self.x, self.y = pyautogui.position()
        self.label.config(text=f"鼠标位置: X={self.x}, Y={self.y}")
        self.root.after(100, self.update_mouse_position)

    def toggle_recording(self, event):
        # 记录鼠标位置
        self.counter += 1
        position = f"{self.counter}. X={self.x}, Y={self.y}\n"
        self.text_area.insert(tk.END, position)
        self.text_area.see(tk.END)  # 滚动到文本区域的末尾
        # 将位置信息保存到文件中
        with open("collected_positions.txt", "a") as file:
            file.write(position)


if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.mainloop()
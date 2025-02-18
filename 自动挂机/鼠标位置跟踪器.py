import tkinter as tk
from tkinter import scrolledtext
import pyautogui

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

        self.ctrl_pressed_count = 0
        self.x = 0
        self.y = 0
        self.update_mouse_position()

    def update_mouse_position(self):
        self.x, self.y = pyautogui.position()
        self.label.config(text=f"鼠标位置: X={self.x}, Y={self.y}")
        self.root.after(100, self.update_mouse_position)

    def toggle_recording(self, event):
        if event.keysym == "Control_L":
            self.ctrl_pressed_count += 1
            if self.ctrl_pressed_count >= 2:  # Double Ctrl press detected
                self.ctrl_pressed_count = 0
                self.counter += 1
                self.text_area.insert(tk.END, f"{self.counter}. X={self.x}, Y={self.y}\n")
                self.text_area.see(tk.END)  # Scroll to the end of the text area
        else:
            self.ctrl_pressed_count = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)
    root.bind("<KeyPress>", app.toggle_recording)
    root.mainloop()

import sys
import random
import time
import threading
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QWidget, QMessageBox, QFileDialog, QDialog, QTextEdit, QShortcut
from PyQt5.QtCore import Qt, QTimer
import pyautogui
from PyQt5.QtGui import QFont


class ClickThread(threading.Thread):
    def __init__(self, positions, interval):
        super().__init__()
        self.positions = positions
        self.interval = interval
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            for x, y in self.positions:
                pyautogui.click(x, y)
                time.sleep(random.randint(1, self.interval))

    def stop(self):
        self.running = False
        if self.is_alive():
            self.join()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("授权保持工具")
        self.setGeometry(500, 500, 600, 500)
        self.click_thread = None
        self.positions = []
        self.init_ui()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # 设置主窗口置顶

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # 提示文字
        self.bottom_text = QLabel("正在挂机操作，请点击停止后！再动鼠标")
        font = QFont()
        font.setPointSize(14)  # 设置字体大小为 14 号
        font.setBold(True)  # 设置字体为粗体
        self.bottom_text.setFont(font)  # 应用字体设置
        self.bottom_text.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.bottom_text)

        # 按钮和位置采集区域
        self.button_and_collect_layout = QVBoxLayout()
        self.main_layout.addLayout(self.button_and_collect_layout)

        # 位置输入区域
        self.input_layout = QVBoxLayout()
        self.button_and_collect_layout.addLayout(self.input_layout)

        # 按钮区域
        self.button_layout = QHBoxLayout()
        self.button_and_collect_layout.addLayout(self.button_layout)
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_clicking)
        self.button_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_clicking)
        self.button_layout.addWidget(self.stop_button)
        self.add_button = QPushButton("增加一个点位")
        self.add_button.clicked.connect(self.add_position)
        self.button_layout.addWidget(self.add_button)

        # 添加“位置采集”按钮
        self.collect_button = QPushButton("位置采集")
        self.collect_button.clicked.connect(self.open_collector_window)
        self.button_layout.addWidget(self.collect_button)

        # 间隔时间输入
        self.interval_layout = QHBoxLayout()
        self.main_layout.addLayout(self.interval_layout)

        # 添加左侧伸缩空间
        self.interval_layout.addStretch()

        self.interval_label = QLabel("随机时间：")
        self.interval_layout.addWidget(self.interval_label)

        self.entry_interval = QLineEdit()
        self.entry_interval.setPlaceholderText("默认10")
        self.entry_interval.setText("10")
        self.entry_interval.setFixedWidth(100)  # 设置固定宽度
        self.interval_layout.addWidget(self.entry_interval)

        self.seconds_label = QLabel("秒")
        self.interval_layout.addWidget(self.seconds_label)

        # 添加右侧伸缩空间
        self.interval_layout.addStretch()

    def add_position(self, x=None, y=None, index=None):
        if index is None or index >= len(self.positions):
            index = len(self.positions)
        position_layout = QHBoxLayout()
        self.input_layout.insertLayout(index, position_layout)
        x_label = QLabel("X：")
        position_layout.addWidget(x_label)
        entry_x = QLineEdit()
        entry_x.setPlaceholderText("X坐标")
        if x is not None:
            entry_x.setText(str(x))
        position_layout.addWidget(entry_x)
        y_label = QLabel("Y：")
        position_layout.addWidget(y_label)
        entry_y = QLineEdit()
        entry_y.setPlaceholderText("Y坐标")
        if y is not None:
            entry_y.setText(str(y))
        position_layout.addWidget(entry_y)
        self.positions.insert(index, (entry_x, entry_y))
        self.adjustSize()  # 调整窗口大小

    def start_clicking(self):
        if self.click_thread and self.click_thread.is_alive():
            QMessageBox.warning(self, "警告", "点击线程已经在运行！")
            return

        positions = []
        for entry_x, entry_y in self.positions:
            try:
                x = int(entry_x.text())
                y = int(entry_y.text())
                positions.append((x, y))
            except ValueError:
                QMessageBox.warning(self, "警告", "请输入有效的坐标值！")
                return

        try:
            interval = int(self.entry_interval.text())
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的间隔时间！")
            return

        self.click_thread = ClickThread(positions, interval)
        self.click_thread.start()

    def stop_clicking(self):
        if self.click_thread:
            self.click_thread.stop()
            self.click_thread = None

    def open_collector_window(self):
        self.collector_window = CollectorWindow(self)
        self.collector_window.exec_()

    def closeEvent(self, event):
        # 删除 collected_positions.txt 文件
        try:
            os.remove("collected_positions.txt")
        except FileNotFoundError:
            pass
        event.accept()


class CollectorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("鼠标位置采集器")
        self.setGeometry(300, 300, 400, 300)
        self.counter = 0
        self.collected_positions = []  # 存储采集的位置
        self.init_ui()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # 设置采集器窗口置顶

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.label = QLabel("鼠标位置: X=0, Y=0", font=QFont("Helvetica", 14))
        self.main_layout.addWidget(self.label)

        self.record_label = QLabel("记录的位置:", font=QFont("Helvetica", 12))
        self.main_layout.addWidget(self.record_label)

        self.text_area = QTextEdit()
        self.main_layout.addWidget(self.text_area)

        # 检查文件是否存在，如果不存在则创建文件
        if not os.path.exists("collected_positions.txt"):
            with open("collected_positions.txt", "w") as file:
                pass

        # 绑定 Ctrl+S 快捷键
        self.shortcut = QShortcut(Qt.CTRL + Qt.Key_S, self)
        self.shortcut.activated.connect(self.record_position)

        self.x = 0
        self.y = 0
        self.update_mouse_position()

    def update_mouse_position(self):
        self.x, self.y = pyautogui.position()
        self.label.setText(f"鼠标位置: X={self.x}, Y={self.y}")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(100)

    def record_position(self):
        self.counter += 1
        position = f"{self.counter}. X={self.x}, Y={self.y}\n"
        self.text_area.append(position)
        self.collected_positions.append((self.x, self.y))  # 存储采集的位置
        with open("collected_positions.txt", "a") as file:
            file.write(position)

    def closeEvent(self, event):
        # 将采集的位置信息传递给主窗口
        if self.parent():
            for x, y in self.collected_positions:
                self.parent().add_position(x, y)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
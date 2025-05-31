import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

import math
import sys
import os
from PyQt6.QtWidgets import QApplication, QSlider, QFileDialog, QLabel, QWidget, QPushButton, QVBoxLayout, QComboBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import random
import tkinter

TK_SILENCE_DEPRECATION = 1
root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.destroy()

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.fedornot = False
        self.cooldown_time = 0
        self.setWindowTitle("Feeding")
        self.move(500, 500)
        self.setFixedSize(300, 300)

        self.randomdirection = "Right"
        self.os_selectedpath = ""
        self.allowed_file_types = [".txt", ".png", ".docx", ".xlsx", ".pdf", ".jpg", ".py", ".cs", ".mp3", ".mp4"]
        self.healthslider = QSlider(Qt.Orientation.Vertical, self)
        self.healthslider.setRange(0, 100)
        self.healthslider.setValue(50)
        self.healthslider.setEnabled(False)
        self.button3 = QPushButton("Feed Ramsey", self)
        self.button4 = QPushButton("Set Folder", self)
        self.button5 = QPushButton("Emergency Stop", self)
        self.label = QLabel("No folder selected")
        self.label1 = QLabel("")
        self.file_type_selector = QComboBox(self)
        self.file_type_selector.addItems(self.allowed_file_types)
        self.file_type_selector.setCurrentIndex(0)

        style_sheet = """
            QPushButton {
                background-color: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 10px;
            }QPushButton:hover {
                background-color: #FF0000;
            }"""

        self.button5.setStyleSheet(style_sheet)

        layout = QVBoxLayout()
        layout.addWidget(self.button4)
        layout.addWidget(self.button3)
        layout.addWidget(self.button5)
        layout.addWidget(self.healthslider)
        layout.addWidget(self.label)
        layout.addWidget(self.label1)
        layout.addWidget(self.file_type_selector)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.my_repeated_function)
        self.timer.start(1000)

        self.slider_timer = QTimer()
        self.slider_timer.timeout.connect(self.update_slider)
        self.slider_timer.start(100)

        self.button5.clicked.connect(self.kill)
        self.button4.clicked.connect(self.set_folder)
        self.button3.clicked.connect(self.feed_ramsey)

    def update_allowed_file_types(self, file_type):
        self.allowed_file_types = [file_type]

    def feed_ramsey(self):
        self.fedornot = True
        self.label1.setText("RAMsey ate")
        self.cooldown_time = random.randint(1000, 20000)
        QTimer.singleShot(self.cooldown_time, self.get_hungry_again)

    def update_slider(self):
        if self.fedornot and self.cooldown_time > 0:
            self.cooldown_time -= 100
            self.healthslider.setValue(self.cooldown_time // 200)
        elif not self.fedornot:
            self.healthslider.setValue(0)

    def my_repeated_function(self):
        if self.fedornot:
            self.label1.setText("RAMsey is full for a bit")
            return

        if self.os_selectedpath:
            files = [f for f in os.listdir(self.os_selectedpath)
                     if os.path.isfile(os.path.join(self.os_selectedpath, f))]

            files = [f for f in files if any(f.endswith(ext) for ext in self.allowed_file_types)]

            if not files:
                self.label1.setText("Folder empty or the selected file type isn't present")
                return

            random_index = random.randint(0, len(files) - 1)
            file_to_delete = files[random_index]
            file_path = os.path.join(self.os_selectedpath, file_to_delete)

            self.ramsey_list[0].eat_file(file_path)
            self.label1.setText(f"File eaten: {file_to_delete}")
            
    def get_hungry_again(self):
        self.fedornot = False
        self.cooldown_time = 0
        self.label1.setText("RAMsey is hungry again!")

    def kill(self):
        self.fedornot = False
        self.timer.stop()
        self.slider_timer.stop()
        self.label1.setText("Emergency Stop Activated! You must restart program to continue!")

    def set_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.os_selectedpath = folder_path
            self.label.setText(f"Selected: {os.path.basename(folder_path)}")

base_path = os.path.dirname(os.path.abspath(__file__))
body_path = os.path.join(base_path, "body.png")
head_path = os.path.join(base_path, "head_top.png")

class ControlPanel(QWidget):
    def __init__(self, ramsey_list):
        super().__init__()
        self.ramsey_list = ramsey_list
        self.current_ramsey_index = 0
        self.setWindowTitle("RAMsey Control Panel")
        self.setFixedSize(300, 400)

        self.button1 = QPushButton("Control RAMsey", self)
        self.button2 = QPushButton("Give up control", self)
        self.spawn_button = QPushButton("Spawn new RAMsey", self)
        self.next_ramsey_button = QPushButton("Next RAMsey", self)
        self.stats_button = QPushButton("Open Stats Board!", self)
        self.info_button = QPushButton("Open Information Tab", self)

        self.ramsey_selector = QComboBox(self)
        self.update_ramsey_selector()

        self.button1.setStyleSheet(
            """QPushButton {
                background-color: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 10px;
            }QPushButton:hover {
                background-color: #555;
            }"""
        )

        self.button2.setStyleSheet(self.button1.styleSheet())
        self.spawn_button.setStyleSheet(self.button1.styleSheet())
        self.next_ramsey_button.setStyleSheet(self.button1.styleSheet())
        self.stats_button.setStyleSheet(self.button1.styleSheet())
        self.info_button.setStyleSheet(self.button1.styleSheet())

        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.spawn_button)
        layout.addWidget(self.next_ramsey_button)
        layout.addWidget(QLabel("Select RAMsey to Control:"))
        layout.addWidget(self.ramsey_selector)
        layout.addWidget(self.stats_button)
        layout.addWidget(self.info_button)
        self.setLayout(layout)

        self.button1.clicked.connect(self.on_clicked1)
        self.button2.clicked.connect(self.on_clicked2)
        self.spawn_button.clicked.connect(self.spawn_ramsey)
        self.next_ramsey_button.clicked.connect(self.next_ramsey)
        self.ramsey_selector.currentIndexChanged.connect(self.select_ramsey)
        self.stats_button.clicked.connect(self.open_stats_board)
        self.info_button.clicked.connect(self.open_info_board)

        self.control_enabled = False

    def open_info_board(self):
        self.info_board = InfoBoard()
        self.info_board.show()

    def open_stats_board(self):
        self.stats_board = StatsBoard(self.ramsey_list)
        self.stats_board.show()

    def update_ramsey_selector(self):
        self.ramsey_selector.clear()
        for i, ramsey in enumerate(self.ramsey_list):
            self.ramsey_selector.addItem(f"RAMsey #{i + 1}")

    def spawn_ramsey(self):
        new_ramsey = RAMsey(self, self.ramsey_list)
        self.ramsey_list.append(new_ramsey)
        new_ramsey.show()
        self.update_ramsey_selector()

    def next_ramsey(self):
        self.current_ramsey_index = (self.current_ramsey_index + 1) % len(self.ramsey_list)
        self.ramsey_selector.setCurrentIndex(self.current_ramsey_index)

    def select_ramsey(self, index):
        if 0 <= index < len(self.ramsey_list):
            self.current_ramsey_index = index

    def on_clicked1(self):
        self.control_enabled = True
        self.setFocus()

    def on_clicked2(self):
        self.control_enabled = False

    def keyPressEvent(self, event):
        if not self.control_enabled:
            # Trigger random movement for all RAMsey instances cus am muy estupido
            for ramsey in self.ramsey_list:
                ramsey.random_movement()
            return

        key = event.key()
        current_ramsey = self.ramsey_list[self.current_ramsey_index]
        if key == Qt.Key.Key_W:
            current_ramsey.jump()
        elif key == Qt.Key.Key_A:
            current_ramsey.move_left = True
        elif key == Qt.Key.Key_D:
            current_ramsey.move_right = True
        elif key == Qt.Key.Key_Shift:
            current_ramsey.shiftpress = True

    def keyReleaseEvent(self, event):
        key = event.key()
        current_ramsey = self.ramsey_list[self.current_ramsey_index]
        if key == Qt.Key.Key_A:
            current_ramsey.move_left = False
        elif key == Qt.Key.Key_D:
            current_ramsey.move_right = False
        elif key == Qt.Key.Key_Shift:
            current_ramsey.shiftpress = False

class RAMsey(QWidget):
    def __init__(self, parent, ramsey_list):
        super().__init__(parent)  
        self.ramsey_list = ramsey_list
        self.files_eaten = 0
        self.total_size_deleted = 0
        self.vy = 0
        self.gravity = 1
        self.on_ground = True
        self.move_left = False
        self.move_right = False
        self.shiftpress = False
        self.speed = 5
        self.sprint_speed = 10
        self.smooth_timer = None
        self.target_x = None

        original_head = QPixmap(head_path)
        self.head_pixmap = original_head.scaled(
            80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        self.body_pixmap = QPixmap(body_path).scaled(
            150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        self.body_label = QLabel(self)
        self.body_label.setPixmap(self.body_pixmap)
        self.body_label.move(0, self.head_pixmap.height() - 10)
        self.body_label.resize(self.body_pixmap.size())

        self.head_label = QLabel(self)
        self.head_label.setPixmap(self.head_pixmap)
        self.head_label.setFixedSize(self.head_pixmap.size())
        self.head_label.setScaledContents(False)

        head_x = (self.body_pixmap.width() - self.head_pixmap.width()) // 2
        head_y = 10
        self.head_label.move(head_x, head_y)
        self.head_label.show()

        total_width = max(self.body_pixmap.width(), self.head_pixmap.width())
        total_height = self.head_pixmap.height() + self.body_pixmap.height() + 10
        self.resize(total_width, total_height)
        self.move(300, 300)  # Start position

        # Make RAMsey a floating window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Timer for random movement
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)

        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.check_idle_and_move)
        self.idle_timer.start(2000)

    def tick(self):
        self.update_movement()
        self.apply_gravity()

        for other_ramsey in self.ramsey_list:
            if self.check_collision(other_ramsey):
                self.handle_collision(other_ramsey)

    def check_idle_and_move(self):
        if not self.move_left and not self.move_right:
            self.random_movement()

    def random_movement(self):
        direction = random.choice(["Left", "Right"])
        distance = random.randint(50, 150)

        if direction == "Left":
            new_x = max(0, self.x() - distance)
        elif direction == "Right":
            screen_width = QApplication.primaryScreen().size().width()
            new_x = min(screen_width - self.width(), self.x() + distance)

        self.start_smooth_movement()

    def start_smooth_movement(self):
        if self.smooth_timer:
            self.smooth_timer.stop()

        self.smooth_timer = QTimer()
        self.smooth_timer.timeout.connect(self.perform_smooth_movement)
        self.smooth_timer.start(30)

    def perform_smooth_movement(self):
        if self.target_x is None:
            return

        current_x = self.x()
        step = 5

        if current_x < self.target_x:
            new_x = min(current_x + step, self.target_x)
        elif current_x > self.target_x:
            new_x = max(current_x - step, self.target_x)
        else:
            self.smooth_timer.stop()
            self.target_x = None
            return

        self.move(new_x, self.y())

    def update_movement(self):
        x = self.x()
        current_speed = self.sprint_speed if self.shiftpress else self.speed

        if self.move_left:
            x -= current_speed
        if self.move_right:
            x += current_speed

        screen_width = QApplication.primaryScreen().size().width()
        min_x = 0
        max_x = screen_width - self.width()

        if x < min_x:
            x = min_x
        elif x > max_x:
            x = max_x

        self.move(x, self.y())

    def jump(self):
        if self.on_ground:
            self.vy = -15
            self.on_ground = False

    def apply_gravity(self):
        if not self.on_ground:
            self.vy += self.gravity
            new_y = self.y() + self.vy

            if new_y >= QApplication.primaryScreen().size().height() - self.height():
                new_y = QApplication.primaryScreen().size().height() - self.height()
                self.vy = 0
                self.on_ground = True

            self.move(self.x(), new_y)

    def check_collision(self, other):
        if self == other:
            return False

        rect1 = self.geometry()
        rect2 = other.geometry()

        return rect1.intersects(rect2)

    def handle_collision(self, other):
        self.move_left = False
        self.move_right = False
        other.move_left = False
        other.move_right = False

        if self.x() < other.x():
            self.move(self.x() - 10, self.y())
            other.move(other.x() + 10, other.y())
        else:
            self.move(self.x() + 10, self.y())
            other.move(other.x() - 10, self.y())

class StatsBoard(QWidget):
    def __init__(self, ramsey_list):
        super().__init__()
        self.ramsey_list = ramsey_list
        self.setWindowTitle("RAMsey Stats Board")
        self.setFixedSize(300, 200)

        self.files_eaten_label = QLabel("Files Eaten: 0", self)
        self.files_eaten_label.move(20, 20)

        self.total_size_label = QLabel("Total Size Deleted: 0KB", self)
        self.total_size_label.move(20, 50)
        
        self.ramsey_count_label = QLabel(f"RAMseys Active: {len(self.ramsey_list)}", self)
        self.ramsey_count_label.move(20, 80)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_stats(self):
        total_files_eaten = sum(ramsey.files_eaten for ramsey in self.ramsey_list)
        total_size_deleted = sum(ramsey.total_size_deleted for ramsey in self.ramsey_list)

        self.files_eaten_label.setText(f"Files Eaten: {total_files_eaten}")
        self.total_size_label.setText(f"Total Size Deleted: {total_size_deleted}KB")
        self.ramsey_count_label.setText(f"RAMseys Active: {len(self.ramsey_list)}")

class InfoBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Information")
        self.setFixedSize(300, 400)

        self.information = QLabel(self)
        self.information.setText(
            '<p>Hello, thank you for choosing to use RAMsey!</p>'
            '<p>If you have chosen to use RAMsey, then you certainly have great taste.</p>'
            '<p>RAMsey is a desk pet that hovers around your desktop and sometimes likes to eat your files.</p>'
            '<p>Visit the <a href="https://github.com/Githubuser1122bruh/RAMsey">GitHub page for RAMsey</a> for more information.</p>'
            '<p>This is made for a project called shipwrecked which is hosted by HackClub, a non profit organisation to help teens code!</p>'
            '<p>To get more information about hackclub, visit hackclub.com. Please star the GitHub repository!</p>'
        )

        self.information.setOpenExternalLinks(True)
        self.information.setWordWrap(True)
        self.information.move(10, 10)
        self.information.resize(280, 380)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ramsey_list = []

    widget = MyWidget()
    first_ramsey = RAMsey(widget, ramsey_list) 
    ramsey_list.append(first_ramsey)
    first_ramsey.show()

    control_panel = ControlPanel(ramsey_list)
    control_panel.move(100, 100)
    control_panel.show()

    widget.show()

    sys.exit(app.exec())
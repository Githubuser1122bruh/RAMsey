import multiprocessing
multiprocessing.set_start_method("spawn", force=True)

import math
import sys
import os
from PyQt6.QtWidgets import QApplication, QSlider, QFileDialog, QLabel, QWidget, QButtonGroup, QPushButton, QWidget, QVBoxLayout, QComboBox
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QTimer
import pyautogui
import math
import tkinter
from PyQt6.QtCore import QTimer
import random

# Silence Tk warning
TK_SILENCE_DEPRECATION = 1
root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.destroy()
print(f"width: {width} height: {height}")

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.fedornot = False
        self.cooldown_time = 0  # Initialize cooldown_time
        self.setWindowTitle("Feeding")
        self.move(500, 500)
        self.setFixedSize(300, 300)

        self.os_selectedpath = ""

        # UI Elements
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

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.button4)
        layout.addWidget(self.button3)
        layout.addWidget(self.button5)
        layout.addWidget(self.healthslider)
        layout.addWidget(self.label)
        layout.addWidget(self.label1)
        layout.addWidget(self.file_type_selector)
        self.setLayout(layout)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.my_repeated_function)
        self.timer.start(1000)  # Runs every second

        # Slider Update Timer
        self.slider_timer = QTimer()
        self.slider_timer.timeout.connect(self.update_slider)
        self.slider_timer.start(100)  # Update slider every 100ms

        # Button connections
        self.button5.clicked.connect(self.kill)
        self.button4.clicked.connect(self.set_folder)
        self.button3.clicked.connect(self.feed_ramsey)

    def update_allowed_file_types(self, file_type):
        """Update the allowed file types based on the users selection"""
        self.allowed_file_types = [file_type]
        print(f"Allowed file types updated: {self.allowed_file_types}")

    def feed_ramsey(self):
        self.fedornot = True
        self.label1.setText("RAMsey ate")
        print("RAMsey is full and won't eat files for a while.")

        # Set a random cooldown period (e.g., 1 to 20 seconds)
        self.cooldown_time = random.randint(1000, 20000)  # in milliseconds
        QTimer.singleShot(self.cooldown_time, self.get_hungry_again)

        print(f"Cooldown time set to: {self.cooldown_time} ms")

    def update_slider(self):
        """Update the slider to reflect the cooldown time."""
        if self.fedornot and self.cooldown_time > 0:
            self.cooldown_time -= 100  # Decrease cooldown time by 100ms
            self.healthslider.setValue(self.cooldown_time // 200)  # Scale to slider range (0-100)
        elif not self.fedornot:
            self.healthslider.setValue(0)  # Reset slider when not in cooldown

    def my_repeated_function(self):
        """Repeated function to perform actions."""
        if self.fedornot:
            self.label1.setText("RAMsey is full for a bit")
            return

        if self.os_selectedpath:
            files = [f for f in os.listdir(self.os_selectedpath)
                     if os.path.isfile(os.path.join(self.os_selectedpath, f))]

            files = [f for f in files if any(f.endswith(ext) for ext in self.allowed_file_types)]

            if not files:
                self.label1.setText("Folder empty or the selected file type isnt present")
                return

            random_index = random.randint(0, len(files) - 1)
            file_to_delete = files[random_index]
            file_path = os.path.join(self.os_selectedpath, file_to_delete)

            try:
                os.remove(file_path)
                self.label1.setText(f"File eaten: {file_to_delete}")
                print(f"Deleted: {file_to_delete}")
            except Exception as e:
                print("Failed to delete file:", e)

    def get_hungry_again(self):
        self.fedornot = False
        self.cooldown_time = 0  # Reset cooldown time
        self.label1.setText("RAMsey is hungry again!")
        print("RAMsey is ready to eat files again!")

    def kill(self):
        """Emergency stop to kill all actions."""
        self.fedornot = False
        self.timer.stop()
        self.slider_timer.stop()
        self.label1.setText("Emergency Stop Activated! You must restart program to continue!")
        print("All actions stopped, restart program to continue.")

    def set_folder(self):
        """Set the folder for RAMsey to operate on."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.os_selectedpath = folder_path
            self.label.setText(f"Selected: {os.path.basename(folder_path)}")

# ---------- Paths ----------
base_path = os.path.dirname(os.path.abspath(__file__))
body_path = os.path.join(base_path, "body.png")
head_path = os.path.join(base_path, "head_top.png")


# ---------- Control Panel ----------
class ControlPanel(QWidget):
    def __init__(self, ramsey_list):
        super().__init__()
        self.ramsey_list = ramsey_list  # List to track all RAMsey instances
        self.current_ramsey_index = 0  # Index of the currently controlled RAMsey
        self.setWindowTitle("RAMsey Control Panel")
        self.setFixedSize(300, 150)

        # Buttons
        self.button1 = QPushButton("Control RAMsey", self)
        self.button2 = QPushButton("Give up control", self)
        self.spawn_button = QPushButton("Spawn new RAMsey", self)
        self.next_ramsey_button = QPushButton("Next RAMsey", self)  # Button to swap control

        # Dropdown to select RAMsey
        self.ramsey_selector = QComboBox(self)
        self.update_ramsey_selector()

        # Button styles
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

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.spawn_button)
        layout.addWidget(self.next_ramsey_button)
        layout.addWidget(QLabel("Select RAMsey to Control:"))
        layout.addWidget(self.ramsey_selector)
        self.setLayout(layout)

        # Button connections
        self.button1.clicked.connect(self.on_clicked1)
        self.button2.clicked.connect(self.on_clicked2)
        self.spawn_button.clicked.connect(self.spawn_ramsey)
        self.next_ramsey_button.clicked.connect(self.next_ramsey)
        self.ramsey_selector.currentIndexChanged.connect(self.select_ramsey)

        self.control_enabled = False

    def update_ramsey_selector(self):
        """Update the dropdown with the list of RAMsey instances."""
        self.ramsey_selector.clear()
        for i, ramsey in enumerate(self.ramsey_list):
            self.ramsey_selector.addItem(f"RAMsey #{i + 1}")

    def spawn_ramsey(self):
        """Spawn a new RAMsey pet."""
        new_ramsey = RAMsey()
        self.ramsey_list.append(new_ramsey)
        new_ramsey.move(100 + len(self.ramsey_list) * 50, 100)
        new_ramsey.show()
        self.update_ramsey_selector()  # Update dropdown
        print(f"Spawned RAMsey #{len(self.ramsey_list)}")

    def next_ramsey(self):
        """Switch control to the next RAMsey."""
        self.current_ramsey_index = (self.current_ramsey_index + 1) % len(self.ramsey_list)
        self.ramsey_selector.setCurrentIndex(self.current_ramsey_index)
        print(f"Switched control to RAMsey #{self.current_ramsey_index + 1}")

    def select_ramsey(self, index):
        """Select a RAMsey to control from the dropdown."""
        if 0 <= index < len(self.ramsey_list):
            self.current_ramsey_index = index
            print(f"Selected RAMsey #{index + 1} for control")

    def on_clicked1(self):
        print("Gain control clicked")
        self.control_enabled = True
        self.setFocus()

    def on_clicked2(self):
        print("Control lost")
        self.control_enabled = False

    def keyPressEvent(self, event):
        if not self.control_enabled:
            return

        key = event.key()
        current_ramsey = self.ramsey_list[self.current_ramsey_index]
        if key == Qt.Key.Key_W:
            current_ramsey.jump()
            print("w press")
        elif key == Qt.Key.Key_A:
            current_ramsey.move_left = True
            print("a press")
        elif key == Qt.Key.Key_S:
            print("s press")
        elif key == Qt.Key.Key_D:
            print("d press")
            current_ramsey.move_right = True

    def keyReleaseEvent(self, event):
        key = event.key()
        current_ramsey = self.ramsey_list[self.current_ramsey_index]
        if key == Qt.Key.Key_A:
            current_ramsey.move_left = False
        elif key == Qt.Key.Key_D:
            current_ramsey.move_right = False


# ---------- Pet Widget ----------
class RAMsey(QWidget):
    def __init__(self):
        super().__init__()
        self.y_pos = 600  # vertical position of the bottom of the body
        self.vy = 0
        self.gravity = 1
        self.ground_y = 1000
        self.on_ground = False
        self.move_left = False
        self.move_right = False
        self.speed = 5

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Load and scale head
        original_head = QPixmap(head_path)
        assert not original_head.isNull(), "Failed to load head image!"
        self.head_pixmap = original_head.scaled(
            80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )

        # Load and scale body
        self.body_pixmap = QPixmap(body_path).scaled(
            150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        assert not self.body_pixmap.isNull(), "Failed to load body image!"

        # Adjust body and head positions
        self.body_label = QLabel(self)
        self.body_label.setPixmap(self.body_pixmap)
        self.body_label.move(0, self.head_pixmap.height() - 10)  # show more of the legs
        self.body_label.resize(self.body_pixmap.size())

        self.head_label = QLabel(self)
        self.head_label.setPixmap(self.head_pixmap)
        self.head_label.setFixedSize(self.head_pixmap.size())
        self.head_label.setScaledContents(False)

        head_x = (self.body_pixmap.width() - self.head_pixmap.width()) // 2
        head_y = 10  # lower the head slightly
        self.head_label.move(head_x, head_y)
        self.head_label.show()

        total_width = max(self.body_pixmap.width(), self.head_pixmap.width())
        # add extra 10 pixels to height to make sure legs visible
        total_height = self.head_pixmap.height() + self.body_pixmap.height() + 10
        self.resize(total_width, total_height)
        self.move(300, 300)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)

    def update_head_position(self):
        mouse_x, mouse_y = pyautogui.position()
        widget_center_x = self.x() + self.width() // 2
        widget_top_y = self.y()

        dx = mouse_x - widget_center_x
        dy = mouse_y - widget_top_y

        angle_degrees = math.degrees(math.atan2(dy, dx))

        transform = QTransform()
        transform.translate(self.head_pixmap.width() / 2, self.head_pixmap.height() / 2)
        transform.rotate(angle_degrees)
        transform.translate(-self.head_pixmap.width() / 2, -self.head_pixmap.height() / 2)

        rotated = self.head_pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        self.head_label.setPixmap(rotated)
        self.head_label.resize(rotated.size())

        head_x = (self.width() - rotated.width()) // 2
        head_y = 10  # keep synced with head placement
        self.head_label.move(head_x, head_y)

    def tick(self):
        self.update_physics()
        self.update_head_position()
        self.update_movement()

    def update_physics(self):
        if not self.on_ground:
            self.vy += self.gravity
            self.y_pos += self.vy
            if self.y_pos >= self.ground_y:
                self.y_pos = self.ground_y
                self.vy = 0
                self.on_ground = True

        # Adjust offset dynamically to reflect new widget height and body image height
        offset = self.height() - self.body_pixmap.height()
        self.move(self.x(), int(self.y_pos - offset))

    def jump(self):
        if self.on_ground:
            self.vy = -20
            self.on_ground = False

    def update_movement(self):
        x = self.x()
        if self.move_left:
            x -= self.speed
        if self.move_right:
            x += self.speed

        screen_width = width
        min_x = 0
        max_x = screen_width - self.width()

        if x < min_x:
            x = min_x
        elif x > max_x:
            x = max_x

        self.move(x, int(self.y()))


# ---------- Main ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = RAMsey()
    pet.show()

    ramsey_list = []

    first_ramsey = RAMsey()
    ramsey_list.append(first_ramsey)
    first_ramsey.show()

    control_panel = ControlPanel(ramsey_list)
    control_panel.move(100, 100)
    control_panel.show()

    widget = MyWidget()
    widget.show()
    sys.exit(app.exec())
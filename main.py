import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QButtonGroup, QPushButton
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QTimer
import pyautogui
import math
import tkinter

# Silence Tk warning
TK_SILENCE_DEPRECATION = 1
root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.destroy()
print(f"width: {width} height: {height}")

# ---------- Paths ----------
base_path = os.path.dirname(os.path.abspath(__file__))
body_path = os.path.join(base_path, "body.png")
head_path = os.path.join(base_path, "head_top.png")


# ---------- Control Panel ----------
class ControlPanel(QWidget):
    def __init__(self, ramsey):
        super().__init__()
        self.move(300, 300)
        self.ramsey = ramsey
        self.setWindowTitle("RAMsey Control Panel")
        self.setFixedSize(300, 100)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.button1 = QPushButton("Control RAMsey", self)
        self.button2 = QPushButton("Give up control", self)

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
        self.button2.setStyleSheet(
            """QPushButton {
                background-color: #333;
                color: white;
                padding: 5px 10px;
                border-radius: 10px;
            }QPushButton:hover {
                background-color: #555;
            }"""
        )

        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.button1)
        self.button_group.addButton(self.button2)

        self.button1.move(30, 30)
        self.button2.move(160, 30)

        self.button1.clicked.connect(self.on_clicked1)
        self.button2.clicked.connect(self.on_clicked2)

        self.control_enabled = False

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
        if key == Qt.Key.Key_W:
            self.ramsey.jump()
            print("w press")
        elif key == Qt.Key.Key_A:
            self.ramsey.move_left = True
            print("a press")
        elif key == Qt.Key.Key_S:
            print("s press")
        elif key == Qt.Key.Key_D:
            print("d press")
            self.ramsey.move_right = True

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_A:
            self.ramsey.move_left = False
        elif key == Qt.Key.Key_D:
            self.ramsey.move_right = False


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
        self.body_label.move(0, self.head_pixmap.height() - 20)  # show more of the legs
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
        # add extra 20 pixels to height to make sure legs visible
        total_height = self.head_pixmap.height() + self.body_pixmap.height() + 20
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

    control_panel = ControlPanel(pet)
    control_panel.move(100, 100)
    control_panel.show()

    sys.exit(app.exec())
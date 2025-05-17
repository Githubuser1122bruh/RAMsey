import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QButtonGroup, QPushButton
from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt, QTimer
import pyautogui
import math
import tkinter
from pynput import keyboard
import threading

# Silence Tk warning
TK_SILENCE_DEPRECATION = 1
root = tkinter.Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.destroy()
print(f"width: {width} height: {height}")

# ---------- Control Panel ----------
class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RAMsey Control Panel")
        self.setFixedSize(300, 100)

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

        self.listener_thread = None
        self.listening = False

    def on_clicked1(self):
        print("Gain control clicked")
        if not self.listening:
            self.listening = True
            self.listener_thread = threading.Thread(target=self.listen_keys, daemon=True)
            self.listener_thread.start()

    def listen_keys(self):
        def on_press(key):
            try:
                if key.char == 'w':
                    print("w press")
                elif key.char == 'a':
                    print("a press")
                elif key.char == 's':
                    print("s press")
                elif key.char == 'd':
                    print("d press")
            except AttributeError:
                # Special keys like ctrl, shift etc.
                pass

        def on_release(key):
            # Stop listener if needed, but here we keep listening
            return self.listening  # keep listening while self.listening is True

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    def on_clicked2(self):
        print("Control lost")
        self.listening = False
        # Listener thread will stop because on_release returns False


# ---------- Pet Widget ----------
class RAMsey(QWidget):
    def __init__(self):
        super().__init__()

        self.y_pos = self.y()
        self.vy = 0
        self.gravity = 1
        self.ground_y = 1000
        self.on_ground = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Load and scale body
        original_body = QPixmap("body.png")
        self.body_pixmap = original_body.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.body_label = QLabel(self)
        self.body_label.setPixmap(self.body_pixmap)
        self.body_label.resize(self.body_pixmap.size())

        # Load and scale head
        original_head = QPixmap("head_top.png")
        self.head_pixmap = original_head.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.head_label = QLabel(self)
        self.head_label.setPixmap(self.head_pixmap)
        self.head_label.resize(self.head_pixmap.size())

        # Resize and move
        self.resize(self.body_pixmap.size())
        self.move(300, 300)

        # Start head tracking
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)

    def tick(self):
        self.update_physics()
        self.update_head_position()

    def update_head_position(self):
        mouse_x, mouse_y = pyautogui.position()

        widget_center_x = self.x() + self.body_label.width() // 2
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

        head_x = self.body_label.x() + self.body_label.width() // 2 - rotated.width() // 2
        head_y = self.body_label.y() - rotated.height() // 2 + 10

        self.head_label.move(head_x, head_y)

    def update_physics(self):
        if not self.on_ground:
            self.vy += self.gravity
            self.y_pos += self.vy

            if self.y_pos >= self.ground_y:
                self.y_pos = self.ground_y
                self.vy = 0
                self.on_ground = True

        self.move(self.x(), int(self.y_pos))


# ---------- Main ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = RAMsey()
    pet.show()

    control_panel = ControlPanel()
    control_panel.move(100, 100)
    control_panel.show()

    sys.exit(app.exec())

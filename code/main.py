import multiprocessing
import math
import sys
import os
import random
import tkinter

multiprocessing.set_start_method("spawn", force=True)

from PyQt6.QtWidgets import QApplication, QSlider, QFileDialog, QLabel, QWidget, QPushButton, QVBoxLayout, QComboBox, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint
import weakref

TK_SILENCE_DEPRECATION = 1

try:
    root = tkinter.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
except Exception as e:
    print(f"Warning: Tkinter initialization failed or not needed: {e}")

    app_for_screen_size = QApplication.instance()
    if app_for_screen_size is None:
        app_for_screen_size = QApplication(sys.argv)
    screen = app_for_screen_size.primaryScreen().size()
    width = screen.width()
    height = screen.height()

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

images_folder = resource_path("images")
body_path = os.path.join(images_folder, "body.png")
head_path = os.path.join(images_folder, "head_top.png")

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

        self.file_type_selector.currentTextChanged.connect(self._update_selected_file_type)

        style_sheet = """
            QPushButton {
                background-color: #555;
                color: white;
                padding: 5px 10px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #777;
            }
        """

        self.button5.setStyleSheet(style_sheet)
        self.button3.setStyleSheet(style_sheet)
        self.button4.setStyleSheet(style_sheet)

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

        self.ramsey_list = []

    def closeEvent(self, event):
        event.ignore()
        self.show()
        print(f"Control panel close attempt")

    def _update_selected_file_type(self, file_type):
        self.allowed_file_types = [file_type]
        print(f"Allowed file types updated to: {self.allowed_file_types}")

    def feed_ramsey(self):
        if self.ramsey_list and len(self.ramsey_list) > 0:
            self.fedornot = True
            self.label1.setText("RAMsey ate!")
            self.cooldown_time = random.randint(10000, 20000)

            self.healthslider.setRange(0, self.cooldown_time // 200)
            self.healthslider.setValue(self.cooldown_time // 200)
            QTimer.singleShot(self.cooldown_time, self.get_hungry_again)
        else:
            self.label1.setText("No RAMsey spawned yet!")

    def update_slider(self):
        if self.fedornot and self.cooldown_time > 0:
            self.cooldown_time -= 100

            current_slider_value = max(0, self.cooldown_time // 200)
            self.healthslider.setValue(current_slider_value)
        elif not self.fedornot:
            self.healthslider.setValue(0)

    def my_repeated_function(self):
        if self.fedornot:
            self.label1.setText("RAMsey is full for a bit")
            return

        if not self.ramsey_list:
            self.label1.setText("No RAMsey to feed!")
            return

        if self.os_selectedpath:
            files = [f for f in os.listdir(self.os_selectedpath)
                     if os.path.isfile(os.path.join(self.os_selectedpath, f)) and
                     any(f.endswith(ext) for ext in self.allowed_file_types)]

            if not files:
                self.label1.setText(f"Folder empty or no '{self.allowed_file_types[0]}' files present.")
                return

            random_index = random.randint(0, len(files) - 1)
            file_to_delete = files[random_index]
            file_path = os.path.join(self.os_selectedpath, file_to_delete)

            self.ramsey_list[0].eat_file(file_path)
            self.label1.setText(f"File eaten: {file_to_delete}")

            self.fedornot = True
            self.cooldown_time = random.randint(10000, 20000)
            self.healthslider.setRange(0, self.cooldown_time // 200)
            self.healthslider.setValue(self.cooldown_time // 200)
            QTimer.singleShot(self.cooldown_time, self.get_hungry_again)

        else:
            self.label1.setText("Select a folder for RAMsey to eat from!")

    def get_hungry_again(self):
        self.fedornot = False
        self.cooldown_time = 0
        self.label1.setText("RAMsey is hungry again!")
        self.healthslider.setValue(0)

    def kill(self):
        self.fedornot = False
        self.timer.stop()
        self.slider_timer.stop()

        for ramsey in self.ramsey_list:
            ramsey.timer.stop()
            ramsey.idle_timer.stop()
            ramsey.cube_timer.stop()
            if ramsey.smooth_timer:
                ramsey.smooth_timer.stop()
            ramsey.hide()

        self.label1.setText("Emergency Stop Activated! Restart program to continue!")

        self.button3.setEnabled(False)
        self.button4.setEnabled(False)
        self.file_type_selector.setEnabled(False)

    def set_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.os_selectedpath = folder_path
            self.label.setText(f"Selected: {os.path.basename(folder_path)}")
        else:
            self.label.setText("No folder selected")

class ControlPanel(QWidget):
    def __init__(self, ramsey_list):
        super().__init__()
        self.ramsey_list = ramsey_list
        self.current_ramsey_index = 0

        self.button1 = QPushButton("Control RAMsey", self)
        self.button2 = QPushButton("Give up control", self)
        self.spawn_button = QPushButton("Spawn new RAMsey", self)
        self.next_ramsey_button = QPushButton("Next RAMsey", self)
        self.stats_button = QPushButton("Open Stats Board!", self)
        self.info_button = QPushButton("Open Information Tab", self)

        self.ramsey_selector = QComboBox(self)
        self.update_ramsey_selector()

        button_style = """
            QPushButton {
                background-color: 
                color: white;
                padding: 5px 10px;
                border-radius: 10px;
            }QPushButton:hover {
                background-color: 
            }"""
        self.button1.setStyleSheet(button_style)
        self.button2.setStyleSheet(button_style)
        self.spawn_button.setStyleSheet(button_style)
        self.next_ramsey_button.setStyleSheet(button_style)
        self.stats_button.setStyleSheet(button_style)
        self.info_button.setStyleSheet(button_style)

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

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def closeEvent(self, event):
        event.ignore()
        self.show()
        print(f"Control panel close attempt")

    def open_info_board(self):
        self.info_board = InfoBoard()
        self.info_board.show()

    def open_stats_board(self):
        self.stats_board = StatsBoard(self.ramsey_list)
        self.stats_board.show()

    def update_ramsey_selector(self):
        self.ramsey_selector.clear()
        if not self.ramsey_list:
            self.ramsey_selector.addItem("No RAMseys")
            self.button1.setEnabled(False) 
            self.next_ramsey_button.setEnabled(False)
            return

        self.button1.setEnabled(True)
        self.next_ramsey_button.setEnabled(True)
        for i, ramsey in enumerate(self.ramsey_list):
            self.ramsey_selector.addItem(f"RAMsey #{i + 1}")

        if self.current_ramsey_index >= len(self.ramsey_list):
            self.current_ramsey_index = 0
        self.ramsey_selector.setCurrentIndex(self.current_ramsey_index)

    def spawn_ramsey(self):
        new_ramsey = RAMsey(None, self.ramsey_list)
        self.ramsey_list.append(new_ramsey)
        new_ramsey.show()
        self.update_ramsey_selector()

        self.ramsey_selector.setCurrentIndex(len(self.ramsey_list) - 1)

    def next_ramsey(self):
        if not self.ramsey_list:
            return
        self.current_ramsey_index = (self.current_ramsey_index + 1) % len(self.ramsey_list)
        self.ramsey_selector.setCurrentIndex(self.current_ramsey_index)

    def select_ramsey(self, index):
        if 0 <= index < len(self.ramsey_list):
            self.current_ramsey_index = index
        else:
            self.current_ramsey_index = 0

    def on_clicked1(self):
        self.control_enabled = True
        self.setFocus() 
        print("Control enabled for RAMsey.")

    def on_clicked2(self):
        self.control_enabled = False
        print("Control disabled for RAMsey.")

    def keyPressEvent(self, event):
        if not self.control_enabled:
            for ramsey in self.ramsey_list:
                ramsey.random_movement()
            return

        key = event.key()
        if not self.ramsey_list: 
            return
        current_ramsey = self.ramsey_list[self.current_ramsey_index]

        if event.isAutoRepeat():
            return

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
        if not self.ramsey_list:
            return
        current_ramsey = self.ramsey_list[self.current_ramsey_index]

        if event.isAutoRepeat():
            return

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
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(30)

        original_head = QPixmap(head_path)
        if original_head.isNull():
            print(f"Error: head_top.png not found at {head_path}")

            self.head_pixmap = QPixmap(80, 80)
            self.head_pixmap.fill(Qt.GlobalColor.blue)
        else:
            self.head_pixmap = original_head.scaled(
                80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )

        self.body_pixmap = QPixmap(body_path)
        if self.body_pixmap.isNull():
            print(f"Error: body.png not found at {body_path}")

            self.body_pixmap = QPixmap(150, 150)
            self.body_pixmap.fill(Qt.GlobalColor.green)
        else:
            self.body_pixmap = self.body_pixmap.scaled(
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
        self.move(300, 300) 

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       
            Qt.WindowType.WindowStaysOnTopHint |      
            Qt.WindowType.Tool                        
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(30) 

        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.check_idle_and_move)
        self.idle_timer.start(2000) 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.GlobalColor.red)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

    def closeEvent(self, event):
        event.ignore()
        self.show()
        print(f"Ramsey was attemped to be yeeted")

    def eat_file(self, file_path):
        try:
            file_size_bytes = os.path.getsize(file_path)
            os.remove(file_path)
            self.files_eaten += 1
            self.total_size_deleted += file_size_bytes / 1024 
            print(f"RAMsey ate {file_path}. Size: {file_size_bytes / 1024:.2f}KB")
        except FileNotFoundError:
            print(f"File not found (already eaten or moved?): {file_path}")
            if hasattr(self.parent(), 'get_hungry_again'):
                self.parent().get_hungry_again()
        except Exception as e:
            print(f"Error eating file {file_path}: {e}")
            if hasattr(self.parent(), 'get_hungry_again'):
                self.parent().get_hungry_again()

    def tick(self):
        self.update_movement()
        self.apply_gravity()
        self.check_collisions()  

        for other_ramsey in self.ramsey_list:
            if self != other_ramsey: 
                if self.check_collision(other_ramsey):
                    self.handle_collision(other_ramsey)

    def check_collisions(self):
        if not hasattr(self.parent(), 'blocks'):
            return

        ramsey_global = QRect(self.mapToGlobal(QPoint(0, 0)), self.size())
        print(f"RAMsey global rect: {ramsey_global}")

        for block in self.parent().blocks[:]:
            if not block.isVisible():
                print(f"Block at {block.pos()} is not visible")
                continue

            block_global = QRect(block.mapToGlobal(QPoint(0, 0)), block.size())
            print(f"Block global rect: {block_global}")

            if ramsey_global.intersects(block_global):
                print(f"Collision detected! RAMsey at {ramsey_global}, Block at {block_global}")
                self.handle_collision(block)
                break  

    def handle_collision(self, block):
        print(f"Handling collision with block at {block.pos()}")
        try:
            self.parent().blocks.remove(block)  
            block.deleteLater()  

            if hasattr(self.parent(), 'stats_board'):
                self.parent().stats_board.collisions += 1

            print(f"Block successfully removed after collision: {block}")
        except ValueError:
            print(f"Block already removed: {block}")

    def check_idle_and_move(self):
        if not self.move_left and not self.move_right and self.target_x is None:
            self.random_movement()

    def random_movement(self):
        self.move_left = False
        self.move_right = False 

        direction = random.choice(["Left", "Right"])
        distance = random.randint(50, 150)

        screen_width = QApplication.primaryScreen().size().width()
        if direction == "Left":
            self.target_x = max(0, self.x() - distance)
        elif direction == "Right":
            self.target_x = min(screen_width - self.width(), self.x() + distance)

        self.start_smooth_movement()

    def start_smooth_movement(self):
        if self.smooth_timer and self.smooth_timer.isActive():
            self.smooth_timer.stop()

        self.smooth_timer = QTimer()
        self.smooth_timer.timeout.connect(self.perform_smooth_movement)
        self.smooth_timer.start(30) 

    def perform_smooth_movement(self):
        if self.target_x is None:
            if self.smooth_timer: self.smooth_timer.stop()
            return

        current_x = self.x()
        step = 5 

        if current_x < self.target_x:
            new_x = min(current_x + step, self.target_x)
        elif current_x > self.target_x:
            new_x = max(current_x - step, self.target_x)
        else:
            if self.smooth_timer: self.smooth_timer.stop()
            self.target_x = None 
            return

        self.move(new_x, self.y())

    def update_movement(self):
        x = self.x()
        current_speed = self.sprint_speed if self.shiftpress else self.speed

        if self.target_x is None:
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

            screen_height = QApplication.primaryScreen().size().height()
            ground_level = screen_height - self.height()

            if new_y >= ground_level:
                new_y = ground_level 
                self.vy = 0 
                self.on_ground = True

            self.move(self.x(), new_y)

    def check_collision(self, other):
        rect1 = self.geometry()
        rect2 = other.geometry()
        return rect1.intersects(rect2)

    def handle_collision(self, other):
        if self.x() < other.x():
            self.move(self.x() - 10, self.y())
            other.move(other.x() + 10, self.y())
        else:
            self.move(self.x() + 10, self.y())
            other.move(other.x() - 10, self.y())

class StatsBoard(QWidget):
    def __init__(self, ramsey_list):
        super().__init__()
        self.ramsey_list = ramsey_list
        self.collisions = 0  
        self.setWindowTitle("RAMsey Stats Board")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        self.files_eaten_label = QLabel("Files Eaten: 0", self)
        self.total_size_label = QLabel("Total Size Deleted: 0KB", self)
        self.ramsey_count_label = QLabel(f"RAMseys Active: {len(self.ramsey_list)}", self)
        self.collisions_label = QLabel("Collisions: 0", self)  

        layout.addWidget(self.files_eaten_label)
        layout.addWidget(self.total_size_label)
        layout.addWidget(self.ramsey_count_label)
        layout.addWidget(self.collisions_label) 
        layout.addStretch()
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def update_stats(self):
        total_files_eaten = sum(ramsey.files_eaten for ramsey in self.ramsey_list)
        total_size_deleted_kb = sum(ramsey.total_size_deleted for ramsey in self.ramsey_list)

        self.files_eaten_label.setText(f"Files Eaten: {total_files_eaten}")

        if total_size_deleted_kb < 1024:
            self.total_size_label.setText(f"Total Size Deleted: {total_size_deleted_kb:.2f}KB")
        elif total_size_deleted_kb < (1024 * 1024):
            self.total_size_label.setText(f"Total Size Deleted: {total_size_deleted_kb / 1024:.2f}MB")
        else:
            self.total_size_label.setText(f"Total Size Deleted: {total_size_deleted_kb / (1024 * 1024):.2f}GB")

        self.ramsey_count_label.setText(f"RAMseys Active: {len(self.ramsey_list)}")
        self.collisions_label.setText(f"Collisions: {self.collisions}") 

class InfoBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Information")
        self.setFixedSize(300, 400)

        layout = QVBoxLayout()
        self.information = QLabel(self)
        self.information.setText(
            '<p>Hello, thank you for choosing to use RAMsey!</p>'
            '<p>If you have chosen to use RAMsey, then you certainly have great taste.</p>'
            '<p>RAMsey is a desk pet that hovers around your desktop and sometimes likes to eat your files.</p>'
            '<p>Visit the <a href="https://github.com/Githubuser1122bruh/RAMsey">GitHub page for RAMsey</a> for more information.</p>'
            '<p>This is made for a project called shipwrecked which is hosted by HackClub, a non profit organisation to help teens code!</p>'
            '<p>To get more information about hackclub, visit <a href="https://hackclub.com">hackclub.com</a>. Please star the GitHub repository!</p>'
            '<p>You can interact with the red spawning apples, those give you achievements and let you advance!</p>'
        )

        self.information.setOpenExternalLinks(True) 
        self.information.setWordWrap(True) 
        layout.addWidget(self.information)
        self.setLayout(layout)

class Block(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        screen_geometry = QApplication.primaryScreen().geometry()
        x = random.randint(0, screen_geometry.width() - 50)
        y = 950
        self.move(x, y)
        QTimer.singleShot(10000, self.deleteLater)

        self.collision_rect = QRect(self.mapToGlobal(QPoint(0, 0)), self.size())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self.color)
        painter.setPen(Qt.GlobalColor.red)  
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))  
        painter.setPen(Qt.PenStyle.NoPen)  
        painter.setBrush(self.color)  
        painter.drawRect(self.rect().adjusted(1, 1, -2, -2))  

class BlockManager:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.blocks = []
        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_block)
        self.spawn_timer.start(5000) 

    def spawn_block(self):
        block = Block(self.parent_widget)
        block.show()
        block.destroyed.connect(lambda: self.remove_block(block))
        self.blocks.append(block)

    def remove_block(self, block):
        try:
            self.blocks.remove(block)
            print(f"Block removed: {block}")
        except ValueError:
            print(f"Block already removed: {block}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    screen = app.primaryScreen().availableGeometry()
    screen_width, screen_height = screen.width(), screen.height()

    ramsey_list = []

    widget = MyWidget()
    widget.ramsey_list = ramsey_list

    first_ramsey = RAMsey(widget, ramsey_list)
    ramsey_list.append(first_ramsey)

    control_panel = ControlPanel(ramsey_list)

    block_manager = BlockManager(widget)
    widget.blocks = block_manager.blocks  

    def center_window(window):
        window.move(
            (screen_width - window.width()) // 2,
            (screen_height - window.height()) // 2
        )

    for w in [widget, first_ramsey, control_panel]:
        w.show()
        center_window(w)

    sys.exit(app.exec())
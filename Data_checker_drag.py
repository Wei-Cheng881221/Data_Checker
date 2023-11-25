from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, \
QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMenuBar, QAction, \
QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QGraphicsScene, QGraphicsView, \
QMessageBox, QAbstractItemView, QScrollArea, QSizePolicy, QShortcut, QGraphicsRectItem, QDesktopWidget
from PyQt5.QtGui import QFont, QPainter, QBrush, QColor, QPalette, QKeySequence
from PyQt5.QtCore import Qt, QRect, QRectF
import sys
import json
import pandas as pd
import argparse
import os 
from datetime import datetime
import  Interactive_Audiogram

class ImageInfoWindow(QMainWindow):
    def __init__(self, path_list, width_, height_):
        super().__init__()
        self.initUI(path_list, width_, height_)

    def initUI(self, path_list, width_, height_):
        self.path_list = path_list
        self.width_ = width_
        self.height_ = height_

        # Create a menubar using the Menubar class
        self.Display_mode = 'checker_mode'
        self.menubar = Menubar(self)
        self.setMenuBar(self.menubar)
        
        # Create a grid layout
        self.file_seq = self.read_log(path_list[0], path_list[1])
        self.grid_layout = GridLayout(self, path_list)

        #keyboard shortcut for next file
        self.shortcut1 = QShortcut(QKeySequence("Alt+Right"), self)
        self.shortcut1.activated.connect(self.menubar.loadNextFile)

        #keyboard shortcut for previous file
        self.shortcut2 = QShortcut(QKeySequence("Alt+Left"), self)
        self.shortcut2.activated.connect(self.menubar.loadPrevFile)

        # Create a central widget and set the grid layout as its layout
        central_widget = QWidget()
        central_widget.setLayout(self.grid_layout)

        # Set the central widget of the main window
        self.setCentralWidget(central_widget)

    def read_log(self, image_path, json_path):
        try:
            with open("info.json", "r") as file:
                info_data = json.load(file)
        except FileNotFoundError:
            print("File not found.")
            return 0
        except json.JSONDecodeError:
            print("Error decoding JSON.")
            return None

        if info_data:
            image_files_old = info_data.get("image_file", [])
            json_files_old = info_data.get("json_path", [])
            last_time = info_data.get("last_time", 0)

            if image_files_old == image_path and json_files_old == json_path:
                return last_time
            else:
                return 0

    def write_log(self, last_stop, image_path, json_path):

        output_data = {
            "image_file" : image_path,
            "json_path" : json_path,
            "last_time": last_stop
        }

        with open("info.json", "w") as output_file:
            json.dump(output_data, output_file, indent=4)

    def closeEvent(self, event):
        # This method is called when the window is about to be closed
        reply = QMessageBox.question(self, "Confirm Exit",
                                     "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Here you can perform actions or gather information before closing
            event.accept()
            self.write_log(self.file_seq, self.path_list[0], self.path_list[1])
        else:
            event.ignore()

class GridLayout(QGridLayout):
    def __init__(self, parent, path_list):
        super().__init__()
        self.parent = parent
        self.setSpacing(10)
        self.json_path = path_list[1][self.parent.file_seq]
        self.image_path = path_list[0][self.parent.file_seq]

        self.label_picture = PictureFrame(parent)
        self.addWidget(self.label_picture, 0, 0, 1, 1)   # y, x, height, width

        self.digital_audiogram = Interactive_Audiogram.Digital_Audiogram(parent)
        self.addWidget(self.digital_audiogram, 0, 1, 1, 1)

class PictureFrame(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # print(self.parent.width_, type(self.parent.width_))
        self.setFixedSize(int(self.parent.width_ / 2)-60, int(self.parent.height_ - 120))
        # self.setFixedSize(950, 850)
        self.drag_pos = None
        self.zoom_factor = 1.0

        self.view = QGraphicsView(self)
        self.view.setFixedSize(int(self.parent.width_ / 2)-60, int(self.parent.height_ - 120))
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        # self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # load first image
        self.load_image()

        # Set the layout for the frame
        layout = QVBoxLayout()
        self.setLayout(layout)


    def load_image(self):
        # print(self.parent.path_list[0][self.parent.file_seq])
        self.im = QPixmap(self.parent.path_list[0][self.parent.file_seq])
        self.coordinate_info = pd.read_json(self.parent.path_list[1][self.parent.file_seq]).iloc[0]
        max_scene_width = int(self.parent.width_ / 2)-60
        max_scene_height = int(self.parent.height_ - 120)
        self.view.resetTransform()
        self.c_im = None
        if not (self.coordinate_info["ear"] == 'right' or \
        self.coordinate_info["ear"] == 'left' or \
        self.coordinate_info["ear"] == 'both'):
            x = self.coordinate_info['x coordinate']
            y = self.coordinate_info['y coordinate']
            w = self.coordinate_info['width ratio']
            h = self.coordinate_info['height ratio']
            cropped_width  = w * self.im.width()
            cropped_height = h * self.im.height()
            self.scale_factor = min(max_scene_width / cropped_width, max_scene_height / cropped_height)
            self.c_im = self.im.copy(int(x * self.im.width() - w * self.im.width() / 2),
                                     int(y * self.im.height() - h * self.im.height() / 2),
                                     int(w * self.im.width()),
                                     int(h * self.im.height()))
            self.view.scale(self.scale_factor, self.scale_factor)

        self.scene = QGraphicsScene(self)
        if(self.c_im):
            self.scene.addPixmap(self.c_im)
        else:
            self.scene.addPixmap(self.im)

        self.original_rect = QRectF(0,0,0,0)
        self.rect_item = QGraphicsRectItem(self.original_rect)
        self.scene.addItem(self.rect_item)

        self.view.setScene(self.scene)

class Menubar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        #set the font size of menubar
        font = QFont()
        font.setPointSize(16)
        self.setFont(font)

        # Add a "File" menu to the menubar
        File_menu = self.addMenu('File')
        Info_menu = self.addMenu('Info')
        Mode_menu = self.addMenu('Mode')

        next_action = QAction('Next', self)
        next_action.triggered.connect(self.loadNextFile)
        File_menu.addAction(next_action)

        prev_action = QAction('Previous', self)
        prev_action.triggered.connect(self.loadPrevFile)
        File_menu.addAction(prev_action)

        how_to_use = QAction('How to use', self)
        Info_menu.addAction(how_to_use)

        checker_mode = QAction('Checker Mode', self)
        checker_mode.triggered.connect(self.change_to_checker)
        clinical_mode = QAction('Clinical Mode', self)
        clinical_mode.triggered.connect(self.change_to_clinical)
        Mode_menu.addAction(checker_mode)
        Mode_menu.addAction(clinical_mode)

    def loadNextFile(self):
        if(self.parent.file_seq == len(self.parent.path_list[1])-1):
            QMessageBox.information(None, 'Reach last file', f'This is the last file in this folder!')
            return
        self.parent.file_seq = self.parent.file_seq + 1
        self.parent.grid_layout.label_picture.load_image()
        self.parent.grid_layout.digital_audiogram.load_in()
        self.parent.grid_layout.json_path = self.parent.path_list[1][self.parent.file_seq]

    def loadPrevFile(self):
        if(self.parent.file_seq == 0):
            QMessageBox.information(None, 'Reach First file', f'This is the first file in this folder!')
            return
        self.parent.file_seq = self.parent.file_seq - 1
        self.parent.grid_layout.label_picture.load_image()
        self.parent.grid_layout.digital_audiogram.load_in()
        self.parent.grid_layout.json_path = self.parent.path_list[1][self.parent.file_seq]

    def change_to_checker(self):
        self.parent.Display_mode = 'checker_mode'
        self.parent.grid_layout.digital_audiogram.set_layout()

    def change_to_clinical(self):
        self.parent.Display_mode = 'clinical_mode'
        self.parent.grid_layout.digital_audiogram.set_layout()

def check_path_valid(image_path, json_path):
    image_names = []
    json_names = []
    if os.path.isfile(image_path) and os.path.isfile(json_path):
        file_names.append(image_path)
        file_names.append(json_path)
    elif os.path.exists(image_path) and os.path.exists(json_path):
        jpg_files = [f for f in os.listdir(image_path) if f.endswith(".jpg")]

        for jpg_file in jpg_files:
            jpg_name_without_extension = os.path.splitext(jpg_file)[0]
            json_file = jpg_name_without_extension + ".json"
            if json_file in os.listdir(json_path):
                json_names.append(os.path.join(json_path, json_file))
                image_names.append(os.path.join(image_path, jpg_file))
        json_names.sort()
        image_names.sort()

    else:
        raise FileNotFoundError(f"File or folder not found: {image_path} or {json_path}  !\nThe program might crash later !")   
    return image_names, json_names

def main():
    parser = argparse.ArgumentParser(description='The following is the arguments of this application')
    parser.add_argument("-i", "--image_path", help = "The input path to one image or a folder path of images", default = './open_image')
    parser.add_argument("-j", "--json_path", help = "The input path to one json or a folder path of json", default = './open_json')
    args = parser.parse_args()
    
    try:
        image_path, json_path = check_path_valid(args.image_path, args.json_path)
        # print(image_path, json_path)
    except FileNotFoundError as fnfe:
        print(fnfe)
        input("Press Enter to continue...")

    app = QApplication(sys.argv)
    screen = QDesktopWidget().screenGeometry()
    width, height = screen.width(), screen.height()
    window = ImageInfoWindow([image_path, json_path], width, height)
    # window.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint);
    # Set the window's size to match the screen
    # window.resize(width, height)
    # window.showFullScreen()
    window.show()
    # window.resize(1920, 1080) # comments this line when using windows

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

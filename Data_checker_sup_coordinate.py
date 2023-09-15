from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, \
QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMenuBar, QAction, \
QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QGraphicsScene, QGraphicsView, \
QMessageBox, QAbstractItemView, QScrollArea, QSizePolicy, QShortcut, QGraphicsRectItem
from PyQt5.QtGui import QFont, QPainter, QBrush, QColor, QPalette, QKeySequence, QPen
from PyQt5.QtCore import Qt, QRect, QRectF
import sys
import json
import pandas as pd
import numpy as np
import argparse
import os 
from datetime import datetime

class ImageInfoWindow(QMainWindow):
    def __init__(self, path_list):
        super().__init__()
        self.initUI(path_list)

    def initUI(self, path_list):
        self.path_list = path_list

        # Create a grid layout
        self.file_seq = self.read_log(path_list[0], path_list[1])
        self.grid_layout = GridLayout(self, path_list)

        # Create a menubar using the Menubar class
        self.menubar = Menubar(self)
        self.setMenuBar(self.menubar)
        
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
        self.addWidget(self.label_picture, 0, 0, 4, 1)   # y, x, height, width
        
        self.dataframe = DataFrame(parent, self.json_path)
        self.addWidget(self.dataframe, 0, 1, 3, 1)

        self.modifyframe = ModifyFrame(self, self.json_path)
        self.addWidget(self.modifyframe, 3, 1, 1, 1)

class PictureFrame(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedSize(1000, 960)
        self.drag_pos = None
        self.zoom_factor = 1.0

        self.view = QGraphicsView(self)
        self.view.setFixedSize(1000, 960)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.load_image()

        # Create zoom in and zoom out buttons
        # self.zoom_in_button = QPushButton("+", self)
        # self.zoom_out_button = QPushButton("-", self)

        # Create a layout for the buttons and the view
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        # layout.addWidget(self.zoom_in_button)
        # layout.addWidget(self.zoom_out_button)

        # Set the layout for the frame
        self.setLayout(layout)

        # Connect the buttons to the zoom functions
        # self.zoom_in_button.clicked.connect(self.zoom_in)
        # self.zoom_out_button.clicked.connect(self.zoom_out)

    def load_image(self):
        print(self.parent.path_list[0][self.parent.file_seq])
        self.im = QPixmap(self.parent.path_list[0][self.parent.file_seq])
        self.coordinate_info = pd.read_json(self.parent.path_list[1][self.parent.file_seq]).iloc[0]
        max_scene_width = 1000
        max_scene_height = 960
        self.view.resetTransform()
        print(self.coordinate_info[0])
        if not (self.coordinate_info["ear"] == 'right' or self.coordinate_info["ear"] == 'left' or self.coordinate_info["ear"] == 'both'):
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
        self.scene.addPixmap(self.c_im)

        self.original_rect = QRectF(0,0,0,0)
        self.rect_item = QGraphicsRectItem(self.original_rect)
        self.scene.addItem(self.rect_item)

        # self.scene.addPixmap(cropped_pixmap)
        self.view.setScene(self.scene)
        # if not (coordinate_info['ear'] == 'right' or coordinate_info['ear'] == 'left' or coordinate_info['ear'] == 'both'):
            
        
    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1 / 1.2, 1 / 1.2)

class DataFrame(QFrame):
    def __init__(self, parent, json_path):
        super().__init__()
        self.parent = parent
        self.json_path = json_path

        self.setStyleSheet("background-color:white")
        self.DataFrame_Layout = QVBoxLayout(self) #QGridLayout()
        self.tables = [MyTable(self.parent) for i in range(5)]
        self.first_time = True
        self.load_in()
        self.setLayout(self.DataFrame_Layout)

    def load_in(self):
        print(self.parent.path_list[1][self.parent.file_seq])
        # print("==========================")
        self.readfile(self.parent.path_list[1][self.parent.file_seq])
        self.all_list = [self.data_air_fal] + [self.data_air_tru] + [self.data_bon_fal] + [self.data_bon_tru]
        symbol_list = ['X', 'O', '☐', '△', '>', '<', ']', '[']
        self.freq = ['125', '250', '500', '750', '1000', '1500', '2000', '3000', '4000', '6000', '8000', '12000']
        self.threshold = []
        self.threshold_SF = [['Both S'], ['AR'],  ['AL'], ['Both C'], ['Both A'], ['Right S'], ['Left S'], ['Right C'], ['Left C'], ['Right A'], ['Left A']]
        self.response = []
        self.response_SF = [['Both S'], ['AR'],  ['AL'], ['Both C'], ['Both A'], ['Right S'], ['Left S'], ['Right C'], ['Left C'], ['Right A'], ['Left A']]
        self.bbox = []
        self.bbox_SF = [[], [], [], [], [], [], [], [], [], [], []]
       # Handle normal data input
        set_l = 0
        set_r = 0
        for k in range(len(self.all_list)):
            response_temp_l = ['']
            response_temp_r = ['']
            bbox_temp_l = []
            bbox_temp_r = []
            threshold_tmep_l = [f'Left   {symbol_list[k*2]} ']
            threshold_tmep_r = [f'Right  {symbol_list[k*2+1]} ']
            for i in self.freq:
                for j in self.all_list[k]:
                    # ear, freq, threshold, response, bbox
                    if (not set_l and i == str(j[1]) and str(j[0]) == 'left'):
                        threshold_tmep_l.append(j[2])
                        response_temp_l.append(j[3])
                        bbox_temp_l.append(j[4])
                        set_l = 1
                        continue
                    if (not set_r and i == str(j[1]) and str(j[0]) == 'right'):
                        threshold_tmep_r.append(j[2])
                        response_temp_r.append(j[3])
                        bbox_temp_r.append(j[4])
                        set_r = 1
                        continue
                if set_l == 0:
                    threshold_tmep_l.append('')
                    response_temp_l.append('')
                    bbox_temp_l.append([])
                if set_r == 0:
                    threshold_tmep_r.append('')
                    response_temp_r.append('')
                    bbox_temp_r.append([])
                set_l = 0
                set_r = 0
            self.threshold.append(threshold_tmep_r)
            self.threshold.append(threshold_tmep_l)

            self.response.append(response_temp_r)
            self.response.append(response_temp_l)

            self.bbox.append(bbox_temp_r)
            self.bbox.append(bbox_temp_l)
        
        # Handle SoundField data input
        for i in self.freq:
            SF_set = [0 for i in range(11)]
            for j in self.data_sf:
                if (i == str(j[1]) and str(j[0]) == 'both' and j[5] == 'SOUND_FIELD' and SF_set[0] == 0):
                    self.threshold_SF[0].append(j[2])
                    self.response_SF[0].append(j[3])
                    self.bbox_SF[0].append(j[4])
                    SF_set[0] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[5] == 'AR' and SF_set[1] == 0):
                    self.threshold_SF[1].append(j[2])
                    self.response_SF[1].append(j[3])
                    self.bbox_SF[1].append(j[4])
                    SF_set[1] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[5] == 'AL' and SF_set[2] == 0):
                    self.threshold_SF[2].append(j[2])
                    self.response_SF[2].append(j[3])
                    self.bbox_SF[2].append(j[4])
                    SF_set[2] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'both' and j[5] == 'COCHLEAR_IMPLANT' and SF_set[3] == 0):
                    self.threshold_SF[3].append(j[2])
                    self.response_SF[3].append(j[3])
                    self.bbox_SF[3].append(j[4])
                    SF_set[3] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'both' and j[5] == 'HEARING_AID' and SF_set[4] == 0):
                    self.threshold_SF[4].append(j[2])
                    self.response_SF[4].append(j[3])
                    self.bbox_SF[4].append(j[4])
                    SF_set[4] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[5] == 'SOUND_FIELD' and SF_set[5] == 0):
                    self.threshold_SF[5].append(j[2])
                    self.response_SF[5].append(j[3])
                    self.bbox_SF[5].append(j[4])
                    SF_set[5] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[5] == 'SOUND_FIELD' and SF_set[6] == 0):
                    self.threshold_SF[6].append(j[2])
                    self.response_SF[6].append(j[3])
                    self.bbox_SF[6].append(j[4])
                    SF_set[6] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[5] == 'COCHLEAR_IMPLANT' and SF_set[7] == 0):
                    self.threshold_SF[7].append(j[2])
                    self.response_SF[7].append(j[3])
                    self.bbox_SF[7].append(j[4])
                    SF_set[7] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[5] == 'COCHLEAR_IMPLANT' and SF_set[8] == 0):
                    self.threshold_SF[8].append(j[2])
                    self.response_SF[8].append(j[3])
                    self.bbox_SF[8].append(j[4])
                    SF_set[8] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[5] == 'HEARING_AID' and SF_set[9] == 0):
                    self.threshold_SF[9].append(j[2])
                    self.response_SF[9].append(j[3])
                    self.bbox_SF[9].append(j[4])
                    SF_set[9] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[5] == 'HEARING_AID' and SF_set[10] == 0):
                    self.threshold_SF[10].append(j[2])
                    self.response_SF[10].append(j[3])
                    self.bbox_SF[10].append(j[4])
                    SF_set[10] = 1
                    continue
            for i in range(len(SF_set)):
                if SF_set[i] == 0:
                    self.threshold_SF[i].append('')
                    self.response_SF[i].append('')
                    self.bbox_SF[i].append('')
        self.title = ['Air without masking', 'Air with masking', 'Bone without masking' , 'Bone with masking', \
                'Sound Field']

        # show the data in the table
        for i in range(5):
            if(i == 4): # SoundField table is bigger
                self.tables[i].update(self.freq, self.threshold_SF, self.response_SF, i)
            else:
                self.tables[i].update(self.freq, self.threshold[i*2:i*2+2], self.response[i*2:i*2+2], i)
            self.tables[i].cellClicked.connect(self.tables[i].handle_cell_clicked)
            if(self.parent.file_seq == 0 and self.first_time == True):
                if(i == 4):
                    self.first_time = False
                title_i = QLabel(self.title[i])
                title_i.setFont(QFont('Arial', 10, QFont.Bold))
                self.DataFrame_Layout.addWidget(title_i)
                self.DataFrame_Layout.addWidget(self.tables[i])
            else:
                self.DataFrame_Layout.insertWidget(i*2+1, self.tables[i])

    def readfile(self, file):
                                # L R
        self.data_air_tru = []  # ☐ △
        self.data_air_fal = []  # X O
        self.data_bon_tru = []  # ] [
        self.data_bon_fal = []  # > <
        self.data_sf = []

        df = pd.read_json(file, dtype={'response': 'bool'})
        self.parent.setWindowTitle(f'{os.path.basename(file)} | Number of symbol detected : {df.shape[0]-1}')
        # print(f'Number of symbol detected : {df.shape[0]-1}')
        # print("==========================")
        for i in range(df.shape[0]):
            # ear, freq, threshold, response, bbox
            if((df.iloc[i]['conduction'] == 'air') and (df.iloc[i]['masking'] == True)):
                self.data_air_tru.append([df.iloc[i]['ear'], int(df.iloc[i]['frequency']), int(df.iloc[i]['threshold']), bool(df.iloc[i]['response']), \
                                         [df.iloc[i]['x coordinate'], df.iloc[i]['y coordinate'], df.iloc[i]['width ratio'], df.iloc[i]['height ratio']]])
            elif(df.iloc[i]['conduction'] == 'air' and df.iloc[i]['masking'] == False):
                # handle the extra cases 'SOUND_FIELD', 'NR_SOUND_FIELD', 'AL', 'AR', 'COCHLEAR_IMPLANT', 'HEARING_AID'
                if(df.iloc[i]['measurementType'] == 'SOUND_FIELD' or \
                    df.iloc[i]['measurementType'] == 'AL' or \
                    df.iloc[i]['measurementType'] == 'AR' or \
                    df.iloc[i]['measurementType'] == 'COCHLEAR_IMPLANT' or \
                    df.iloc[i]['measurementType'] == 'HEARING_AID'):
                    # ear, freq, threshold, response, bbox, measurementType
                    self.data_sf.append([df.iloc[i]['ear'], int(df.iloc[i]['frequency']), int(df.iloc[i]['threshold']), bool(df.iloc[i]['response']), \
                                         [df.iloc[i]['x coordinate'], df.iloc[i]['y coordinate'], df.iloc[i]['width ratio'], df.iloc[i]['height ratio']], \
                                         df.iloc[i]['measurementType']])
                else:
                    self.data_air_fal.append([df.iloc[i]['ear'], int(df.iloc[i]['frequency']), int(df.iloc[i]['threshold']), df.iloc[i]['response'], \
                                             [df.iloc[i]['x coordinate'], df.iloc[i]['y coordinate'], df.iloc[i]['width ratio'], df.iloc[i]['height ratio']]])
            elif(df.iloc[i]['conduction'] == 'bone' and df.iloc[i]['masking'] == True):
                self.data_bon_tru.append([df.iloc[i]['ear'], int(df.iloc[i]['frequency']), int(df.iloc[i]['threshold']), bool(df.iloc[i]['response']), \
                                         [df.iloc[i]['x coordinate'], df.iloc[i]['y coordinate'], df.iloc[i]['width ratio'], df.iloc[i]['height ratio']]])
            elif(df.iloc[i]['conduction'] == 'bone' and df.iloc[i]['masking'] == False):
                self.data_bon_fal.append([df.iloc[i]['ear'], int(df.iloc[i]['frequency']), int(df.iloc[i]['threshold']), bool(df.iloc[i]['response']), \
                                         [df.iloc[i]['x coordinate'], df.iloc[i]['y coordinate'], df.iloc[i]['width ratio'], df.iloc[i]['height ratio']]])

    def update_Table(self, json_path, which_type, side, freq_1, response, value):
        self.parent.grid_layout.json_path = json_path
        self.readfile(self.parent.grid_layout.json_path)
        item = QTableWidgetItem(value)
        item.setBackground(QBrush(QColor(255, 165, 0))) # yellow-orange color
        if(response == 'False'):
            item.setForeground(QBrush(QColor(120, 120, 120))) # custom light grey
        item.setTextAlignment(Qt.AlignCenter)
        index = self.freq.index(freq_1)
        if(which_type >= 4):
            self.tables[4].setItem(which_type-4, index+1, item)
        else:
            self.tables[which_type].setItem(0 if side == 'Right' else 1, index+1, item)
            find = 0
            for i, (ear, freq_2, _, _, [x, y, w, h]) in enumerate(self.parent.grid_layout.dataframe.all_list[which_type]):
                if ((ear == 'left' and side == 'Left') or (ear == 'right' and side == 'Right')) and int(freq_1) == freq_2:
                    find = 1
                    self.parent.grid_layout.dataframe.all_list[which_type][i][3] = bool(response) if response == 'True' else (False if response == 'False' else ' ')

            if find == 0:
                self.parent.grid_layout.dataframe.all_list[which_type].append(
                    [side, freq_1, value, response, [0, 0, 0, 0]])

class MyTable(QTableWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setStyleSheet(
            "QTableView { border: 2px solid black; gridline-color: black; background-color: lightblue; }"
            "QHeaderView::section { border-bottom: 1px solid black; background-color: red; }"
        )
        self.currentCellChanged.connect(self.handle_cell_clicked)

    def update(self, freq, threshold, response, which_table):
        self.which_table = which_table
        match self.which_table:
            case 0:
                self.table = 'Air without masking'
            case 1:
                self.table = 'Air with masking'
            case 2:
                self.table = 'Bone without masking'
            case 3:
                self.table = 'Bone with masking'
            case 4:
                self.table = 'Sound Field'
            
        font = QFont('Arial', 10, QFont.Bold)
        self.setFont(font)

        # Set number of rows and columns
        if(self.table == 'Sound Field'):
            self.setRowCount(11)
        else:
            self.setRowCount(2)
        self.setColumnCount(len(freq)+1)
        
        # Set column headers
        self.setHorizontalHeaderLabels(['Ear']+freq)
        
        header = self.horizontalHeader()
        header.setFont(font)
        custom_color = QColor(211, 211, 211)  # RGB values for light gray
        lighter_color = custom_color.lighter(150)  # Adjust the brightness (150 here)
        header.setStyleSheet("QHeaderView::section { background-color: %s }" % lighter_color.name())

        # Set row header (threshold)
        self.setVerticalHeaderLabels(['threshold'])
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setFont(font)

        # Set cell values for threshold row
        for j in range(len(threshold)):
            for i in range(len(threshold[0])):
                item = QTableWidgetItem(str(threshold[j][i]))
                if(response[j][i] == False):
                    item.setForeground(QBrush(QColor(120, 120, 120)))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(j, i, item)
                self.resizeColumnsToContents()

    def handle_cell_clicked(self, row, column):
        # Retrieve the content of the clicked cell
        item = self.item(row, column)
        content = "None" if item.text() == '' else item.text()
        
        if(self.which_table == 4):
            match row:
                case 0 | 5 | 6 : SF_combo = 'SOUND_FIELD'
                case 1 : SF_combo = 'AR'
                case 2 : SF_combo = 'AL'
                case 3 | 7 | 8 : SF_combo = 'COCHLEAR_IMPLANT'
                case 4 | 9 | 10 : SF_combo = 'HEARING_AID'
            self.parent.grid_layout.modifyframe.combo1.setCurrentIndex(self.parent.grid_layout.modifyframe.combo1.findText(SF_combo)) # type
            self.parent.grid_layout.modifyframe.combo2.setCurrentIndex(self.parent.grid_layout.modifyframe.combo2.findText('Both' if row == 0 or row == 3 or row == 4 \
                else ('Left' if row == 2 or row == 6 or row == 8 or row == 10 else'Right'))) # ear
            self.parent.grid_layout.modifyframe.combo3.setCurrentIndex(self.parent.grid_layout.modifyframe.combo3.findText(self.parent.grid_layout.dataframe.freq[column-1])) # frequency
            found = False
            for ear, freq, threshold, response, _, measurementtype in self.parent.grid_layout.dataframe.data_sf:
                if self.parent.grid_layout.dataframe.freq[column-1] == str(freq):
                    if (row == 0 and ear == 'both' and measurementtype == 'SOUND_FIELD') or \
                    (row == 1 and ear == 'right' and measurementtype == 'AR')or (row == 2 and ear == 'left' and measurementtype == 'AL') or \
                    (row == 3 and ear == 'both' and measurementtype == 'COCHLEAR_IMPLANT') or (row == 4 and ear == 'both' and measurementtype == 'HEARING_AID')or \
                    (row == 5 and ear == 'right' and measurementtype == 'SOUND_FIELD')or (row == 6 and ear == 'left' and measurementtype == 'SOUND_FIELD') or \
                    (row == 7 and ear == 'right' and measurementtype == 'COCHLEAR_IMPLANT')or (row == 8 and ear == 'left' and measurementtype == 'COCHLEAR_IMPLANT') or \
                    (row == 9 and ear == 'right' and measurementtype == 'HEARING_AID') or (row == 10 and ear == 'left' and measurementtype == 'HEARING_AID'):
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(self.parent.grid_layout.modifyframe.combo4.findText(str(response))) # response
                        found = True
            if found == False:
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(0) # response empty blank
            self.parent.grid_layout.modifyframe.input_line1.setText(content)
            if(len(self.parent.grid_layout.dataframe.bbox_SF[row][column-1]) == 4):
                x, y, w, h = self.parent.grid_layout.dataframe.bbox_SF[row][column-1]

                self.parent.grid_layout.modifyframe.input_save["x coordinate"] = x
                self.parent.grid_layout.modifyframe.input_save["y coordinate"] = y
                self.parent.grid_layout.modifyframe.input_save["width ratio"] = w
                self.parent.grid_layout.modifyframe.input_save["height ratio"] = h

                self.parent.grid_layout.label_picture.scene.removeItem(self.parent.grid_layout.label_picture.rect_item)
                im = self.parent.grid_layout.label_picture.im
                c_im = self.parent.grid_layout.label_picture.c_im
                x = (x * im.width() - int(self.parent.grid_layout.label_picture.coordinate_info['x coordinate'] * im.width() - self.parent.grid_layout.label_picture.coordinate_info['width ratio'] * im.width() / 2))
                y = (y * im.height() - int(self.parent.grid_layout.label_picture.coordinate_info['y coordinate'] * im.height() - self.parent.grid_layout.label_picture.coordinate_info['height ratio'] * im.height() / 2))
                w = w * im.width()
                h = h * im.height()

                x2 = x - w/2
                y2 = y - h/2
                pen = QPen(QColor(0, 255, 0))
                pen.setWidth(2)
                self.parent.grid_layout.label_picture.rect_item = self.parent.grid_layout.label_picture.scene.addRect(x2, y2, w, h, pen)
        else:
            self.parent.grid_layout.modifyframe.combo1.setCurrentIndex(self.parent.grid_layout.modifyframe.combo1.findText(self.table)) # type
            self.parent.grid_layout.modifyframe.combo2.setCurrentIndex(self.parent.grid_layout.modifyframe.combo2.findText('Left' if row == 1 else 'Right')) # ear
            self.parent.grid_layout.modifyframe.combo3.setCurrentIndex(self.parent.grid_layout.modifyframe.combo3.findText(self.parent.grid_layout.dataframe.freq[column-1])) # frequency
            found = False
            for ear, freq, threshold, response, _ in self.parent.grid_layout.dataframe.all_list[self.which_table]:
                if self.parent.grid_layout.dataframe.freq[column-1] == str(freq):
                    if (row == 0 and ear == 'right') or(row == 1 and ear == 'left'):
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(self.parent.grid_layout.modifyframe.combo4.findText(str(response))) # response
                        found = True
            if found == False:
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(0) # response empty blank
            if(len(self.parent.grid_layout.dataframe.bbox[self.which_table*2+row][column-1]) == 4):
                x, y, w, h = self.parent.grid_layout.dataframe.bbox[self.which_table*2+row][column-1]

                self.parent.grid_layout.modifyframe.input_save["x coordinate"] = x
                self.parent.grid_layout.modifyframe.input_save["y coordinate"] = y
                self.parent.grid_layout.modifyframe.input_save["width ratio"] = w
                self.parent.grid_layout.modifyframe.input_save["height ratio"] = h

                self.parent.grid_layout.label_picture.scene.removeItem(self.parent.grid_layout.label_picture.rect_item)
                im = self.parent.grid_layout.label_picture.im
                c_im = self.parent.grid_layout.label_picture.c_im
                x = (x * im.width() - int(self.parent.grid_layout.label_picture.coordinate_info['x coordinate'] * im.width() - self.parent.grid_layout.label_picture.coordinate_info['width ratio'] * im.width() / 2))
                y = (y * im.height() - int(self.parent.grid_layout.label_picture.coordinate_info['y coordinate'] * im.height() - self.parent.grid_layout.label_picture.coordinate_info['height ratio'] * im.height() / 2))
                w = w * im.width()
                h = h * im.height()

                x2 = x - w/2
                y2 = y - h/2
                pen = QPen(QColor(0, 255, 0))
                pen.setWidth(2)
                self.parent.grid_layout.label_picture.rect_item = self.parent.grid_layout.label_picture.scene.addRect(x2, y2, w, h, pen)
        self.parent.grid_layout.modifyframe.input_line1.setText(content)

class ModifyFrame(QFrame):
    def __init__(self, parent, json_path):
        super().__init__()
        self.parent = parent
        self.been_modify = False

        self.json_path = json_path
        self.new_file = "NEW FILE"
        self.get_file_version()
        
        self.input_save = {"Type": "None", "Side": "None", "Frequency" : "None", "Response": "None",
        "x coordinate" : "None", "y coordinate" : "None", "width ratio" : "None", "height ratio" : "None"}

        self.setStyleSheet("background-color:lightgrey")
        ModifyFrame_Layout = QVBoxLayout()

        self.Modify_Up_Frame = QFrame()
        ModifyFrame_Up_Layout = QGridLayout()

        Label1 = QLabel('Type : ')
        Label1.setFont(QFont('Arial', 12))
        Label1.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label1, 0, 0, 1, 1)
        self.combo1 = QComboBox()
        self.combo1.addItems([' ', 'Air without masking', 'Air with masking', 'Bone without masking', 'Bone with masking', \
            'SOUND_FIELD', 'AR', 'AL', 'COCHLEAR_IMPLANT', 'HEARING_AID'])
        self.combo1.currentIndexChanged.connect(lambda : self.GetCombo('Type'))
        self.combo1.setFont(QFont('Arial', 12))
        ModifyFrame_Up_Layout.addWidget(self.combo1, 0, 1, 1, 3)

        Label2 = QLabel('Side : ')
        Label2.setFont(QFont('Arial', 12))
        Label2.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label2, 0, 4, 1, 1)
        self.combo2 = QComboBox()
        self.combo2.addItems([' ', 'Left','Right', 'Both'])
        self.combo2.currentIndexChanged.connect(lambda : self.GetCombo('Side'))
        self.combo2.setFont(QFont('Arial', 12))
        ModifyFrame_Up_Layout.addWidget(self.combo2, 0, 5, 1, 2)

        Label3 = QLabel('Frequency : ')
        Label3.setFont(QFont('Arial', 12))
        Label3.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label3, 0, 7, 1, 1)
        self.combo3 = QComboBox()
        self.combo3.addItems(['']+self.parent.dataframe.freq)
        self.combo3.currentIndexChanged.connect(lambda : self.GetCombo('Frequency'))
        self.combo3.setFont(QFont('Arial', 12))
        ModifyFrame_Up_Layout.addWidget(self.combo3, 0, 8, 1, 2)

        self.Modify_Up_Frame.setLayout(ModifyFrame_Up_Layout)

        ###########################################
        
        self.Modify_Down_Frame = QFrame()
        ModifyFrame_Down_Layout = QGridLayout()

        Label4 = QLabel('Response : ')
        Label4.setFont(QFont('Arial', 12))
        Label4.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label4, 0, 0, 1, 1)

        self.combo4 = QComboBox()
        self.combo4.addItems([' ', 'True', 'False'])
        self.combo4.currentIndexChanged.connect(lambda : self.GetCombo('Response'))
        self.combo4.setFont(QFont('Arial', 12))
        ModifyFrame_Down_Layout.addWidget(self.combo4, 0, 1, 1, 1)

        Label5 = QLabel('Value : ')
        Label5.setFont(QFont('Arial', 12))
        Label5.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label5, 0, 2, 1, 1)

        self.input_line1 = QLineEdit(self.Modify_Down_Frame)
        self.input_line1.setFont(QFont('Arial', 12))
        ModifyFrame_Down_Layout.addWidget(self.input_line1, 0, 3, 1, 1)

        Label6 = QLabel('Name : ')
        Label6.setFont(QFont('Arial', 12))
        Label6.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label6, 0, 4, 1, 1)

        self.input_line2 = QLineEdit(self.Modify_Down_Frame)
        self.input_line2.setFont(QFont('Arial', 12))
        ModifyFrame_Down_Layout.addWidget(self.input_line2, 0, 5, 1, 1)

        Update_BTN = QPushButton(self.Modify_Down_Frame)
        Update_BTN.setText('確認更改')
        Update_BTN.clicked.connect(self.Output_Modity)

        ModifyFrame_Down_Layout.addWidget(Update_BTN, 0, 6, 1, 1)

        self.Modify_Down_Frame.setLayout(ModifyFrame_Down_Layout)

        ###################################################

        ModifyFrame_Layout.addWidget(self.Modify_Up_Frame)
        ModifyFrame_Layout.addWidget(self.Modify_Down_Frame)
        # ModifyFrame_Layout.addWidget(self.Modify_Check_Frame)
        self.setLayout(ModifyFrame_Layout)

    def GetCombo(self, which_combo):
        combo = self.sender()
        text = combo.currentText()
        self.input_save[which_combo] = text
        # num = combo.currentIndex()

    def Output_Modity(self):
        print(f'Type      : {self.input_save["Type"]}')
        print(f'Side      : {self.input_save["Side"]}')
        print(f'Frequency : {self.input_save["Frequency"]}')
        print(f'Response  : {self.input_save["Response"]}')
        print(f'{self.input_save["x coordinate"]}, {self.input_save["y coordinate"]}, {self.input_save["width ratio"]}, {self.input_save["height ratio"]}')
        value = self.input_line1.text()
        name  = self.input_line2.text()
        print(f'The value you input is {value}, and your name is {name}')
        print(f'The file you are modifying is {self.parent.json_path}') # grid_layout.json_path
        print(f'The saving file is {self.new_file}')
        measurementType = None
        ear = None
        conduction = None
        masking = None
        if self.input_save["Type"] == 'Air with masking':
            change_type = 1 # which table
            conduction = "air"
            masking = True
            if self.input_save["Side"] == 'Left':
                ear = 'left'
                measurementType = 'AIR_MASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                measurementType = 'AIR_MASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'Air without masking':
            change_type = 0
            conduction = "air"
            masking = False
            if self.input_save["Side"] == 'Left':
                ear = 'left'
                measurementType = 'AIR_UNMASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                measurementType = 'AIR_UNMASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'Bone with masking':
            change_type = 3
            conduction = "bone"
            masking = True
            if self.input_save["Side"] == 'Left':
                ear = 'left'
                measurementType = 'BONE_UNMASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                measurementType = 'BONE_UNMASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'Bone without masking':
            change_type = 2
            conduction = "bone"
            masking = True
            if self.input_save["Side"] == 'Left':
                ear = 'left'
                measurementType = 'BONE_UNMASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                measurementType = 'BONE_UNMASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'SOUND_FIELD':
            conduction = "air"
            masking = False
            measurementType = 'SOUND_FIELD'
            if self.input_save["Side"] == 'Both':
                ear = 'both'
                change_type = 4
            elif self.input_save["Side"] == 'Left':
                ear = 'left'
                change_type = 9
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                change_type = 10
        elif self.input_save["Type"] == 'AR':
            change_type = 5
            conduction = "air"
            masking = False
            measurementType = 'AR'
            if self.input_save["Side"] == 'Right':
                ear = 'right'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'AL':
            change_type = 6
            conduction = "air"
            masking = False
            measurementType = 'AL'
            if self.input_save["Side"] == 'Left':
                ear = 'left'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'COCHLEAR_IMPLANT':
            conduction = "air"
            masking = False
            measurementType = 'COCHLEAR_IMPLANT'
            if self.input_save["Side"] == 'Both':
                ear = 'both'
                change_type = 7
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                change_type = 11
            elif self.input_save["Side"] == 'Left':
                ear = 'left'
                change_type = 12
        elif self.input_save["Type"] == 'HEARING_AID':
            conduction = "air"
            masking = False
            measurementType = 'HEARING_AID'
            if self.input_save["Side"] == 'Both':
                ear = 'both'
                change_type = 8
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                change_type = 13
            elif self.input_save["Side"] == 'Left':
                ear = 'left'
                change_type = 14
        
        #if no modify and press then return
        if ear == None and conduction == None and masking == None:
            QMessageBox.information(None, 'Empty Input', 'You did not choose or input anything !')
            return
        
        #Write to a new json file
        self.been_modify = True
        df = pd.read_json(self.parent.json_path, dtype={'response': 'bool'})
        if(self.parent.json_path != self.new_file):
            for i in range(df.shape[0]):
                df.loc[i, 'Version'] = "Original"
                df.loc[i, 'Modify_by'] = "Original"
                df.loc[i, 'Modify_Time'] = "Original"
        exist = 0
        for i in range(df.shape[0]):
            if(df.iloc[i]['measurementType'] == measurementType and df.iloc[i]['frequency'] == int(self.input_save["Frequency"])):
                if(value == '' or value == 'None'):
                    df.loc[i, 'threshold'] = None
                    df.loc[i, 'response'] = None
                    self.input_save["Response"] = ' '
                else:
                    df.loc[i, 'threshold'] = int(value)
                    df.loc[i, 'response'] = self.input_save["Response"]
                df.loc[i, 'Version'] = int(self.version)
                df.loc[i, 'Modify_by'] = name
                df.loc[i, 'Modify_Time'] = str(datetime.now())
                exist = 1
        if(exist == 0):
            new_insert = {'type' : [np.nan], 'x coordinate':[self.input_save["x coordinate"]], 'y coordinate':[self.input_save["y coordinate"]], \
            'width ratio':[self.input_save["width ratio"]], 'height ratio':[self.input_save["height ratio"]],\
            'ear':ear, 'conduction':conduction, 'masking':masking, 'measurementType':measurementType, \
            'frequency':[self.input_save["Frequency"]], 'threshold': [int(value)], 'response': [False if self.input_save["Response"] == 'False' else True],\
            'Version': [int(self.version)], 'Modify_by': [name], 'Modify_Time': [str(datetime.now())]}
            new_row_df = pd.DataFrame(new_insert)
            df = pd.concat([df, new_row_df], ignore_index=True)
            # df.loc[len(df)] = new_insert
        
        new_file_content = df.to_json(orient='records', indent=4)
        
        with open(self.new_file, 'w') as file:
            file.write(new_file_content)

        #load new file
        self.parent.dataframe.update_Table(self.new_file, change_type, self.input_save["Side"], self.input_save["Frequency"], self.input_save["Response"], value)
        
    def get_file_version(self):
        self.version = 1
        while True:
            self.new_file = f"{os.path.splitext(self.parent.json_path)[0]}_v{self.version}.json"
            if not os.path.exists(self.new_file):
                break
            self.version += 1

class Menubar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        #set the font size of menubar
        font = QFont()
        font.setPointSize(16)
        self.setFont(font)

        # Add a "File" menu to the menubar
        file_menu = self.addMenu('File')

        next_action = QAction('Next', self)
        next_action.triggered.connect(self.loadNextFile)
        file_menu.addAction(next_action)

        prev_action = QAction('Previous', self)
        prev_action.triggered.connect(self.loadPrevFile)
        file_menu.addAction(prev_action)

    def loadNextFile(self):
        if(self.parent.file_seq == len(self.parent.path_list[1])-1):
            QMessageBox.information(None, 'Reach last file', f'This is the last file in this folder!')
            return
        if(self.parent.grid_layout.modifyframe.been_modify):
            self.parent.path_list[1][self.parent.file_seq] = self.parent.grid_layout.modifyframe.new_file
            self.parent.grid_layout.modifyframe.been_modify = False
        self.parent.file_seq = self.parent.file_seq + 1
        self.parent.grid_layout.label_picture.load_image()
        self.parent.grid_layout.json_path = self.parent.path_list[1][self.parent.file_seq]
        self.parent.grid_layout.dataframe.load_in()
        self.parent.grid_layout.modifyframe.get_file_version()

    def loadPrevFile(self):
        if(self.parent.file_seq == 0):
            QMessageBox.information(None, 'Reach First file', f'This is the first file in this folder!')
            return
        if(self.parent.grid_layout.modifyframe.been_modify):
            self.parent.path_list[1][self.parent.file_seq] = self.parent.grid_layout.modifyframe.new_file
            self.parent.grid_layout.modifyframe.been_modify = False
        self.parent.file_seq = self.parent.file_seq - 1
        self.parent.grid_layout.label_picture.load_image()
        self.parent.grid_layout.dataframe.load_in()
        self.parent.grid_layout.json_path = self.parent.path_list[1][self.parent.file_seq]
        self.parent.grid_layout.modifyframe.get_file_version()

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
    except FileNotFoundError as fnfe:
        print(fnfe)
        input("Press Enter to continue...")

    app = QApplication(sys.argv)
    window = ImageInfoWindow([image_path, json_path])
    window.show()
    # window.resize(1920, 1080) # comments this line when using windows

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
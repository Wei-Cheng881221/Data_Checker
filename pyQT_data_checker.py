from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, \
QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMenuBar, QAction, \
QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QGraphicsScene, QGraphicsView, \
QMessageBox, QAbstractItemView, QScrollArea, QSizePolicy
from PyQt5.QtGui import QFont, QPainter, QBrush, QColor, QPalette
from PyQt5.QtCore import Qt
import sys
import json
import pandas as pd
import argparse
import os 
from datetime import datetime

class ImageInfoWindow(QMainWindow):
    def __init__(self, path_list):
        super().__init__()
        # self.image_path = args.image_path
        # self.json_path = args.json_path
        self.initUI(path_list)

    def initUI(self, path_list):
        self.path_list = path_list

        # Create a grid layout
        self.file_seq = 0
        self.grid_layout = GridLayout(self, path_list)

        # Create a menubar using the Menubar class
        menubar = Menubar(self)
        self.setMenuBar(menubar)

        # Create a central widget and set the grid layout as its layout
        central_widget = QWidget()
        central_widget.setLayout(self.grid_layout)
        # self.setStyleSheet("background-color: #B0E0E6;")

        # Set the central widget of the main window
        self.setCentralWidget(central_widget)

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
        # self.im = QPixmap(image_path)
        # self.scene = QGraphicsScene(self)
        # self.scene.addPixmap(self.im)
        # self.view.setScene(self.scene)

        # Create zoom in and zoom out buttons
        self.zoom_in_button = QPushButton("+", self)
        self.zoom_out_button = QPushButton("-", self)

        # Create a layout for the buttons and the view
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.zoom_in_button)
        layout.addWidget(self.zoom_out_button)

        # Set the layout for the frame
        self.setLayout(layout)

        # Connect the buttons to the zoom functions
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_out_button.clicked.connect(self.zoom_out)

    def load_image(self):
        self.im = QPixmap(self.parent.path_list[0][self.parent.file_seq])
        self.scene = QGraphicsScene(self)
        self.scene.addPixmap(self.im)
        self.view.setScene(self.scene)

    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1 / 1.2, 1 / 1.2)

class DataFrame(QFrame):
    def __init__(self, parent, json_path):
        super().__init__()
        self.parent = parent
        self.json_path = json_path

        self.setStyleSheet("background-color:darkgrey")
        self.DataFrame_Layout = QVBoxLayout(self) #QGridLayout()
        self.tables = [MyTable(self.parent) for i in range(5)]
        self.load_in()
        self.setLayout(self.DataFrame_Layout)


    def load_in(self):
        
        self.readfile(self.parent.path_list[1][self.parent.file_seq])
        self.all_list = [self.data_air_fal] + [self.data_air_tru] + [self.data_bon_fal] + [self.data_bon_tru]
        symbol_list = ['X', 'O', '☐', '△', '>', '<', ']', '[']
        # symbol_list_SF = ['S', 'S', 'S', 'AL', 'AR', 'A', 'C']
        self.freq = ['125', '250', '500', '750', '1000', '1500', '2000', '3000', '4000', '6000', '8000', '12000']
        self.threshold = []
        self.threshold_SF = [['Both S'], ['AL'], ['AR'], ['Both C'], ['Both A'], ['Left S'], ['Right S'], ['Left C'], ['Right C'], ['Left A'], ['Right A']]
        
        
       # Handle normal data input
        set_l = 0
        set_r = 0
        for k in range(len(self.all_list)):
            threshold_tmep_l = [f'Left   {symbol_list[k*2]} ']
            threshold_tmep_r = [f'Right  {symbol_list[k*2+1]} ']
            for i in self.freq:
                for j in self.all_list[k]:
                    if (i == str(j[1]) and str(j[0]) == 'left'):
                        threshold_tmep_l.append(j[2])
                        set_l = 1
                        continue
                    if (i == str(j[1]) and str(j[0]) == 'right'):
                        threshold_tmep_r.append(j[2])
                        set_r = 1
                        continue
                if set_l == 0:
                    threshold_tmep_l.append('')
                if set_r == 0:
                    threshold_tmep_r.append('')
                set_l = 0
                set_r = 0
            self.threshold.append(threshold_tmep_l)
            self.threshold.append(threshold_tmep_r)
        
        
        # Handle SoundField data input
        for i in self.freq:
            SF_set = [0 for i in range(11)]
            for j in self.data_sf:
                if (i == str(j[1]) and str(j[0]) == 'both' and j[4] == 'SOUND_FIELD'):
                    self.threshold_SF[0].append(j[2])
                    SF_set[0] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[4] == 'AL'):
                    self.threshold_SF[1].append(j[2])
                    SF_set[1] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[4] == 'AR'):
                    self.threshold_SF[2].append(j[2])
                    SF_set[2] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'both' and j[4] == 'COCHLEAR_IMPLANT'):
                    self.threshold_SF[3].append(j[2])
                    SF_set[3] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'both' and j[4] == 'HEARING_AID'):
                    self.threshold_SF[4].append(j[2])
                    SF_set[4] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[4] == 'SOUND_FIELD'):
                    self.threshold_SF[5].append(j[2])
                    SF_set[5] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[4] == 'SOUND_FIELD'):
                    self.threshold_SF[6].append(j[2])
                    SF_set[6] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[4] == 'COCHLEAR_IMPLANT'):
                    self.threshold_SF[7].append(j[2])
                    SF_set[7] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[4] == 'COCHLEAR_IMPLANT'):
                    self.threshold_SF[8].append(j[2])
                    SF_set[8] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'left' and j[4] == 'HEARING_AID'):
                    self.threshold_SF[9].append(j[2])
                    SF_set[9] = 1
                    continue
                if (i == str(j[1]) and str(j[0]) == 'right' and j[4] == 'HEARING_AID'):
                    self.threshold_SF[10].append(j[2])
                    SF_set[10] = 1
                    continue
            for i in range(len(SF_set)):
                if SF_set[i] == 0:
                    self.threshold_SF[i].append('')

        self.title = ['Air without masking', 'Air with masking', 'Bone without masking' , 'Bone with masking', \
                'Sound Field']

        # Normal PTA Table
        
        for i in range(5):
            if(i == 4): # SoundField table is bigger
                self.tables[i].update(self.freq, self.threshold_SF, i)
            else:
                self.tables[i].update(self.freq, self.threshold[i*2:i*2+2], i)
            self.tables[i].cellClicked.connect(self.tables[i].handle_cell_clicked)
            if(self.parent.file_seq == 0):
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

        df = pd.read_json(file)

        for i in range(df.shape[0]):
            if((df.iloc[i]['conduction'] == 'air') and (df.iloc[i]['masking'] == True)):
                self.data_air_tru.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5], df.iloc[i][6]]) # ear, freq, threshold, response
            elif(df.iloc[i]['conduction'] == 'air' and df.iloc[i]['masking'] == False):
                if(df.iloc[i]['measurementType'] == 'SOUND_FIELD' or \
                    df.iloc[i]['measurementType'] == 'AL' or \
                    df.iloc[i]['measurementType'] == 'AR' or \
                    df.iloc[i]['measurementType'] == 'COCHLEAR_IMPLANT' or \
                    df.iloc[i]['measurementType'] == 'HEARING_AID'):   # handle the extra cases 'SOUND_FIELD', 'NR_SOUND_FIELD', 'AL', 'AR', 'COCHLEAR_IMPLANT', 'HEARING_AID'
                    self.data_sf.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5], df.iloc[i][6], df.iloc[i]['measurementType']]) # ear, freq, threshold, response, measurementType
                else:
                    self.data_air_fal.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5], df.iloc[i][6]])
            elif(df.iloc[i]['conduction'] == 'bone' and df.iloc[i]['masking'] == True):
                self.data_bon_tru.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5], df.iloc[i][6]])
            elif(df.iloc[i]['conduction'] == 'bone' and df.iloc[i]['masking'] == False):
                self.data_bon_fal.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5], df.iloc[i][6]])

    def update_Table(self, json_path, type, side, freq, response, value):
        self.parent.grid_layout.json_path = json_path
        self.readfile(self.parent.grid_layout.json_path)
        item = QTableWidgetItem(value)
        item.setBackground(QBrush(QColor(255, 0, 0)))
        item.setTextAlignment(Qt.AlignCenter)
        index = self.freq.index(freq)
        if(type >= 4):
            self.tables[type].setItem(type-4, index+1, item)
        else:
            self.tables[type].setItem(0 if side == 'Left' else 1, index+1, item)
        

class MyTable(QTableWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def update(self, freq, threshold, which_table):
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

        # Set row header (threshold)
        self.setVerticalHeaderLabels(['threshold'])
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setFont(font)

        # Set cell values for threshold row
        for j in range(len(threshold)):
            for i in range(len(threshold[0])):
                item = QTableWidgetItem(str(threshold[j][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(j, i, item)
                self.resizeColumnsToContents()

    def handle_cell_clicked(self, row, column):
        # Retrieve the content of the clicked cell
        item = self.item(row, column)
        # content = item.text()
        content = "None" if item.text() == '' else item.text()
        
        if(self.which_table == 4):
            match row:
                case 0 | 5 | 6 : SF_combo = 'SOUND_FIELD'
                case 1 : SF_combo = 'AL'
                case 2 : SF_combo = 'AR'
                case 3 | 7 | 8 : SF_combo = 'COCHLEAR_IMPLANT'
                case 4 | 9 | 10 : SF_combo = 'HEARING_AID'
            self.parent.grid_layout.modifyframe.combo1.setCurrentIndex(self.parent.grid_layout.modifyframe.combo1.findText(SF_combo)) # type
            self.parent.grid_layout.modifyframe.combo2.setCurrentIndex(self.parent.grid_layout.modifyframe.combo2.findText('Both' if row == 0 or row == 3 or row == 4 \
                else ('Left' if row == 1 or row == 5 or row == 7 or row == 9 else'Right'))) # ear
            self.parent.grid_layout.modifyframe.combo3.setCurrentIndex(self.parent.grid_layout.modifyframe.combo3.findText(self.parent.grid_layout.dataframe.freq[column-1])) # frequency
            found = False
            for ear, freq, threshold, response, measurementtype in self.parent.grid_layout.dataframe.data_sf:
                if self.parent.grid_layout.dataframe.freq[column-1] == str(freq):
                    if (row == 0 and ear == 'both' and measurementtype == 'SOUND_FIELD') or \
                    (row == 1 and ear == 'left' and measurementtype == 'AL') or (row == 1 and ear == 'right' and measurementtype == 'AR')or \
                    (row == 1 and ear == 'both' and measurementtype == 'COCHLEAR_IMPLANT') or (row == 1 and ear == 'both' and measurementtype == 'HEARING_AID')or \
                    (row == 1 and ear == 'left' and measurementtype == 'SOUND_FIELD') or (row == 1 and ear == 'right' and measurementtype == 'SOUND_FIELD')or \
                    (row == 1 and ear == 'left' and measurementtype == 'COCHLEAR_IMPLANT') or (row == 1 and ear == 'right' and measurementtype == 'COCHLEAR_IMPLANT')or \
                    (row == 1 and ear == 'left' and measurementtype == 'HEARING_AID') or (row == 1 and ear == 'right' and measurementtype == 'HEARING_AID'):
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(self.parent.grid_layout.modifyframe.combo4.findText(str(response))) # response
                        found = True
            if found == False:
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(0) # response empty blank
            self.parent.grid_layout.modifyframe.input_line1.setText(content)
        else:
            self.parent.grid_layout.modifyframe.combo1.setCurrentIndex(self.parent.grid_layout.modifyframe.combo1.findText(self.table)) # type
            self.parent.grid_layout.modifyframe.combo2.setCurrentIndex(self.parent.grid_layout.modifyframe.combo2.findText('Left' if row == 0 else 'Right')) # ear
            self.parent.grid_layout.modifyframe.combo3.setCurrentIndex(self.parent.grid_layout.modifyframe.combo3.findText(self.parent.grid_layout.dataframe.freq[column-1])) # frequency
            found = False
            for ear, freq, threshold, response in self.parent.grid_layout.dataframe.all_list[self.which_table]:
                if self.parent.grid_layout.dataframe.freq[column-1] == str(freq):
                    if (row == 0 and ear == 'left') or(row == 1 and ear == 'right'):
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(self.parent.grid_layout.modifyframe.combo4.findText(str(response))) # response
                        found = True
            if found == False:
                        self.parent.grid_layout.modifyframe.combo4.setCurrentIndex(0) # response empty blank
        self.parent.grid_layout.modifyframe.input_line1.setText(content)

class ModifyFrame(QFrame):
    def __init__(self, parent, json_path):
        super().__init__()
        self.parent = parent

        self.json_path = json_path
        self.new_file = "NEW FILE"
        self.get_file_version()
        
        self.input_save = {"Type": "None", "Side": "None", "Frequency" : "None", "Response": "None"}

        self.setStyleSheet("background-color:lightgrey")
        ModifyFrame_Layout = QVBoxLayout()

        self.Modify_Up_Frame = QFrame()
        ModifyFrame_Up_Layout = QGridLayout()

        Label1 = QLabel('Type : ')
        Label1.setFont(QFont('Arial', 12))
        Label1.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label1, 0, 0, 1, 1)
        self.combo1 = QComboBox()
        self.combo1.addItems([' ', 'Air with masking', 'Air without masking', 'Bone with masking', 'Bone without masking', \
            'SOUND_FIELD', 'AL', 'AR', 'COCHLEAR_IMPLANT', 'HEARING_AID'])
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
        # This part is not using right now
        self.length = pd.read_json(self.json_path).shape[0]

        self.Modify_Check_Frame = QFrame()
        ModifyFrame_Check_Layout = QGridLayout()

        Label_detect_amount = QLabel(f"Detected amount of symblos : ")
        Label_detect_amount.setFont(QFont('Arial', 12))
        ModifyFrame_Check_Layout.addWidget(Label_detect_amount, 0, 1, 1, 1)  # y, x, height, width

        self.input_line3 = QLineEdit(self.Modify_Check_Frame)
        self.input_line3.setFont(QFont('Arial', 12))
        self.input_line3.setText(f'{self.length}')
        ModifyFrame_Check_Layout.addWidget(self.input_line3, 0, 2, 1, 1)

        Label_real_amoount = QLabel("Please input the real amount base on the picture left : ")
        Label_real_amoount.setFont(QFont('Arial', 12))
        ModifyFrame_Check_Layout.addWidget(Label_real_amoount, 0, 3, 1, 1)

        self.input_line4 = QLineEdit(self.Modify_Check_Frame)
        self.input_line4.setFont(QFont('Arial', 12))
        ModifyFrame_Check_Layout.addWidget(self.input_line4, 0, 4, 1, 1)

        Submit_BTN = QPushButton(self.Modify_Down_Frame)
        Submit_BTN.setText('新增統計資料')

        ModifyFrame_Check_Layout.addWidget(Submit_BTN, 0, 6, 1, 1)

        self.Modify_Check_Frame.setLayout(ModifyFrame_Check_Layout)

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
        value = self.input_line1.text()
        name  = self.input_line2.text()
        print(f'The value you input is {value}, and your name is {name}')
        print(f'The file you are modifying is {self.parent.json_path}') # grid_layout.json_path
        print(f'The saving file is {self.new_file}')
        # [' ', 'Air with masking', 'Air without masking', 'Bone with masking', 'Bone without masking', \
        #     'SOUND_FIELD', 'NR_SOUND_FIELD', 'AL', 'AR', 'COCHLEAR_IMPLANT', 'HEARING_AID']
        measurementType = None
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
        elif self.input_save["Type"] == 'AL':
            change_type = 5
            conduction = "air"
            masking = False
            measurementType = 'AL'
            if self.input_save["Side"] == 'Left':
                ear = 'left'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'AR':
            change_type = 6
            conduction = "air"
            masking = False
            measurementType = 'AR'
            if self.input_save["Side"] == 'Right':
                ear = 'right'
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
            elif self.input_save["Side"] == 'Left':
                ear = 'left'
                change_type = 11
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                change_type = 12
        elif self.input_save["Type"] == 'HEARING_AID':
            conduction = "air"
            masking = False
            measurementType = 'HEARING_AID'
            if self.input_save["Side"] == 'Both':
                ear = 'both'
                change_type = 8
            elif self.input_save["Side"] == 'Left':
                ear = 'left'
                change_type = 13
            elif self.input_save["Side"] == 'Right':
                ear = 'right'
                change_type = 14
        
        #Write to a new json file
        df = pd.read_json(self.parent.json_path)
        if(self.parent.json_path != self.new_file):
            for i in range(df.shape[0]):
                df.loc[i, 'Version'] = "Original"
                df.loc[i, 'Modify_by'] = "Original"
                df.loc[i, 'Modify_Time'] = "Original"
        exist = 0
        for i in range(df.shape[0]):
            if(df.iloc[i]['measurementType'] == measurementType and df.iloc[i]['frequency'] == int(self.input_save["Frequency"])):
                df.loc[i, 'threshold'] = int(value)
                df.loc[i, 'response'] = self.input_save["Response"]
                df.loc[i, 'Version'] = int(self.version)
                df.loc[i, 'Modify_by'] = name
                df.loc[i, 'Modify_Time'] = str(datetime.now())
                exist = 1
        if(exist == 0):
            new_insert = [ear, conduction, masking, measurementType, \
            self.input_save["Frequency"], int(value), self.input_save["Response"],\
            int(self.version), name, str(datetime.now())]
            df.loc[len(df)] = new_insert

        new_file_content = df.to_json(orient='records', indent=4)
        
        with open(self.new_file, 'w') as file:
            file.write(new_file_content)
        #load new file
        self.parent.dataframe.update_Table(self.new_file, change_type, self.input_save["Side"], self.input_save["Frequency"], self.input_save["Response"], value)
        
    def get_file_version(self):
        print(self.parent.json_path)
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

    def loadNextFile(self):
        self.parent.file_seq = self.parent.file_seq + 1
        self.parent.grid_layout.label_picture.load_image()
        self.parent.grid_layout.dataframe.load_in()
        self.parent.grid_layout.json_path = self.parent.path_list[1][self.parent.file_seq]
        self.parent.grid_layout.modifyframe.get_file_version()
        
def check_path_valid(input_path):
    file_names = []
    if os.path.isfile(input_path):
        file_names.append(input_path)
    elif os.path.exists(input_path):
        for file_name in os.listdir(input_path):
            file_names.append(os.path.join(input_path, file_name))
    else:
        raise FileNotFoundError(f"File or folder not found: {input_path}  !\nThe program might crash later !")
    
    return file_names
        

def main():
    parser = argparse.ArgumentParser(description='The following is the arguments of this application')
    parser.add_argument('--image_path', help = "The input path to one image or a folder path of images", default = './example_image/example_PTA_2.jpg')
    parser.add_argument('--json_path', help = "The input path to one json or a folder path of json", default = './example_json/example_PTA_2.json')
    args = parser.parse_args()
    
    try:
        image_path = check_path_valid(args.image_path)
        json_path = check_path_valid(args.json_path)
    except FileNotFoundError as e:
        print(e)
        input("Press Enter to continue...")
    
    # print(sys.argv) # ['pyQT_data_checker.py']
    app = QApplication(sys.argv)
    window = ImageInfoWindow([image_path, json_path])
    window.show()
    # window.resize(1920, 1080) # comments this line when using windows

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, \
QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMenuBar, QAction, \
QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QGraphicsScene, QGraphicsView, \
QMessageBox
from PyQt5.QtGui import QFont, QPainter, QMouseEvent, QPen, QBrush, QColor, QPolygonF, QWheelEvent
from PyQt5.QtCore import Qt, QPoint, QPointF, QSize, QRect
import sys
import json
import pandas as pd
import argparse
import os 
from datetime import datetime

class ImageInfoWindow(QMainWindow):
    def __init__(self, args):
        super().__init__()
        # self.image_path = args.image_path
        # self.json_path = args.json_path
        self.initUI(args)
        
    def initUI(self, args):
        # self.status = self.statusBar()
        # self.status.showMessage("狀態列")

        # Create a grid layout
        self.grid_layout = GridLayout(args)

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
    def __init__(self, args):
        super().__init__()
        self.setSpacing(10)
        # file name : example_PTA_2
        # Add a QLabel with the image to the left side of the grid
        self.label_picture = PictureFrame(args.image_path)
        
        self.addWidget(self.label_picture, 0, 0, 4, 1)   # y, x, height, width
        
        self.dataframe = DataFrame(self)
        self.addWidget(self.dataframe, 0, 1, 3, 2)

        self.modifyframe = ModifyFrame(self, args.json_path)
        self.addWidget(self.modifyframe, 3, 1, 1, 2)

class PictureFrame(QFrame):
    def __init__(self, image_path):
        super().__init__()
        
        self.setFixedSize(800, 960)
        self.drag_pos = None
        self.zoom_factor = 1.0

        self.view = QGraphicsView(self)
        self.view.setFixedSize(800, 960)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        print(image_path)
        self.im = QPixmap("./example/example_PTA_2.jpg")
        self.scene = QGraphicsScene(self)
        self.scene.addPixmap(self.im)
        self.view.setScene(self.scene)

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
    
    def zoom_in(self):
        self.view.scale(1.2, 1.2)

    def zoom_out(self):
        self.view.scale(1 / 1.2, 1 / 1.2)

class DataFrame(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setStyleSheet("background-color:darkgrey")
        
        self.DataFrame_Layout = QVBoxLayout(self) #QGridLayout()

                                # L R
        self.data_air_tru = []  # ■ ▲
        self.data_air_fal = []  # X O
        self.data_bon_tru = []  # ] [
        self.data_bon_fal = []  # > <
        self.readfile('./example/example_PTA_2.json')
        all_list = [self.data_air_tru] + [self.data_air_fal] + [self.data_bon_tru] + [self.data_bon_fal]
        symbol_list = ['■', '▲', 'X', 'O', ']', '[', '>', '<']

        self.freq = ['125', '250', '500', '1000', '2000', '3000', '4000', '6000', '8000']
        threshold = []
        set_l = 0
        set_r = 0
        for k in range(len(all_list)):
            threshold_tmep_l = [f'Left    {symbol_list[k*2]} ']
            threshold_tmep_r = [f'Right  {symbol_list[k*2+1]} ']
            for i in self.freq:
                for j in all_list[k]:
                    if (i == str(j[1]) and str(j[0]) == 'left'):
                        threshold_tmep_l.append(j[2])
                        set_l = 1
                        break
                    if (i == str(j[1]) and str(j[0]) == 'right'):
                        threshold_tmep_r.append(j[2])
                        set_r = 1
                        break
                if set_l == 0:
                    threshold_tmep_l.append('')
                if set_r == 0:
                    threshold_tmep_r.append('')
                set_l = 0
                set_r = 0
            threshold.append(threshold_tmep_l)
            threshold.append(threshold_tmep_r)

        title = ['Air with masking', 'Air without masking', 'Bone with masking', 'Bone without masking']

        for i in range(4):
            title_i = QLabel(title[i])
            title_i.setFont(QFont('Arial', 14, QFont.Bold))
            table = MyTable(self.parent, self.freq, threshold[i*2:i*2+2], i)
            table.cellClicked.connect(table.handle_cell_clicked)

            self.DataFrame_Layout.addWidget(title_i)
            self.DataFrame_Layout.addWidget(table)
        self.setLayout(self.DataFrame_Layout)

    def readfile(self, file):
        df = pd.read_json(file)

        # print(df)
        # print(df.iloc[0])   # first row
        for i in range(df.shape[0]):
            if((df.iloc[i]['conduction'] == 'air') and (df.iloc[i]['masking'] == True)):
                self.data_air_tru.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5]])
            elif(df.iloc[i]['conduction'] == 'air' and df.iloc[i]['masking'] == False):
                self.data_air_fal.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5]])
            elif(df.iloc[i]['conduction'] == 'bone' and df.iloc[i]['masking'] == True):
                self.data_bon_tru.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5]])
            elif(df.iloc[i]['conduction'] == 'bone' and df.iloc[i]['masking'] == False):
                self.data_bon_fal.append([df.iloc[i][0], df.iloc[i][4], df.iloc[i][5]])
        
class MyTable(QTableWidget):
    def __init__(self, parent, freq, threshold, which_table):
        super().__init__()
        self.parent = parent

        match which_table:
            case 0:
                self.table = 'Air with masking'
            case 1:
                self.table = 'Air without masking'
            case 2:
                self.table = 'Bone with masking'
            case 3:
                self.table = 'Bone without masking'

        font = QFont('Arial', 12, QFont.Bold)
        self.setFont(font)

        # Set number of rows and columns
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

        #print(threshold)
        # Set cell values for threshold row
        for j in range(len(threshold)):
            for i in range(len(threshold[0])):
                item = QTableWidgetItem(str(threshold[j][i]))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(j, i, item)

    def handle_cell_clicked(self, row, column):
        # Retrieve the content of the clicked cell
        item = self.item(row, column)
        # content = item.text()
        content = "None" if item.text() == '' else item.text()
            
        # Print the clicked cell's information
        # print(f"This table is {self.table}")
        # print("Clicked Cell - Row:", row, "Column:", column)
        # print("Content:", content)
        
        self.parent.modifyframe.combo1.setCurrentIndex(self.parent.modifyframe.combo1.findText(self.table)) # type
        self.parent.modifyframe.combo2.setCurrentIndex(self.parent.modifyframe.combo2.findText('Left' if row == 0 else 'Right')) # ear
        self.parent.modifyframe.combo3.setCurrentIndex(self.parent.modifyframe.combo3.findText(self.parent.dataframe.freq[column-1])) # frequency
        self.parent.modifyframe.input_line1.setText(content)

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
        Label1.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label1, 0, 0, 1, 1)
        self.combo1 = QComboBox()
        self.combo1.addItems([' ', 'Air with masking', 'Air without masking', 'Bone with masking', 'Bone without masking', \
            'SOUND_FIELD', 'NR_SOUND_FIELD', 'AL', 'AR', 'COCHLEAR_IMPLANT', 'HEARING_AID'])
        self.combo1.currentIndexChanged.connect(lambda : self.GetCombo('Type'))
        ModifyFrame_Up_Layout.addWidget(self.combo1, 0, 1, 1, 3)

        Label2 = QLabel('Side : ')
        Label2.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label2, 0, 4, 1, 1)
        self.combo2 = QComboBox()
        self.combo2.addItems([' ', 'Left','Right', 'Both'])
        self.combo2.currentIndexChanged.connect(lambda : self.GetCombo('Side'))
        ModifyFrame_Up_Layout.addWidget(self.combo2, 0, 5, 1, 2)

        Label3 = QLabel('Frequency : ')
        Label3.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label3, 0, 7, 1, 1)
        self.combo3 = QComboBox()
        self.combo3.addItems([' ', '125', '250', '500', '1000', '2000', '3000', '4000', '6000', '8000'])
        self.combo3.currentIndexChanged.connect(lambda : self.GetCombo('Frequency'))
        ModifyFrame_Up_Layout.addWidget(self.combo3, 0, 8, 1, 2)

        self.Modify_Up_Frame.setLayout(ModifyFrame_Up_Layout)

        ###########################################
        
        self.Modify_Down_Frame = QFrame()
        ModifyFrame_Down_Layout = QGridLayout()

        Label4 = QLabel('Response : ')
        Label4.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label4, 0, 0, 1, 1)

        combo4 = QComboBox()
        combo4.addItems([' ', 'True', 'False'])
        combo4.currentIndexChanged.connect(lambda : self.GetCombo('Response'))
        # ModifyFrame_Up_Layout.addWidget(combo4, 0, 8, 1, 2)
        # self.input_line1 = QLineEdit(self.Modify_Down_Frame)
        ModifyFrame_Down_Layout.addWidget(combo4, 0, 1, 1, 1)

        Label5 = QLabel('Value : ')
        Label5.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label5, 0, 2, 1, 1)

        self.input_line1 = QLineEdit(self.Modify_Down_Frame)
        ModifyFrame_Down_Layout.addWidget(self.input_line1, 0, 3, 1, 1)

        Label6 = QLabel('Name : ')
        Label6.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label6, 0, 4, 1, 1)

        self.input_line2 = QLineEdit(self.Modify_Down_Frame)
        ModifyFrame_Down_Layout.addWidget(self.input_line2, 0, 5, 1, 1)

        Submit_BTN = QPushButton(self.Modify_Down_Frame)
        Submit_BTN.setText('確認更改')
        #Submit_BTN.clicked.connect(lambda: self.Get_Certain_Input(self.input_line1))
        Submit_BTN.clicked.connect(self.Output_Modity)

        ModifyFrame_Down_Layout.addWidget(Submit_BTN, 0, 6, 1, 1)

        self.Modify_Down_Frame.setLayout(ModifyFrame_Down_Layout)

        ###################################################
        
        ModifyFrame_Layout.addWidget(self.Modify_Up_Frame)
        ModifyFrame_Layout.addWidget(self.Modify_Down_Frame)
        self.setLayout(ModifyFrame_Layout)

    def GetCombo(self, which_combo):
        combo = self.sender()
        text = combo.currentText()
        # print(f'The {which_combo} you choose is {text}')
        self.input_save[which_combo] = text
        num = combo.currentIndex()

    def Get_Certain_Input(self, input_line):
        text = input_line.text()
        print(text)

    def Output_Modity(self):

        print(f'Type      : {self.input_save["Type"]}')
        print(f'Side      : {self.input_save["Side"]}')
        print(f'Frequency : {self.input_save["Frequency"]}')
        print(f'Response  : {self.input_save["Response"]}')
        value = self.input_line1.text()
        name  = self.input_line2.text()
        print(f'The value you input is {value}, and your name is {name}')
        print(f'The file you are modifying is {self.json_path}')
        print(f'The saving file is {self.new_file}')
        # [' ', 'Air with masking', 'Air without masking', 'Bone with masking', 'Bone without masking', \
        #     'SOUND_FIELD', 'NR_SOUND_FIELD', 'AL', 'AR', 'COCHLEAR_IMPLANT', 'HEARING_AID']
        if self.input_save["Type"] == 'Air with masking':
            if self.input_save["Side"] == 'Left':
                measurementType = 'AIR_MASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                measurementType = 'AIR_MASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'Air without masking':
            if self.input_save["Side"] == 'Left':
                measurementType = 'AIR_UNMASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                measurementType = 'AIR_UNMASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'Bone with masking':
            if self.input_save["Side"] == 'Left':
                measurementType = 'BONE_UNMASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                measurementType = 'BONE_UNMASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return
        elif self.input_save["Type"] == 'Bone without masking':
            if self.input_save["Side"] == 'Left':
                measurementType = 'BONE_UNMASKED_LEFT'
            elif self.input_save["Side"] == 'Right':
                measurementType = 'BONE_UNMASKED_RIGHT'
            else:
                QMessageBox.warning(None, 'Wrong Type', f'You can not choose {self.input_save["Side"]} for {self.input_save["Type"]}!')
                return

        #Write to a new json file
        df = pd.read_json(self.json_path)
        
        df['Version'] = "Original"
        df['Modify_by'] = "Original"
        df['Modify_Time'] = "Original"
        for i in range(df.shape[0]):
            if(df.iloc[i]['measurementType'] == measurementType and df.iloc[i]['frequency'] == int(self.input_save["Frequency"])):
                df.loc[i, 'threshold'] = int(value)
                df.loc[i, 'Version'] = int(self.version)
                df.loc[i, 'Modify_by'] = name
                df.loc[i, 'Modify_Time'] = str(datetime.now())

        new_file_content = df.to_json(orient='records', indent=4)
        
        with open(self.new_file, 'w') as file:
            file.write(new_file_content)

    def get_file_version(self):
        self.version = 1
        while True:
            self.new_file = f"{os.path.splitext(self.json_path)[0]}_v{self.version}.json"
            if not os.path.exists(self.new_file):
                break
            self.version += 1

class Menubar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)

        #set the font size of menubar
        font = QFont()
        font.setPointSize(16)
        self.setFont(font)

        # Add a "File" menu to the menubar
        file_menu = self.addMenu('File')
        next_menu = self.addMenu('Next')

        # Add a "New" action to the "File" menu
        new_action = QAction('New', self)
        file_menu.addAction(new_action)

        # Add a "Open" action to the "File" menu
        open_action = QAction('Open', self)
        file_menu.addAction(open_action)

        # Add a "Save" action to the "File" menu
        save_action = QAction('Save', self)
        file_menu.addAction(save_action)

def check_path_valid(input_path):
    file_names = []
    if os.path.isfile(input_path):
        file_names.append(os.path.basename(input_path))
    elif os.path.exists(input_path):
        # print(f"Valid path: {input_path}")
        # Process the valid path
        for file_name in os.listdir(input_path):
            file_names.append(file_name)
    else:
        raise FileNotFoundError(f"File or folder not found: {input_path}  !\nThe program might crash later !")
        # print(f"Cannot find path: {input_path}")
    # print(file_names)

def main():
    parser = argparse.ArgumentParser(description='The following is the arguments of this application')
    parser.add_argument('--image_path', help = "The input path to one image or a folder path of images", default = './example/example_PTA_2.jpg')
    parser.add_argument('--json_path', help = "The input path to one json or a folder path of json", default = './example/example_PTA_2.json')
    args = parser.parse_args()
    
    try:
        check_path_valid(args.image_path)
        check_path_valid(args.json_path)
    except FileNotFoundError as e:
        print(e)
        input("Press Enter to continue...")
    
    # print(sys.argv) # ['pyQT_data_checker.py']
    app = QApplication(sys.argv)
    window = ImageInfoWindow(args)
    window.show()
    window.resize(1920, 1080)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
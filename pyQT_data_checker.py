from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, \
QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QMenuBar, QAction, \
QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QGraphicsScene, QGraphicsView
from PyQt5.QtGui import QFont, QPainter, QMouseEvent, QPen, QBrush, QColor, QPolygonF, QWheelEvent
from PyQt5.QtCore import Qt, QPoint, QPointF, QSize, QRect
import sys
import json
import pandas as pd
import argparse
import os 

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
        
        self.dataframe = DataFrame(args.json_path)
        self.addWidget(self.dataframe, 0, 1, 3, 2)

        self.modifyframe = ModifyFrame()
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
    def __init__(self, json_path):
        super().__init__()

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

        freq = ['125', '250', '500', '1000', '2000', '3000', '4000', '6000', '8000']
        threshold = []
        set_l = 0
        set_r = 0
        for k in range(len(all_list)):
            threshold_tmep_l = [f'Left    {symbol_list[k*2]} ']
            threshold_tmep_r = [f'Right  {symbol_list[k*2+1]} ']
            for i in freq:
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
            table = MyTable(freq, threshold[i*2:i*2+2])
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
    def __init__(self, freq, threshold):
        super().__init__()
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
        content = "Empty" if item.text() == '' else item.text()
            
        # Print the clicked cell's information
        print("Clicked Cell - Row:", row, "Column:", column)
        print("Content:", content)
    
class ModifyFrame(QFrame):
    def __init__(self):
        super().__init__()

        self.input_save = {"Type": "None", "Side": "None", "Frequency" : "None"}

        self.setStyleSheet("background-color:lightgrey")
        ModifyFrame_Layout = QVBoxLayout()

        self.Modify_Up_Frame = QFrame()
        ModifyFrame_Up_Layout = QGridLayout()

        Label1 = QLabel('Type : ')
        Label1.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label1, 0, 0, 1, 1)
        combo1 = QComboBox()
        combo1.addItems([' ', 'Air with masking', 'Air without masking', 'Bone with masking', 'Bone without masking'])
        combo1.currentIndexChanged.connect(lambda : self.GetCombo('Type'))
        ModifyFrame_Up_Layout.addWidget(combo1, 0, 1, 1, 3)

        Label2 = QLabel('Side : ')
        Label2.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label2, 0, 4, 1, 1)
        combo2 = QComboBox()
        combo2.addItems([' ', 'Left','Right'])
        combo2.currentIndexChanged.connect(lambda : self.GetCombo('Side'))
        ModifyFrame_Up_Layout.addWidget(combo2, 0, 5, 1, 2)

        Label3 = QLabel('Frequency : ')
        Label3.setAlignment(Qt.AlignCenter)
        ModifyFrame_Up_Layout.addWidget(Label3, 0, 7, 1, 1)
        combo3 = QComboBox()
        combo3.addItems([' ', '125', '250', '500', '1000', '2000', '3000', '4000', '6000', '8000'])
        combo2.currentIndexChanged.connect(lambda : self.GetCombo('Frequency'))
        ModifyFrame_Up_Layout.addWidget(combo3, 0, 8, 1, 2)

        self.Modify_Up_Frame.setLayout(ModifyFrame_Up_Layout)

        ###########################################
        
        self.Modify_Down_Frame = QFrame()
        ModifyFrame_Down_Layout = QGridLayout()

        Label4 = QLabel('Value : ')
        Label4.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label4, 0, 0, 1, 1)

        self.input_line1 = QLineEdit(self.Modify_Down_Frame)
        ModifyFrame_Down_Layout.addWidget(self.input_line1, 0, 1, 1, 1)

        Label5 = QLabel('Name : ')
        Label5.setAlignment(Qt.AlignCenter)
        ModifyFrame_Down_Layout.addWidget(Label5, 0, 2, 1, 1)

        self.input_line2 = QLineEdit(self.Modify_Down_Frame)
        ModifyFrame_Down_Layout.addWidget(self.input_line2, 0, 3, 1, 1)

        Submit_BTN = QPushButton(self.Modify_Down_Frame)
        Submit_BTN.setText('確認更改')
        #Submit_BTN.clicked.connect(lambda: self.Get_Certain_Input(self.input_line1))
        Submit_BTN.clicked.connect(self.Get_All_Input)

        ModifyFrame_Down_Layout.addWidget(Submit_BTN, 0, 5, 1, 1)

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

    def Get_All_Input(self):
        value = self.input_line1.text()
        name  = self.input_line2.text()
        # print(self.input_save)
        print(f'Type      : {self.input_save["Type"]}')
        print(f'Side      : {self.input_save["Side"]}')
        print(f'Frequency : {self.input_save["Frequency"]}')
        print(f'The value you input is {value}, and your name is {name}')

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
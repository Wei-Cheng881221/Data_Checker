import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem,\
QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QMessageBox, QComboBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter, QFont
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF
import json
import math
import os

class DraggableSymbol(QGraphicsTextItem):
    def __init__(self, parent, symbol, s_type, x, y, size, pen):
        self.parent = parent
        self.position = symbol.find('↓')
        if(self.position != -1):
            self.response = False
        else:
            self.response = True

        symbol = symbol.replace('↓', '')
        super().__init__(symbol, None)
        self.s_type = s_type
        self.symbol = symbol

        self.setDefaultTextColor(pen.color())

        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

        
        self.text_width = self.boundingRect().width()
        self.text_height = self.boundingRect().height()

        if(not self.response):
            if(self.position == 0):
                self.setPlainText('↓'+self.symbol)
            else:
                self.setPlainText(self.symbol+'↓')

        left_shift_width = self.boundingRect().width() - self.text_width

        if(self.symbol == 'O' or self.symbol == 'X' or self.symbol == '△' or self.symbol == '☐' or \
        self.symbol == 'S' or self.symbol == 'A' or self.symbol == 'C' or self.symbol == 'AR' or self.symbol == 'AL'):
            if (not self.response) and (self.position == 0):
                self.setPos(x - self.text_width / 2 - left_shift_width, y - self.text_height / 2)
            else:
                self.setPos(x - self.text_width / 2, y - self.text_height / 2)
        elif(self.symbol == '<' or self.symbol == '['):
            if (not self.response) and (self.position == 0):
                self.setPos(x - self.text_width / 2 - 12 - left_shift_width, y - self.text_height / 2)
            else:
                self.setPos(x - self.text_width / 2 - 12, y - self.text_height / 2)
        elif(self.symbol == '>' or self.symbol == ']'):
            self.setPos(x - self.text_width / 2 + 12, y - self.text_height / 2)

        self.initial_pos = [x, y]
        self.change_pos = [0, 0]
        self.setFlag(QGraphicsTextItem.ItemIsMovable)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setFlag(QGraphicsTextItem.ItemIsMovable, True)
        elif event.button() == Qt.RightButton:
            self.setFlag(QGraphicsTextItem.ItemIsMovable, False)
            message_box = QMessageBox()
            message_box.setWindowTitle("Delete")
            message_box.setText(f'Are you sure you want to delete this {self.toPlainText()} symbol?')
            message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            # Connect the "OK" button to a function
            ok_button = message_box.button(QMessageBox.Ok)
            ok_button.clicked.connect(self.ok_button_clicked)

            result = message_box.exec_()
        else:
            self.setFlag(QGraphicsTextItem.ItemIsMovable, False)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if((round(event.scenePos().x() / 40) * 40 >= 0 and round(event.scenePos().x() / 40) * 40 <= 400) and \
        round(event.scenePos().y() / 20) * 20 >= 0 and round(event.scenePos().y() / 20) * 20 <= 520):
            if(self.symbol == 'O' or self.symbol == 'X' or self.symbol == '△' or self.symbol == '☐' \
            or self.symbol == 'S' or self.symbol == 'A' or self.symbol == 'C' or self.symbol == 'AR' or self.symbol == 'AL'):
                if (not self.response) and (self.position == 0):
                    self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
                else:
                    self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
            elif(self.symbol == '<' or self.symbol == '['):
                if (not self.response) and (self.position == 0):
                    self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2 - 12, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
                else:
                    self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2 - 12, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
            elif(self.symbol == '>' or self.symbol == ']'):
                self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2 + 12, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
        

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # print(self.pos().x() + self.text_width / 2, self.initial_pos[0])
            if((self.symbol == 'O' or self.symbol == 'X' or self.symbol == '△' or self.symbol == '☐' \
            or self.symbol == 'S' or self.symbol == 'A' or self.symbol == 'C' or self.symbol == 'AR' or self.symbol == 'AL') and \
            (int(self.pos().x() + self.text_width / 2) != int(self.initial_pos[0]) or self.pos().y() + self.text_height / 2 != self.initial_pos[1])):
                self.change_pos = [self.change_pos[0]+(self.pos().x() + self.text_width / 2 - self.initial_pos[0])/40, self.change_pos[1]+(self.pos().y() + self.text_height / 2 - self.initial_pos[1])/20]
                self.initial_pos = [self.pos().x() + self.text_width / 2, self.pos().y() + self.text_height / 2]
            elif(self.symbol == '<' or self.symbol == '[' or self.symbol == '↓<' or self.symbol == '↓['):
                self.change_pos = [self.change_pos[0]+(self.pos().x() + self.text_width / 2 + 12 - self.initial_pos[0])/40, self.change_pos[1]+(self.pos().y() + self.text_height / 2 - self.initial_pos[1])/20]
                self.initial_pos = [self.pos().x() + self.text_width / 2 + 12, self.pos().y() + self.text_height / 2]
            elif(self.symbol == '>' or self.symbol == ']' or self.symbol == '>↓' or self.symbol == ']↓'):
                self.change_pos = [self.change_pos[0]+(self.pos().x() + self.text_width / 2 - 12 - self.initial_pos[0])/40, self.change_pos[1]+(self.pos().y() + self.text_height / 2 - self.initial_pos[1])/20]
                self.initial_pos = [self.pos().x() + self.text_width / 2 - 12, self.pos().y() + self.text_height / 2]

    def ok_button_clicked(self):
        # Your custom action when the "OK" button is clicked
        self.parent.scene.removeItem(self)
        for symbol in self.parent.all_symbol_list[self.s_type]:
            if(symbol[0] == self):
                self.parent.all_symbol_list[self.s_type].remove(symbol)
        
class Add_Symbol(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()  # Create a horizontal layout
        self.label1 = QLabel('Ear : ')
        self.combo1 = QComboBox()  # Create a combo box
        self.combo1.addItems([' ', 'O', 'X', '△', '☐', \
            '<', '>', '[', ']', 'S', 'A', 'C', 'AL', 'AR'])
        
        self.label2 = QLabel('Side(SF) : ')
        self.combo2 = QComboBox()  # Create a combo box
        self.combo2.addItems([' ', 'right', 'left', 'both'])

        self.label3 = QLabel('Response : ')
        self.combo3 = QComboBox()  # Create a combo box
        self.combo3.addItems(['True', 'False'])
        
        button = QPushButton("Add symbol on Audiogram")  # Create a button
        button.clicked.connect(self.AddSymbolButtonClicked)

        layout.addWidget(self.label1)  # Add the combo box to the left
        layout.addWidget(self.combo1)  # Add the combo box to the left
        layout.addWidget(self.label2)  # Add the combo box to the middle
        layout.addWidget(self.combo2)  # Add the combo box to the middle
        layout.addWidget(self.label3)  # Add the combo box to the right
        layout.addWidget(self.combo3)  # Add the combo box to the right
        layout.addWidget(button)  # Add the button to the right

        self.setLayout(layout)
        
    def AddSymbolButtonClicked(self):
        if self.combo1.currentIndex() == 0:
            return
        if ((self.combo2.currentIndex() == 3) and (self.combo1.currentIndex() < 9)) or \
            ((self.combo2.currentIndex() == 1) and (self.combo1.currentIndex()%2 == 0) and (self.combo1.currentIndex() < 9)) or \
            ((self.combo2.currentIndex() == 2) and (self.combo1.currentIndex()%2 == 1) and (self.combo1.currentIndex() < 9)):
            QMessageBox.information(None, 'Wrong Format', \
            f'The {self.combo1.currentText()} symbol can\'t be use with ear type: {self.combo2.currentText()}.\nFor Usage Rule please access the How To Use page.')
            return
        
        red_pen = QPen(QColor("red"), 1, Qt.SolidLine)
        blue_pen = QPen(QColor("blue"), 1, Qt.SolidLine)
        black_pen = QPen(QColor("black"), 1, Qt.SolidLine)
        match self.combo1.currentIndex()-1:
            case 0 | 2 | 4 | 6 | 12:
                pen = red_pen
            case 1 | 3 | 5 | 7 | 11:
                pen = blue_pen
            case 8 | 9 | 10:
                pen = black_pen
        
        match self.combo1.currentIndex()-1:
            case 0 | 1 | 2 | 3 | 8 | 9 | 10 :
                size = 18
            case 4 | 5 | 6 | 7 :
                size = 15
            case 11 | 12:
                size = 14
        
        symbol = DraggableSymbol(self, self.combo1.currentText(), self.combo1.currentIndex(), \
        0 * 40, 0 * 20, size, pen)
        self.parent.scene.addItem(symbol)
        match self.combo1.currentIndex()-1:
            case 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 :
                self.parent.all_symbol_list[self.combo1.currentIndex()-1].append([symbol, 0, 0, self.combo3.currentText()])
            case 8 | 9 | 10 | 11 | 12:
                self.parent.all_symbol_list[self.combo1.currentIndex()-1].append([symbol, 0, 0, self.combo3.currentText(), self.combo2.currentText()])

class LorR(QWidget):
    def __init__(self, parent):
        self.parent = parent
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout()

        button_right_ear = QPushButton("Right Ear")  # Create a button
        button_right_ear.clicked.connect(self.Set_R)
        
        button_left_ear = QPushButton("Left Ear")  # Create a button
        button_left_ear.clicked.connect(self.Set_L)

        layout.addWidget(button_right_ear)  # Add the button to the right
        layout.addWidget(button_left_ear)  # Add the button to the left

        self.setLayout(layout)

    def Set_R(self):
        self.parent.side = 'right'
        self.parent.load_in()
    
    def Set_L(self):
        self.parent.side = 'left'
        self.parent.load_in()

class Digital_Audiogram(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()
        # self.setFixedSize(800, 720)

    def initUI(self):

        # Create a QGraphicsView and QGraphicsScene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.map_freq_to_coordinate = {125:0, 250:1, 500:2, 750:3, 1000:4, 1500:5, 2000:6,
                                    3000:7, 4000:8, 6000:9, 8000:10, 12000:11}
        self.map_coordinate_to_freq = {0:125, 1:250, 2:500, 3:750, 4:1000, 5:1500, 6:2000,
                                    7:3000, 8:4000, 9:6000, 10:8000, 11:12000}
        self.map_thres_to_coordinate = {-10:0, -5:1, 0:2, 5:3, 10:4, 15:5, 20:6, 25:7, 30:8, 35:9, 40:10,
                                    45:11, 50:12, 55:13, 60:14, 65:15, 70:16, 75:17, 80:18, 85:19, 90:20,
                                    95:21, 100:22, 105:23, 110:24, 115:25, 120:26}
        self.map_coordinate_to_thres = {0:-10, 1:-5, 2:0, 3:5, 4:10, 5:15, 6:20, 7:25, 8:30, 9:35, 10:40,
                                    11:45, 12:50, 13:55, 14:60, 15:65, 16:70, 17:75, 18:80, 19:85, 20:90,
                                    21:95, 22:100, 23:105, 24:110, 25:115, 26:120}
        
        self.measurementType_to_num = {"AIR_UNMASKED_RIGHT":0, "AIR_UNMASKED_LEFT":1, "AIR_MASKED_RIGHT":4, "AIR_MASKED_LEFT":5,
                "BONE_UNMASKED_RIGHT":2, "BONE_UNMASKED_LEFT":3, "BONE_MASKED_RIGHT":6, "BONE_MASKED_LEFT":7,
                "SOUND_FIELD":8, "HEARING_AID":9, "COCHLEAR_IMPLANT":10, "AL":11, "AR":12}
        self.num_to_measurementType = {0:"AIR_UNMASKED_RIGHT", 1:"AIR_UNMASKED_LEFT", 4:"AIR_MASKED_RIGHT", 5:"AIR_MASKED_LEFT",
                2:"BONE_UNMASKED_RIGHT", 3:"BONE_UNMASKED_LEFT", 6:"BONE_MASKED_RIGHT", 7:"BONE_MASKED_LEFT",
                8:"SOUND_FIELD", 9:"HEARING_AID", 10:"COCHLEAR_IMPLANT", 11:"AL", 12:"AR"}

        self.all_symbol_list = [[] for _ in range(13)]

        # Add vertical grid lines
        for i in range(12):
            x = i * 40
            line = QGraphicsLineItem(x, 0, x, 520)
            line.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            self.scene.addItem(line)

            # Add labels to the x-axis aligned with grid lines
            x_labels = ['125', '250', '500', '750', '1K', '1.5K', '2K', '3K', '4K', '6K', '8K', '12K']
            x_label = QGraphicsTextItem(str(x_labels[i]))
            x_label.setPos(x - x_label.boundingRect().width() / 2, 530)
            self.scene.addItem(x_label)

        # Add horizontal grid lines
        for j in range(14):
            y = j * 40
            line = QGraphicsLineItem(0, y, 440, y)
            line.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            self.scene.addItem(line)

            # Add labels to the y-axis aligned with grid lines
            y_labels = [120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0, -10]
            y_label = QGraphicsTextItem(str(y_labels[13 - j]))
            y_label.setPos(-10 - y_label.boundingRect().width(), y - y_label.boundingRect().height() / 2)
            self.scene.addItem(y_label)

        self.side = 'right'
        left_or_right = LorR(self)
        add_symbol = Add_Symbol(self)
        
        output_button = QPushButton("Output")
        output_button.clicked.connect(self.outputButtonClicked)

        self.load_in()

        # Create a widget to hold the button
        button_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(left_or_right)
        layout.addWidget(add_symbol)
        layout.addWidget(output_button)
        self.setLayout(layout)

    def load_in(self):
        for i_list in self.all_symbol_list:
            for i in i_list:
                self.scene.removeItem(i[0])
        
        self.datas = self.read_json(self.parent.path_list[1][self.parent.file_seq])
        
        red_pen = QPen(QColor("red"), 1, Qt.SolidLine)
        blue_pen = QPen(QColor("blue"), 1, Qt.SolidLine)
        black_pen = QPen(QColor("black"), 1, Qt.SolidLine)

        for i_list in self.all_symbol_list:
            i_list.clear()

        number_of_audiogram = 1
        if 'type' in self.datas[0]:
            number_of_audiogram = self.datas[0]["number of audiograms"]
            self.datas.pop(0)

        for data in self.datas:
            if(number_of_audiogram == 2 and self.side != data['ear']):
                continue
            match data['measurementType']:
                case 'AIR_UNMASKED_RIGHT':
                    if self.find_same(self.all_symbol_list[0], data['frequency']):
                        continue
                    if(data['response'] == True):
                        red_circle = DraggableSymbol(self, 'O', 0, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, red_pen)
                        self.all_symbol_list[0].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        red_circle = DraggableSymbol(self, '↓O', 0, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, red_pen)
                        self.all_symbol_list[0].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(red_circle)
                
                case 'AIR_UNMASKED_LEFT':
                    if self.find_same(self.all_symbol_list[1], data['frequency']):
                        continue
                    if(data['response'] == True):
                        blue_cross = DraggableSymbol(self, 'X', 1, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, blue_pen)
                        self.all_symbol_list[1].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        blue_cross = DraggableSymbol(self, 'X↓', 1, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, blue_pen)
                        self.all_symbol_list[1].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(blue_cross)
                case 'BONE_UNMASKED_RIGHT':
                    if self.find_same(self.all_symbol_list[2], data['frequency']):
                        continue
                    if(data['response'] == True):
                        red_circle = DraggableSymbol(self, '<', 2, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, red_pen)
                        self.all_symbol_list[2].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        red_circle = DraggableSymbol(self, '↓<', 2, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, red_pen)
                        self.all_symbol_list[2].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(red_circle)
                case 'BONE_UNMASKED_LEFT':
                    if self.find_same(self.all_symbol_list[3], data['frequency']):
                        continue
                    if(data['response'] == True):
                        blue_cross = DraggableSymbol(self, '>', 3, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, blue_pen)
                        self.all_symbol_list[3].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        blue_cross = DraggableSymbol(self, '>↓', 3, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, blue_pen)
                        self.all_symbol_list[3].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(blue_cross)
                case 'AIR_MASKED_RIGHT':
                    if self.find_same(self.all_symbol_list[4], data['frequency']):
                        continue
                    if(data['response'] == True):
                        red_circle = DraggableSymbol(self, '△', 4, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, red_pen)
                        self.all_symbol_list[4].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        red_circle = DraggableSymbol(self, '↓△', 4, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, red_pen)
                        self.all_symbol_list[4].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(red_circle)
                case 'AIR_MASKED_LEFT':
                    if self.find_same(self.all_symbol_list[5], data['frequency']):
                        continue
                    if(data['response'] == True):
                        blue_cross = DraggableSymbol(self, '☐', 5, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, blue_pen)
                        self.all_symbol_list[5].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        blue_cross = DraggableSymbol(self, '☐↓', 5, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, blue_pen)
                        self.all_symbol_list[5].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(blue_cross)
                case 'BONE_MASKED_RIGHT':
                    if self.find_same(self.all_symbol_list[6], data['frequency']):
                        continue
                    if(data['response'] == True):
                        red_circle = DraggableSymbol(self, '[', 6, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, red_pen)
                        self.all_symbol_list[6].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        red_circle = DraggableSymbol(self, '↓[', 6, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, red_pen)
                        self.all_symbol_list[6].append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(red_circle)
                case 'BONE_MASKED_LEFT':
                    if self.find_same(self.all_symbol_list[7], data['frequency']):
                        continue
                    if(data['response'] == True):
                        blue_cross = DraggableSymbol(self, ']', 7, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, blue_pen)
                        self.all_symbol_list[7].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True])
                    else:
                        blue_cross = DraggableSymbol(self, ']↓', 7, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 15, blue_pen)
                        self.all_symbol_list[7].append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False])
                    self.scene.addItem(blue_cross)
                case 'SOUND_FIELD':
                    if self.find_same(self.all_symbol_list[8], data['frequency']):
                        continue
                    if(data['response'] == True):
                        symbol1 = DraggableSymbol(self, 'S', 8, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, black_pen)
                        self.all_symbol_list[8].append([symbol1, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], True, data['ear']])
                    else:
                        symbol1 = DraggableSymbol(self, 'S↓', 8, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, black_pen)
                        self.all_symbol_list[8].append([symbol1, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], False, data['ear']])
                    self.scene.addItem(symbol1)
                case 'HEARING_AID':
                    if self.find_same(self.all_symbol_list[9], data['frequency']):
                        continue
                    symbol2 = DraggableSymbol(self, 'A', 9, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, black_pen)
                    self.scene.addItem(symbol2)
                    self.all_symbol_list[9].append([symbol2, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], None, data['ear']])
                case 'COCHLEAR_IMPLANT':
                    if self.find_same(self.all_symbol_list[10], data['frequency']):
                        continue
                    symbol3 = DraggableSymbol(self, 'C', 10, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 18, black_pen)
                    self.scene.addItem(symbol3)
                    self.all_symbol_list[10].append([symbol3, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], None, data['ear']])
                case 'AR':
                    if self.find_same(self.all_symbol_list[11], data['frequency']):
                        continue
                    symbol4 = DraggableSymbol(self, 'AR', 11, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 14, red_pen)
                    self.scene.addItem(symbol4)
                    self.all_symbol_list[11].append([symbol4, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], None, data['ear']])
                case 'AL':
                    if self.find_same(self.all_symbol_list[12], data['frequency']):
                        continue
                    symbol5 = DraggableSymbol(self, 'AL', 12, self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 14, blue_pen)
                    self.scene.addItem(symbol5)
                    self.all_symbol_list[12].append([symbol5, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']], None, data['ear']])
                
    def read_json(self, file):
        with open(file, "r") as file:
            data = json.load(file)
        return data
    
    def outputButtonClicked(self):
        # Handle the "Output" button click event
        output_list = []
        for i in range(13):
            if(i >= 8):
                temp_list = []
                both_list  = []
                right_list = []
                left_list  = []
                for item in self.all_symbol_list[i]:
                    if item[4] == 'right':
                        right_list.append(item)
                    elif item[4] == 'left':
                        left_list.append(item)
                    elif item[4] == 'both':
                        both_list.append(item)
                
                both_list = sorted(both_list, key=lambda x: x[1])
                right_list = sorted(right_list, key=lambda x: x[1])
                left_list = sorted(left_list, key=lambda x: x[1])
                if(len(both_list) != 0):
                    temp_list += both_list

                if(len(right_list) != 0):
                    temp_list += right_list

                if(len(left_list) != 0):
                    temp_list += left_list
            else:
                temp_list = sorted(self.all_symbol_list[i], key=lambda x: x[1])
            
            if(len(temp_list) != 0):
                self.format_data(output_list, temp_list, self.num_to_measurementType[i])
        file_dir = os.path.dirname(self.parent.path_list[1][self.parent.file_seq])
        file_name = os.path.basename(self.parent.path_list[1][self.parent.file_seq])
        base_name, file_type = os.path.splitext(file_name)
        if(len(base_name) > 4 and base_name[-4:] != '_new'):
            file_name = os.path.basename(self.parent.path_list[1][self.parent.file_seq])[:-5]+'_new.json'
        new_file = os.path.join(file_dir, file_name)
        with open(new_file, "w") as json_file:
            # Write the list of data to the JSON file
            json.dump(output_list, json_file, indent = 4)
        self.parent.path_list[1][self.parent.file_seq] = new_file

    def format_data(self, output_list, data_list, m_type):
        parts = m_type.split("_")
        if(len(parts) >= 3): #regular normal type
        #no 4 in this version
            for symbol in data_list:
                data = {
                    "ear": "right", #'left'
                    "conduction": "air", #"bone"
                    "masking": False,   #True
                    "measurementType": m_type,
                    "frequency": 125,
                    "threshold": 0,
                    "response": True
                }
                if((parts[2] == 'RIGHT' and len(parts) == 3) or (len(parts) == 4 and parts[3] == 'RIGHT')):
                    data["ear"] = 'right'
                elif((parts[2] == 'LEFT' and len(parts) == 3) or (len(parts) == 4 and parts[3] == 'LEFT')):
                    data["ear"] = 'left'
                
                if((parts[0] == 'AIR' and len(parts) == 3) or (len(parts) == 4 and parts[1] == 'AIR')):
                    data["conduction"] = 'air'
                elif((parts[0] == 'BONE' and len(parts) == 3) or (len(parts) == 4 and parts[1] == 'BONE')):
                    data["conduction"] = 'bone'

                if((parts[1] == 'UNMASKED' and len(parts) == 3) or (len(parts) == 4 and parts[2] == 'UNMASKED')):
                    data["masking"] = False
                elif((parts[1] == 'MASKED' and len(parts) == 3) or (len(parts) == 4 and parts[2] == 'MASKED')):
                    data["masking"] = True

                if(symbol[0].change_pos == [0, 0]):
                    data["frequency"] = self.map_coordinate_to_freq[symbol[1]]
                    data["threshold"] = self.map_coordinate_to_thres[symbol[2]]
                else:
                    data["frequency"] = self.map_coordinate_to_freq[symbol[1] + symbol[0].change_pos[0]]
                    data["threshold"] = self.map_coordinate_to_thres[symbol[2] + symbol[0].change_pos[1]]
                
                data["response"] = symbol[3]

                output_list.append(data)
        else:
            for symbol in data_list:
                data = {
                    "ear": symbol[4],
                    "conduction": None,
                    "masking": None,
                    "measurementType": m_type,
                    "frequency": 125,
                    "threshold": 0,
                    "response": True
                }

                if(symbol[3] == ' '):
                    data["response"] = true
                elif(symbol[3] == 'False'):
                    data["response"] = False
                
                if(symbol[0].change_pos == [0, 0]):
                    data["frequency"] = self.map_coordinate_to_freq[symbol[1]]
                    data["threshold"] = self.map_coordinate_to_thres[symbol[2]]
                else:
                    data["frequency"] = self.map_coordinate_to_freq[symbol[1] + symbol[0].change_pos[0]]
                    data["threshold"] = self.map_coordinate_to_thres[symbol[2] + symbol[0].change_pos[1]]
                
                output_list.append(data)

    def find_same(self, symbol_list:list, input_freq: int) -> bool:
        for symbol in symbol_list:
            if symbol[1] == input_freq:
                print(f'Found Different !!! Frequency = {input_freq}')
                return True
        return False
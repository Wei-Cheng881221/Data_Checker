import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem,\
QPushButton, QVBoxLayout, QWidget, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter, QFont
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF
import json
import math
import os

class DraggableSymbol(QGraphicsTextItem):
    def __init__(self, symbol, x, y, size, pen, boundary, parent=None):
        super().__init__(symbol, parent)
        self.symbol = symbol

        self.setDefaultTextColor(pen.color())

        font = self.font()
        font.setPointSize(size)
        self.setFont(font)

        self.text_width = self.boundingRect().width()
        self.text_height = self.boundingRect().height()

        if(self.symbol == 'O' or self.symbol == 'X' or self.symbol == '△' or self.symbol == '☐' or self.symbol == 'S'):
            self.setPos(x - self.text_width / 2, y - self.text_height / 2)
        elif(self.symbol == '<' or self.symbol == '['):
            self.setPos(x - self.text_width / 2 - 15, y - self.text_height / 2)
        elif(self.symbol == '>' or self.symbol == ']'):
            self.setPos(x - self.text_width / 2 + 15, y - self.text_height / 2)

        self.initial_pos = [x, y]
        self.change_pos = [0, 0]
        self.setFlag(QGraphicsTextItem.ItemIsMovable)

    def mouseMoveEvent(self, event):
        if((round(event.scenePos().x() / 40) * 40 >= 0 and round(event.scenePos().x() / 40) * 40 <= 400) and \
        round(event.scenePos().y() / 20) * 20 >= 0 and round(event.scenePos().y() / 20) * 20 <= 520):
            if(self.symbol == 'O' or self.symbol == 'X' or self.symbol == '△' or self.symbol == '☐' or self.symbol == 'S'):
                self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
            elif(self.symbol == '<' or self.symbol == '['):
                self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2 - 15, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
            elif(self.symbol == '>' or self.symbol == ']'):
                self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2 + 15, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
        

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # print(self.pos().x() + self.text_width / 2, self.initial_pos[0])
            if((self.symbol == 'O' or self.symbol == 'X' or self.symbol == '△' or self.symbol == '☐' or self.symbol == 'S') and \
            (int(self.pos().x() + self.text_width / 2) != int(self.initial_pos[0]) or self.pos().y() + self.text_height / 2 != self.initial_pos[1])):
                self.change_pos = [self.change_pos[0]+(self.pos().x() + self.text_width / 2 - self.initial_pos[0])/40, self.change_pos[1]+(self.pos().y() + self.text_height / 2 - self.initial_pos[1])/20]
                self.initial_pos = [self.pos().x() + self.text_width / 2, self.pos().y() + self.text_height / 2]
            elif(self.symbol == '<' or self.symbol == '['):
                self.change_pos = [self.change_pos[0]+(self.pos().x() + self.text_width / 2 + 15 - self.initial_pos[0])/40, self.change_pos[1]+(self.pos().y() + self.text_height / 2 - self.initial_pos[1])/20]
                self.initial_pos = [self.pos().x() + self.text_width / 2 + 15, self.pos().y() + self.text_height / 2]
            elif(self.symbol == '>' or self.symbol == ']'):
                self.change_pos = [self.change_pos[0]+(self.pos().x() + self.text_width / 2 - 15 - self.initial_pos[0])/40, self.change_pos[1]+(self.pos().y() + self.text_height / 2 - self.initial_pos[1])/20]
                self.initial_pos = [self.pos().x() + self.text_width / 2 - 15, self.pos().y() + self.text_height / 2]

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

        # Define the boundary for the table
        table_boundary = QRectF(0, 0, 400, 400)

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
        
        self.AIR_UNMASKED_RIGHT = []
        self.AIR_UNMASKED_LEFT = []
        self.BONE_UNMASKED_RIGHT = []
        self.BONE_UNMASKED_LEFT = []
        self.AIR_MASKED_RIGHT = []
        self.AIR_MASKED_LEFT = []
        self.BONE_MASKED_RIGHT = []
        self.BONE_MASKED_LEFT = []

        # self.for_delete = []

        # Add vertical grid lines
        for i in range(11):
            x = i * 40
            line = QGraphicsLineItem(x, 0, x, 520)
            line.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            self.scene.addItem(line)

            # Add labels to the x-axis aligned with grid lines
            x_labels = ['125', '500', '750', '1K', '1.5K', '2K', '3K', '4K', '6K', '8K', '12K']
            x_label = QGraphicsTextItem(str(x_labels[i]))
            x_label.setPos(x - x_label.boundingRect().width() / 2, 530)
            self.scene.addItem(x_label)

        # Add horizontal grid lines
        for j in range(14):
            y = j * 40
            line = QGraphicsLineItem(0, y, 400, y)
            line.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            self.scene.addItem(line)

            # Add labels to the y-axis aligned with grid lines
            y_labels = [120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0, -10]
            y_label = QGraphicsTextItem(str(y_labels[13 - j]))
            y_label.setPos(-50 - y_label.boundingRect().width(), y - y_label.boundingRect().height() / 2)
            self.scene.addItem(y_label)

        output_button = QPushButton("Output")
        output_button.clicked.connect(self.outputButtonClicked)
        
        self.load_in()

        # Create a widget to hold the button
        button_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(output_button)
        self.setLayout(layout)

    def load_in(self):
        
        for i in self.AIR_UNMASKED_RIGHT:
            self.scene.removeItem(i[0])
        for i in self.AIR_UNMASKED_LEFT:
            self.scene.removeItem(i[0])
        for i in self.BONE_UNMASKED_RIGHT:
            self.scene.removeItem(i[0])
        for i in self.BONE_UNMASKED_LEFT:
            self.scene.removeItem(i[0])
        for i in self.AIR_MASKED_RIGHT:
            self.scene.removeItem(i[0])
        for i in self.AIR_MASKED_LEFT:
            self.scene.removeItem(i[0])
        for i in self.BONE_MASKED_RIGHT:
            self.scene.removeItem(i[0])
        for i in self.BONE_MASKED_LEFT:
            self.scene.removeItem(i[0])

        self.datas = self.read_json(self.parent.path_list[1][self.parent.file_seq])
        
        red_pen = QPen(QColor("red"), 1, Qt.SolidLine)
        blue_pen = QPen(QColor("blue"), 1, Qt.SolidLine)
        self.AIR_UNMASKED_RIGHT = []
        self.AIR_UNMASKED_LEFT = []
        self.BONE_UNMASKED_RIGHT = []
        self.BONE_UNMASKED_LEFT = []
        self.AIR_MASKED_RIGHT = []
        self.AIR_MASKED_LEFT = []
        self.BONE_MASKED_RIGHT = []
        self.BONE_MASKED_LEFT = []

        # print(self.datas)
        self.datas.pop(0)
        for data in self.datas:
            table_boundary = QRectF(0, 0, 400, 400)
            match data['measurementType']:
                case 'AIR_UNMASKED_RIGHT':
                    if self.find_same(self.AIR_UNMASKED_RIGHT, data['frequency']):
                        continue
                    red_circle = DraggableSymbol('O', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    # self.for_delete.append(red_circle)
                    self.AIR_UNMASKED_RIGHT.append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'AIR_UNMASKED_LEFT':
                    blue_cross = DraggableSymbol('X', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    # self.for_delete.append(blue_cross)
                    self.AIR_UNMASKED_LEFT.append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'BONE_UNMASKED_RIGHT':
                    red_circle = DraggableSymbol('<', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    # self.for_delete.append(red_circle)
                    self.BONE_UNMASKED_RIGHT.append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'BONE_UNMASKED_LEFT':
                    blue_cross = DraggableSymbol('>', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    # self.for_delete.append(blue_cross)
                    self.BONE_UNMASKED_LEFT.append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'AIR_MASKED_RIGHT':
                    red_circle = DraggableSymbol('△', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    # self.for_delete.append(red_circle)
                    self.AIR_MASKED_RIGHT.append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'AIR_MASKED_LEFT':
                    blue_cross = DraggableSymbol('☐', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    # self.for_delete.append(blue_cross)
                    self.AIR_MASKED_LEFT.append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'BONE_MASKED_RIGHT':
                    red_circle = DraggableSymbol('[', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    # self.for_delete.append(red_circle)
                    self.BONE_MASKED_RIGHT.append([red_circle, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])
                case 'BONE_MASKED_LEFT':
                    blue_cross = DraggableSymbol(']', self.map_freq_to_coordinate[data['frequency']] * 40, self.map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    # self.for_delete.append(blue_cross)
                    self.BONE_MASKED_LEFT.append([blue_cross, self.map_freq_to_coordinate[data['frequency']], self.map_thres_to_coordinate[data['threshold']]])

    def read_json(self, file):
        with open(file, "r") as file:
            data = json.load(file)
        return data
    
    def outputButtonClicked(self):
        # Handle the "Output" button click event
        output_list = []
        AIR_UNMASKED_RIGHT = sorted(self.AIR_UNMASKED_RIGHT, key=lambda x: x[1])
        self.format_data(output_list, AIR_UNMASKED_RIGHT, 'AIR_UNMASKED_RIGHT')
        AIR_UNMASKED_LEFT = sorted(self.AIR_UNMASKED_LEFT, key=lambda x: x[1])
        self.format_data(output_list, AIR_UNMASKED_LEFT, 'AIR_UNMASKED_LEFT')
        BONE_UNMASKED_RIGHT = sorted(self.BONE_UNMASKED_RIGHT, key=lambda x: x[1])
        self.format_data(output_list, BONE_UNMASKED_RIGHT, 'BONE_UNMASKED_RIGHT')
        BONE_UNMASKED_LEFT = sorted(self.BONE_UNMASKED_LEFT, key=lambda x: x[1])
        self.format_data(output_list, BONE_UNMASKED_LEFT, 'BONE_UNMASKED_LEFT')
        AIR_MASKED_RIGHT = sorted(self.AIR_MASKED_RIGHT, key=lambda x: x[1])
        self.format_data(output_list, AIR_MASKED_RIGHT, 'AIR_MASKED_RIGHT')
        AIR_MASKED_LEFT = sorted(self.AIR_MASKED_LEFT, key=lambda x: x[1])
        self.format_data(output_list, AIR_MASKED_LEFT, 'AIR_MASKED_LEFT')
        BONE_MASKED_RIGHT = sorted(self.BONE_MASKED_RIGHT, key=lambda x: x[1])
        self.format_data(output_list, BONE_MASKED_RIGHT, 'BONE_MASKED_RIGHT')
        BONE_MASKED_LEFT = sorted(self.BONE_MASKED_LEFT, key=lambda x: x[1])
        self.format_data(output_list, BONE_MASKED_LEFT, 'BONE_MASKED_LEFT')
        # print(output_list)

        file_name = os.path.basename(self.parent.path_list[1][self.parent.file_seq])[:-5]+'_new.json'
        with open(file_name, "w") as json_file:
            # Write the list of data to the JSON file
            json.dump(output_list, json_file, indent = 4)
        
    def format_data(self, output_list, data_list, m_type):
        parts = m_type.split("_")
        if(len(parts) >= 3): #regular normal type
            for symbol in data_list:
                data = {
                    "ear": "right", #'left'
                    "conduction": "air", #"bone"
                    "masking": False,   #True
                    "measurementType": "BONE_UNMASKED_RIGHT",
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
                    
                data["measurementType"] = m_type

                if(symbol[0].change_pos == [0, 0]):
                    # print(self.map_coordinate_to_freq[symbol[1]], self.map_coordinate_to_thres[symbol[2]])
                    data["frequency"] = self.map_coordinate_to_freq[symbol[1]]
                    data["threshold"] = self.map_coordinate_to_thres[symbol[2]]
                else:
                    data["frequency"] = self.map_coordinate_to_freq[symbol[1] + symbol[0].change_pos[0]]
                    data["threshold"] = self.map_coordinate_to_thres[symbol[2] + symbol[0].change_pos[1]]
                # print(data["frequency"], data["threshold"])
                
                if(len(parts) == 4):
                    data["response"] = False
                elif(len(parts) == 3):
                    data["response"] = True

                # print(data)
                output_list.append(data)
                # print(output_list)

    def find_same(self, symbol_list:list, input_freq: int) -> bool:
        for symbol in symbol_list:
            if symbol[1] == input_freq:
                print(f'Found Different !!! Frequency = {input_freq}')
                return True
        return False
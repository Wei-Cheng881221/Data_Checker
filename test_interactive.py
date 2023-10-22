import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem,\
QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor, QPainter, QFont
from PyQt5.QtWidgets import QGraphicsEllipseItem
from PyQt5.QtCore import QRectF
import json


class DraggableSymbol(QGraphicsTextItem):
    def __init__(self, symbol, x, y, size, pen, boundary, parent=None):
        super().__init__(symbol, parent)
        self.setDefaultTextColor(pen.color())
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self.text_width = self.boundingRect().width()
        self.text_height = self.boundingRect().height()
        self.setPos(x - self.text_width / 2, y - self.text_height / 2)
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.boundary = boundary
        self.boundary.setX(boundary.x() - x)
        self.boundary.setY(boundary.y() - y)
        self.boundary.setWidth(boundary.width() - x)
        self.boundary.setHeight(boundary.height() - y)

        # print(boundary)

    def mouseMoveEvent(self, event):
        # Snap to the nearest grid position
        self.setPos(round(event.scenePos().x() / 40) * 40 - self.text_width / 2, round(event.scenePos().y() / 20) * 20 - self.text_height / 2)
        

class GridTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Grid Table App')

        # Create a QGraphicsView and QGraphicsScene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        # Define the boundary for the table
        table_boundary = QRectF(0, 0, 400, 400)

        map_freq_to_coordinate = {125:0, 250:1, 500:2, 750:3, 1000:4, 1500:5, 2000:6,
                                    3000:7, 4000:8, 6000:9, 8000:10, 12000:11}
        map_thres_to_coordinate = {-10:0, -5:1, 0:2, 5:3, 10:4, 15:5, 20:6, 25:7, 30:8, 35:9, 40:10,
                                    45:11, 50:12, 55:13, 60:14, 65:15, 70:16, 75:17, 80:18, 85:19, 290:20,
                                    95:21, 100:22, 105:23, 110:24, 115:25, 120:26}
        
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

        self.datas = self.read_json("./open_json/example_PTA_2.json")
        # print(self.data)

        red_pen = QPen(QColor("red"), 1, Qt.SolidLine)
        blue_pen = QPen(QColor("blue"), 1, Qt.SolidLine)
        self.AIR_UNMASKED_RIGHT = []
        AIR_UNMASKED_LEFT = []
        BONE_UNMASKED_RIGHT = []
        BONE_UNMASKED_LEFT = []
        for data in self.datas:
            match data['measurementType']:
                case 'AIR_UNMASKED_RIGHT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    red_circle = DraggableSymbol('O', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    self.AIR_UNMASKED_RIGHT.append(red_circle)
                case 'AIR_UNMASKED_LEFT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    blue_cross = DraggableSymbol('X', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    AIR_UNMASKED_LEFT.append(blue_cross)
                case 'BONE_UNMASKED_RIGHT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    red_circle = DraggableSymbol('<', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    BONE_UNMASKED_RIGHT.append(red_circle)
                case 'BONE_UNMASKED_LEFT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    blue_cross = DraggableSymbol('>', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    BONE_UNMASKED_LEFT.append(blue_cross)
                case 'AIR_MASKED_RIGHT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    red_circle = DraggableSymbol('△', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    AIR_UNMASKED_RIGHT.append(red_circle)
                case 'AIR_MASKED_LEFT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    blue_cross = DraggableSymbol('☐', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    AIR_UNMASKED_LEFT.append(blue_cross)
                case 'BONE_MASKED_RIGHT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    red_circle = DraggableSymbol('[', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, red_pen, table_boundary)
                    self.scene.addItem(red_circle)
                    BONE_UNMASKED_RIGHT.append(red_circle)
                case 'BONE_MASKED_LEFT':
                    table_boundary = QRectF(0, 0, 400, 400)
                    blue_cross = DraggableSymbol(']', map_freq_to_coordinate[data['frequency']] * 40, map_thres_to_coordinate[data['threshold']] * 20, 20, blue_pen, table_boundary)
                    self.scene.addItem(blue_cross)
                    BONE_UNMASKED_LEFT.append(blue_cross)
        self.show()
        output_button = QPushButton("Output")
        output_button.clicked.connect(self.outputButtonClicked)
        
        # Create a widget to hold the button
        button_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(output_button)
        button_widget.setLayout(layout)

        # Add the widget to the QMainWindow
        self.setMenuWidget(button_widget)
    
    def read_json(self, file):
        with open(file, "r") as file:
            data = json.load(file)
        return data
    
    def outputButtonClicked(self):
        # Handle the "Output" button click event
        for symbol in self.AIR_UNMASKED_RIGHT:
            # print(symbol.pos())
            continue
    
def main():
    app = QApplication(sys.argv)
    ex = GridTableApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

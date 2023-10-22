import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import QRectF

class SymbolItem(QGraphicsTextItem):
    def __init__(self, x, y, text, symbol_type, font_size, parent=None):
        super().__init__(text, parent)
        self.setDefaultTextColor(QColor("blue"))
        self.symbol_type = symbol_type
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.grid_size = 40

    def mouseMoveEvent(self, event):
        # Snap to grid coordinates while dragging
        grid_x = round(event.scenePos().x() / self.grid_size) * self.grid_size
        grid_y = round(event.scenePos().y() / self.grid_size) * self.grid_size
        self.setPos(grid_x, grid_y)

class GridTableApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('Symbol On Grid App')

        # Create a QGraphicsView and QGraphicsScene
        self.view = QGraphicsView(self)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)

        # Define the boundary for the grid table
        table_boundary = QRectF(0, 0, 400, 400)

        # Add vertical grid lines
        for i in range(11):
            x = i * 40
            line = QGraphicsLineItem(x, 0, x, 400)
            line.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            self.scene.addItem(line)

        # Add horizontal grid lines
        for j in range(11):
            y = j * 40
            line = QGraphicsLineItem(0, y, 400, y)
            line.setPen(QPen(Qt.lightGray, 1, Qt.SolidLine))
            self.scene.addItem(line)

        # Create a centered text item with a symbol type and a larger font size
        centered_text = SymbolItem(7 * 40, 2 * 40, "Symbol", "X", 30)  # Adjust the font size as needed
        self.scene.addItem(centered_text)

        self.show()

def main():
    app = QApplication(sys.argv)
    ex = GridTableApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

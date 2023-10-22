from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys

app = QApplication(sys.argv)
scene = QGraphicsScene()

# Load the JPG file
image_path = "../Ear_Model/test_set/5924125_2016-11-14_PTAold1_page_9.jpg"  # Replace with the path to your JPG file
pixmap = QPixmap(image_path)
if not pixmap.isNull():
    # Add the image to the scene
    image_item = QGraphicsPixmapItem(pixmap)
    scene.addItem(image_item)
    # Set the position of the rectangle on the image
    rect = scene.addRect(1479, 767, 751, 740, Qt.blue)
    # rect.setPos(50, 50)  # Adjust the position as needed

view = QGraphicsView(scene)
view.show()
sys.exit(app.exec_())

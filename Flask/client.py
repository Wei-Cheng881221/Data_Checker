import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt
import requests
import json
import subprocess
import shutil
import os

class FileSenderGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.file_path_label = QLabel("\
        Welcome to NTUH listening center.\n\
        Please choose the picture(jpg, png) to run.")
        self.choose_file_button = QPushButton("Choose Image File")
        self.send_button = QPushButton("Send to Server")

        layout = QVBoxLayout()
        layout.addWidget(self.file_path_label)
        layout.addWidget(self.choose_file_button)
        layout.addWidget(self.send_button)

        self.choose_file_button.clicked.connect(self.choose_file)
        self.send_button.clicked.connect(self.send_to_server)

        self.setLayout(layout)
        self.setFixedSize(600, 400)

    def choose_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose Image File", "", "Image Files (*.jpg *.jpeg *.png);;All Files (*)", options=options)
        if file_name:
            self.file_path_label.setText(f"Selected File: {file_name}")
            self.file_path = file_name

    def send_to_server(self):
        try:
            with open(self.file_path, 'rb') as file:
                files = {'file': open(self.file_path, 'rb')}
                # Replace this URL with your server's URL
                server_url = 'http://127.0.0.1:5000/process'
                response = requests.post(server_url, files=files)

            basename = os.path.basename(self.file_path)
            filename = basename.split(f'.')[0]
            response.raise_for_status()
            server_response = response.json()
            with open(f'input_json/{filename}.json', 'w') as file:
                json.dump(server_response, file, indent=4)
            print("Get server response")

            # You can add logic here to handle the server response
            self.close()
            shutil.copyfile(f'{self.file_path}', f'input_image/{basename}')

            # Run another program using subprocess
            another_program_command = f'python Data_checker_drag.py \
            -i input_image \
            -j input_json'
            subprocess.run(another_program_command, shell=True)

        except Exception as e:
            print("Error:", e)


class FileSenderApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = FileSenderGUI()

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    app = FileSenderApp()
    app.run()

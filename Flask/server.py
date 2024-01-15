from flask import Flask, request, jsonify
import os
import subprocess
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process', methods=['POST'])
def process_file():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({"error": "No selected file"})

        # Check if the file has a valid extension
        if file and allowed_file(file.filename):
            # Save the uploaded file to the server
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            new_directory = '../Ear_Model'
            old_directory = '../Data_Checker'
            # Change the current working directory
            os.chdir(new_directory)

            # Replace 'your_command_here' with the actual shell command you want to run
            command = 'python PTA_script1111.py \
            -i ../Data_Checker/uploads/ -o ../Data_Checker/downloads/ -g 0 -c hsv -s ./models/symbols/0802/weights/best.pt'

            # Run the command
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Print the result
            print(f"Command output: {result.stdout}")
            print(f"Errors, if any: {result.stderr}")
            print(f"Return code: {result.returncode}")

            os.chdir(old_directory)
            basename = os.path.basename(file.filename).split('.')[0]
            with open(f'downloads/{basename}.json', 'r') as result_file:
                data = json.load(result_file)
            
            command = 'rm -r downloads && \
            rm -r uploads/'

            # Run the command
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"Command output: {result.stdout}")
            print(f"Errors, if any: {result.stderr}")
            print(f"Return code: {result.returncode}")
            
            # Return a response
            return jsonify(data)

        return jsonify({"error": "Invalid file format"})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000)

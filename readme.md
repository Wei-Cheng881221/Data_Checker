# Enviroment
If you would like to set up the enviroment using anaconda, simply type `make` in the shell
This will create a enviroment called Ear_Project with the package this project need.

You can also use the command `pip install -r requirements.txt` to update the packages if you need.

## Environment problem resolve
If you encounter any problem opening this app, please delete the environment and create the environment as follow.
```
conda create --name=Ear_Project python=3.10
conda activate Ear_Project
pip install PyQt5
pip install panda
# pip uninstall opencv-python (If you have this install previous automatically)
pip install opencv-python-headless
# sudo apt install libxcb-* (If you are using remote ssh with x11 forwardin)
# conda install -c conda-forge gcc (If you are using remote ssh with x11 forwardin)
```

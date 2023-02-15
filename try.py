#icon = r'/home/r11922164/2T/data/Tkinter/ear_icon_125585.ico'
import tkinter as tk
from tkinter.constants import *

def plus():
    print("你點擊了按鈕")

def show():
    input_str=input1.get()
    print(input_str)
    input1.delete(0, END)

m=tk.Tk()
m.iconbitmap("@ear_icon_125585.xbm")
m.title("AudioGram Checker")
m.geometry('380x400')

Btn1 = tk.Button(text="確認", command=show)
Btn1.pack(side="bottom", fill = "x")

#input1 = tk.Entry(show="*")
input1 = tk.Entry()
input1.pack()

m.mainloop()


import tkinter as tk
from tkinter import ttk
import os
from util.simplify import path

root = tk.Tk()
root.title("test")
# root.geometry('200x200')

tk.Label(root, text = "destination", padx= 10).grid(row= 0, column= 0)

d= os.getcwd()
b = tk.Button(root, text= d, relief= tk.SUNKEN, width= 50, bg= 'White', anchor= 'w', fg= 'gray', activebackground= 'White', activeforeground= 'gray')
b.grid(row= 0, column= 1)

root.mainloop()
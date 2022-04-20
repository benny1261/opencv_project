import tkinter as tk
from tkinter import  Menu, OptionMenu, StringVar, messagebox
from tkinter.ttk import Labelframe
# from util.simplify import path

def auto():
    print("NMSL")

def fetch(var):
    print(var)

def on_closing():
    if messagebox.askokcancel("quit", "Confirm quit?"):
        root.destroy()

def renew():
    root.quit
    root = tk.Tk()
    root.title("GUI")
    initframe = Labelframe(root, padding= 40)
    initframe.pack(padx= 30, pady= 20)
    lb = tk.Label(initframe, text = "White light image")
    lb.grid(row= 0, column= 0)
    w_img = tk.Entry(initframe)
    w_img.grid(row= 0, column= 1)
    lb = tk.Label(initframe, text = "Fluorescent image")
    lb.grid(row= 1, column= 0)
    f_img = tk.Entry(initframe)
    f_img.grid(row= 1, column= 1)
    lb = tk.Label(initframe, text = "")
    lb.grid(row= 2, columnspan= 2)
    lb = tk.Label(initframe, text = "Optimize thereshold")
    lb.grid(row= 3, columnspan= 2)
    aut = tk.Button(initframe, text = "auto", bg="skyblue", width=8, height=2)
    aut.config(command = auto)
    aut.grid(row= 4, column= 0)
    mnl = tk.Button(initframe, text = "manual", bg="#FF4D40", width=8, height=2)
    mnl.config(command = manual)
    mnl.grid(row= 4, column= 1)

def manual():
    initframe.destroy()
    root.geometry("1400x700")
    thres = Labelframe(root, text= "Threshold", padding= 10)
    thres.pack(padx= 10, pady= 10)
    
    bar = tk.Scale(thres, orient= tk.HORIZONTAL, length= 600)
    bar.config(from_= 0, to_= 255, command= fetch)      
    bar.grid(row = 0)
    # bar.place(anchor= CENTER, relx= 0.5, rely= 0.4)

def hello():
    root = tk.Tk()
    root.title("GUI")
    root.protocol("WM_DELETE_WINDOW", on_closing)                            # execute on_closing when esc

    mymenu = Menu(root)
    root.config(menu= mymenu)
    # create menu item
    file_menu= Menu(mymenu)
    mymenu.add_cascade(label= "File", menu= file_menu)
    file_menu.add_command(label= "New", command= renew)
    file_menu.add_separator()
    file_menu.add_command(label= "Exit", command= root.quit)
    view_menu= Menu(mymenu)
    view_menu.add_cascade(label= "View", menu= file_menu)

    initframe = Labelframe(root, padding= 40)
    initframe.pack(padx= 30, pady= 20)

    lb = tk.Label(initframe, text = "White light image")
    lb.grid(row= 0, column= 0)
    w_img = tk.Entry(initframe)
    w_img.grid(row= 0, column= 1)
    lb = tk.Label(initframe, text = "Fluorescent image")
    lb.grid(row= 1, column= 0)
    f_img = tk.Entry(initframe)
    f_img.grid(row= 1, column= 1)
    lb = tk.Label(initframe, text = "")
    lb.grid(row= 2, columnspan= 2)
    lb = tk.Label(initframe, text = "Optimize thereshold")
    lb.grid(row= 3, columnspan= 2)
    aut = tk.Button(initframe, text = "auto", bg="skyblue", width=8, height=2)
    aut.config(command = auto)
    aut.grid(row= 4, column= 0)
    mnl = tk.Button(initframe, text = "manual", bg="#FF4D40", width=8, height=2)
    mnl.config(command = manual)
    mnl.grid(row= 4, column= 1)

    root.mainloop()

root = tk.Tk()
root.title("GUI")
hello()
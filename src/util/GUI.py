import tkinter as tk
from tkinter import  Menu, messagebox
from tkinter.ttk import Labelframe
# from util.simplify import path

class window:

    def __init__(self, f1_dict = {}, f2_dict = {}):
        self.f1_dict = f1_dict
        self.f2_dict = f2_dict

    def auto():
        print("NMSL")

    def fetch():
        pass

    def on_closing(root):
        if messagebox.askokcancel("quit", "Confirm quit?"):
            root.destroy()

    def renew(self):
        self.quit
        self = tk.Tk()
        self.title("GUI")
        initframe = Labelframe(self, padding= 40)
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
        aut.config(command = window.auto)
        aut.grid(row= 4, column= 0)
        mnl = tk.Button(initframe, text = "manual", bg="#FF4D40", width=8, height=2)
        mnl.config(command = window.manual)
        mnl.grid(row= 4, column= 1)

    def manual(self):
        # initframe.destroy()
        self.geometry("1400x700")
        thres = Labelframe(self, text= "Threshold", padding= 10)
        thres.pack(padx= 10, pady= 10)
        
        bar = tk.Scale(thres, orient= tk.HORIZONTAL, length= 600)
        bar.config(from_= 0, to_= 255, command= window.fetch)      
        bar.grid(row = 0)

    def hello(self):
        self = tk.Tk()
        self.title("GUI")
        self.protocol("WM_DELETE_WINDOW", window.on_closing(self))                            # execute on_closing when esc

        mymenu = Menu(self)
        self.config(menu= mymenu)
        # create menu item
        file_menu= Menu(mymenu)
        mymenu.add_cascade(label= "File", menu= file_menu)
        file_menu.add_command(label= "New", command= window.renew)
        file_menu.add_separator()
        file_menu.add_command(label= "Exit", command= self.quit)
        view_menu= Menu(mymenu)
        view_menu.add_cascade(label= "View", menu= file_menu)

        initframe = Labelframe(self, padding= 40)
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
        aut.config(command = window.auto)
        aut.grid(row= 4, column= 0)
        mnl = tk.Button(initframe, text = "manual", bg="#FF4D40", width=8, height=2)
        mnl.config(command = window.manual)
        mnl.grid(row= 4, column= 1)

        self.mainloop()
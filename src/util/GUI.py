import tkinter as tk
from tkinter.ttk import Labelframe

def auto():
    print("NMSL")

def fetch(self):
    bar = tk.Scale()
    print(bar.get())

def manual():
    thres = tk.Toplevel()
    thres.title("Threshold")
    thres.geometry("800x200")
    bar = tk.Scale(thres, orient= tk.HORIZONTAL, length= 600)
    bar.config(from_= 0, to_= 255)
    # bar.config(label= "Threshold")
    bar.place(anchor= tk.CENTER, relx= 0.5, rely= 0.4)
    bar.config(command= fetch)

# def hello():
win = tk.Tk()
win.title("GUI")
initframe = Labelframe(win, padding= 30)
initframe.pack(padx= 10, pady= 10)

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

win.mainloop()
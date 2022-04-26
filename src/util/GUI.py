import tkinter as tk
import os
from tkinter import messagebox
from tkinter import filedialog
# from PIL import ImageTk
# from util.simplify import path

class Frame:
    def __init__(self, window, fmname: str = None, padx= 30, pady= 30):

        self.frame =  tk.LabelFrame(window, text= fmname, padx= padx, pady= pady)
        self.btn = {}
        self.ety = {}
        self.lbl = {}
    
    # def apd_btn(self, name: str, bg: str = None, wid: int = None, hei: int = None, cmd: callable = None):
    #     self.btn[name] = tk.Button(self, text = name, bg = bg, width = wid, height = hei, command= cmd)
    # def apd_ety():
    # def apd_lbl():

# {'text':'...'}-> W.frame['text'].lb.['?']

class Window:

    def __init__(self, frames = {}):
        self.frames = frames                                                                     # initializing dict of frames
        # initializing root window
        self.root = tk.Tk()
        self.root.title("Hsu.exe")
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.hello()                                                                            # execute
        self.root.mainloop()    # end of gui program when this loop broke

    def auto(self):
        print("NMSL")

    def fetch(self):
        pass

    def viewer(self):
        pass
    
    # TESTING FUNC
    def pt(self, widg):
        # print(widg.get())
        self.frames['init'].ety['test']= widg.get()

    def on_closing(self):
        if messagebox.askokcancel("quit", "Confirm quit?"):
            self.root.quit()

    def renew(self):
        for children in self.root.winfo_children():
            children.destroy()
        self.hello()
    
    def browse(self):
        self.root.filename = filedialog.askopenfilename(initialdir= os.getcwd(), title= "Select a file", filetypes=(("all files", "*.*"),("jpg files", "*.jpg")))

    def manual(self):
        # switching frames
        self.frames['init'].frame.pack_forget()
        self.frames['manual'] = Frame(self.root, 'Manual Threshold', padx= 40, pady= 40)
        self.frames['manual'].frame.pack(padx= 10, pady= 10)

        bar = tk.Scale(self.frames['manual'].frame, orient= tk.HORIZONTAL, length= 600)
        bar.config(from_= 0, to_= 255, command= self.fetch)      
        bar.grid(row = 0)

    def hello(self):
        mymenu = tk.Menu(self.root)                                                             # create menu
        self.root.config(menu= mymenu)                                                          # bound "mymenu" to window

        # create menu items
        file_menu= tk.Menu(mymenu, tearoff= 0)                                                  # create "file" submenu under mymenu, tearoff= 0 to remove slash
        file_menu.add_command(label= "New", command= self.renew)                                # create commands under "file"
        file_menu.add_command(label= "Browse", command= self.browse)
        file_menu.add_separator()                                                               # create divider
        file_menu.add_command(label= "Exit", command= self.root.quit)
        view_menu= tk.Menu(mymenu, tearoff= 0)
        view_menu.add_command(label= "Images", command= self.viewer)

        # placing submenus
        mymenu.add_cascade(label= "File", menu= file_menu)
        mymenu.add_cascade(label= "View", menu= view_menu)

        # establish home frame
        init = Frame(self.root, "Home")
        self.frames['init'] = init                                                               # make following code cleaner
        init.frame.pack(padx= 30, pady= 20)

        # add widgets in home frame
        # test = tk.Entry(init.frame)
        # test.pack()
        # self.root.bind('<Return>',lambda arg=test: self.pt(test))

        tk.Label(init.frame, text = "White light image").grid(row= 0, column= 0)
        w_img = tk.Entry(init.frame).grid(row= 0, column= 1)
        tk.Label(init.frame, text = "Fluorescent image").grid(row= 1, column= 0)
        f_img = tk.Entry(init.frame).grid(row= 1, column= 1)
        tk.Label(init.frame).grid(row= 2, columnspan= 2)
        lb = tk.Label(init.frame, text = "Optimize thereshold")
        lb.grid(row= 3, columnspan= 2)
        aut = tk.Button(init.frame, text = "auto", bg="skyblue", width=8, height=2)
        aut.config(command = lambda arg= self: Window.auto(self))
        aut.grid(row= 4, column= 0)
        mnl = tk.Button(init.frame, text = "manual", bg="#FF4D40", width=8, height=2)
        mnl.config(command = lambda arg= self: Window.manual(self))
        mnl.grid(row= 4, column= 1)

if __name__ == '__main__':
    prog = Window()
    # print(prog.frames['init'].ety['test'])
import tkinter as tk
import os
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
# from PIL import ImageTk
from simplify import path

class Frame:
    def __init__(self, window, fmname: str = None, padx= 30, pady= 30):

        self.frame =  tk.LabelFrame(window, text= fmname, padx= padx, pady= pady)
        self.btn = {}
        self.entry = {}
        self.label = {}
        self.scaler = []

class Window:

    def __init__(self, frames = {}):

        # initializing dict of frames
        self.frames = frames
        # initializing root window
        self.root = tk.Tk()
        self.root.title("Hsu.exe")
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.export = os.getcwd()

        self.hello()                                                                            # execute
        self.root.mainloop()                                                                    # end of gui program when this loop broke

    def auto(self):
        print("NMSL")

    def fetch(self, new_value):
        print(int(new_value))

    def viewer(self):
        pass

    def on_closing(self):
        '''Command triggered when user close window directly'''

        if messagebox.askokcancel("quit", "Confirm quit?"):
            self.root.quit()

    def renew(self):
        '''Refresh window to home page by destroying old frames and widgets in root then create a new one'''

        for children in self.root.winfo_children():
            children.destroy()
        self.hello()
    
    def choose_cwd(self):
        '''Let user select directory where they put data'''

        path.mov(filedialog.askdirectory(initialdir= os.getcwd()))
        self.root.stat_bar.config(text= os.getcwd())
        # self.root.filename = filedialog.askopenfilename(initialdir= os.getcwd(), filetypes=(("all files", "*.*"),("jpg files", "*.jpg")))

    def export(self):
        '''export widgets'''

        export = tk.Toplevel(self.root)
        export.title('Export')
        self.frames['export'] = export
        destination = tk.Button(export, text = "export folder", relief= 'SUNKEN')
        destination.config(command = self.choose_des)
        destination.pack()

    def choose_des(self):
        '''Let user select directory where they export data'''

        export = filedialog.askdirectory(initialdir= self.export)
        if not export:
            print("canceled")
        else:
            self.export = export
        
    def manual(self):
        '''Manual adjusting threshold'''

        # switching frames
        self.frames['init'].frame.grid_forget()
        manl = Frame(self.root, 'Manual Threshold', padx= 40, pady= 40)
        self.frames['manual'] = manl
        manl.frame.grid(row= 0, column= 0, padx= 10, pady= 5)

        manl.scaler = tk.Scale(self.frames['manual'].frame, orient= tk.HORIZONTAL, length= 600, from_= 0, to_= 255)
        manl.scaler.pack()
        manl.scaler.config(command= self.fetch)

    def hello(self):
        '''Starting GUI program'''

        # create menu
        mymenu = tk.Menu(self.root)
        self.root.config(menu= mymenu)                                                          # bound "mymenu" to window

        # create menu items
        file_menu= tk.Menu(mymenu, tearoff= 0)                                                  # create "file" submenu under mymenu, tearoff= 0 to remove slash
        file_menu.add_command(label= "New", command= self.renew)                                # create commands under "file"
        file_menu.add_command(label= "Choose CWD", command= self.choose_cwd)
        file_menu.add_command(label= "Export", command = self.export)
        file_menu.add_separator()                                                               # create divider
        file_menu.add_command(label= "Exit", command= self.root.quit)
        view_menu= tk.Menu(mymenu, tearoff= 0)
        view_menu.add_command(label= "CWD Images", command= self.viewer)

        # placing menus
        mymenu.add_cascade(label= "File", menu= file_menu)
        mymenu.add_cascade(label= "View", menu= view_menu)

        # create and place status bar in root
        self.root.stat_bar = tk.Label(self.root, borderwidth= 2, relief= "sunken", text= "cwd: " + os.getcwd(), anchor= tk.E)
        self.root.stat_bar.grid(row= 1, column= 0, sticky="W"+"E")

        # establish home frame
        init = Frame(self.root, "Home")
        self.frames['init'] = init                                                               # make following code cleaner
        init.frame.grid(row= 0, column= 0, padx= 10, pady= 5)
        
        # add widgets in home frame
        tk.Label(init.frame, text = "White light image").grid(row= 0, column= 0)
        w_img = tk.Entry(init.frame).grid(row= 0, column= 1)
        tk.Label(init.frame, text = "Fluorescent image").grid(row= 1, column= 0)
        f_img = tk.Entry(init.frame).grid(row= 1, column= 1)
        lb = tk.Label(init.frame, text = "Optimize thereshold")
        lb.grid(row= 3, columnspan= 2, ipady= 5)
        aut = tk.Button(init.frame, text = "auto", bg="skyblue", width=8, height=2)
        aut.config(command = self.auto)
        aut.grid(row= 4, column= 0)
        mnl = tk.Button(init.frame, text = "manual", bg="#FF4D40", width=8, height=2)
        mnl.config(command = self.manual)
        mnl.grid(row= 4, column= 1)
        init.frame.rowconfigure(2, minsize= 20)

        # initializing window position
        self.root.update_idletasks()
        cord_x = (self.root.winfo_screenwidth()-self.root.winfo_width())/2
        cord_y = (self.root.winfo_screenheight()-self.root.winfo_height())/2
        self.root.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')                                     # uses f-string mothod

if __name__ == '__main__':
    prog = Window()
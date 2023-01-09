from threading import Thread
import tkinter as tk
import os
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
# from PIL import ImageTk
from opencv import Import_thread
from opencv import Cv_api

class Frame:
    def __init__(self, window, fmname: str = None, padx= 30, pady= 30):

        self.frame =  tk.LabelFrame(window, text= fmname, padx= padx, pady= pady)
        self.btn = {}
        self.combobox = {}
        self.label = {}
        self.scaler = []
        self.checkbtn = {}

class Window:

    def __init__(self):
        # initializing root window
        self.root = tk.Tk()
        self.root.title("Hsu.exe")
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.temp_directory = os.getcwd()
        self.export_directory = os.getcwd()
        self.api = Cv_api(self)

        # initializing home frame and its widgets
        self.home_fm = Frame(self.root, "Home", padx= 20, pady= 10)
        self.home_fm.btn['f_img'] = tk.Button(self.home_fm.frame, command =lambda: self.choose_filefolder())
        self.home_fm.btn['f_img'].configure(relief= tk.SUNKEN, width= 20, bg= 'White', fg= 'gray', activebackground= 'White', activeforeground= 'gray')        
        self.home_fm.combobox['target'] = ttk.Combobox(self.home_fm.frame, values= ["CTC", "others..."])
        self.home_fm.combobox['target'].current(0)
        self.home_fm.btn['auto'] = tk.Button(self.home_fm.frame, text = "auto", bg="skyblue", width=8, height=2, command= self.auto)
        self.home_fm.btn['manual'] = tk.Button(self.home_fm.frame, text = "manual", bg="orange", width=8, height=2, command= self.manual)
        self.home_fm.btn['export'] = tk.Button(self.home_fm.frame, text= 'Export', bg='#FF4D40', command= lambda: self.api.export_td())

        # initializing export window,frame and its widgets
        self.export_win = tk.Toplevel(self.root)
        self.export_win.title('Export settings')
        self.export_win.resizable(0,0)
        self.export_win.withdraw()
        self.export_win.protocol("WM_DELETE_WINDOW", self.export_win.withdraw)

        self.export_fm = Frame(self.export_win, fmname= 'export settings')
        self.export_fm.checkbtn['binary0'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['binary1'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['binary3'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['mask'] = tk.BooleanVar(value= True)
        self.export_fm.btn['destination'] = tk.Button(self.export_win, text= self.export_directory, command = self.choose_des)
        self.export_fm.btn['destination'].configure(relief= tk.SUNKEN, width= 50, bg= 'White', anchor= 'w', fg= 'gray', activebackground= 'White', activeforeground= 'gray')
        # export_frame.btn['save'] = tk.Button(export_win, text= 'save', command= lambda: [thread123.start(), export_win.destroy()])  # use lambda to realize multiple commands
        self.export_fm.btn['save'] = tk.Button(self.export_win, text= 'save', command= lambda: self.export_win.withdraw())

        self.hello()                                                                                # execute


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

    def home(self):
        '''return frame to home page'''
        for children in self.root.winfo_children():
            try:
                children.grid_forget()
            except:
                children.withdraw()                                                             # in case children is a toplevel

        # placing menu
        self.root.config(menu= self.mymenu)
        # placing status bar
        self.root.stat_bar.grid(row= 1, column= 0, sticky="W"+"E")
        # placing frame and widgits
        self.home_fm.frame.grid(row= 0, column= 0, padx= 10, pady= 5)
    
    def choose_cwd(self):
        '''Let user select directory where they import data'''

        os.chdir(filedialog.askdirectory(initialdir= os.getcwd()))
        self.root.stat_bar.config(text= os.getcwd())

    def thread_monitor(self, window, thread, command):
        '''check whether the thread in window is alive, if not, run command'''

        if thread.is_alive():
            window.after(100, lambda: self.thread_monitor(window, thread, command))
        else:
            command()

    def export_setting(self):
        '''export custumization'''

        self.export_fm.btn['destination'].configure(text= self.export_directory)
        self.export_win.deiconify()                                                             # show the window

        # place frame
        self.export_fm.frame.grid(row= 0, column= 0, columnspan= 2, padx= 30, pady= 10, sticky= tk.W)

        # place widgets in frame
        tk.Checkbutton(self.export_fm.frame, text= 'binary0', variable= self.export_fm.checkbtn['binary0']).grid(row= 0, column= 0)
        tk.Checkbutton(self.export_fm.frame, text= 'binary1', variable= self.export_fm.checkbtn['binary1']).grid(row= 0, column= 1)
        tk.Checkbutton(self.export_fm.frame, text= 'binary3', variable= self.export_fm.checkbtn['binary3']).grid(row= 1, column= 0)
        tk.Checkbutton(self.export_fm.frame, text= 'mask', variable= self.export_fm.checkbtn['mask']).grid(row= 1, column= 1)

        # widgets below frame
        tk.Label(self.export_win, text = "destination:", padx= 10).grid(row= 2, column= 0)
        self.export_fm.btn['destination'].grid(row= 2, column= 1, padx= 5, pady= 10)
        self.export_fm.btn['save'].grid(row= 3, column= 1, sticky= 'E', padx= 10, pady= 5)

    def choose_des(self):
        '''Let user select directory where they export data'''

        des = filedialog.askdirectory(initialdir= os.getcwd())
        if des:
            self.export_directory = des
            self.export_fm.btn['destination'].configure(text= self.export_directory)
    
    def choose_filefolder(self):
        '''Choose material pictures'''
        
        folder = filedialog.askdirectory(initialdir= os.getcwd())   
        if folder:
            self.temp_directory = folder
            self.import_td = Import_thread(folder)                              # create class inherited from threading, initialize each time when choosing folder

            # create progress bar toplevel
            progwin = tk.Toplevel(self.root)
            progwin.title('Importing...')
            progwin.resizable(0,0)

            # progress bar widget
            progbar = ttk.Progressbar(progwin, length= 200, mode= "indeterminate")
            progbar.start()
            progbar.pack(padx= 20, pady= 10)

            # initializing bar position
            progwin.update_idletasks()
            cord_x = (progwin.winfo_screenwidth()-progwin.winfo_width())/2
            cord_y = (progwin.winfo_screenheight()-progwin.winfo_height())/2
            progwin.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')               # uses f-string mothod
            
            # connect to imported threading function from opencv.py
            self.import_td.start()                                              # this will start the run() method in Import_thread
            self.thread_monitor(progwin, self.import_td, progwin.destroy)

            self.home_fm.btn['f_img'].configure(text= os.path.basename(os.path.normpath(folder)))
            self.export_directory = self.temp_directory

    def manual(self):
        '''Manual adjusting threshold'''

        # switching frames
        self.home_fm.frame.grid_forget()
        self.manual_fm = Frame(self.root, 'Manual Threshold', padx= 40, pady= 40)
        self.manual_fm.frame.grid(row= 0, column= 0, padx= 10, pady= 5)

        self.manual_fm.scaler = tk.Scale(self.manual_fm.frame, orient= tk.HORIZONTAL, length= 600, from_= 0, to_= 255)
        self.manual_fm.scaler.pack()
        self.manual_fm.scaler.config(command= self.fetch)

    def hello(self):
        '''Starting GUI program'''

        # create menu
        self.mymenu = tk.Menu(self.root)
        self.root.config(menu= self.mymenu)                                                         # bound "self.mymenu" to window

        # create menu items
        self.file_menu= tk.Menu(self.mymenu, tearoff= 0)                                            # create "file" submenu under self.mymenu, tearoff= 0 to remove slash
        self.file_menu.add_command(label= "Home", command= self.home)
        self.file_menu.add_command(label= "Choose CWD", command= self.choose_cwd)
        self.file_menu.add_command(label= "Export settings", command = self.export_setting)
        self.file_menu.add_separator()                                                              # create divider
        self.file_menu.add_command(label= "Exit", command= self.root.quit)
        self.view_menu= tk.Menu(self.mymenu, tearoff= 0)
        self.view_menu.add_command(label= "CWD Images", command= self.viewer)

        # placing menus
        self.mymenu.add_cascade(label= "File", menu= self.file_menu)
        self.mymenu.add_cascade(label= "View", menu= self.view_menu)

        # create and place status bar in root
        self.root.stat_bar = tk.Label(self.root, borderwidth= 2, relief= "sunken", text= "cwd: " + os.getcwd(), anchor= tk.E)
        self.root.stat_bar.grid(row= 1, column= 0, sticky="W"+"E")

        # place home frame
        self.home_fm.frame.grid(row= 0, column= 0, padx= 10, pady= 5)

        # add widgets in home frame
        tk.Label(self.home_fm.frame, text = "Fluorescent image folder").grid(row= 0, column= 0, sticky= 'W')
        self.home_fm.btn['f_img'].grid(row= 0, column= 1)
        tk.Label(self.home_fm.frame, text = "Target cell").grid(row= 1, column= 0, sticky= 'W')
        self.home_fm.combobox['target'].grid(row= 1, column= 1, pady= 5)

        self.home_fm.frame.rowconfigure(2, minsize= 10)
        tk.Label(self.home_fm.frame, text = "Optimize thereshold").grid(row= 3, columnspan= 2, ipady= 5)
        self.home_fm.btn['auto'].grid(row= 4, column= 0)
        self.home_fm.btn['manual'].grid(row= 4, column= 1)

        self.home_fm.frame.rowconfigure(5, minsize= 20)
        self.home_fm.btn['export'].grid(row= 6, column= 1, columnspan= 2, sticky= tk.SE)

        # initializing window position
        self.root.update_idletasks()
        cord_x = (self.root.winfo_screenwidth()-self.root.winfo_width())/2
        cord_y = (self.root.winfo_screenheight()-self.root.winfo_height())/2
        self.root.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')                                     # uses f-string mothod

if __name__ == '__main__':
    prog = Window()
    prog.root.mainloop()                                                                            # end of gui program when this loop broke

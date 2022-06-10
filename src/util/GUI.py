from threading import Thread
import tkinter as tk
import os
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
# from PIL import ImageTk
from simplify import path
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
        # initializing dict of frames
        self.frames = {}
        # initializing root window
        self.root = tk.Tk()
        self.root.title("Hsu.exe")
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.working_dic = os.getcwd()
        self.api = Cv_api(self)

        self.hello()                                                                            # execute

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
        '''Let user select directory where they import data'''

        path.mov(filedialog.askdirectory(initialdir= os.getcwd()))
        self.root.stat_bar.config(text= os.getcwd())

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
        progwin.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')                                       # uses f-string mothod
        
        # connect to imported threading function from opencv.py
        import_td = Import_thread()                                                                 # create object inherited from threading
        import_td.start()                                                                           # this will start the run() method in Import_thread
        self.thread_monitor(progwin, import_td, progwin.destroy)

    def thread_monitor(self, window, thread, command):
        '''check whether the thread in window is alive, if not, run command'''

        if thread.is_alive():
            window.after(100, lambda: self.thread_monitor(window, thread, command))
        else:
            command()

    def export_setting(self):
        '''export custumization'''
        # create toplevel
        export_win = tk.Toplevel(self.root)
        export_win.title('Export settings')
        export_win.resizable(0,0)
        self.frames['export'] = export_win

        # create frame
        export_frame = Frame(export_win, fmname= 'external exports')
        self.frames['ex_export'] = export_frame
        export_frame.frame.grid(row= 0, column= 0, rowspan=2, columnspan= 2, padx= 30, pady= 10, sticky= 'W')

        # widgets in frame
        export_frame.checkbtn['gray'] = tk.BooleanVar()
        export_frame.checkbtn['blurred'] = tk.BooleanVar()
        export_frame.checkbtn['binary'] = tk.BooleanVar()
        export_frame.checkbtn['mask'] = tk.BooleanVar()
        tk.Checkbutton(export_frame.frame, text= 'gray', variable= export_frame.checkbtn['gray']).grid(row= 0, column= 0)
        tk.Checkbutton(export_frame.frame, text= 'blurred', variable= export_frame.checkbtn['blurred']).grid(row= 0, column= 1)
        tk.Checkbutton(export_frame.frame, text= 'binary', variable= export_frame.checkbtn['binary']).grid(row= 1, column= 0)
        tk.Checkbutton(export_frame.frame, text= 'mask', variable= export_frame.checkbtn['mask']).grid(row= 1, column= 1)

        # widgets on the right side of frame
        tk.Label(export_win, text= "export type:").grid(row= 0, column= 1, sticky= 'SE', padx= 50)
        export_types= ["jpg", "png"]
        export_frame.combobox['type'] = ttk.Combobox(export_win, values= export_types)
        export_frame.combobox['type'].current(0)
        export_frame.combobox['type'].grid(row= 1, column= 1, sticky= 'NE', padx= 10)

        # establish export thread
        t1 = Thread(target= self.api.export)

        # widgets below frame
        export_frame.label['destination'] = tk.Label(export_win, text = "destination:", padx= 10).grid(row= 2, column= 0)
        export_frame.btn['destination'] = tk.Button(export_win, text= self.working_dic, command = self.choose_des)
        export_frame.btn['destination'].configure(relief= tk.SUNKEN, width= 50, bg= 'White', anchor= 'w', fg= 'gray', activebackground= 'White', activeforeground= 'gray')
        export_frame.btn['destination'].grid(row= 2, column= 1, padx= 5, pady= 10)
        export_frame.btn['export'] = tk.Button(export_win, text= 'Export', bg='orange', command= lambda: [t1.start(), export_win.destroy()])   # use lambda to realize multiple commands
        export_frame.btn['export'].grid(row= 3, column= 1, sticky= 'E', padx= 10, pady= 5)

    def choose_des(self):
        '''Let user select directory where they export data'''

        wd = filedialog.askdirectory(initialdir= self.working_dic)
        if not wd:
            print("canceled")
        else:
            self.working_dic = wd
            self.frames['export'].btn['destination'].configure(text= self.working_dic)
    
    def choose_file(self, picture_cate):
        '''Choose material pictures'''
        
        filetypes = (('jpg files', '*.jpg'), ('all files', '*.*'))
        pic = filedialog.askopenfilename(initialdir= self.working_dic, filetypes= filetypes)
        if pic:
            if picture_cate == 'w':
                self.frames['init'].btn['w_img'].configure(text= pic)
            else:
                self.frames['init'].btn['f_img'].configure(text= pic)
        

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
        file_menu.add_command(label= "Export", command = self.export_setting)
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
        init.btn['w_img'] = tk.Button(init.frame, command =lambda: self.choose_file('w'))
        init.btn['w_img'].configure(relief= tk.SUNKEN, width= 20, bg= 'White', fg= 'gray', activebackground= 'White', activeforeground= 'gray')
        init.btn['w_img'].grid(row= 0, column= 1)
        tk.Label(init.frame, text = "Fluorescent image").grid(row= 1, column= 0, pady= (3,0))
        init.btn['f_img'] = tk.Button(init.frame, command =lambda: self.choose_file('f'))
        init.btn['f_img'].configure(relief= tk.SUNKEN, width= 20, bg= 'White', fg= 'gray', activebackground= 'White', activeforeground= 'gray')
        init.btn['f_img'].grid(row= 1, column= 1, pady= (3,0))

        lb = tk.Label(init.frame, text = "Optimize thereshold")
        lb.grid(row= 3, columnspan= 2, ipady= 5)
        aut = tk.Button(init.frame, text = "auto", bg="skyblue", width=8, height=2)
        aut.config(command = self.auto)
        aut.grid(row= 4, column= 0)
        mnl = tk.Button(init.frame, text = "manual", bg="#FF4D40", width=8, height=2)
        mnl.config(command = self.manual)
        mnl.grid(row= 4, column= 1)
        init.frame.rowconfigure(2, minsize= 20)
        # self.root.filename = filedialog.askopenfilename(initialdir= os.getcwd(), filetypes=(("all files", "*.*"),("jpg files", "*.jpg")))

        # initializing window position
        self.root.update_idletasks()
        cord_x = (self.root.winfo_screenwidth()-self.root.winfo_width())/2
        cord_y = (self.root.winfo_screenheight()-self.root.winfo_height())/2
        self.root.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')                                     # uses f-string mothod

if __name__ == '__main__':
    prog = Window()
    prog.root.mainloop()                                                                            # end of gui program when this loop broke

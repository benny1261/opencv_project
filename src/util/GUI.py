import tkinter as tk
import os
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkSliderWidget import Slider
from opencv import Import_thread
from opencv import Cv_api

class Frame:
    def __init__(self, window, fmname: str = None, padx= 30, pady= 30):

        self.frame =  tk.LabelFrame(window, text= fmname, padx= padx, pady= pady)
        self.btn = {}
        self.combobox = {}
        self.label = {}
        self.scaler = {}
        self.checkbtn = {}
        self.treeview = []

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

        # data
        self.img_0, self.img_1, self.img_2, self.img_3 = None, None, None, None
        self.pre_0, self.pre_1, self.pre_2, self.pre_3 = None, None, None, None
        self.df, self.result = [], []
        self.import_flag = False
        self.th_hct, self.th_wbc, self.th_round = tk.DoubleVar(value= 0.9), tk.DoubleVar(value= 0.3), tk.DoubleVar(value= 0.7)
        self.th_sharp = tk.IntVar(value= 14000)
        self.target, self.nontarget = tk.IntVar(), tk.IntVar()

        # create menu
        self.mymenu = tk.Menu(self.root)
        self.root.config(menu= self.mymenu)                                                         # bound "self.mymenu" to root window
        # create menu items
        self.file_menu= tk.Menu(self.mymenu, tearoff= 0)                                            # create "file" submenu under self.mymenu, tearoff= 0 to remove slash
        self.file_menu.add_command(label= "Home", command= lambda: self.clean(True))
        self.file_menu.add_command(label= "Choose CWD", command= self.choose_cwd)
        self.file_menu.add_command(label= "Export settings", command = self.export_setting)
        self.file_menu.add_separator()                                                              # create divider
        self.file_menu.add_command(label= "Exit", command= self.root.quit)
        self.view_menu= tk.Menu(self.mymenu, tearoff= 0)
        self.view_menu.add_command(label= "TreeView", command= self.viewer)
        self.mymenu.add_cascade(label= "File", menu= self.file_menu)
        self.mymenu.add_cascade(label= "View", menu= self.view_menu)

        # create status bar
        self.root.stat_bar = tk.Label(self.root, borderwidth= 2, relief= "sunken", text= "cwd: " + os.getcwd(), anchor= tk.E)

        # initializing home frame and its widgets
        self.home_fm = Frame(self.root, "Home", padx= 20, pady= 10)
        self.home_fm.btn['f_img'] = tk.Button(self.home_fm.frame, command= lambda: self.choose_filefolder())
        self.home_fm.btn['f_img'].configure(relief= tk.SUNKEN, width= 20, bg= 'White', fg= 'gray', activebackground= 'White', activeforeground= 'gray')        
        self.home_fm.combobox['target'] = ttk.Combobox(self.home_fm.frame, values= ["CTC", "others..."], state= 'readonly')
        self.home_fm.combobox['target'].current(0)
        self.home_fm.btn['auto'] = tk.Button(self.home_fm.frame, text = "auto", bg="skyblue", width=8, height=2, command= self.auto)
        self.home_fm.btn['manual'] = tk.Button(self.home_fm.frame, text = "manual", bg="gray", width=8, height=2,
                                            command= lambda: [self.manual(), self.fetch(0)])            # use lambda to realize multiple commands
        self.home_fm.label['target'] = tk.Label(self.home_fm.frame, textvariable= self.target)
        self.home_fm.label['nontarget'] = tk.Label(self.home_fm.frame, textvariable= self.nontarget)
        self.home_fm.btn['export'] = tk.Button(self.home_fm.frame, text= 'Export', bg='#FF4D40', command= lambda: self.api.export_td())

        # placing widgets in home frame
        tk.Label(self.home_fm.frame, text = "Fluorescent image folder").grid(row= 0, column= 0, sticky= 'W')
        self.home_fm.btn['f_img'].grid(row= 0, column= 1, columnspan= 3)
        tk.Label(self.home_fm.frame, text = "Target cell").grid(row= 1, column= 0, sticky= 'W')
        self.home_fm.combobox['target'].grid(row= 1, column= 1, columnspan= 3, pady= 5)
        self.home_fm.frame.rowconfigure(2, minsize= 10)
        tk.Label(self.home_fm.frame, text = "Optimize thereshold").grid(row= 3, columnspan= 2, ipady= 5)
        self.home_fm.btn['auto'].grid(row= 4, column= 0, rowspan= 2)
        self.home_fm.btn['manual'].grid(row= 4, column= 1, rowspan= 2, sticky= 'W', padx= 20)
        tk.Label(self.home_fm.frame, text= 'target:').grid(row= 4, column= 2, sticky= 'W')
        tk.Label(self.home_fm.frame, text= 'nontarget:').grid(row= 5, column= 2, sticky= 'W')
        self.home_fm.label['target'].grid(row= 4, column= 3)
        self.home_fm.label['nontarget'].grid(row= 5, column= 3)
        self.home_fm.frame.rowconfigure(6, minsize= 20)
        self.home_fm.btn['export'].grid(row= 7, column= 2, columnspan= 2, sticky= tk.SE)

        # initializing export window,frame and its widgets
        self.export_win = tk.Toplevel(self.root)
        self.export_win.title('Export settings')
        self.export_win.resizable(0,0)
        self.export_win.withdraw()
        self.export_win.protocol("WM_DELETE_WINDOW", self.export_win.withdraw)

        self.export_fm = Frame(self.export_win, fmname= 'export settings')
        self.export_fm.checkbtn['binary0'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['binary1'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['binary2'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['binary3'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['mark'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['mask'] = tk.BooleanVar(value= True)
        self.export_fm.checkbtn['raw_data'] = tk.BooleanVar(value= False)
        self.export_fm.checkbtn['result_data'] = tk.BooleanVar(value= True)
        self.export_fm.btn['destination'] = tk.Button(self.export_win, text= self.export_directory, command = self.choose_des)
        self.export_fm.btn['destination'].configure(relief= tk.SUNKEN, width= 50, bg= 'White', anchor= 'w', fg= 'gray', activebackground= 'White', activeforeground= 'gray')
        self.export_fm.btn['save'] = tk.Button(self.export_win, text= 'save', command= lambda: self.export_win.withdraw())

        # initializing manual frame and its widgets
        self.manual_fm = Frame(self.root, 'Manual Threshold', padx= 40, pady= 40)
        self.manual_fm.scaler['hct'] = ttk.Scale(self.manual_fm.frame, length= 600, from_= 0, to= 1, command= self.fetch, variable= self.th_hct)
        self.manual_fm.label['hct'] = tk.Label(self.manual_fm.frame, textvariable= self.th_hct)
        self.manual_fm.scaler['wbc'] = ttk.Scale(self.manual_fm.frame, length= 600, from_= 0, to= 1, command= self.fetch, variable= self.th_wbc)
        self.manual_fm.label['wbc'] = tk.Label(self.manual_fm.frame, textvariable= self.th_wbc)
        self.manual_fm.scaler['roundness'] = ttk.Scale(self.manual_fm.frame, length= 600, from_= 0, to= 1, command= self.fetch, variable= self.th_round)
        self.manual_fm.label['roundness'] = tk.Label(self.manual_fm.frame, textvariable= self.th_round)
        self.manual_fm.scaler['sharpness'] = ttk.Scale(self.manual_fm.frame, length= 600, from_= 6000, to= 20000, command= self.fetch, variable= self.th_sharp)
        self.manual_fm.label['sharpness'] = tk.Label(self.manual_fm.frame, textvariable= self.th_sharp)
        self.manual_fm.scaler['diameter'] = Slider(self.manual_fm.frame, width= 600, height= 40, min_val= 0, max_val= 50, init_lis=[10, 27],
                                            show_value= True, removable= False, addable= False)
        self.manual_fm.scaler['diameter'].setValueChageCallback(lambda vals: self.fetch(vals))
        self.manual_monitor = Frame(self.manual_fm.frame, 'monitor')
        self.manual_monitor.label['target'] = tk.Label(self.manual_monitor.frame, textvariable= self.target)
        self.manual_monitor.label['nontarget'] = tk.Label(self.manual_monitor.frame, textvariable= self.nontarget)

        # placing widgets in manual frame
        tk.Label(self.manual_fm.frame, text= 'hoechst').grid(row= 0, column= 0, sticky= 'W')
        self.manual_fm.scaler['hct'].grid(row= 0, column = 1)
        self.manual_fm.label['hct'].grid(row= 1, column= 1)
        tk.Label(self.manual_fm.frame, text= 'wbc').grid(row= 2, column= 0, sticky= 'W')
        self.manual_fm.scaler['wbc'].grid(row= 2, column = 1)
        self.manual_fm.label['wbc'].grid(row= 3, column= 1)
        tk.Label(self.manual_fm.frame, text= 'roundness').grid(row= 4, column= 0, sticky= 'W')
        self.manual_fm.scaler['roundness'].grid(row= 4, column = 1)
        self.manual_fm.label['roundness'].grid(row= 5, column= 1)
        tk.Label(self.manual_fm.frame, text= 'sharpness').grid(row= 6, column= 0, sticky= 'W')
        self.manual_fm.scaler['sharpness'].grid(row= 6, column = 1)
        self.manual_fm.label['sharpness'].grid(row= 7, column= 1)
        tk.Label(self.manual_fm.frame, text= 'diameter').grid(row= 8, column= 0, sticky= 'W')
        self.manual_fm.scaler['diameter'].grid(row= 8, column = 1)
        self.manual_monitor.frame.grid(rowspan= 9, row= 0, column= 2, padx= 10, sticky= 'NE')
        tk.Label(self.manual_monitor.frame, text= 'target:').grid(row= 0, column= 0, sticky= 'W')
        tk.Label(self.manual_monitor.frame, text= 'nontarget:').grid(row= 1, column= 0, sticky= 'W')
        self.manual_monitor.label['target'].grid(row= 0, column= 1)
        self.manual_monitor.label['nontarget'].grid(row= 1, column= 1)

        # initializing view frame and its widgets
        self.view_fm = Frame(self.root, 'tree view', padx= 10, pady= 10)
        self.view_fm.treeview = ttk.Treeview(self.view_fm.frame)
        # define columns
        self.view_fm.treeview['columns'] = ("ID", "hct", "wbc", "roundness", "sharpness", "size")
        self.view_fm.treeview.column("#0", width= 0, stretch= False)
        self.view_fm.treeview.column("ID", anchor= 'w', width= 50)
        self.view_fm.treeview.column("hct", anchor= 'w', width= 100)
        self.view_fm.treeview.column("wbc", anchor= 'w', width= 100)
        self.view_fm.treeview.column("roundness", anchor= 'w', width= 100)
        self.view_fm.treeview.column("sharpness", anchor= 'w', width= 100)
        self.view_fm.treeview.column("size", anchor= 'w', width= 100)
        # create headings
        self.view_fm.treeview.heading("#0", text= "")
        self.view_fm.treeview.heading("ID", text= "ID", anchor= 'w')
        self.view_fm.treeview.heading("hct", text= "hct", anchor= 'w')
        self.view_fm.treeview.heading("wbc", text= "wbc", anchor= 'w')
        self.view_fm.treeview.heading("roundness", text= "roundness", anchor= 'w')
        self.view_fm.treeview.heading("sharpness", text= "sharpness", anchor= 'w')
        self.view_fm.treeview.heading("size", text= "size", anchor= 'w')

        self.zoom_fm = Frame(self.root, 'zoom view', padx= 20, pady= 20)

        # placing widgets in view frame
        self.view_fm.treeview.pack()

        # place home frame
        self.home_fm.frame.grid(row= 0, column= 0, padx= 10, pady= 5)
        # place status bar in root
        self.root.stat_bar.grid(row= 1, column= 0, sticky="W"+"E")

        # initializing window position
        self.root.update_idletasks()
        cord_x = (self.root.winfo_screenwidth()-self.root.winfo_width())/2
        cord_y = (self.root.winfo_screenheight()-self.root.winfo_height())/2
        self.root.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')                                     # uses f-string method


    def auto(self):
        self.home_fm.btn['auto'].configure(bg= 'skyblue')
        self.home_fm.btn['manual'].configure(bg= 'gray')
        if self.import_flag:
            self.result = self.api.analysis(self.df)
            y, n = self.api.count_target(self.result)
            self.target.set(y)
            self.nontarget.set(n)

    def fetch(self, var):                           # var is the value of scalebar
        if self.import_flag:
            self.result = self.api.analysis(self.df, hct_thres= self.th_hct.get(), wbc_thres= self.th_wbc.get(), roundness_thres= self.th_round.get(),
                            sharpness_thres= self.th_sharp.get(), diameter_thres= self.manual_fm.scaler['diameter'].getValues())
            y, n = self.api.count_target(self.result)
            self.target.set(y)
            self.nontarget.set(n)

    def viewer(self):
        self.clean()
        self.view_fm.frame.grid(row= 0, column= 0)

    def on_closing(self):
        '''Command triggered when user close window directly'''

        if messagebox.askokcancel("quit", "Confirm quit?"):
            self.root.quit()

    def clean(self, home= False):
        '''return frame to home page'''
        for children in self.root.winfo_children():
            if children is not self.root.stat_bar:
                try:
                    children.grid_forget()
                except:
                    children.withdraw()                                                             # in case children is a toplevel
        if home:
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

            self.import_flag = thread.flag
            # showing success or not
            if thread.flag:
                self.home_fm.btn['export'].configure(bg='#82D900')

                # pass data after thread closed
                self.img_0, self.img_1, self.img_2, self.img_3 = thread.img_0, thread.img_1, thread.img_2, thread.img_3
                self.pre_0, self.pre_1, self.pre_3 = thread.pre_0, thread.pre_1, thread.pre_3
                self.df = thread.df

                # update result in home frame
                self.auto()
            else:
                self.home_fm.btn['export'].configure(bg='#FF4D40')
                self.target.set(0)
                self.nontarget.set(0)

    def export_setting(self):
        '''export custumization'''

        self.export_fm.btn['destination'].configure(text= self.export_directory)
        self.export_win.deiconify()                                                             # show the window

        # place frame
        self.export_fm.frame.grid(row= 0, column= 0, columnspan= 2, padx= 30, pady= 10, sticky= tk.W)

        # place widgets in frame
        tk.Checkbutton(self.export_fm.frame, text= 'binary0', variable= self.export_fm.checkbtn['binary0']).grid(row= 0, column= 0)
        tk.Checkbutton(self.export_fm.frame, text= 'binary1', variable= self.export_fm.checkbtn['binary1']).grid(row= 0, column= 1)
        tk.Checkbutton(self.export_fm.frame, text= 'binary2', variable= self.export_fm.checkbtn['binary2']).grid(row= 1, column= 0)
        tk.Checkbutton(self.export_fm.frame, text= 'binary3', variable= self.export_fm.checkbtn['binary3']).grid(row= 1, column= 1)
        tk.Checkbutton(self.export_fm.frame, text= 'mark', variable= self.export_fm.checkbtn['mark']).grid(row= 0, column= 2)
        tk.Checkbutton(self.export_fm.frame, text= 'mask', variable= self.export_fm.checkbtn['mask']).grid(row= 1, column= 2)
        tk.Checkbutton(self.export_fm.frame, text= 'raw data', variable= self.export_fm.checkbtn['raw_data']).grid(row= 0, column= 3)
        tk.Checkbutton(self.export_fm.frame, text= 'result data', variable= self.export_fm.checkbtn['result_data']).grid(row= 1, column= 3)

        # widgets below frame
        tk.Label(self.export_win, text = "destination:", padx= 10).grid(row= 1, column= 0)
        self.export_fm.btn['destination'].grid(row= 1, column= 1, padx= 5, pady= 10)
        self.export_fm.btn['save'].grid(row= 2, column= 1, sticky= 'E', padx= 10, pady= 5)

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
            import_td = Import_thread(folder)                              # create class inherited from threading, initialize each time when choosing folder

            # create progress bar toplevel
            progwin = tk.Toplevel(self.root)
            progwin.title('Importing and preprocessing...')
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
            import_td.start()                                                   # this will start the run() method in Import_thread
            self.thread_monitor(progwin, import_td, progwin.destroy)

            self.home_fm.btn['f_img'].configure(text= os.path.basename(os.path.normpath(folder)))
            self.export_directory = self.temp_directory

    def manual(self):
        '''Manual adjusting threshold'''

        # switching frames
        self.home_fm.frame.grid_forget()
        self.manual_fm.frame.grid(row= 0, column= 0, padx= 10, pady= 5)

        # change button color
        self.home_fm.btn['auto'].configure(bg= 'gray')
        self.home_fm.btn['manual'].configure(bg= 'skyblue')


if __name__ == '__main__':
    prog = Window()
    prog.root.mainloop()                                                                            # end of gui program when this loop broke

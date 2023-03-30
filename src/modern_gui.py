import customtkinter as ctk
import tkinter as tk
from customtkinter import ThemeManager
import os
from PIL import Image, ImageTk
from tkinter import filedialog
import pandas as pd
from util.opencv import Import_thread, Cv_api, Preprocess_thread, PROTOCOL_THRES, PROTOCOL_NAME, ROUNDNESS_THRESHOLD, SHARPNESS_THRESHOLD, DIAMETER_THRESHOLD
import util.opencv as ccv
from util.tkSliderWidget import Slider
from pandastable.core import Table, config, RowHeader, IndexHeader, ColumnHeader, ToolBar, statusBar
from pandastable.dialogs import applyStyle, AutoScrollbar
from pandastable.util import check_multiindex
from pandastable.headers import createSubMenu
from pandastable.data import TableModel

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hsu project.py")
        self.api = Cv_api(self)

        # classwise variables
        self.cwd = ctk.StringVar(value= os.getcwd())
        self.data_dir = ctk.StringVar()
        self.export_dir = ctk.StringVar()

        self.imgs = (None, None, None, None)
        self.pres = (None, None, None, None)
        self.import_flag, self.preprocess_flag = False, False
        self.df, self.result = pd.DataFrame(), pd.DataFrame()

        # initializing window position to screen center
        min_width, min_height = 720, 450
        self.geometry(f'{min_width}x{min_height}')
        self.minsize(width= min_width, height= min_height)
        cord_x = (self.winfo_screenwidth()-min_width)/2
        cord_y = (self.winfo_screenheight()-min_height)/2        
        self.geometry(f'+{int(cord_x)}+{int(cord_y)}')          # The reason why we can't get normal self.winfo_geometry() is unknown

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # set init dark mode
        ctk.set_appearance_mode('dark')

        # load icons with light and dark mode image
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "logo_icon.png")), size=(30, 30))
        self.large_test_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "logo_icon.png")), size=(500, 150))
        self.image_icon_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "logo_icon.png")), size=(20, 20))
        self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "home_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "home_dark.png")), size=(20, 20))
        self.filter_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "filter_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "filter_dark.png")), size=(20, 20))
        self.examine_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "examine_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "examine_dark.png")), size=(20, 20))
        self.export_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "export_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "export_dark.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight= 1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text= "  Cell Counter", image= self.logo_image,
                                                compound="left", font=ctk.CTkFont(size= 20, weight= "bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        navigation_font = ctk.CTkFont(size= 15, weight= 'bold', slant= 'roman')
        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Home", font= navigation_font,
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.home_image, anchor="w", command= lambda :self.select_frame_by_name("home"))
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.filter_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Filter", font= navigation_font,
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.filter_image, anchor="w", command= lambda :self.select_frame_by_name("filter"))
        self.filter_button.grid(row=2, column=0, sticky="ew")

        self.examine_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Examine", font= navigation_font,
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.examine_image, anchor="w", command= lambda :self.select_frame_by_name("examine"))
        self.examine_button.grid(row=3, column=0, sticky="ew")

        self.exportf_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Export", font= navigation_font,
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.export_image, anchor="w", command= lambda :self.select_frame_by_name("export"))
        self.exportf_button.grid(row=4, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"],
                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(1, weight= 1)          # make column width able to fill all space

        self.home_frame_cwd_label = ctk.CTkLabel(self.home_frame, text= "CWD")
        self.home_frame_cwd_label.grid(row=0, column=0, padx=20, pady=20, sticky= 'w')
        self.home_frame_cwd = ctk.CTkButton(self.home_frame, width= 360, text= self.cwd, fg_color= ThemeManager.theme["CTkEntry"]["fg_color"],
                            text_color= ("#C6A300", "#977C00"), border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                            border_width= ThemeManager.theme["CTkEntry"]["border_width"], corner_radius= ThemeManager.theme["CTkEntry"]["corner_radius"],
                            hover_color= ("gray80", "gray30"), textvariable= self.cwd, command= self.choose_cwd)
        self.home_frame_cwd.grid(row=0, column=1, padx=(0, 20), pady=20, sticky= 'we')

        self.home_frame_src_label = ctk.CTkLabel(self.home_frame, text= "Image Folder")
        self.home_frame_src_label.grid(row=1, column=0, padx=20, pady=20, sticky= 'w')
        self.home_frame_src = ctk.CTkButton(self.home_frame, width= 360, text= self.data_dir, fg_color= ThemeManager.theme["CTkEntry"]["fg_color"],
                            text_color= ("#C6A300", "#977C00"), border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                            border_width= ThemeManager.theme["CTkEntry"]["border_width"], corner_radius= ThemeManager.theme["CTkEntry"]["corner_radius"],
                            hover_color= ("gray80", "gray30"), textvariable= self.data_dir, command= self.choose_filefolder)
        self.home_frame_src.grid(row=1, column=1, padx=(0, 20), pady=20, sticky= 'we')

        type_list = list(PROTOCOL_NAME.keys())
        type_list.insert(0,'None')
        self.home_frame_type_label = ctk.CTkLabel(self.home_frame, text= "Target Type")
        self.home_frame_type_label.grid(row=2, column=0, padx=20, pady=20, sticky= 'e')
        self.home_frame_type = ctk.CTkOptionMenu(self.home_frame, values= type_list, state= 'disabled', command= self.change_type)
        self.home_frame_type.grid(row=2, column=1, padx=0, pady=20, sticky= 'w')

        # create filter frame
        self.filter_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.filter_frame.grid_rowconfigure(0, weight= 1)
        self.filter_frame.grid_columnconfigure(0, weight= 1)
        self.filter_tab = MyTabView(self.filter_frame, self)
        self.filter_tab.grid(row= 0, column= 0, sticky= 'nsew', padx= 10, pady= 10)

        # create examine frame
        self.examine_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.table = MyTable(self.examine_frame, master = self)
        self.table.show()

        # create export frame
        self.export_frame = ExportFrame(self)

        # select default frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.filter_button.configure(fg_color=("gray75", "gray25") if name == "filter" else "transparent")
        self.examine_button.configure(fg_color=("gray75", "gray25") if name == "examine" else "transparent")
        self.exportf_button.configure(fg_color=("gray75", "gray25") if name == "export" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "filter":
            self.filter_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.filter_frame.grid_forget()
        if name == "examine":
            self.examine_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.examine_frame.grid_forget()
        if name == "export":
            self.export_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.export_frame.grid_forget()

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def choose_cwd(self):
        '''Let user select directory where they import data'''

        _ = filedialog.askdirectory(initialdir= self.cwd.get())
        if _:
            self.cwd.set(_)
            os.chdir(_)
    
    def choose_filefolder(self):
        '''Choose material pictures'''
        
        folder = filedialog.askdirectory(initialdir= self.cwd.get())   
        if folder:
            self.data_dir.set(folder)
            import_td = Import_thread(folder)                              # create class inherited from threading, initialize each time when choosing folder

            # create progress bar toplevel
            progwin = ToplevelProgressBar(self)
            progwin.title('Importing')
            
            # connect to imported threading function from opencv.py
            import_td.start()                                               # this will start the run() method in Import_thread
            self.thread_monitor(progwin, import_td, lambda: self.after_import(import_td))

            if self.export_frame.destination_switch.get():
                self.export_dir.set(self.data_dir.get())

    def change_type(self, event):
        '''preprocess + update widgets'''

        self.filter_tab.on_update_types(event)
        if event == 'None':
            # clear previous data and update table
            self.df, self.result = pd.DataFrame(), pd.DataFrame()
            self.table.storeCurrent()
            self.table.updateModel(TableModel(rows=20,columns=5))
            # self.table.redrawVisible()
            self.table.redraw()

            # disable widgets as same as preprocess not successful
            self.export_frame.button.configure(state= 'disabled')
            self.filter_tab.target.set(0)
            self.filter_tab.nontarget.set(0)
        else:
            pre_td = Preprocess_thread(event, *self.imgs)

            progwin = ToplevelProgressBar(self)
            progwin.title('preprocessing...')

            # connect to imported threading function from opencv.py
            pre_td.start()
            self.thread_monitor(progwin, pre_td, lambda: self.after_preprocess(pre_td))

    def thread_monitor(self, window, thread, command):
        '''check whether the thread in window is alive, if not, run command'''

        if thread.is_alive():
            window.after(100, lambda: self.thread_monitor(window, thread, command))
        else:
            window.destroy()
            command()

    def after_import(self, thread):

        self.import_flag= thread.flag
        # showing success or not
        if self.import_flag:
            self.home_frame_src.configure(text_color= ("#C6A300", "#977C00"), border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                                            fg_color= ThemeManager.theme["CTkEntry"]["fg_color"])
            self.home_frame_type.configure(state= 'normal')

            # pass data after thread closed
            self.imgs = thread.imgs

        else:
            self.home_frame_src.configure(text_color= ("#CE0000", "#750000"), border_color= "#AD5A5A", fg_color= ("#FFD2D2", "#743A3A"))
            self.home_frame_type.configure(state= 'disabled')
            self.export_frame.button.configure(state= 'disabled')
            self.filter_tab.target.set(0)
            self.filter_tab.nontarget.set(0)

            # shut down preprocess flag as well
            self.preprocess_flag = self.import_flag

    def after_preprocess(self, thread):

        self.preprocess_flag= thread.flag
        # showing success or not
        if self.preprocess_flag:
            self.export_frame.button.configure(state= 'normal')

            # pass data after thread closed
            self.pres = thread.pres
            self.df = thread.df

            # update result in home frame
            self.filter_tab.auto()          # table data updated in auto()
        
        else:
            self.export_frame.button.configure(state= 'disabled')
            self.filter_tab.target.set(0)
            self.filter_tab.nontarget.set(0)

    def choose_des(self):
        '''Let user select directory where they export data'''

        des = filedialog.askdirectory(initialdir= os.getcwd())
        if des:
            self.export_dir.set(des)

    def destination_toggle(self):
        if self.export_frame.destination_switch.get():
            self.export_frame.destination_button.configure(state= "disabled")
            self.export_dir.set(self.data_dir.get())
        else:
            self.export_frame.destination_button.configure(state= "normal")


class FlipSwitch(ctk.CTkSwitch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0, minsize=self._apply_widget_scaling(6))
        self._text_label.grid(row=0, column=0)
        self._canvas.grid(row=0, column=1, sticky= "e")


class MyTabView(ctk.CTkTabview):
    def __init__(self, master, main_program, **kwargs):
        super().__init__(master, command= self.switch_tab, **kwargs)
        self.root = main_program
        self.th_scaler = {}
        self.th_var = [ctk.DoubleVar(), ctk.DoubleVar(), ctk.DoubleVar(), ctk.DoubleVar()]
        self.th_round = ctk.DoubleVar(value= ROUNDNESS_THRESHOLD)
        self.th_sharp = ctk.IntVar(value= SHARPNESS_THRESHOLD)
        self.target, self.nontarget= ctk.IntVar(), ctk.IntVar()
        self.FIXED_NUM = 3
        self.FIXED_MANUAL = self.FIXED_NUM*2-1

        self.add('auto')
        self.add('manual')
        self.tab("auto").grid_rowconfigure(tuple(range(self.FIXED_NUM)), weight= 1)
        self.tab("auto").grid_columnconfigure(0, weight= 1)
        self.tab("manual").grid_columnconfigure(1, weight= 1)
        self.tab("manual").grid_rowconfigure(self.FIXED_MANUAL, weight= 1)                      # need to be moved downwards if add more scalers

        ctk.CTkLabel(self.tab("auto"), text= f'roundness threshold: {ROUNDNESS_THRESHOLD}', anchor= 'w').grid(row= 0, column= 0, sticky= 'we')
        ctk.CTkLabel(self.tab("auto"), text= f'sharpness threshold: {SHARPNESS_THRESHOLD}', anchor= 'w').grid(row= 1, column= 0, sticky= 'we')
        ctk.CTkLabel(self.tab("auto"), text= f'diameter threshold: {DIAMETER_THRESHOLD}', anchor= 'w').grid(row= 2, column= 0, sticky= 'we')
        ctk.CTkLabel(self.tab("auto"), text= 'target:', text_color= ("#C6A300", "#977C00")).grid(row= 0, column= 1)
        ctk.CTkLabel(self.tab("auto"), textvariable= self.target, text_color= ("#C6A300", "#977C00")).grid(row= 0, column= 2, padx= 10)
        ctk.CTkLabel(self.tab("auto"), text= 'nontarget:', text_color= ("#C6A300", "#977C00")).grid(row= 1, column= 1)
        ctk.CTkLabel(self.tab("auto"), textvariable= self.nontarget, text_color= ("#C6A300", "#977C00")).grid(row= 1, column= 2)

        ctk.CTkLabel(self.tab("manual"), text= 'roundness').grid(row= 0, column= 0, sticky= 'w')
        self.roundness_scaler = ctk.CTkSlider(self.tab("manual"), from_= 0, to= 1, command= self.fetch, variable= self.th_round)
        self.roundness_scaler.grid(row= 0, column= 1, sticky= 'we')
        self.roundness_number = ctk.CTkLabel(self.tab("manual"), textvariable= self.th_round).grid(row= 1, column= 1, sticky= 'we')
        ctk.CTkLabel(self.tab("manual"), text= 'sharpness').grid(row= 2, column= 0, sticky= 'w')
        self.sharpness_scaler = ctk.CTkSlider(self.tab("manual"), from_= 6000, to= 20000, command= self.fetch, variable= self.th_sharp)
        self.sharpness_scaler.grid(row= 2, column= 1, sticky= 'we')
        self.sharpness_number = ctk.CTkLabel(self.tab("manual"), textvariable= self.th_sharp).grid(row= 3, column= 1, sticky= 'we')
        ctk.CTkLabel(self.tab("manual"), text= 'diameter').grid(row= 4, column= 0, sticky= 'w')
        self.diameter_scaler = Slider(self.tab("manual"), width= 500, height= 40, min_val= 0, max_val= 60,
                                      init_lis=[DIAMETER_THRESHOLD[0],DIAMETER_THRESHOLD[1]], show_value= True)
        self.diameter_scaler.setValueChageCallback(lambda vals: self.fetch(vals))
        self.diameter_scaler.grid(row= 4, column= 1, sticky= 'we')

        self.monitor_frame = ctk.CTkFrame(self.tab("manual"), fg_color= 'transparent')
        self.monitor_frame.grid_rowconfigure(0, weight= 1)
        self.monitor_frame.grid_columnconfigure(tuple(range(4)), weight= 1)
        self.monitor_frame.grid(row= self.FIXED_MANUAL, columnspan= 2, sticky= 'nsew')          # need to be moved downwards if add more scalers
        ctk.CTkLabel(self.monitor_frame, text= 'target:', text_color= ("#C6A300", "#977C00")).grid(row= 0, column= 0, sticky= 'e')
        ctk.CTkLabel(self.monitor_frame, textvariable= self.target, text_color= ("#C6A300", "#977C00")).grid(row= 0, column= 1, padx= 10, sticky= 'w')
        ctk.CTkLabel(self.monitor_frame, text= 'nontarget:', text_color= ("#C6A300", "#977C00")).grid(row= 0, column= 2, sticky= 'e')
        ctk.CTkLabel(self.monitor_frame, textvariable= self.nontarget, text_color= ("#C6A300", "#977C00")).grid(row= 0, column= 3, padx= 10, sticky= 'w')

    def on_update_types(self, cell_type):

        if cell_type == 'None':
            dynamic_rows = 0
        else:
            dynamic_rows = len([x for x in PROTOCOL_THRES[cell_type] if x is not None])

        current_rows_a = self.tab("auto").grid_size()[1]
        current_rows_m = self.tab("manual").grid_size()[1]

        # kill all widgets in dynamic rows
        for row_indexes in range(self.FIXED_NUM, current_rows_a):
            for widget in self.tab("auto").grid_slaves(row=row_indexes):
                widget.destroy()
                self.tab("auto").grid_rowconfigure(row_indexes, weight= 0)
            
        for row_indexes in range(self.FIXED_MANUAL, current_rows_m):
            for widget in self.tab("manual").grid_slaves(row=row_indexes):
                if row_indexes == current_rows_m - 1:                       # monitor frame
                    widget.grid_forget()            
                else:
                    widget.destroy()
                self.tab("manual").grid_rowconfigure(row_indexes, weight= 0)

        self.tab("auto").grid_rowconfigure(tuple(range(self.FIXED_NUM + dynamic_rows)), weight= 1)
        self.tab("manual").grid_rowconfigure(self.FIXED_MANUAL+dynamic_rows*2, weight= 1)
        self.monitor_frame.grid(row= self.FIXED_MANUAL+dynamic_rows*2, columnspan= 2, sticky= 'nsew')
        if cell_type != 'None':
            # rebuild dynamic rows
            count = 0
            for i in range(4):
                if PROTOCOL_THRES[cell_type][i] is not None:            # i is index of channel
                    label = ctk.CTkLabel(self.tab("auto"), text= PROTOCOL_NAME[cell_type][i]+' threshold: '+str(PROTOCOL_THRES[cell_type][i]), anchor= 'w')
                    label.grid(row= self.FIXED_NUM+count, column= 0, sticky= 'we')

                    self.th_var[i].set(PROTOCOL_THRES[cell_type][i])
                    ctk.CTkLabel(self.tab("manual"), text= PROTOCOL_NAME[cell_type][i]).grid(row= self.FIXED_MANUAL+ count*2, column= 0, sticky= 'w')
                    self.th_scaler[i] = ctk.CTkSlider(self.tab("manual"), from_= 0, to= 1, command= self.fetch, variable= self.th_var[i])
                    self.th_scaler[i].grid(row= self.FIXED_MANUAL+ count*2, column= 1, sticky= 'we')
                    ctk.CTkLabel(self.tab("manual"), textvariable= self.th_var[i]).grid(row= self.FIXED_MANUAL+ count*2+ 1, column= 1, sticky= 'we')
                    count+=1

    def fetch(self, var):                           # var is the value of scalebar
        if self.root.preprocess_flag:
            cell_type = self.root.home_frame_type.get()
            inter_thres = (self.th_var[0].get(), self.th_var[1].get(), self.th_var[2].get(), self.th_var[3].get())
            self.root.result = ccv.analysis(cell_type, self.root.df, inter_thres, roundness_thres= self.th_round.get(),
                                            sharpness_thres= self.th_sharp.get(), diameter_thres= self.diameter_scaler.getValues())
            y, n = ccv.count_target(self.root.result)
            self.target.set(y)
            self.nontarget.set(n)

            self.root.table.update_table_data()

    def auto(self):

        if self.root.preprocess_flag:
            cell_type = self.root.home_frame_type.get()
            self.root.result = ccv.analysis(cell_type, self.root.df, PROTOCOL_THRES[cell_type])
            y, n = ccv.count_target(self.root.result)
            self.target.set(y)
            self.nontarget.set(n)

            self.root.table.update_table_data()

    def switch_tab(self):
        if self.get() == "auto":
            self.auto()
        elif self.get() == "manual":
            self.fetch(0)


class ExportFrame(ctk.CTkFrame):
    def __init__(self, master, corner_radius= 0, fg_color= "transparent", **kwargs):
        super().__init__(master, corner_radius= corner_radius, fg_color= fg_color, **kwargs)

        self.grid_rowconfigure(0, weight= 2)
        self.grid_rowconfigure(1, weight= 1)
        self.grid_columnconfigure(1, weight= 1)
        self.setting_frame = ctk.CTkFrame(self, corner_radius= 20)
        self.setting_frame.grid(row= 0, column= 0, rowspan= 2, padx= (20, 10), pady= 20, sticky= 'nsew')
        self.destination_frame = ctk.CTkFrame(self, corner_radius= 20)
        self.destination_frame.grid(row= 0, column= 1, padx= (10, 20), pady= (20, 0), sticky= 'nsew')
        self.button = ctk.CTkButton(self, text= 'export ', state= 'disabled', font= ctk.CTkFont(size= 40, weight= 'bold', slant= 'italic'),
                                           text_color_disabled= "#930000", text_color= "#01B468",  corner_radius= 10, command= master.api.export_td)
        self.button.grid(row= 1, column= 1, padx= 60, pady= 60, sticky= 'nsew')

        # export setting widgets
        self.setting_frame.grid_columnconfigure(0, weight= 1)
        self.setting_frame.grid_rowconfigure(tuple(range(7)), weight= 1)
        self.binary0_switch = FlipSwitch(self.setting_frame, text= 'binary 0')
        self.binary1_switch = FlipSwitch(self.setting_frame, text= 'binary 1')
        self.binary2_switch = FlipSwitch(self.setting_frame, text= 'binary 2')
        self.binary3_switch = FlipSwitch(self.setting_frame, text= 'binary 3')
        self.mask_switch = FlipSwitch(self.setting_frame, text= 'mask')
        self.mask_switch.select()
        self.raw_data_switch = FlipSwitch(self.setting_frame, text= 'raw data')
        self.result_data_switch = FlipSwitch(self.setting_frame, text= 'result')
        self.binary0_switch.grid(row = 0, column = 0, padx= 10, pady= (30, 0))
        self.binary1_switch.grid(row = 1, column = 0)
        self.binary2_switch.grid(row = 2, column = 0)
        self.binary3_switch.grid(row = 3, column = 0)
        self.mask_switch.grid(row = 4, column = 0)
        self.raw_data_switch.grid(row = 5, column = 0)
        self.result_data_switch.grid(row = 6, column = 0, pady= (0, 30))

        # export destination widgets
        self.destination_frame.grid_columnconfigure(1, weight= 1)
        self.destination_frame.grid_rowconfigure(tuple(range(2)), weight= 1)
        self.destination_switch = FlipSwitch(self.destination_frame, text= 'same as source directory', command= master.destination_toggle)
        self.destination_switch._text_label.grid_configure(padx= (0, 5))
        self.destination_switch.select()
        self.destination_switch.grid(row= 0, columnspan= 2, pady= (40, 0))
        self.destination_label = ctk.CTkLabel(self.destination_frame, text= "export folder")
        self.destination_label.grid(row= 1, column= 0, padx= 10, pady= (0, 40), sticky= 'e')
        self.destination_button = ctk.CTkButton(self.destination_frame, text= master.export_dir, fg_color= ThemeManager.theme["CTkEntry"]["fg_color"],
                    text_color= ("#C6A300", "#977C00"), border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                    border_width= ThemeManager.theme["CTkEntry"]["border_width"], corner_radius= ThemeManager.theme["CTkEntry"]["corner_radius"],
                    hover_color= ("gray80", "gray30"), textvariable= master.export_dir, command= master.choose_des, state= 'disabled')
        self.destination_button.grid(row= 1, column= 1, padx= (0, 10), pady= (0, 40), sticky= 'we')


class ToplevelProgressBar(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.resizable(0,0)
        self.attributes('-topmost', 'true')

        # progress bar widget
        progbar = ctk.CTkProgressBar(self, mode= "indeterminate")
        progbar.start()
        progbar.pack(padx= 20, pady= 10)

        # initializing bar position
        cord_x = self.master.winfo_x()+(self.master.winfo_width()-self.winfo_width())/2
        cord_y = self.master.winfo_y()+(self.master.winfo_height()-self.winfo_height())/2
        self.geometry(f'+{int(cord_x)}+{int(cord_y)}')              # uses f-string mothod


class MyTable(Table):
    def __init__(self, parent=None, model=None, dataframe=None, width=None, height=None, rows=20, cols=5,
                 showtoolbar=False, showstatusbar=True, editable=False, enable_menus=True, master = None, **kwargs):       # add master myself
        super().__init__(parent, model, dataframe, width, height, rows, cols, showtoolbar, showstatusbar, editable, enable_menus, **kwargs)

        self.master = master
        self.bind("<Alt-Button-1>",self.handle_left_alt_click)
        self.bind("<Alt-Button-3>", self.handle_right_alt_click)

        self.setTheme('dark')
        options = {
        # 'align': 'w',
        # 'cellbackgr': '#F4F4F3',
        # 'cellwidth': 80,
        # 'floatprecision': 2,
        # 'font': 'Arial',
        # 'fontsize': 12,
        # 'fontstyle': '',
        # 'grid_color': '#ABB1AD',
        # 'linewidth': 1,
        # 'rowheight': 22,
        # 'textcolor': 'black'
        'rowselectedcolor': '#313300',
        # 'boxoutlinecolor' : 'white',
        'showindex': True     # make header of row is the number of index
        }
        config.apply_options(options, self)
        self.toggle_color = '#A5A552'
        self.toggled_cell = []
        self.viewer = None

    def redrawVisible(self, event=None, callback=None):
        """Overridden function, custumized to make textcolor in toggled cell not covered by redrawing
        """

        if not hasattr(self, 'colheader'):
            return
        model = self.model
        self.rows = len(self.model.df.index)
        self.cols = len(self.model.df.columns)
        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect','colrect')
            self.delete('currentrect','fillrect')
            self.delete('gridline','text')
            self.delete('multicellrect','multiplesel')
            self.delete('colorrect')
            self.setColPositions()
            if self.cols == 0:
                self.colheader.redraw()
            if self.rows == 0:
                self.visiblerows = []
                self.rowheader.redraw()
            return
        self.tablewidth = (self.cellwidth) * self.cols
        self.configure(bg=self.cellbackgr)
        self.setColPositions()

        #are we drawing a filtered subset of the recs?
        if self.filtered == True:
            self.delete('colrect')

        self.rowrange = list(range(0,self.rows))
        self.configure(scrollregion=(0,0, self.tablewidth+self.x_start,
                        self.rowheight*self.rows+10))

        x1, y1, x2, y2 = self.getVisibleRegion()
        startvisiblerow, endvisiblerow = self.getVisibleRows(y1, y2)
        self.visiblerows = list(range(startvisiblerow, endvisiblerow))
        startvisiblecol, endvisiblecol = self.getVisibleCols(x1, x2)
        self.visiblecols = list(range(startvisiblecol, endvisiblecol))

        self.drawGrid(startvisiblerow, endvisiblerow)
        align = self.align
        self.delete('fillrect')
        bgcolor = self.cellbackgr
        df = self.model.df

        prec = self.floatprecision
        rows = self.visiblerows
        for col in self.visiblecols:
            coldata = df.iloc[rows,col]
            colname = df.columns[col]
            cfa = self.columnformats['alignment']
            if colname in cfa:
                align = cfa[colname]
            else:
                align = self.align
            if prec != 0:
                if coldata.dtype == 'float64':
                    coldata = coldata.apply(lambda x: self.setPrecision(x, prec), 1)
            coldata = coldata.astype(object).fillna('')
            offset = rows[0]
            for row in self.visiblerows:
                text = coldata.iloc[row-offset]
                # modified chunk ##################
                if (row, col) in self.toggled_cell:
                    self.drawText(row, col, text, align, self.toggle_color)
                else:
                    self.drawText(row, col, text, align, self.textcolor)
                ###################################

        self.colorColumns()
        self.colorRows()
        self.colheader.redraw(align=self.align)
        self.rowheader.redraw()
        self.rowindexheader.redraw()
        self.drawSelectedRow()
        self.drawSelectedRect(self.currentrow, self.currentcol)

        if len(self.multiplerowlist)>1:
            self.rowheader.drawSelectedRows(self.multiplerowlist)
            self.drawMultipleRows(self.multiplerowlist)
            self.drawMultipleCells()

        self.drawHighlighted()
        return

    class AdjColumnHeader(ColumnHeader):
        '''adjust function in ColumnHeader module'''
        def __init__(self, parent=None, table=None, bg='gray25'):
            super().__init__(parent, table, bg)
        
        def popupMenu(self, event):
            """Add left and right click behaviour for column header"""

            df = self.table.model.df
            if len(df.columns)==0:
                return
            ismulti = check_multiindex(df.columns)
            colname = str(df.columns[self.table.currentcol])
            currcol = self.table.currentcol
            multicols = self.table.multiplecollist
            colnames = list(df.columns[multicols])[:4]
            colnames = [str(i)[:20] for i in colnames]
            if len(colnames)>2:
                colnames = ','.join(colnames[:2])+'+%s others' %str(len(colnames)-2)
            else:
                colnames = ','.join(colnames)
            popupmenu = tk.Menu(self, tearoff = 0)
            def popupFocusOut(event):
                popupmenu.unpost()

            # columncommands = {"Rename": self.renameColumn,
            #                 "Add": self.table.addColumn,
            #                 #"Delete": self.table.deleteColumn,
            #                 "Copy": self.table.copyColumn,
            #                 "Move to Start": self.table.moveColumns,
            #                 "Move to End": lambda: self.table.moveColumns(pos='end')
            #                 }
            formatcommands = {'Set Color': self.table.setColumnColors,
                            'Color by Value': self.table.setColorbyValue,
                            'Alignment': self.table.setAlignment,
                            # 'Wrap Header' : self.table.setWrap
                            }
            popupmenu.add_command(label="Sort by " + colnames + ' \u2193',
                        command=lambda : self.table.sortTable(ascending=[1 for i in multicols]))
            popupmenu.add_command(label="Sort by " + colnames + ' \u2191',
                command=lambda : self.table.sortTable(ascending=[0 for i in multicols]))
            # popupmenu.add_command(label="Set %s as Index" %colnames, command=self.table.setindex)
            # popupmenu.add_command(label="Delete Column(s)", command=self.table.deleteColumn)
            # if ismulti == True:
            #     popupmenu.add_command(label="Flatten Index", command=self.table.flattenIndex)
            # popupmenu.add_command(label="Fill With Data", command=self.table.fillColumn)
            # popupmenu.add_command(label="Create Categorical", command=self.table.createCategorical)
            # popupmenu.add_command(label="Apply Function", command=self.table.applyColumnFunction)
            # popupmenu.add_command(label="Resample/Transform", command=self.table.applyTransformFunction)
            # popupmenu.add_command(label="Value Counts", command=self.table.valueCounts)
            # popupmenu.add_command(label="String Operation", command=self.table.applyStringMethod)
            # popupmenu.add_command(label="Date/Time Conversion", command=self.table.convertDates)
            # popupmenu.add_command(label="Set Data Type", command=self.table.setColumnType)

            # createSubMenu(popupmenu, 'Column', columncommands)
            createSubMenu(popupmenu, 'Format', formatcommands)
            popupmenu.bind("<FocusOut>", popupFocusOut)
            popupmenu.focus_set()
            popupmenu.post(event.x_root, event.y_root)
            applyStyle(popupmenu)
            return popupmenu

        def handle_mouse_drag(self, event):
            """Handle column drag, move cols function deleted"""

            x=int(self.canvasx(event.x))
            if self.atdivider == 1:
                self.table.delete('resizeline')
                self.delete('resizeline')
                self.table.create_line(x, 0, x, self.table.rowheight*self.table.rows,
                                    width=2, fill='gray', tag='resizeline')
                self.create_line(x, 0, x, self.height,
                                    width=2, fill='gray', tag='resizeline')
                # return
            # else:
            #     w = self.table.cellwidth
            #     self.draggedcol = self.table.get_col_clicked(event)
            #     coords = self.coords('dragrect')
            #     if len(coords)==0:
            #         return
            #     x1, y1, x2, y2 = coords
            #     x=int(self.canvasx(event.x))
            #     y = self.canvasy(event.y)
            #     self.move('dragrect', x-x1-w/2, 0)

            return

    class AdjRowHeader(RowHeader):
        '''adjust function in RowHeader module'''
        def __init__(self, parent=None, table=None, width=50, bg='gray75'):
            super().__init__(parent, table, width, bg)
        
        def popupMenu(self, event, rows=None, cols=None, outside=None):
            """Add left and right click behaviour for canvas, should not have to override
                this function, it will take its values from defined dicts in constructor"""

            defaultactions = {"Sort by index" : lambda: self.table.sortTable(index=True),
                            # "Reset index" : lambda: self.table.resetIndex(),
                            # "Toggle index" : lambda: self.toggleIndex(),
                            "Copy index to column" : lambda: self.table.copyIndex(),
                            # "Rename index" : lambda: self.table.renameIndex(),
                            # "Sort columns by row" : lambda: self.table.sortColumnIndex(),
                            "Select All" : self.table.selectAll,
                            # "Add Row(s)" : lambda: self.table.addRows(),
                            # "Delete Row(s)" : lambda: self.table.deleteRow(ask=True),
                            # "Duplicate Row(s)":  lambda: self.table.duplicateRows(),
                            "Set Row Color" : lambda: self.table.setRowColors(cols='all')}
            main = ["Sort by index", "Copy index to column", "Set Row Color"]

            popupmenu = tk.Menu(self, tearoff = 0)
            def popupFocusOut(event):
                popupmenu.unpost()
            for action in main:
                popupmenu.add_command(label=action, command=defaultactions[action])

            popupmenu.bind("<FocusOut>", popupFocusOut)
            popupmenu.focus_set()
            popupmenu.post(event.x_root, event.y_root)
            applyStyle(popupmenu)
            return popupmenu

    def popupMenu(self, event, rows=None, cols=None, outside=None):
        """overridden function by myself"""

        defaultactions = {
                        "Copy" : lambda: self.copy(rows, cols),
                        "Undo" : lambda: self.undo(),
                        #"Paste" : lambda: self.paste(rows, cols),
                        "Fill Down" : lambda: self.fillDown(rows, cols),
                        #"Fill Right" : lambda: self.fillAcross(cols, rows),
                        "Add Row(s)" : lambda: self.addRows(),
                        #"Delete Row(s)" : lambda: self.deleteRow(),
                        "Add Column(s)" : lambda: self.addColumn(),
                        "Delete Column(s)" : lambda: self.deleteColumn(),
                        "Clear Data" : lambda: self.deleteCells(rows, cols),
                        "Select All" : self.selectAll,
                        #"Auto Fit Columns" : self.autoResizeColumns,
                        "Table Info" : self.showInfo,
                        "Set Color" : self.setRowColors,
                        "Show as Text" : self.showasText,
                        "Filter Rows" : self.queryBar,
                        "New": self.new,
                        "Open": self.load,
                        "Save": self.save,
                        "Save As": self.saveAs,
                        "Import Text/CSV": lambda: self.importCSV(dialog=True),
                        "Import hdf5": lambda: self.importHDF(dialog=True),
                        "Export": self.doExport,
                        "Plot Selected" : self.plotSelected,
                        "Hide plot" : self.hidePlot,
                        "Show plot" : self.showPlot,
                        "Preferences" : self.showPreferences,
                        "Table to Text" : self.showasText,
                        "Clean Data" : self.cleanData,
                        "Clear Formatting" : self.clearFormatting,
                        "Undo Last Change": self.undo,
                        "Copy Table": self.copyTable,
                        "Find/Replace": self.findText}

        main = ["Undo", "Set Color"]
        general = ["Select All", "Filter Rows", "Table Info", "Preferences"]

        def add_commands(fieldtype):
            """Add commands to popup menu for column type and specific cell"""
            functions = self.columnactions[fieldtype]
            for f in list(functions.keys()):
                func = getattr(self, functions[f])
                popupmenu.add_command(label=f, command= lambda : func(row,col))
            return

        popupmenu = tk.Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()

        if outside == None:
            #if outside table, just show general items
            row = self.get_row_clicked(event)
            col = self.get_col_clicked(event)
            coltype = self.model.getColumnType(col)
            def add_defaultcommands():
                """now add general actions for all cells"""
                for action in main:
                    if action == 'Fill Down' and (rows == None or len(rows) <= 1):
                        continue
                    if action == 'Fill Right' and (cols == None or len(cols) <= 1):
                        continue
                    if action == 'Undo' and self.prevdf is None:
                        continue
                    else:
                        popupmenu.add_command(label=action, command=defaultactions[action])
                return

            if coltype in self.columnactions:
                add_commands(coltype)
            add_defaultcommands()

        for action in general:
            popupmenu.add_command(label=action, command=defaultactions[action])

        popupmenu.bind("<FocusOut>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        applyStyle(popupmenu)
        return popupmenu
    
    def show(self, callback=None):
        """Overridden function in Table submodule to use changed function in headers submodule"""

        #Add the table and header to the frame
        self.rowheader = self.AdjRowHeader(self.parentframe, self)
        self.colheader = self.AdjColumnHeader(self.parentframe, self, bg='gray25')                          # custumized
        self.rowindexheader = IndexHeader(self.parentframe, self, bg='gray75')
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient='vertical',command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient="horizontal",command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.colheader['xscrollcommand'] = self.Xscrollbar.set
        self.rowheader['yscrollcommand'] = self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.rowindexheader.grid(row=0,column=0,rowspan=1,sticky='news')
        self.colheader.grid(row=0,column=1,rowspan=1,sticky='news')
        self.rowheader.grid(row=1,column=0,rowspan=1,sticky='news')
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)

        self.adjustColumnWidths()
        #bind redraw to resize, may trigger redraws when widgets added
        self.parentframe.bind("<Configure>", self.resized) #self.redrawVisible)
        self.colheader.xview("moveto", 0)
        self.xview("moveto", 0)
        if self.showtoolbar == True:
            self.toolbar = ToolBar(self.parentframe, self)
            self.toolbar.grid(row=0,column=3,rowspan=2,sticky='news')
        if self.showstatusbar == True:
            self.statusbar = statusBar(self.parentframe, self)
            self.statusbar.grid(row=3,column=0,columnspan=2,sticky='ew')

        self.currwidth = self.parentframe.winfo_width()
        self.currheight = self.parentframe.winfo_height()
        if hasattr(self, 'pf'):
            self.pf.updateData()
        return

    def drawSelectedRow(self):
        """Overridden function, delete original draw single row function"""

        self.delete('rowrect')
        row = self.currentrow
        return
    
    def drawSelectedRect(self, row, col, color='#084B8A', fillcolor=None):
        """Overridden function, change Rect color"""

        if col >= self.cols:
            return
        self.delete('currentrect')
        if color == None:
            color = 'gray25'
        w=2
        if row == None:
            return
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        rect = self.create_rectangle(x1+w/2+1,y1+w/2+1,x2-w/2,y2-w/2,
                                  outline=color,
                                  fill=fillcolor,
                                  width=w,
                                  tag='currentrect')
        #raise text above all
        self.lift('celltext'+str(col)+'_'+str(row))
        return

    # Not overridden part of pandastable
    def handle_right_alt_click(self, event):
        '''toggle boolean when alt+left click'''

        rowclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)

        if not self.model.df.isnull().values.any():
            self.model.df.iat[rowclicked, colclicked] = bool(not self.model.df.iat[rowclicked, colclicked])     # toggle

            # toggle font color
            if (rowclicked, colclicked) not in self.toggled_cell:
                self.toggled_cell.append((rowclicked, colclicked))
                self.drawText(rowclicked, colclicked, self.model.df.iat[rowclicked, colclicked], align= self.align, fgcolor= self.toggle_color)
            else:
                self.toggled_cell.remove((rowclicked, colclicked))
                self.drawText(rowclicked, colclicked, self.model.df.iat[rowclicked, colclicked], align= self.align, fgcolor= self.textcolor)

            self.master.result.iat[rowclicked, colclicked] = self.model.df.iat[rowclicked, colclicked]          # propagate back data

            # toggle row background color and 'target' column in result dataframe
            if self.model.df.iloc[rowclicked, :].values.all():
                self.setRowColors(rows= rowclicked, clr= "#984B4B",cols= 'all')
                self.master.result.iat[rowclicked, -1] = True
            else:
                self.setRowColors(rows= rowclicked, clr= self.cellbackgr,cols= 'all')
                self.master.result.iat[rowclicked, -1] = False

    def handle_left_alt_click(self, event):
        '''open corresponding view of index'''

        self.handle_left_click(event)
        if self.master.preprocess_flag:
            rowclicked = self.get_row_clicked(event)
            self.open_viewer(rowclicked)

    def open_viewer(self, id:int= None):
        if self.viewer == None or not self.viewer.winfo_exists():
            self.viewer = self.ToplevelViewer(id)
        else:
            self.viewer.update_id(id)
            # self.viewer.focus()

    def update_table_data(self):
        '''pass data to table and configure row color,\n
        use this only for change in result dataframe or adding data first time'''

        self.model.df = self.master.result.iloc[:, :-1]      # uses iloc to choose data without 'target' column, and this makes a copy(or not?)
        self.redrawVisible()
        # initialize bg color
        self.setRowColors(rows= self.master.result.index.to_list(), clr= self.cellbackgr, cols= 'all')
        # initialize font color
        for _ in self.toggled_cell:
            self.drawText(*_, self.master.result.iat[_], align= self.align, fgcolor= self.textcolor)
        self.toggled_cell = []

        target_rows = self.master.result.query('target > 0').index.tolist()
        self.setRowColors(rows= target_rows, clr= "#984B4B",cols= 'all')  # set target row red background, this will call self.redraw()

    class ToplevelViewer(ctk.CTkToplevel):
        def __init__(self, id, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.resizable(0,0)
            self.title("magnified viewer")
            self.pixel_scale:int = 2
            self.canvas_length:int = 400        # actual image size is canvas_length/pixel_scale
            self.id = id
            self.channels = ['UV', 'FITC', 'PE', 'APC']
            self.channel_index:int = 0

            self.update_id(self.id)

            self.channel_switch = ctk.CTkSegmentedButton(self, values= self.channels, command= self.segmentated_button_callback)
            self.channel_switch.set('UV')
            self.channel_switch.grid(row= 0, column= 0, sticky= 'we')

        def update_id(self, id):
            self.all_slices = ccv.image_slice(self.master.df, id, self.pixel_scale, self.canvas_length, *self.master.imgs)
            self.zd = ZoomDrag(self, self.all_slices[self.channel_index], width= self.canvas_length, height= self.canvas_length)
            self.zd.grid(row= 1, column= 0)
        
        def segmentated_button_callback(self, channel):
            self.channel_index = self.channels.index(channel)
            self.zd._load_image(self.all_slices[self.channel_index])


class ZoomDrag(tk.Canvas):
    def __init__(self, master: any, image, width: int = 400, height: int = 400, bg = 'black', **kwargs):
        super().__init__(master, width=width, height=height, bg= bg, **kwargs)

        self.image = image
        self.canv_len = width
        self.scale = 1.0
        self._add_bindings()
        self.offset = (0,0)

        self.pil_image = Image.fromarray(self.image)
        self.tkimage = ImageTk.PhotoImage(self.pil_image)
        self.image_item = self.create_image(int(self.canv_len/2), int(self.canv_len/2), image=self.tkimage, anchor= 'center')        
    
    def _add_bindings(self):
        self.bind('<Button-1>', self._start_drag)
        self.bind('<B1-Motion>', self._drag)
        self.bind('<MouseWheel>', self._zoom)
        self.bind('<Button-4>', self._zoom)
        self.bind('<Button-5>', self._zoom)

    def _load_image(self, alt_img = None):

        self.delete('all')
        if alt_img is not None:
            self.image = alt_img
            self.pil_image = Image.fromarray(self.image)
            width = int(self.pil_image.size[0] * self.scale)
            height = int(self.pil_image.size[1] * self.scale)
            resized_image = self.pil_image.resize((width, height), Image.LANCZOS)
            self.tkimage = ImageTk.PhotoImage(resized_image)
            anchor_x, anchor_y = int(self.canv_len/2)+self.offset[0], int(self.canv_len/2)+self.offset[1]
            self.image_item = self.create_image(anchor_x, anchor_y, image=self.tkimage, anchor='center')

    def _start_drag(self, event):
        self.start_x, self.start_y = event.x, event.y
    
    def _drag(self, event):

        if self.scale > 1:
            dx = event.x- self.start_x
            dy = event.y- self.start_y
            self.move(self.image_item, dx, dy)

            self.start_x, self.start_y = event.x, event.y

            # get bounding box of image item
            bbox = self.bbox(self.image_item)

            # check if the new position of the image exceeds the boundaries of the canvas
            if bbox[0] > 0:
                # the image is exceeding the left boundary
                self.move(self.image_item, -bbox[0], 0)
            elif bbox[2] < self.winfo_width():
                # the image is exceeding the right boundary
                self.move(self.image_item, self.winfo_width() - bbox[2], 0)
            if bbox[1] > 0:
                # the image is exceeding the top boundary
                self.move(self.image_item, 0, -bbox[1])
            elif bbox[3] < self.winfo_height():
                # the image is exceeding the bottom boundary
                self.move(self.image_item, 0, self.winfo_height() - bbox[3])
        
        # update offset
        bbox = self.bbox(self.image_item)
        offset_x = int((bbox[0]+bbox[2]-self.canv_len)/2)
        offset_y = int((bbox[1]+bbox[3]-self.canv_len)/2)
        self.offset = offset_x, offset_y

    def _zoom(self, event):
        scale_before = self.scale

        # update offset
        bbox = self.bbox(self.image_item)
        offset_x = int((bbox[0]+bbox[2]-self.canv_len)/2)
        offset_y = int((bbox[1]+bbox[3]-self.canv_len)/2)
        self.offset = offset_x, offset_y

        if event.delta > 0 or event.num == 4:
            self.scale *= 1.1
        elif event.delta < 0 or event.num == 5:
            self.scale /= 1.1
        self.scale = min(max(self.scale, 1), 10.0)  # limit scale between 1 and 10.0
        scale_after = self.scale

        self.offset = tuple(map(lambda x: int(x*(scale_after/scale_before)), self.offset))  # scale the offset simultaneously
        self._resize_image()
    
    def _resize_image(self):
        width = int(self.pil_image.size[0] * self.scale)
        height = int(self.pil_image.size[1] * self.scale)
        resized_image = self.pil_image.resize((width, height), Image.LANCZOS)
        self.tkimage = ImageTk.PhotoImage(resized_image)
        self.delete('all')

        anchor_x, anchor_y = int(self.canv_len/2)+self.offset[0], int(self.canv_len/2)+self.offset[1]
        self.image_item = self.create_image(anchor_x, anchor_y, image=self.tkimage, anchor='center')

        bbox = self.bbox(self.image_item)
        # check if the new position of the image exceeds the boundaries of the canvas, and update offset
        if bbox[0] > 0:
            # the image is exceeding the left boundary
            self.move(self.image_item, -bbox[0], 0)
        elif bbox[2] < self.winfo_width():
            # the image is exceeding the right boundary
            self.move(self.image_item, self.winfo_width() - bbox[2], 0)
        if bbox[1] > 0:
            # the image is exceeding the top boundary
            self.move(self.image_item, 0, -bbox[1])
        elif bbox[3] < self.winfo_height():
            # the image is exceeding the bottom boundary
            self.move(self.image_item, 0, self.winfo_height() - bbox[3])

if __name__ == "__main__":
    app = App()
    app.mainloop()
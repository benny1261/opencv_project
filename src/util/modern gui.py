import customtkinter as ctk
from customtkinter import ThemeManager
import os
from PIL import Image
from tkinter import filedialog
from opencv import Import_thread, Cv_api
import opencv as ccv

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hsu project.py")
        self.api = Cv_api(self)

        # classwise variables
        self.cwd = ctk.StringVar(value= os.getcwd())
        self.data_dir = ctk.StringVar()
        self.export_dir = ctk.StringVar()

        self.img_0, self.img_1, self.img_2, self.img_3 = None, None, None, None
        self.pre_0, self.pre_1, self.pre_2, self.pre_3 = None, None, None, None
        self.import_flag = False
        self.df, self.result = [], []
        self.th_hct, self.th_wbc, self.th_round = ctk.DoubleVar(value= 0.9), ctk.DoubleVar(value= 0.3), ctk.DoubleVar(value= 0.7)
        self.th_sharp = ctk.IntVar(value= 14000)
        self.target, self.nontarget = ctk.IntVar(), ctk.IntVar()

        # initializing window position to screen center
        min_width, min_height = 720, 450
        self.geometry(f'{min_width}x{min_height}')
        self.minsize(width= min_width, height= min_height)
        cord_x = (self.winfo_screenwidth()-min_width)/2
        cord_y = (self.winfo_screenheight()-min_height)/2        
        self.geometry(f'+{int(cord_x)}+{int(cord_y)}')

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # set init dark mode
        ctk.set_appearance_mode('dark')

        # load icons with light and dark mode image
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'icons')
        self.logo_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "logo_icon.png")), size=(30, 30))
        self.large_test_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "logo_icon.png")), size=(500, 150))
        self.image_icon_image = ctk.CTkImage(Image.open(os.path.join(icon_path, "logo_icon.png")), size=(20, 20))
        self.home_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "home_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "home_dark.png")), size=(20, 20))
        self.filter_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "filter_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "filter_dark.png")), size=(20, 20))
        self.export_image = ctk.CTkImage(light_image=Image.open(os.path.join(icon_path, "export_light.png")),
                                        dark_image=Image.open(os.path.join(icon_path, "export_dark.png")), size=(20, 20))

        # create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

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

        self.export_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Export", font= navigation_font,
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.export_image, anchor="w", command= lambda :self.select_frame_by_name("export"))
        self.export_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"], 
                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight= 1)
        self.home_frame.grid_columnconfigure(2, minsize= 30)

        self.home_frame_cwd_label = ctk.CTkLabel(self.home_frame, text= "CWD")
        self.home_frame_cwd_label.grid(row=0, column=0, padx=20, pady=20)
        self.home_frame_cwd = ctk.CTkButton(self.home_frame, width= 360, text= self.cwd, fg_color= ThemeManager.theme["CTkEntry"]["fg_color"],
                            text_color= ("#C6A300", "#977C00"), border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                            border_width= ThemeManager.theme["CTkEntry"]["border_width"], corner_radius= ThemeManager.theme["CTkEntry"]["corner_radius"],
                            hover_color= ("gray80", "gray30"), textvariable= self.cwd, command= self.choose_cwd)
        self.home_frame_cwd.grid(row=0, column=1, padx=0, pady=20)

        self.home_frame_src_label = ctk.CTkLabel(self.home_frame, text= "Image Folder")
        self.home_frame_src_label.grid(row=1, column=0, padx=20, pady=20)
        self.home_frame_src = ctk.CTkButton(self.home_frame, width= 360, text= self.data_dir, fg_color= ThemeManager.theme["CTkEntry"]["fg_color"],
                            text_color= ("#C6A300", "#977C00"), border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                            border_width= ThemeManager.theme["CTkEntry"]["border_width"], corner_radius= ThemeManager.theme["CTkEntry"]["corner_radius"],
                            hover_color= ("gray80", "gray30"), textvariable= self.data_dir, command= self.choose_filefolder)
        self.home_frame_src.grid(row=1, column=1, padx=0, pady=20)

        self.home_frame_type_label = ctk.CTkLabel(self.home_frame, text= "Target Type")
        self.home_frame_type_label.grid(row=2, column=0, padx=0, pady=20)
        self.home_frame_type = ctk.CTkOptionMenu(self.home_frame, values= ["CTC", "others"])
        self.home_frame_type.grid(row=2, column=1, padx=0, pady=20, sticky= 'w')

        # create filter frame
        self.filter_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create export frame
        self.export_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")


    def select_frame_by_name(self, name):
        # set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.filter_button.configure(fg_color=("gray75", "gray25") if name == "filter" else "transparent")
        self.export_button.configure(fg_color=("gray75", "gray25") if name == "export" else "transparent")

        # show selected frame
        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "filter":
            self.filter_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.filter_frame.grid_forget()
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
            progwin = ctk.CTkToplevel(self)
            progwin.title('Importing and preprocessing...')
            progwin.resizable(0,0)
            progwin.attributes('-topmost', 'true')

            # progress bar widget
            progbar = ctk.CTkProgressBar(progwin, mode= "indeterminate")
            progbar.start()
            progbar.pack(padx= 20, pady= 10)

            # initializing bar position
            cord_x = self.winfo_x()+(self.winfo_width()-progwin.winfo_width())/2
            cord_y = self.winfo_y()+(self.winfo_height()-progwin.winfo_height())/2
            progwin.geometry(f'+{int(cord_x)}+{int(cord_y)}')               # uses f-string mothod
            
            # connect to imported threading function from opencv.py
            import_td.start()                                               # this will start the run() method in Import_thread
            # progwin.grab_set()
            self.thread_monitor(progwin, import_td, progwin.destroy)

            self.export_dir.set(self.data_dir.get())

    def thread_monitor(self, window, thread, command):
        '''check whether the thread in window is alive, if not, run command'''

        if thread.is_alive():
            window.after(100, lambda: self.thread_monitor(window, thread, command))
        else:
            command()

            self.import_flag = thread.flag
            # showing success or not
            if self.import_flag:
                # self.home_fm.btn['export'].configure(bg='#82D900')    #########################

                # pass data after thread closed
                self.img_0, self.img_1, self.img_2, self.img_3 = thread.img_0, thread.img_1, thread.img_2, thread.img_3
                self.pre_0, self.pre_1, self.pre_3 = thread.pre_0, thread.pre_1, thread.pre_3
                self.df = thread.df

                # update result in home frame
                self.auto()
                print(self.target.get(), self.nontarget.get()) ################################
                
                # pass data to treeview
                # self.treeview_data(self.result) #############################################

            else:
                # self.home_fm.btn['export'].configure(bg='#FF4D40')  # change####################
                self.target.set(0)
                self.nontarget.set(0)
    
    def auto(self):
        # self.home_fm.btn['auto'].configure(bg= 'skyblue')
        # self.home_fm.btn['manual'].configure(bg= 'gray')
        if self.import_flag:
            self.result = ccv.analysis(self.df)
            y, n = ccv.count_target(self.result)
            self.target.set(y)
            self.nontarget.set(n)

if __name__ == "__main__":
    app = App()
    app.mainloop()
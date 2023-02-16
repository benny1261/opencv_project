import customtkinter as ctk
import os
from PIL import Image
from customtkinter import ThemeManager


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Hsu project.py")
        self.geometry("700x450")

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
                                                compound="left", font=ctk.CTkFont(size= 15, weight= "bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Home",
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.home_image, anchor="w", command= lambda :self.select_frame_by_name("home"))
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.filter_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Filter",
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.filter_image, anchor="w", command= lambda :self.select_frame_by_name("filter"))
        self.filter_button.grid(row=2, column=0, sticky="ew")

        self.export_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="  Export",
                                                fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                image=self.export_image, anchor="w", command= lambda :self.select_frame_by_name("export"))
        self.export_button.grid(row=3, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["Dark", "Light", "System"], 
                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # create home frame
        self.home_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.home_frame.grid_columnconfigure(0, weight= 1)
        self.home_frame.grid_columnconfigure(2, minsize= 50)

        # self.home_frame_large_image_label = ctk.CTkLabel(self.home_frame, text="", image=self.large_test_image)
        # self.home_frame_large_image_label.grid(row=0, column=0, padx=20, pady=10)
        self.home_frame_src_label = ctk.CTkLabel(self.home_frame, text= "Image Folder")
        self.home_frame_src_label.grid(row=0, column=0, padx=0, pady=30)
        self.home_frame_src = ctk.CTkButton(self.home_frame, width= 360, text= "", fg_color= ThemeManager.theme["CTkEntry"]["fg_color"],
                            text_color= ThemeManager.theme["CTkEntry"]["text_color"], border_color= ThemeManager.theme["CTkEntry"]["border_color"],
                            border_width= ThemeManager.theme["CTkEntry"]["border_width"], corner_radius= ThemeManager.theme["CTkEntry"]["corner_radius"],
                            hover_color= "gray30")
        self.home_frame_src.grid(row=0, column=1, padx=0, pady=30)
        self.home_frame_type_label = ctk.CTkLabel(self.home_frame, text= "Target Type")
        self.home_frame_type_label.grid(row=1, column=0, padx=0, pady=20)
        self.home_frame_type = ctk.CTkOptionMenu(self.home_frame, values= ["CTC", "others"], state= 'readonly')
        self.home_frame_type.grid(row=1, column=1, padx=0, pady=20, sticky= 'w')

        # create filter frame
        self.filter_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # create export frame
        self.export_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # select default frame
        self.select_frame_by_name("home")

        # initializing window position to screen center
        self.update_idletasks()
        cord_x = (self.winfo_screenwidth()-self.winfo_width())/2
        cord_y = (self.winfo_screenheight()-self.winfo_height())/2
        self.geometry(f'+{int(cord_x)}+{int(cord_y)-100}')                                  # uses f-string method

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


if __name__ == "__main__":
    app = App()
    app.mainloop()
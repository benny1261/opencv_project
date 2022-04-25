import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
# from util.simplify import path

# class Frame:
#     def __init__(self, root, padding):
#         self.frame =  Labelframe(root, padding)
#         self.lb = {}
#         self.

#         return self.frame
    
#     def make_lb:

#         add to dict
#     def ..:

# {'text':'...'}-> W.frame['text'].lb.['?']

class Window:

    def __init__(self, frame = {}):
        self.frame = frame                                                                      # initializing dict of frames
        # initializing root window
        self.root = tk.Tk()
        self.root.title("Hsu.exe")
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", lambda arg=self:Window.on_closing(self))

        self.hello()                                                                            # execute
        self.root.mainloop()    # end of gui program when this loop broke

    def auto(self):
        print("NMSL")

    def fetch(self):
        pass

    def viewer(self):
        pass

    def on_closing(self):
        if messagebox.askokcancel("quit", "Confirm quit?"):
            self.root.quit()

    def renew(self):
        for children in self.root.winfo_children():
            children.destroy()
        self.hello()

    def manual(self):
        self.frame['init'].pack_forget()
        self.frame['manual'] = tk.LabelFrame(self.root, padx= 40, pady= 40, text= 'Manual Threshold')
        self.frame['manual'].pack(padx= 10, pady= 10)

        bar = tk.Scale(self.frame['manual'], orient= tk.HORIZONTAL, length= 600)
        bar.config(from_= 0, to_= 255, command= Window.fetch)      
        bar.grid(row = 0)

    def hello(self):
        mymenu = tk.Menu(self.root)                                                             # create menu
        self.root.config(menu= mymenu)                                                          # bound "mymenu" to window

        # create menu items
        file_menu= tk.Menu(mymenu, tearoff= 0)                                                  # create "file" submenu under mymenu, tearoff= 0 to remove slash
        file_menu.add_command(label= "New", command= lambda arg=self: Window.renew(self))       # create commands under "file"
        file_menu.add_separator()                                                               # create divider
        file_menu.add_command(label= "Exit", command= self.root.quit)
        view_menu= tk.Menu(mymenu, tearoff= 0)
        view_menu.add_command(label= "Browse files", command= Window.viewer)

        # placing submenus
        mymenu.add_cascade(label= "File", menu= file_menu)
        mymenu.add_cascade(label= "View", menu= view_menu)

        # establish home frame
        self.frame['init'] = tk.LabelFrame(self.root, padx= 40, pady= 40, text= 'HOME')
        init = self.frame['init']                                                               # make following code cleaner
        init.pack(padx= 30, pady= 20)

        # add widgets in home frame
        tk.Label(init, text = "White light image").grid(row= 0, column= 0)
        w_img = tk.Entry(init).grid(row= 0, column= 1)
        tk.Label(init, text = "Fluorescent image").grid(row= 1, column= 0)
        f_img = tk.Entry(init).grid(row= 1, column= 1)
        tk.Label(init).grid(row= 2, columnspan= 2)
        lb = tk.Label(init, text = "Optimize thereshold")
        lb.grid(row= 3, columnspan= 2)
        aut = tk.Button(init, text = "auto", bg="skyblue", width=8, height=2)
        aut.config(command = lambda arg= self: Window.auto(self))
        aut.grid(row= 4, column= 0)
        mnl = tk.Button(init, text = "manual", bg="#FF4D40", width=8, height=2)
        mnl.config(command = lambda arg= self: Window.manual(self))
        mnl.grid(row= 4, column= 1)

if __name__ == '__main__':
    prog = Window()
    # print(prog.frame['init'])
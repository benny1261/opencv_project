import tkinter as tk
from tkinter import ttk
import os
import cv2
import glob
from util.simplify import path
from util.simplify import cv
from threading import Thread
import time

# command = threading.Thread(target= myfunction).start()

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.resizable(0, 0)
        self.title('Test')

        self.pb = ttk.Progressbar(self, length= 200, mode= "indeterminate")
        self.pb.start()
        self.pb.pack(padx= 20, pady= 10)

        print('1')
        td = Pause()
        td.start()
        self.monitor(td)
        print('2')
    
    def monitor(self, my_thread):
        if my_thread.is_alive():
            self.after(100, lambda: self.monitor(my_thread))
            print('aaa')
        else:
            self.destroy()


class Pause(Thread):
    def __init__(self):
        super().__init__()
    
    def run(self):
        time.sleep(3)
        print('awake')
    
    def run2(self):
        time.sleep(3)
        print('awake2')





if __name__ == '__main__':
    app = App()
    app.mainloop()
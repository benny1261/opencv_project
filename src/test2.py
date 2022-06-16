import os
from tkinter import filedialog
# ph= 'D:\hsu_project\opencv_project\data\blur.jpg'

filetypes = (('jpg files', '*.jpg'), ('all files', '*.*'))
pic = filedialog.askopenfilename(initialdir= os.getcwd(), filetypes= filetypes)
print(pic)
print(os.path.basename(pic))
print(os.path.basename(pic).split(".")[0])
import os
import cv2
import glob
import numpy as np
import util.opencv as cv
import math
import pandas as pd
from skimage import measure, morphology
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

path = r'./data'
img_list = glob.glob(os.path.join(path, "*.jpg"))

for i in img_list:
    if '_0.jpg' in i:
        img_0 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_1.jpg' in i:
        img_1 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_2.jpg' in i:
        img_2 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_3.jpg' in i:
        img_3 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

df = pd.read_excel(os.path.join(path, 'data.xlsx'), index_col= 0)
# result = pd.read_excel(os.path.join(path, 'result.xlsx'), index_col= 0)
# print(df)

# cv.show(img_0, 'test')
cv2.waitKey(0)

class MyApp(ctk.CTk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.resizable(0,0)
        # self.grid_rowconfigure(0, weight= 1)
        # self.grid_columnconfigure(0, weight= 1)

        self.img_test= img_0[1000:1300, 1000:1300]
        self.img_test2 = img_0[3300:3600, 3300:3600]
        self.img_test3 = cv.image_slice(img_0, img_1, img_3, df, 10)[0]
        self.img = ctk.CTkImage(Image.fromarray(img_0), size= (300,300))
        self.img2 = ctk.CTkImage(Image.fromarray(img_1), size= (300,300))

        self.zd = ZoomDrag(self, self.img_test3)
        self.zd.grid(row= 0, column= 0)
        self.zd = ZoomDrag(self, self.img_test2)
        self.zd.grid(row= 0, column= 1)


class ZoomDrag(tk.Canvas):
    def __init__(self, master: any, image, width: int = 300, height: int = 300, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)

        self.image = image
        self.canv_len = width
        self.scale = 1.0
        self._add_bindings()
        self._load_image()
        self.offset = (0,0)
    
    def _add_bindings(self):
        self.bind('<Button-1>', self._start_drag)
        self.bind('<B1-Motion>', self._drag)
        self.bind('<MouseWheel>', self._zoom)
        self.bind('<Button-4>', self._zoom)
        self.bind('<Button-5>', self._zoom)

    def _load_image(self):
        self.pil_image = Image.fromarray(self.image)
        self.tkimage = ImageTk.PhotoImage(self.pil_image)
        self.scale = 1.0
        self.image_item = self.create_image(int(self.canv_len/2), int(self.canv_len/2), image=self.tkimage, anchor= 'center')

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

    def _zoom(self, event):
        scale_before = self.scale

        # update offset due to drag or resize
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


app = MyApp()
app.mainloop()


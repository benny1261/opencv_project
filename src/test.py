import tkinter as tk
from tkinter import ttk
import os
import cv2
import glob
import math
import numpy as np
from threading import Thread
import util.opencv as cv

os.chdir("data")
wbc = cv2.imread('wbc.jpg', cv2.IMREAD_GRAYSCALE)
wbc = np.array(wbc)
print(wbc.shape)

def patching(img, divide= 5):
    size = img.shape[0]
    patch = np.zeros((divide, divide), dtype= np.uint)
    # 9081 (0-1816, 1817-3632, 3633-5448, 5449-7264, 7265-9080)

    for y in range (divide):
        for x in range (divide):
            if y == 0:
                if x == 0:
                    patch[y, x] = img[0: int(np.floor(size/divide)), 0: int(np.floor(size/divide))]
                patch[y, x] = img[0: np.floor(size/divide), np.floor(x*size/divide) + 1: np.floor((x+1)*size/divide)]      
            elif x == 0:
                patch[y, x] = img[np.floor(y*size/divide) + 1: np.floor((y+1)*size/divide), 0: np.floor(size/divide)]
            else:
                patch[y, x] = img[np.floor(y*size/divide) + 1: np.floor((y+1)*size/divide), np.floor(x*size/divide) + 1: np.floor((x+1)*size/divide)]
    
    return patch

# tst = patching(wbc)
# cv.show(tst[3][1], "patching")
# cv.show(wbc[7265:8000, 7265:9081], 't')

cv2.waitKey(0)
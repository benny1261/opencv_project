import tkinter as tk
from tkinter import ttk
import os
import cv2
import glob
import math
import numpy as np
import util.opencv as cv

os.chdir("data")
wbc = cv2.imread('wbc.jpg', cv2.IMREAD_GRAYSCALE)
wbc = np.array(wbc)
print(wbc.shape)
# wbc_bor = cv2.copyMakeBorder(wbc, 2, 2, 2, 2, cv2.BORDER_DEFAULT)
# print(wbc_bor.shape)

def padding(img, divide= 5):
    '''the size should be int after divide'''
    
    size = img.shape[0]
    print(size)
    pad = np.zeros((divide, divide, int(size/divide), int(size/divide)), dtype= np.uint8)
    # 9085 (0-1816, 1817-3633)

    for y in range (divide):
        for x in range (divide):
            pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide) , int(x*size/divide) : int((x+1)*size/divide)]
            if y == divide - 1:
                pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide) + 1, int(x*size/divide) : int((x+1)*size/divide)]
                if x == divide - 1:
                    pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide) + 1, int(x*size/divide) : int((x+1)*size/divide) + 1]
            elif x == divide - 1:
                pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide), int(x*size/divide) : int((x+1)*size/divide) + 1]
    
    return pad

def auto_border(img, divide= 5, border_type = cv2.BORDER_DEFAULT):
    '''upper/lower are pixels added respectivly'''

    size = img.shape[0]
    if size % divide == 0:
        return ()
    
    else:
        patch = divide - size%divide
        upper = int(np.floor(patch/2))
        lower = patch - upper
        img_bor = cv2.copyMakeBorder(img, upper, lower, upper, lower, borderType= border_type)

        return (img_bor, upper, lower)

# tst = padding(wbc)
# cv.show(tst[3, 1], "patching")
tst = auto_border(wbc)
print(tst)

cv2.waitKey(0)
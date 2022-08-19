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

kernal = (5,5)

bor = cv.auto_border(wbc)
tst = cv.padding(bor[0], thresholding= True, kernal_size= kernal)

# cv.show(tst[3, 1], "patching")
ret, th = cv.otsu_th(tst[3, 1], kernal)
cv.show(th, "th")

cv2.waitKey(0)
import tkinter as tk
from tkinter import ttk
import os
import cv2
import glob
from util.simplify import path
import util.opencv as cv
from threading import Thread
import numpy as np

# cv2.Sobel()
# cv2.canny()
# need ROI: a[3][0]
# need normalize: a[3][1]
# -----------------------------------------------------------------------------------------

os.chdir("data")
wbc = cv2.imread("wbc.jpg", cv2.IMREAD_GRAYSCALE)
kernal = (5,5)

a = [np.array_split(_, 5, 1) for _ in np.array_split(wbc, 5)]   # list comprehension

for y in range(len(a)):
    for x in range(len(a[:])):
        ret, a[y][x] = cv.otsu_th(a[y][x], kernal)
        print(a[y][x].shape, ret)

# b = np.block(a)
# cv.show(b, "b")

cv2.waitKey(0)
cv2.destroyAllWindows()             # enables close all image by one press
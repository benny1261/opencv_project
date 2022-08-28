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

a = [np.array_split(_, 5, 1) for _ in np.array_split(wbc, 5)]   # list comprehension

for y in range(len(a)):
    for x in range(len(a[:])):
        ret, a[y][x] = cv.otsu_th(a[y][x], kernal)
        print(a[y][x].shape, ret)

b = np.block(a)
cv.show(b, "b")

cv2.waitKey(0)
import tkinter as tk
from tkinter import ttk
import os
import cv2
import glob
from util.simplify import path
import util.opencv as cv
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt

# cv2.Sobel()
# cv2.canny()
# need ROI: a[3][0]
# need normalize: a[3][1]

# PARAMETERS--------------------------------------------------------------------------------
os.chdir("data")
wbc = cv2.imread("wbc.jpg", cv2.IMREAD_GRAYSCALE)
blur_kernal = (5,5)
RESIZE_FACTOR = 30
CLIP_LIMIT = 4
TILEGRIDSIZE = 16

# DEVIDE&PROCESS----------------------------------------------------------------------------
clahe = cv2.createCLAHE(clipLimit= CLIP_LIMIT, tileGridSize= (TILEGRIDSIZE, TILEGRIDSIZE))                          # default tileGridSize 8x8

a = [np.array_split(_, 5, 1) for _ in np.array_split(wbc, 5)]                                                       # list comprehension

for y in range(len(a)):
    for x in range(len(a[:])):
        img = cv2.resize(a[y][x], None, fx= RESIZE_FACTOR, fy = RESIZE_FACTOR, interpolation= cv2.INTER_CUBIC)      # cubic for enlarge
        # img = clahe.apply(a[y][x])
        img = clahe.apply(img)
        img = cv2.resize(img, None, fx= 1/RESIZE_FACTOR, fy = 1/RESIZE_FACTOR, interpolation= cv2.INTER_AREA)       # area for shrink
        _, a[y][x] = cv.otsu_th(img, blur_kernal)
        print("coordinate: ",y,x,"->",a[y][x].shape, "threshold=",_)

b = np.block(a)
cv.show(b, "b")
cv2.imwrite("fin_re.jpg", b)

# t = a[3][1]
t = a[3][0]
# t_hist = cv2.calcHist([t], [0], None, [256], [0, 256])
# plt.plot(t_hist, label = "original")
# cv.show(t, "orig")
t_big = cv2.resize(t, None, fx= RESIZE_FACTOR, fy = RESIZE_FACTOR, interpolation= cv2.INTER_CUBIC)                  # cubic for enlarge

# THRES--------------------------------------
# thres = cv.otsu_th(t, blur_kernal)[1]
# cv.show(thres, "only_th")

# CLAHE-------------------------------------------------------------------------------------
clahe = cv2.createCLAHE(clipLimit= CLIP_LIMIT, tileGridSize= (TILEGRIDSIZE, TILEGRIDSIZE))                          # default tileGridSize 8x8
clahe_big = clahe.apply(t_big)
clahe_big = cv2.resize(clahe_big, None, fx= 1/RESIZE_FACTOR, fy = 1/RESIZE_FACTOR, interpolation= cv2.INTER_AREA)   # area for shrink
# clahe_hist = cv2.calcHist([clahe_big], [0], None, [256], [0, 256])
# plt.plot(clahe_hist, label = "clahe")
# plt.title("CLAHE")
# plt.xlabel("intensity")
# plt.ylabel("number of pixels")
# plt.legend()
# plt.show()

# cv.show(clahe_big, "clahe_big")
# cv2.imwrite("1_clahe"f'{TILEGRIDSIZE}'".jpg", clahe_big)

_, thres_clahe = cv.otsu_th(clahe_big, blur_kernal)
print("threshold of clahed image= ", _)
# cv.show(thres_clahe, "thres")
# cv2.imwrite("thres"f'{TILEGRIDSIZE}'".jpg", thres_clahe)
fin = cv.erode_dilate(thres_clahe, kernal_size= 3, iterations= 2)
# cv.show(fin, "fin")
# cv2.imwrite("clahe_fin"f'{TILEGRIDSIZE}'".jpg", fin)

# test effect of resize (resize is a litle bit better, more small signal showed)------------
# clahe_orig = clahe.apply(t)
# _, thres_orig = cv.otsu_th(clahe_orig, blur_kernal)
# print("threshold of orignal clahed image= ", _)
# fin_orig = cv.erode_dilate(thres_orig, kernal_size= 3, iterations= 2)
# cv.show(fin_orig, "fin_orig")

cv2.waitKey(0)
cv2.destroyAllWindows()             # enables close all image by one press
import cv2
import numpy
import os

img = cv2.imread('.\data\W_1.jpg')
if img is not None:
    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.imshow('img', img)
    print(img.shape)
    cv2.waitKey(0)

else:
    raise IOError ("Can't find file")
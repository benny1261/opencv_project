import cv2
import numpy

img = cv2.imread('W_1.jpg')

cv2.namedWindow('img', cv2.WINDOW_NORMAL)
cv2.imshow('img', img)
print(img.shape)
cv2.waitKey(0)
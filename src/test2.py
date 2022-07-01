import os
import cv2
import glob
import util.opencv as cv

os.chdir("data")
img_list = (glob.glob('*.jpg'))

img_dict = {}
for i in img_list:
    img_dict[i.split(".")[0]] = cv2.imread(i)

cv.show(img_dict['F_4_0'],'F_4_0')

cv2.waitKey(0)
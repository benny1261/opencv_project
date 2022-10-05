import os
import cv2
import glob
import numpy as np
import util.opencv as cv

os.chdir("data")
img_list = (glob.glob('*.jpg'))
img_dict = {}
for i in img_list:
    if "fin_" in i:
        print(i)
        img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_UNCHANGED)

ep = img_dict["fin_ep"]
hct = img_dict["fin_hct"]
wbc = img_dict["fin_wbc"]

cv2.waitKey(0)
cv2.destroyAllWindows()
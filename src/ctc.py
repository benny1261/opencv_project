import os
import cv2
import glob
import numpy as np
import util.opencv as cv

# Input =======================================================================================
os.chdir("data")
img_list = (glob.glob('*.jpg'))
blur_kernal = (5, 5)

# Reading =====================================================================================
img_dict = {} # dtype=uint8, shape=(9081, 9081, 3)
for i in img_list:
    img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE) # shape=(9081, 9081)

# EpCam =======================================================================================
ret,th_ep = cv.otsu_th(img_dict['epcam'], blur_kernal)
fin_ep = cv.erode_dilate(th_ep, kernal_size= 3, iterations= 3)

# cv.show(th,'otsu')
# cv.show(fin_ep,'di_ep')
print('ep: ',ret)
# cv2.imwrite("ep_bin.jpg", fin_ep)

# hoechest ====================================================================================
ret,th_hoe = cv.otsu_th(img_dict['hcst'], blur_kernal)
cv.show(th_hoe,'th_hoe')
print('hoe: ',ret)

# =============================================================================================
bgd = np.dstack((np.zeros_like(fin_ep), np.zeros_like(fin_ep), fin_ep))
cover = np.dstack((th_hoe, np.zeros_like(th_hoe), np.zeros_like(th_hoe)))
merge = cv2.bitwise_or(bgd, cover, mask= fin_ep)

# merge = np.dstack((th_hoe, fin_ep, fin_ep))

# cv.show(merge, 'merge')
cv2.imwrite("merge.jpg", merge)

# ar = np.array(th)
# print(ar.shape)

cv2.waitKey(0)
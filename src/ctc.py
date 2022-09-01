import os
import cv2
import glob
import numpy as np
import util.opencv as cv

# Input =======================================================================================
os.chdir("data")
img_list = (glob.glob('*.jpg'))
kernal = np.ones((3,3), np.uint8)
blur_kernal = (5, 5)

# Reading =====================================================================================
img_dict = {} # dtype=uint8, shape=(9081, 9081, 3)
for i in img_list:
    img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE) # shape=(9081, 9081)

# EpCam =======================================================================================
ret,th_ep = cv.otsu_th(img_dict['epcam'], blur_kernal)
erode_ep = cv2.erode(th_ep, kernal, iterations=3)
dilate_ep = cv2.dilate(erode_ep, kernal, iterations=3)

# cv.show(th,'otsu')
# cv.show(dilate_ep,'di_ep')
print('ep: ',ret)
# cv2.imwrite("ep_bin.jpg", dilate_ep)

# hoechest ====================================================================================
ret,th_hoe = cv.otsu_th(img_dict['hcst'], blur_kernal)

print('hoe: ',ret)

# =============================================================================================
# bgd = cv2.cvtColor(dilate_ep, cv2.COLOR_GRAY2BGR)
bgd = np.dstack((np.zeros_like(dilate_ep), np.zeros_like(dilate_ep), dilate_ep))
cover = np.dstack((th_hoe, np.zeros_like(th_hoe), np.zeros_like(th_hoe)))
merge = cv2.bitwise_or(bgd, cover, mask= dilate_ep)

# merge = np.dstack((th_hoe, dilate_ep, dilate_ep))

# cv.show(merge, 'merge')
cv2.imwrite("merge.jpg", merge)

# ar = np.array(th)
# print(ar.shape)

cv2.waitKey(0)
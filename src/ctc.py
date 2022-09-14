import os
import cv2
import glob
import numpy as np
import util.opencv as cv

# Input =======================================================================================
os.chdir("data")
img_list = (glob.glob('*.jpg'))

# Parameters ==================================================================================
blur_kernal = (5, 5)
SPLIT = 5
CLIP_LIMIT = 4
TILEGRIDSIZE = 8

# Reading =====================================================================================
img_dict = {} # dtype=uint8, shape=(9081, 9081, 3)
for i in img_list:
    img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

clahe = cv2.createCLAHE(clipLimit= CLIP_LIMIT, tileGridSize= (TILEGRIDSIZE, TILEGRIDSIZE))
# EpCam =======================================================================================

img = img_dict['epcam']
# img = clahe.apply(img_dict['epcam'])
# cv.show(img,'imf')
ret, a = cv.otsu_th(img, blur_kernal)
a = cv.erode_dilate(a)
print("threshold= ", ret)
fin_ep = cv.crop(a)
cv.show(fin_ep, "fin_ep")
cv2.imwrite("ep_b.jpg", fin_ep)

print('ep: ',ret)

# hoechest ====================================================================================
ret,th_hoe = cv.otsu_th(img_dict['hcst'], blur_kernal)
# cv.show(th_hoe,'th_hoe')
print('hoe: ',ret)

# =============================================================================================
bgd = np.dstack((np.zeros_like(fin_ep), np.zeros_like(fin_ep), fin_ep))
cover = np.dstack((th_hoe, np.zeros_like(th_hoe), np.zeros_like(th_hoe)))
merge = cv2.bitwise_or(bgd, cover, mask= fin_ep)

# merge = np.dstack((th_hoe, fin_ep, fin_ep))

# cv.show(merge, 'merge')
# cv2.imwrite("merge.jpg", merge)

cv2.waitKey(0)
cv2.destroyAllWindows()
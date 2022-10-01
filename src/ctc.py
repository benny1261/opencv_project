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
img_dict = {}                                                                                       # dtype=uint8, shape=(9081, 9081, 3)
for i in img_list:
    img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

clahe = cv2.createCLAHE(clipLimit= CLIP_LIMIT, tileGridSize= (TILEGRIDSIZE, TILEGRIDSIZE))

# EpCam =======================================================================================
img = img_dict['epcam']
# img = clahe.apply(img_dict['epcam'])
# cv.show(img,'imf')
ret, a = cv.otsu_th(img, blur_kernal)
a = cv.erode_dilate(a)
fin_ep = cv.crop(a)
# cv.show(fin_ep, "fin_ep")
# cv2.imwrite("fin_ep.jpg", fin_ep)

print('ep: ',ret)

# hoechest ====================================================================================
hct = img_dict['hcst']
a = [np.array_split(_, SPLIT, 1) for _ in np.array_split(hct, SPLIT)]                               # list comprehension

for iter in np.ndindex((len(a), len(a[:]))):
    img = a[iter[0]][iter[1]]
    img = clahe.apply(img)
    ret, img = cv.otsu_th(img, blur_kernal)
    a[iter[0]][iter[1]] = cv.erode_dilate(img)

    print("coordinate:", iter, ",threshold= ", ret)

fin_hct = cv.crop(np.block(a))
# cv.show(fin_hct, "fin_hct")
# cv2.imwrite("fin_hct.jpg", fin_hct)

# wbc =========================================================================================
wbc = img_dict['wbc']
a = [np.array_split(_, SPLIT, 1) for _ in np.array_split(wbc, SPLIT)]

for iter in np.ndindex((len(a), len(a[:]))):
    img = a[iter[0]][iter[1]]
    img = clahe.apply(img)
    ret, img = cv.otsu_th(img, blur_kernal)
    a[iter[0]][iter[1]] = cv.erode_dilate(img)

    print("coordinate:", iter, ",threshold= ", ret)

fin_wbc = cv.crop(np.block(a))
# cv.show(fin_wbc, "fin_wbc")
# cv2.imwrite("fin_wbc.jpg", fin_wbc)

# =============================================================================================
bgd = np.dstack((np.zeros_like(fin_ep), np.zeros_like(fin_ep), fin_ep))
cover = np.dstack((hct, np.zeros_like(hct), np.zeros_like(hct)))
merge = cv2.bitwise_or(bgd, cover, mask= fin_ep)

# merge = np.dstack((hct, fin_ep, fin_ep))

cv.show(merge, 'merge')
cv2.imwrite("merge.jpg", merge)

cv2.waitKey(0)
cv2.destroyAllWindows()
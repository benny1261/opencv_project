import os
import cv2
import glob
from cv2 import MARKER_CROSS
import numpy as np
import util.opencv as cv
import pandas as pd

# Input =======================================================================================
os.chdir("data")
img_list = glob.glob('*.jpg')

# Parameters ==================================================================================
blur_kernal = (5, 5)
SPLIT = 5
CLIP_LIMIT = 4
TILEGRIDSIZE = 8
MARK = True
TRANS = True
BETA = 0.3

# Reading =====================================================================================
img_dict = {}                                                                                       # dtype=uint8, shape=(9081, 9081, 3)
for i in img_list:
    img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

clahe = cv2.createCLAHE(clipLimit= CLIP_LIMIT, tileGridSize= (TILEGRIDSIZE, TILEGRIDSIZE))

# EpCam preprocessing =========================================================================
ep = img_dict['epcam']
img = clahe.apply(ep)
ret, a = cv.otsu_th(img, blur_kernal)                                       # use otsu's threshold but use original image for thresholding
_, th = cv2.threshold(ep, ret, 255, cv2.THRESH_BINARY)
a = cv.erode_dilate(th)
fin_ep = cv.crop(a)
print('epcam>>>')
print(ret)

# cv.show(fin_ep, "fin_ep")
cv2.imwrite("fin_ep.jpg", fin_ep)

# hoechest preprocessing ======================================================================
hct = img_dict['hcst']
a = [np.array_split(_, SPLIT, 1) for _ in np.array_split(hct, SPLIT)]                               # list comprehension
print("hoechst>>>")

for iter in np.ndindex((len(a), len(a[:]))):
    img = a[iter[0]][iter[1]]
    img = clahe.apply(img)
    ret, img = cv.otsu_th(img, blur_kernal)
    a[iter[0]][iter[1]] = cv.erode_dilate(img)

    print("coordinate:", iter, ",threshold= ", ret)

fin_hct = cv.crop(np.block(a))
# cv.show(fin_hct, "fin_hct")
cv2.imwrite("fin_hct.jpg", fin_hct)

# wbc preprocessing ===========================================================================
wbc = img_dict['wbc']
a = [np.array_split(_, SPLIT, 1) for _ in np.array_split(wbc, SPLIT)]
print("wbc>>>")

for iter in np.ndindex((len(a), len(a[:]))):
    img = a[iter[0]][iter[1]]
    img = clahe.apply(img)
    ret, img = cv.otsu_th(img, blur_kernal)
    a[iter[0]][iter[1]] = cv.erode_dilate(img)

    print("coordinate:", iter, ",threshold= ", ret)

fin_wbc = cv.crop(np.block(a))
# cv.show(fin_wbc, "fin_wbc")
cv2.imwrite("fin_wbc.jpg", fin_wbc)

# provide dataframe and export image ==========================================================
imgs = (fin_ep, fin_hct, fin_wbc)
df = cv.img2dataframe(*imgs)                                            # *operater unpacks iterable and pass as positional arguments
cv.image_postprocessing(*imgs, df, marks= MARK, transparent= TRANS, beta= BETA)
with pd.ExcelWriter("dataframe.xlsx") as writer:
    df.to_excel(writer)

cv2.waitKey(0)
cv2.destroyAllWindows()
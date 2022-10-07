import os
import cv2
import glob
import numpy as np
import util.opencv as cv
import pandas as pd
import time

start_time = time.time()
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
BETA = 0.4

# Reading =====================================================================================
hct_dict = {}                                                                               # dtype=uint8, shape=(9081, 9081, 3)
epcam_dict = {}
wbc_dict = {}

for i in img_list:
    if '_0.jpg' in i:
        hct_dict[i.split("_0.")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_1.jpg' in i:
        epcam_dict[i.split("_1.")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_3.jpg' in i:
        wbc_dict[i.split("_3.")[0]] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

if (not hct_dict) or (not epcam_dict) or (not wbc_dict):
    raise IOError(FileNotFoundError, "insufficient required image")
elif not (len(hct_dict) == len(epcam_dict) == len(wbc_dict)):
    raise IOError("number of different fluorescent images are not equal")

clahe = cv2.createCLAHE(clipLimit= CLIP_LIMIT, tileGridSize= (TILEGRIDSIZE, TILEGRIDSIZE))

for key in epcam_dict.keys():                                                   # key is identical for same set of fluorescent
    print(key+">>>>>>>>>>>\npreprocessing")
    # EpCam preprocessing =====================================================================
    ep = epcam_dict[key]
    img = clahe.apply(ep)
    ret, a = cv.otsu_th(img, blur_kernal)                                       # use otsu's threshold but use original image for thresholding
    _, th = cv2.threshold(ep, ret, 255, cv2.THRESH_BINARY)
    a = cv.erode_dilate(th)
    fin_ep = cv.crop(a)
    cv2.imwrite("fin_ep.jpg", fin_ep)

    # hoechest preprocessing ==================================================================
    hct = hct_dict[key]
    a = [np.array_split(_, SPLIT, 1) for _ in np.array_split(hct, SPLIT)]       # list comprehension

    for iter in np.ndindex((len(a), len(a[:]))):
        img = a[iter[0]][iter[1]]
        img = clahe.apply(img)
        ret, img = cv.otsu_th(img, blur_kernal)
        a[iter[0]][iter[1]] = cv.erode_dilate(img)
    fin_hct = cv.crop(np.block(a))
    cv2.imwrite("fin_hct.jpg", fin_hct)

    # wbc preprocessing =======================================================================
    wbc = wbc_dict[key]
    a = [np.array_split(_, SPLIT, 1) for _ in np.array_split(wbc, SPLIT)]

    for iter in np.ndindex((len(a), len(a[:]))):
        img = a[iter[0]][iter[1]]
        img = clahe.apply(img)
        ret, img = cv.otsu_th(img, blur_kernal)
        a[iter[0]][iter[1]] = cv.erode_dilate(img)
    fin_wbc = cv.crop(np.block(a))
    cv2.imwrite("fin_wbc.jpg", fin_wbc)

    # provide dataframe and export image ======================================================
    print("creating dataframe and identifying")
    imgs = (fin_ep, fin_hct, fin_wbc)
    df = cv.img2dataframe(*imgs)                                        # *operater unpacks iterable and pass as positional arguments
    cv.image_postprocessing(*imgs, df, marks= MARK, transparent= TRANS, beta= BETA)
    with pd.ExcelWriter(key+".xlsx") as writer:
        df.to_excel(writer)

end_time = time.time()
print("++++++++++++++++++++++++++++++++++++++++++")
print("elapsed time:", end_time-start_time,"seconds")

cv2.waitKey(0)
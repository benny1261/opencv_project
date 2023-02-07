import os
import cv2
import glob
import numpy as np
import util.opencv as cv
import pandas as pd
import time

start_time = time.time()
# Input =======================================================================================
DATADIRECTORY = "data"
root_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
os.chdir(root_dir)
data_dir = os.path.join(os.getcwd(), DATADIRECTORY)
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
img_list = glob.glob(os.path.join(DATADIRECTORY, "*.jpg"))

# Parameters ==================================================================================
MARK = True
MASK = True
BETA = 0.4

# Reading =====================================================================================
for i in img_list:
    if '_0.jpg' in i:
        hct = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_1.jpg' in i:
        epcam = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    elif '_3.jpg' in i:
        wbc = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

# df
pre_0 = cv.preprocess_full(hct, 16)
pre_1 = cv.preprocess_rare(epcam, 81)
pre_3 = cv.preprocess_full(wbc, 26)

cv2.imwrite(os.path.join(DATADIRECTORY, "binary0n.jpg"), pre_0)
cv2.imwrite(os.path.join(DATADIRECTORY, "binary1n.jpg"), pre_1)
cv2.imwrite(os.path.join(DATADIRECTORY, "binary3n.jpg"), pre_3)

# provide dataframe and export image ======================================================
# print("creating dataframe")
# df = cv.img2dataframe(pre_1, pre_0, pre_3)
# print("post-processing")
# cv.image_postprocessing(pre_1, pre_0, pre_3, df, path= DATADIRECTORY, mark= MARK, mask= MASK, beta= BETA)

# with pd.ExcelWriter(os.path.join(DATADIRECTORY, "CTC.xlsx")) as writer:
#     df.to_excel(writer)

end_time = time.time()
print("++++++++++++++++++++++++++++++++++++++++++")
print("elapsed time:", end_time-start_time,"seconds")

cv2.waitKey(0)
import glob
import cv2
from cv2 import THRESH_BINARY
import numpy as np
from util.simplify import cv
from util.simplify import path
from util.simplify import Data

path.mov('data')
img_list = (glob.glob('*.jpg'))

img_dict = {}
for i in range(len(img_list)):
    img_dict[img_list[i].split(".")[0]] = Data(cv2.imread(img_list[i]), img_list[i].split(".")[0])

# img_dict['F_1_Merge'].show()
img_dict['W_1'].show()

gray = cv2.cvtColor(img_dict['F_1_Merge'].img, cv2.COLOR_BGR2GRAY)

autoblur = cv2.medianBlur(gray, 3)
# cv.show(autoblur, 'autoblur')

# th = cv2.adaptiveThreshold(autoblur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, 3, 1)
ret, th = cv2.threshold(autoblur, 80, 255, cv2.THRESH_BINARY)
# ret, th = cv2.threshold(autoblur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# cv.show(th, 'th')

kernal = np.ones((3,3), np.uint8)
dilate = cv2.dilate(th, kernal, iterations=7)
# cv.show(dilate, 'dilate')
erode = cv2.erode(dilate, kernal, iterations=7)
# cv.show(erode, 'erode')
inv_msk = cv2.bitwise_not(erode)
cut = cv2.bitwise_and(img_dict['W_1'].img, img_dict['W_1'].img, mask = inv_msk)
cv.show(cut, 'cut')

# manual canny
# def empty(x):
#     pass
# cv2.namedWindow('GUI')
# cv2.resizeWindow('GUI', 640, 320)

# cv2.createTrackbar('canny min', 'GUI', 0, 225, empty)
# cv2.createTrackbar('canny max', 'GUI', 0, 225, empty)

# while True:
#     if cv2.getWindowProperty("GUI", cv2.WND_PROP_VISIBLE) == 0:
#         cv2.destroyAllWindows()
#         break
#     can = cv2.Canny(blur, cv2.getTrackbarPos('canny min', 'GUI'), cv2.getTrackbarPos('canny max', 'GUI'))
#     cv2.namedWindow("manual canny", cv2.WINDOW_NORMAL)
#     cv2.imshow("manual canny", can)
#     cv2.waitKey(1)

cv2.waitKey(0)
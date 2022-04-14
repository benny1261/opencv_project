import cv2
from util.simplify import path
from util.simplify import Data
from util.simplify import cv

path.mov('data')

img = Data(cv2.imread('W_1.jpg'), 'W_1')
img.show()

# img = cv2.imread('W_1.jpg')
# cv2.namedWindow("NMSL", cv2.WINDOW_NORMAL)
# cv2.imshow("NMSL", img)
cv2.waitKey(0)
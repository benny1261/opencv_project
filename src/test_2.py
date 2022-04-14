import glob
import cv2
from util.simplify import path
from util.simplify import Data

path.mov('data')
img_list = (glob.glob('*.jpg'))

img_dict = {}
for i in range(len(img_list)):
    img_dict[img_list[i].split(".")[0]] = Data(cv2.imread(img_list[i]), img_list[i].split(".")[0])

print(img_dict['F_1_Merge'].name)
img_dict['F_1_Merge'].show()

cv2.namedWindow("ig", cv2.WINDOW_NORMAL)
cv2.imshow("ig", img_dict['W_1'].img)
cv2.waitKey(0)
import cv2
import os
from util import mod_path

# loc = mod_path.path.get_parent(__file__)
# print(loc)
# loc2 = mod_path.path.get_root(__file__)
# print(loc2)

# print(os.path.basename(__file__))
mod_path.mov.location('data')
img = cv2.imread('W_1.jpg')
os.system("pause")
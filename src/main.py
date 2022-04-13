# from genericpath import exists
import os
import cv2
from util.simplify import path
from util.simplify import Data

path.mov('data')
file = 'W_1.jpg'

if os.path.isfile(file): 
    # locals()[file] = Data(cv2.imread(file), file)
    img = Data(cv2.imread(file), file)

else:
    raise FileNotFoundError


img.show()
cv2.waitKey(0)

# blur = Data(cv2.GaussianBlur(img.img, (3, 3), 0), 'blur')
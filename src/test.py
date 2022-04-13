import cv2
from util import simplify as sp

sp.path.mov('data')

img = sp.Data(cv2.imread('W_1.jpg'), 'W_1.jpg')
# print(img)
print(img.img)
# print(img.name)
img.show()
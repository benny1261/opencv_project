import glob
import cv2
import numpy as np
from simplify import cv
from simplify import path
from threading import Thread

class Import_thread(Thread):                                                                # define a class that inherits from 'Thread' class
    def __init__(self):
        super().__init__()                                                                  # run __init__ of parent class

        self.img_dict = {}

    def run(self):                                                                          # overwrites run() method from parent class

        img_list = (glob.glob('*.jpg'))
        for i in img_list:
            self.img_dict[i.split(".")[0]] = cv2.imread(i)


if __name__ == '__main__':
    path.mov('data')
    img_list = (glob.glob('*.jpg'))

    img_dict = {}
    for i in img_list:
        img_dict[i.split(".")[0]] = cv2.imread(i)

    cv.show(img_dict['F_1_Merge'],'F_1_Merge')
    cv.show(img_dict['W_1'],'W_1')

    gray = cv2.cvtColor(img_dict['F_1_Merge'], cv2.COLOR_BGR2GRAY)
    cv2.imwrite("gray.jpg", gray)

    autoblur = cv2.medianBlur(gray, 3)
    # cv.show(autoblur, 'autoblur')
    cv2.imwrite("blur.jpg", autoblur)

    # th = cv2.adaptiveThreshold(autoblur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, 3, 1)
    ret, th = cv2.threshold(autoblur, 80, 255, cv2.THRESH_BINARY)
    # ret, th = cv2.threshold(autoblur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv.show(th, 'th')
    cv2.imwrite("thres.jpg", th)

    kernal = np.ones((3,3), np.uint8)
    dilate = cv2.dilate(th, kernal, iterations=7)
    # cv.show(dilate, 'dilate')
    erode = cv2.erode(dilate, kernal, iterations=7)
    # cv.show(erode, 'erode')
    cv2.imwrite("lower_noise.jpg", erode)
    mask = cv2.bitwise_not(erode)
    cv2.imwrite("mask.jpg", mask)
    cut = cv2.bitwise_and(img_dict['W_1'], img_dict['W_1'], mask = mask)
    cv.show(cut, 'cut')
    cv2.imwrite("cut.jpg", cut)

    # create transparent image
    maskRGBA = np.dstack((mask, mask, mask, erode))
    # print(maskRGBA.shape)
    cv2.imwrite("Transparent.png", maskRGBA)
    # cv.show(maskRGBA, 'A')

    cv2.waitKey(0)
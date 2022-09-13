import math
import glob
import cv2
import os
import numpy as np
from threading import Thread
import matplotlib.pyplot as plt

class Import_thread(Thread):                                                            # define a class that inherits from 'Thread' class
    def __init__(self):
        super().__init__()                                                              # run __init__ of parent class
        self.img_list = []
        self.img_dict = {}

    def run(self):                                                                      # overwrites run() method from parent class

        self.img_list.extend(glob.glob('*.jpg'))
        for i in self.img_list:
            self.img_dict[i.split(".")[0]] = cv2.imread(i)
    
    def single_file(self, file):                                                        # external method for importing single file, not thread
        if os.path.basename(file) in self.img_list:                                     # prevents file be repeatedly imported
            print('repeated file')
        elif os.path.isfile(file):
            self.img_dict[os.path.basename(file).split(".")[0]] = cv2.imread(file)
        else:
            print('invalid parameter')
        

class Cv_api:
    def __init__(self, app):
        self.app = app

    def export(self):
        print('export thread')
        print(self.app.frames['export'].checkbtn['gray'].get())


def show(img, name):

    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, img)


def otsu_th(img, kernal_size):
    blur = cv2.GaussianBlur(img, kernal_size, 0)
    ret, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return ret, th

def erode_dilate(img, kernal_size= 3, iterations= 3):
    '''kernal size must be odd and >= 3'''
    kernal = np.ones((kernal_size,kernal_size), np.uint8)
    _ = cv2.erode(img, kernal, iterations= iterations)
    _ = cv2.dilate(_, kernal, iterations= iterations)
    return _

def crop(img):
    block = int(np.floor(img.shape[0]/5))
    radius = int(block*1.5*math.sqrt(2))
    center = int(np.floor(img.shape[0]/2))
    mask = cv2.circle(np.zeros_like(img), (center, center), radius, (255, 255, 255), -1)
    masked = cv2.bitwise_and(img, mask)
    return masked

if __name__ == '__main__':
    os.chdir("data")
    img_list = (glob.glob('*.jpg'))

    img_dict = {}
    for i in img_list:
        img_dict[i.split(".")[0]] = cv2.imread(i)

    wbc = img_dict["wbc"]
    show(crop(wbc), "cp")

    # create transparent image
    # maskRGBA = np.dstack((mask, mask, mask, erode))
    # print(maskRGBA.shape)
    # cv2.imwrite("Transparent.png", maskRGBA)
    # Cv.show(maskRGBA, 'A')

    cv2.waitKey(0)
import math
import glob
import cv2
import os
import numpy as np
from threading import Thread
import pandas as pd

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


def img2dataframe(img):
    '''find contours from img, calculate properties of each one and store in dataframe'''
    contours, _ = cv2.findContours(cv2.Canny(img, 50, 100), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    center = []
    roundness = []

    for _ in contours:
        M = cv2.moments(_)
        cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        center.append((cx, cy))
        e = 4*math.pi*cv2.contourArea(_)/cv2.arcLength(_, closed= True)**2
        roundness.append(e)
    
    data = {
        "center":center,
        "roundness":roundness
    }
    return pd.DataFrame(data)

def show(img, name):

    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, img)

def otsu_th(img, kernal_size):
    blur = cv2.GaussianBlur(img, kernal_size, 0)
    ret, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return ret, th

def erode_dilate(img, kernal_size= 3, iterations= 2):
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

    # grades = {
    # "name": ["Mike", "Sherry", "Cindy", "John"],
    # "math": [80, 75, 93, 86],
    # "chinese": [63, 90, 85, 70]
    # }
    # df = ContourDF(grades)

    os.chdir("data")
    img_list = (glob.glob('*.jpg'))
    img_dict = {}
    for i in img_list:
        if "fin_" in i:
            print(i)
            img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_UNCHANGED)

    ep = img_dict["fin_ep"]
    hct = img_dict["fin_hct"]
    wbc = img_dict["fin_wbc"]

    df = img2dataframe(ep)
    # print(df[["roundness"]])

    cv2.waitKey(0)
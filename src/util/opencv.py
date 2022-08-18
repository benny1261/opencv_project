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


def padding(img, divide= 5):
    '''needs to notice the number should be int after divide'''
    
    size = img.shape[0]
    print(size)
    pad = np.zeros((divide, divide, int(size/divide), int(size/divide)), dtype= np.uint8)
    # 9085 (0-1816, 1817-3633)

    for y in range (divide):
        for x in range (divide):
            pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide) , int(x*size/divide) : int((x+1)*size/divide)]
            if y == divide - 1:
                pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide) + 1, int(x*size/divide) : int((x+1)*size/divide)]
                if x == divide - 1:
                    pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide) + 1, int(x*size/divide) : int((x+1)*size/divide) + 1]
            elif x == divide - 1:
                pad[y, x] = img[int(y*size/divide): int((y+1)*size/divide), int(x*size/divide) : int((x+1)*size/divide) + 1]
    
    return pad


if __name__ == '__main__':
    os.chdir("data")
    img_list = (glob.glob('*.jpg'))

    img_dict = {}
    for i in img_list:
        img_dict[i.split(".")[0]] = cv2.imread(i)

    # show(img_dict['F_4_2'],'F_4_2')

    gray = cv2.cvtColor(img_dict['F_4_0'], cv2.COLOR_BGR2GRAY)
    # cv2.imwrite("gray.jpg", gray)
    show(gray, 'gray')

    # plotting -------------------------------------------------------------------------------------------------------
    # intensity = np.arange(256, dtype= np.uint)                                              # or use np.linspace
    # amount = np.zeros_like(intensity)
    # for i in intensity:
    #     amount[i] = np.count_nonzero(gray == i)

    # print(amount)
    # plt.plot(intensity, amount)
    # plt.xlabel("intensity")
    # plt.ylabel("amount")
    # plt.show()
    # ----------------------------------------------------------------------------------------------------------------

    # autoblur = cv2.medianBlur(gray, 3)
    # Cv.show(autoblur, 'autoblur')

    # th = cv2.adaptiveThreshold(autoblur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 1)
    ret, th = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)
    show(th, 'th')
    cv2.imwrite("thres.jpg", th)

    # cv.show(cv.auto_thres(autoblur), 'at')

    # kernal = np.ones((3,3), np.uint8)
    # dilate = cv2.dilate(th, kernal, iterations=7)
    # Cv.show(dilate, 'dilate')
    # erode = cv2.erode(dilate, kernal, iterations=7)
    # Cv.show(erode, 'erode')
    # mask = cv2.bitwise_not(erode)
    # cut = cv2.bitwise_and(img_dict['W_1'], img_dict['W_1'], mask = mask)
    # Cv.show(cut, 'cut')

    # create transparent image
    # maskRGBA = np.dstack((mask, mask, mask, erode))
    # print(maskRGBA.shape)
    # cv2.imwrite("Transparent.png", maskRGBA)
    # Cv.show(maskRGBA, 'A')

    cv2.waitKey(0)
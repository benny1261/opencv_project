import os
from statistics import median
import cv2
import numpy as np

class path:

    def get_parent(loc):                                        # loc should be a path: eg.get_parent(__file__)
        return(os.path.dirname(loc))                            # returns the str of parent path


    def get_root(loc):                                          #loc should be a path: eg.get_root(__file__)
        if "opencv_project" in loc:
            while os.path.split(loc)[1] !=  "opencv_project":   
                loc = os.path.dirname(loc)
            return loc                                          # returns the str of root path
        else:                                                   # prevents looping forever
            raise ("__file__ location not in proper root folder")


    def mov(target = None):                                     # target can be only directory
        if target != None:                                      # default(no arguments passed in) is to do nothing
            try:
                os.chdir(target)
            except NotADirectoryError:
                print(target + " is not a directory")
            except FileNotFoundError:
                print("Can't find directory: " + target)

    def root():                                                 # move cwd to root directory
        try:
            os.chdir(path.get_root(os.getcwd()))
        except FileNotFoundError:
            print("current working directory is not in proper root folder")



class cv:
    
    def show(img, name):
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.imshow(name, img)

    def auto_canny(image, sigma = 0.33):
        # calculate median number of only middle part
        v = np.median(cv.crop(image))
        # canny parameters
        lower = int(max(0, (1.0 - sigma)*v))
        upper = int(min(255, (1.0 + sigma)*v))
        edged = cv2.Canny(image, lower, upper)
        return edged
    
    def crop(img):
        size = img.shape[0]
        lower = round(size/5)
        upper = round(size*4/5)
        return img[lower:upper, lower:upper]



class Data:

    def __init__(self, img, name):
        self.img = img
        self.name = name
    
    # shows the image in class itself (by calling cv.show)
    def show(self):
        cv.show(self.img, self.name)
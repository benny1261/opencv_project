import os
import cv2
import numpy as np

class path:

    def get_parent(loc):
        '''loc should be a path: eg.get_parent(__file__)'''

        return(os.path.dirname(loc))                            # returns the str of parent path


    def get_root(loc):
        '''loc should be a path: eg.get_root(__file__)'''

        if "opencv_project" in loc:
            while os.path.split(loc)[1] !=  "opencv_project":   
                loc = os.path.dirname(loc)
            return loc                                              # returns the str of root path
        else:                                                       # prevents looping forever
            raise ("__file__ location not in proper root folder")


    def mov(target = None):
        '''target can be only directory'''

        if not target:                                              # when target == '' or default (no arguments passed in) is to do nothing
            print('move path canceled')
        else:
            try:
                os.chdir(target)
            except NotADirectoryError:
                print(target + " is not a directory")
            except FileNotFoundError:
                print("Can't find directory: " + target)

    def root():
        '''move cwd to root directory'''

        try:
            os.chdir(path.get_root(os.getcwd()))
        except FileNotFoundError:
            print("current working directory is not in proper root folder")
import os
import cv2
import glob
import numpy as np
import util.opencv as cv
import math
from skimage import measure, morphology

def exp(ex, al=[]):
    al.append(ex)
    return al

def exp2(ex):
    al=[]
    al.append(ex)
    return al

print(exp(1))
print(exp(2))

print(exp2(1))
print(exp2(2))

cv2.waitKey(0)
cv2.destroyAllWindows()
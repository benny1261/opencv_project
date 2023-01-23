import os
import cv2
import glob
import numpy as np
import util.opencv as cv
import math
from skimage import measure, morphology
# test morphology.remove_small_holes and remove_small_objects
# see plotly

a = np.zeros((7, 6), dtype=int)
a[3:5, 2:4] = 1
a[5, 4] = 1
a[:2, :3] = 1
a[0, 5] = 1

aa = measure.label(a, connectivity= 2)
print(aa)

center = []
area = []
perimeter = []
diameter = []
max_dia = []
roundness = []
image = []

properties = measure.regionprops(aa)
for props in properties:
    center.append(tuple(map(round, props.centroid)))
    area.append(props.area)
    perimeter.append(props.perimeter_crofton)
    diameter.append(props.equivalent_diameter_area)
    max_dia.append(props.feret_diameter_max)
    roundness.append(4*math.pi*props.area/props.perimeter_crofton**2)
    image.append(props.image)

print(center)
print(area)
print(perimeter)
print(diameter)
print(max_dia)
print(roundness)
# print(image)          # use slice instead

cv2.waitKey(0)
cv2.destroyAllWindows()
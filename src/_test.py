import os
import cv2
import glob
import numpy as np
import util.opencv as cv
import math
import pandas as pd
from skimage import measure, morphology

df = pd.DataFrame({"A":[1,2,3],"B":[4,5,6], "C":[7,8,9]})
print(df)

df2 = df.iloc[0:2, 0:2]
print(df2)
df2[1,1]= 99
print(df)

cv2.waitKey(0)
cv2.destroyAllWindows()
import cv2
import glob
from util.simplify import path
# from util.GUI import Window


# Input Area =================================================================================
path.mov('data')
img_list = (glob.glob('*.jpg'))

# graphic user interface =====================================================================
# prog =  Window()

# Reading Area ===============================================================================
if img_list:
    img_dict = {}
    for i in img_list:
        img_dict[i.split(".")[0]] = cv2.imread(i)

else:
    raise FileNotFoundError

print(img_dict)

# Processing Area ============================================================================
# cv2.waitKey(0)
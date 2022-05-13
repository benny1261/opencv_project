import cv2
import glob
from util.simplify import path
from util.simplify import Data
from util.GUI import Window


# Input Area =================================================================================
path.mov('data')
img_list = (glob.glob('*.jpg'))

# graphic user interface =====================================================================
# prog =  Window()

# Reading Area ===============================================================================
if img_list:
    img_dict = {}
    for i in range(len(img_list)):
        img_dict[img_list[i].split(".")[0]] = Data(cv2.imread(img_list[i]), img_list[i].split(".")[0])

else:
    raise FileNotFoundError

print(img_list)

# Processing Area ============================================================================
cv2.waitKey(0)
import os
import cv2
import glob
import numpy as np
import util.opencv as cv

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


bg = np.dstack((np.zeros_like(ep), np.zeros_like(ep), np.zeros_like(ep)))
epbg = np.dstack((ep, ep, ep))

canny = cv2.Canny(ep, 50, 100)
cv2.imwrite("canny.jpg", canny)
contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# print(type(contours[1]))
# print(len(contours))
# cv2.drawContours(epbg, contours, -1, (0,255,0), 1)
# cv2.imwrite("wtf.jpg", epbg)

# contours, hierarchy = cv2.findContours(ep, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(epbg, contours, -1, (0,255,0), 1)
# cv2.imwrite("wtf.jpg", epbg)

# for _ in contours:
#     (cx, cy), (a, b), angle = cv2.fitEllipse(contours[_])
#     cv2.circle(epbg, (cx, cy), a, (0,0,255), 1)
# cv2.imwrite("wtf2.jpg", epbg)

# for _ in contours:
#     (cx, cy), radius = cv2.minEnclosingCircle(_)
#     cv2.circle(epbg, (cx, cy), radius, (0,0,255), 2)
# cv2.imwrite("wtf2.jpg", epbg)

for _ in contours:      # len=125
    M = cv2.moments(_)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    cv2.circle(epbg, (cx, cy), 30, (0,0,255), 2)
cv2.imwrite("wtf2.jpg", epbg)

print(contours)

cv2.waitKey(0)
cv2.destroyAllWindows()
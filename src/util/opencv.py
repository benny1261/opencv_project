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


def img2dataframe(ep_img, hct_img, wbc_img, marks= True, transparent= False, beta = 0.3):
    '''find contours from epcam img, calculate properties of each one and store in dataframe, also optional marks on exported image, parameter img should be grayscale'''
    EPCAM_MARK = (0,0,255)
    NONEPCAM_MARK = (18,153,255)
    MARKFONT = cv2.FONT_HERSHEY_TRIPLEX
    MARKCOORDINATE = (-30, -40)
    
    RGBep = np.dstack((ep_img, ep_img, ep_img))                                         # white
    RGBhct = np.dstack((hct_img, np.zeros_like(hct_img), np.zeros_like(hct_img)))       # blue
    RGBwbc = np.dstack((np.zeros_like(wbc_img), wbc_img, np.zeros_like(wbc_img)))       # green
    if transparent:
        bg = np.dstack((np.zeros_like(ep_img), np.zeros_like(ep_img), np.zeros_like(ep_img)))

    contours, _ = cv2.findContours(cv2.Canny(ep_img, 50, 100), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    hct_contours, _ = cv2.findContours(cv2.Canny(hct_img, 50, 100), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    wbc_contours, _ = cv2.findContours(cv2.Canny(wbc_img, 50, 100), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # make merge image of epcam, hoechst and wbc
    hctwbc_mix = cv2.add(RGBhct, RGBwbc)
    merge = cv2.addWeighted(RGBep, 1-beta, hctwbc_mix, beta, gamma= 0)

    # add contours in only where epcam signal are
    mask_withcontour = cv2.drawContours(RGBep, wbc_contours, -1, (0, 255, 0), thickness= 1)
    mask_withcontour = cv2.drawContours(mask_withcontour, hct_contours, -1, (255, 0, 0), thickness= 1)
    blk2 = cv2.bitwise_and(merge, merge, mask= cv2.bitwise_not(ep_img))                         # make region in mask black(clean)
    final2 = cv2.add(blk2, cv2.bitwise_and(mask_withcontour, mask_withcontour, mask= ep_img))   # make region in mask white
 
    center = []
    roundness = []
    hct = []
    wbc = []

    for _ in range(len(contours)):                                                      # needs index so use _ in range(len())
        M = cv2.moments(contours[_])
        cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        center.append((cx, cy))         # add center to df
        e = 4*math.pi*cv2.contourArea(contours[_])/cv2.arcLength(contours[_], closed= True)**2
        roundness.append(e)             # add roundness to df

        # detection of intersection in ROI
        x, y, w, h = cv2.boundingRect(contours[_])
        eproi = ep_img[y:y+h, x:x+w]
        hctroi = hct_img[y:y+h, x:x+w]
        wbcroi = wbc_img[y:y+h, x:x+w]
        intersection_1 = cv2.bitwise_and(eproi, hctroi, mask = eproi)
        intersection_2 = cv2.bitwise_and(eproi, wbcroi, mask = eproi)
        if np.count_nonzero(intersection_1) >= 5:
            hct.append(True)
        else:
            hct.append(False)
        if np.count_nonzero(intersection_2) >= 30:
            wbc.append(True)
        else:
            wbc.append(False)

        if marks:
            if ((hct[_]) & (not wbc[_])):
                cv2.circle(final2, center[_], 30, EPCAM_MARK, 2)
                cv2.putText(final2, f'{_},e={round(e,3)}', (cx+MARKCOORDINATE[0], cy+MARKCOORDINATE[1]), fontFace= MARKFONT, fontScale= 1,color= EPCAM_MARK, thickness= 2)
            else:
                cv2.circle(final2, center[_], 30, NONEPCAM_MARK, 2)
                cv2.putText(final2, f'{_},e={round(e,3)}', (cx+MARKCOORDINATE[0], cy+MARKCOORDINATE[1]), fontFace= MARKFONT, fontScale= 1,color= NONEPCAM_MARK, thickness= 2)
        
        if transparent:
            if ((hct[_]) & (not wbc[_])):
                cv2.circle(bg, center[_], 30, EPCAM_MARK, 2)
                cv2.putText(bg, f'{_},e={round(e,3)}', (cx+MARKCOORDINATE[0], cy+MARKCOORDINATE[1]), fontFace= MARKFONT, fontScale= 1,color= EPCAM_MARK, thickness= 2)
            else:
                cv2.circle(bg, center[_], 30, NONEPCAM_MARK, 2)
                cv2.putText(bg, f'{_},e={round(e,3)}', (cx+MARKCOORDINATE[0], cy+MARKCOORDINATE[1]), fontFace= MARKFONT, fontScale= 1,color= NONEPCAM_MARK, thickness= 2)

    if transparent:
        markgray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        _, markmask = cv2.threshold(markgray, 1, 255, cv2.THRESH_BINARY)
        bgra = np.dstack((bg, markmask))
        cv2.imwrite("mark.png", bgra)
    cv2.imwrite("final.jpg", final2)

    data = {
        "center":center,
        "roundness":roundness,
        "hct":hct,
        "wbc":wbc
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

    df = img2dataframe(ep, hct, wbc, transparent= True)
    with pd.ExcelWriter("x.xlsx") as writer:
        df.to_excel(writer)

    cv2.waitKey(0)
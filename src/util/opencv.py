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


def img2dataframe(ep_img: np.ndarray, hct_img: np.ndarray, wbc_img: np.ndarray):
    '''find contours from epcam img, calculate properties of each one and store in dataframe, 
also optional marks on exported image, parameter img should be grayscale\n
@ret pandas dataframe'''
    contours, _ = cv2.findContours(cv2.Canny(ep_img, 50, 100), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    ROI = 60
    HCT_THRESHOLD = 20                                                                  # pixels of epcam-hct intersection
    WBC_THRESHOLD = 0.5                                                                 # ratio, epcam-wbc intersection/epcam
    # cellsize = 12^2~25^2
    center = []
    roundness = []
    hct = []
    wbc = []
    wbc_sharpness = []                                                                  # lower means more blur

    for _ in range(len(contours)):                                                      # needs index so use _ in range(len())
        M = cv2.moments(contours[_])
        if M["m00"] > 1e-5:
            cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        # else:
        #     cx, cy = int(M["m10"] / (M["m00"]+1e-5)), int(M["m01"] / (M["m00"]+1e-5)) # or add 1e-5 to avoid division by zero

            center.append((cx, cy))         # add center to df, notice (X,Y)
            e = 4*math.pi*cv2.contourArea(contours[_])/cv2.arcLength(contours[_], closed= True)**2
            roundness.append(e)                                                         # add roundness to df

            # detection of intersection in ROI
            x, y, w, h = cv2.boundingRect(contours[_])
            eproi = ep_img[y:y+h, x:x+w]
            hctroi = hct_img[y:y+h, x:x+w]
            wbcroi = wbc_img[y:y+h, x:x+w]
            fuzzyroi = wbc_img[cy-int(ROI/2):cy+int(ROI/2), cx-int(ROI/2):cx+int(ROI/2)]        # check if the ROI is too fuzzy
            howblur = cv2.Laplacian(fuzzyroi, cv2.CV_64F).var()
            wbc_sharpness.append(howblur)
            # print(_, howblur)
            
            intersection_1 = cv2.bitwise_and(eproi, hctroi, mask = eproi)
            intersection_2 = cv2.bitwise_and(eproi, wbcroi, mask = eproi)
            if np.count_nonzero(intersection_1) >= HCT_THRESHOLD:
                hct.append(True)
            else:
                hct.append(False)
            if np.count_nonzero(intersection_2)/np.count_nonzero(eproi) >= WBC_THRESHOLD:
                wbc.append(True)
            else:
                wbc.append(False)

    data = {
        "center":center,
        "roundness":roundness,
        "hct":hct,
        "wbc":wbc,
        "wbc_sharpness":wbc_sharpness
    }
    return pd.DataFrame(data)


def image_postprocessing(ep_img: np.ndarray, hct_img: np.ndarray, wbc_img: np.ndarray, df: pd.DataFrame, marks= True, transparent= False, beta = 0.3):
    '''mark -> add mark on merge image\n
    transparent -> only mark no background'''
    SHARPNESS_THRESHOLD = 14000                                                         # laplace blurness detection of roi in wbc
    ROUNDNESS_THRESHOLD = 0.5

    CTC_MARK = (0,0,255)
    NONCTC_MARK = (18,153,255)
    LOWROUNDNESS_MARK = (221, 160, 221)
    BLUR_MARK = (250, 51, 153)
    MARKFONT = cv2.FONT_HERSHEY_TRIPLEX
    MARKCOORDINATE = (-30, -45)         # (x, y)
    
    RGBep = np.dstack((ep_img, ep_img, ep_img))                                         # white
    RGBhct = np.dstack((hct_img, np.zeros_like(hct_img), np.zeros_like(hct_img)))       # blue
    RGBwbc = np.dstack((np.zeros_like(wbc_img), wbc_img, np.zeros_like(wbc_img)))       # green
    if transparent:
        bg = np.dstack((np.zeros_like(ep_img), np.zeros_like(ep_img), np.zeros_like(ep_img)))

    # make merge image of epcam, hoechst and wbc
    hctwbc_mix = cv2.add(RGBhct, RGBwbc)
    merge = cv2.addWeighted(RGBep, 1-beta, hctwbc_mix, beta, gamma= 0)
    intersection = cv2.bitwise_and(ep_img, cv2.bitwise_or(hct_img, wbc_img))
    onlyep_mask = cv2.bitwise_and(ep_img, cv2.bitwise_not(intersection))

    # replace non intersection epcam area by pure white
    blk = cv2.bitwise_and(merge, merge, mask= cv2.bitwise_not(onlyep_mask))             # make region in mask black(clean)
    final = cv2.add(blk, np.dstack((onlyep_mask, onlyep_mask, onlyep_mask)))            # make region in mask white

    for _ in df.index:
        center = df['center'][_]
        e = df['roundness'][_]
        sharpness = df['wbc_sharpness'][_]
        if sharpness < SHARPNESS_THRESHOLD:
            color = BLUR_MARK
        elif (df['hct'][_]) & (not df['wbc'][_]):
            if e < ROUNDNESS_THRESHOLD:
                color = LOWROUNDNESS_MARK
            else: color = CTC_MARK
        else:
            color = NONCTC_MARK

        if marks:
            cv2.circle(final, center, 30, color, 2)
            cv2.putText(final, f'{_}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]),
            fontFace= MARKFONT, fontScale= 1,color= color, thickness= 1)
            cv2.putText(final, f'e={round(e,3)}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]+12),
            fontFace= MARKFONT, fontScale= 0.5,color= color, thickness= 1)
        if transparent:
            cv2.circle(bg, center, 30, color, 2)
            cv2.putText(bg, f'{_}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]),
            fontFace= MARKFONT, fontScale= 1,color= color, thickness= 1)
            cv2.putText(bg, f'e={round(e,3)}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]+12),
            fontFace= MARKFONT, fontScale= 0.5,color= color, thickness= 1)
    
    if transparent:
        markgray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        _, markmask = cv2.threshold(markgray, 1, 255, cv2.THRESH_BINARY)
        bgra = np.dstack((bg, markmask))
        return final, bgra
    return final, None


def show(img: np.ndarray, name: str):

    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, img)


def otsu_th(img: np.ndarray, kernal_size: tuple):
    blur = cv2.GaussianBlur(img, kernal_size, 0)
    ret, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return ret, th


def erode_dilate(img: np.ndarray, kernal_size= 3, iterations= 2):
    '''kernal size must be odd and >= 3'''
    kernal = np.ones((kernal_size,kernal_size), np.uint8)
    _ = cv2.erode(img, kernal, iterations= iterations)
    _ = cv2.dilate(_, kernal, iterations= iterations)
    return _


def crop(img: np.ndarray):
    block = int(np.floor(img.shape[0]/5))
    radius = int(block*1.5*math.sqrt(2))
    center = int(np.floor(img.shape[0]/2))
    mask = cv2.circle(np.zeros_like(img), (center, center), radius, (255, 255, 255), -1)
    masked = cv2.bitwise_and(img, mask)
    return masked

if __name__ == '__main__':

    os.chdir("data")
    img_list = glob.glob('*.jpg')
    img_dict = {}
    for i in img_list:
        if "fin_" in i:
            print(i)
            img_dict[i.split(".")[0]] = cv2.imread(i, cv2.IMREAD_UNCHANGED)

    ep = img_dict["fin_ep"]
    hct = img_dict["fin_hct"]
    wbc = img_dict["fin_wbc"]

    df = img2dataframe(ep, hct, wbc)
    image_postprocessing(ep, hct, wbc, df, transparent= True)
    with pd.ExcelWriter("x.xlsx") as writer:
        df.to_excel(writer)

    cv2.waitKey(0)
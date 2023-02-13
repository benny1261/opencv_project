import math
import glob
import cv2
import os
import numpy as np
from threading import Thread
import pandas as pd
from skimage import measure, morphology
import time

# preprocess parameters
BLUR_KERNAL = (5, 5)
CLIP_LIMIT = 4
TILEGRIDSIZE = 8
SPLIT = 5
ELIM_HCT_SIZE = 16
ELIM_EPCAM_SIZE = 81
ELIM_WBC_SIZE = 26
BETA = 0.4
# analysis parameters
HCT_AREA = 42
WBC_AREA = 60
HCT_THRESHOLD = 0.9                                                                 # ratio, epcam-hct intersection/average hct area
WBC_THRESHOLD = 0.3                                                                 # ratio, epcam-wbc intersection/average wbc area
SHARPNESS_THRESHOLD = 14000                                                         # laplace blurness detection of roi in wbc
ROUNDNESS_THRESHOLD = 0.7
DIAMETER_THRESHOLD = (10, 27)
# marking color
CTC_MARK = (0,0,255)
NONCTC_MARK = (18,153,255)
LOWROUNDNESS_MARK = (221, 160, 221)
BLUR_MARK = (250, 51, 153)
MARKFONT = cv2.FONT_HERSHEY_TRIPLEX
MARKCOORDINATE = (-30, -45)         # (x, y)

class Import_thread(Thread):                                                        # define a class that inherits from 'Thread' class
    def __init__(self, path: str):
        super().__init__()                                                          # run __init__ of parent class
        self.img_list = glob.glob(os.path.join(path, "*.jpg"))
        self.img_0, self.img_1, self.img_2, self.img_3 = None, None, None, None
        self.pre_0, self.pre_1, self.pre_2, self.pre_3 = None, None, None, None
        self.df: pd.DataFrame
        self.flag = False

    def run(self):                                                                  # overwrites run() method from parent class
        for i in self.img_list:
            if '_0.jpg' in i:
                self.img_0 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
            elif '_1.jpg' in i:
                self.img_1 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
            elif '_2.jpg' in i:
                self.img_2 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
            elif '_3.jpg' in i:
                self.img_3 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

        if any(x is None for x in [self.img_0, self.img_1, self.img_2, self.img_3]):
            raise IOError(FileNotFoundError, "insufficient required image")

        self.pre_0 = preprocess_full(self.img_0, ELIM_HCT_SIZE)
        self.pre_1 = preprocess_rare(self.img_1, ELIM_EPCAM_SIZE)
        self.pre_3 = preprocess_full(self.img_3, ELIM_WBC_SIZE)
        if any(x is None for x in [self.pre_0, self.pre_1, self.pre_3]):
            print("Error in preprocessing")
        else: 
            self.df = img2dataframe(self.pre_1, self.pre_0, self.pre_3)
            self.flag = True


class Cv_api:
    def __init__(self, app):
        self.app = app
        self.busy_flag = False

    def export_td(self):                                                            # needs to be able to thread repeatedly
        if self.app.import_flag:
            if not self.busy_flag:                                                  # block creating new thread before previous one terminates
                self.busy_flag = True
                # establish export thread
                thread = Thread(target= self.export)
                thread.start()
    
    def export(self):

        if self.app.export_fm.checkbtn['binary0'].get():
            cv2.imwrite(os.path.join(self.app.export_directory, "binary0.jpg"), self.app.pre_0)
        if self.app.export_fm.checkbtn['binary1'].get():
            cv2.imwrite(os.path.join(self.app.export_directory, "binary1.jpg"), self.app.pre_1)
        if self.app.export_fm.checkbtn['binary3'].get():
            cv2.imwrite(os.path.join(self.app.export_directory, "binary3.jpg"), self.app.pre_3)

        if self.app.home_fm.combobox['target'].get() == 'CTC':

            image_postprocessing(self.app.pre_1, self.app.pre_0, self.app.pre_3,
            self.app.df, self.app.result, path= self.app.export_directory,
            mark= self.app.export_fm.checkbtn['mark'].get(),
            mask= self.app.export_fm.checkbtn['mask'].get(), beta= BETA)

            if self.app.export_fm.checkbtn['raw_data'].get():
                with pd.ExcelWriter(os.path.join(self.app.export_directory, 'data.xlsx')) as writer:
                    self.app.df.to_excel(writer)
            if self.app.export_fm.checkbtn['result_data'].get():
                with pd.ExcelWriter(os.path.join(self.app.export_directory, 'result.xlsx')) as writer:
                    self.app.result.to_excel(writer)
        
        self.busy_flag = False
    
    def analysis(self, data:pd.DataFrame, hct_thres = HCT_THRESHOLD, wbc_thres = WBC_THRESHOLD, roundness_thres = ROUNDNESS_THRESHOLD,
                sharpness_thres = SHARPNESS_THRESHOLD, diameter_thres = DIAMETER_THRESHOLD) -> pd.DataFrame:
        '''Quick analysis for GUI feedback'''

        # True represents pass
        hct = []
        wbc = []
        roundness = []
        sharpness = []
        size = []
        target = []

        diameter_index = data.query('max_diameter >= @diameter_thres[0]').query('max_diameter <= @diameter_thres[1]').index.tolist()

        for _ in data.index:
            if data['hct_intersect'][_]/HCT_AREA >= hct_thres:
                hct.append(True)
            else:
                hct.append(False)

            if data['wbc_intersect'][_]/WBC_AREA < wbc_thres:
                wbc.append(True)
            else:
                wbc.append(False)

            if data['roundness'][_] >= roundness_thres:
                roundness.append(True)
            else:
                roundness.append(False)
            
            if data['wbc_sharpness'][_] >= sharpness_thres:
                sharpness.append(True)
            else:
                sharpness.append(False)
            
            if _ in diameter_index:
                size.append(True)
            else:
                size.append(False)
            
            check = [hct[-1], wbc[-1], roundness[-1], sharpness[-1], size[-1]]
            if any(x == False for x in check):
                target.append(False)
            else:
                target.append(True)

        result = {
            "hoechst":hct,
            "wbc":wbc,
            "roundness":roundness,
            "sharpness":sharpness,
            "size":size,
            "target":target
        }
        return pd.DataFrame(result)

    def count_target(self, dataframe:pd.DataFrame) -> int:
        '''A 'target' column in dataframe required'''
        target_amount = dataframe['target'].sum()
        nontarget_amount = (~dataframe['target']).sum()
        return target_amount, nontarget_amount


def img2dataframe(ep_img: np.ndarray, hct_img: np.ndarray, wbc_img: np.ndarray) -> pd.DataFrame:
    '''find contours from epcam img, calculate properties of each one and store in dataframe, 
also optional marks on exported image, parameter img should be grayscale\n
@ret pandas dataframe'''
    labeled = measure.label(ep_img, connectivity= 2)
    properties = measure.regionprops(labeled)
    ROI = 60
    center = []
    area = []
    roundness = []
    max_diameter = []
    roi = []
    hct = []
    wbc = []
    wbc_sharpness = []                                                                  # lower means more blur

    for prop in properties:
        cy, cx = map(round, prop.centroid)                  # (x, y)
        center.append((cx, cy))
        area.append(prop.area)
        roundness.append(4*math.pi*prop.area/prop.perimeter_crofton**2)
        max_diameter.append(prop.feret_diameter_max)
        roi.append(prop.slice)

        fuzzyroi = wbc_img[cy-int(ROI/2):cy+int(ROI/2), cx-int(ROI/2):cx+int(ROI/2)]        # check if wbc too fuzzy
        howblur = cv2.Laplacian(fuzzyroi, cv2.CV_64F).var()
        wbc_sharpness.append(howblur)

        # detection of intersection in ROI
        eproi = prop.image
        hctroi = hct_img[prop.slice]
        wbcroi = wbc_img[prop.slice]

        intersection_01 = np.logical_and(eproi, hctroi)
        intersection_13 = np.logical_and(eproi, wbcroi)
        hct.append(np.count_nonzero(intersection_01))
        wbc.append(np.count_nonzero(intersection_13))

    data = {
        "center":center,
        "area":area,
        "roundness":roundness,
        "max_diameter":max_diameter,
        "roi":roi,
        "hct_intersect":hct,
        "wbc_intersect":wbc,
        "wbc_sharpness":wbc_sharpness
    }
    return pd.DataFrame(data)


def image_postprocessing(ep_img: np.ndarray, hct_img: np.ndarray, wbc_img: np.ndarray, df: pd.DataFrame, result: pd.DataFrame,
                         path: str, mark= False, mask= False, beta = BETA):
    '''takes both information and result dataframe as input\n
    mark -> add mark on merge image\n
    mask -> only mark no background'''

    RGBep = np.dstack((ep_img, ep_img, ep_img))                                         # white
    RGBhct = np.dstack((hct_img, np.zeros_like(hct_img), np.zeros_like(hct_img)))       # blue
    RGBwbc = np.dstack((np.zeros_like(wbc_img), wbc_img, np.zeros_like(wbc_img)))       # green
    if mask:
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
        if result['target'][_]:
            color = CTC_MARK
        else:
            color = NONCTC_MARK

        if mark:
            cv2.circle(final, center, 30, color, 2)
            cv2.putText(final, f'{_}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]),        # label index starts from 1
            fontFace= MARKFONT, fontScale= 1,color= color, thickness= 1)
            cv2.putText(final, f'e={round(e,3)}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]+12),
            fontFace= MARKFONT, fontScale= 0.5,color= color, thickness= 1)
        if mask:
            cv2.circle(bg, center, 30, color, 2)
            cv2.putText(bg, f'{_}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]),
            fontFace= MARKFONT, fontScale= 1,color= color, thickness= 1)
            cv2.putText(bg, f'e={round(e,3)}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]+12),
            fontFace= MARKFONT, fontScale= 0.5,color= color, thickness= 1)
    if mark:
        cv2.imwrite(os.path.join(path, 'mark.jpg'), final)

    if mask:
        markgray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
        _, markmask = cv2.threshold(markgray, 1, 255, cv2.THRESH_BINARY)
        bgra = np.dstack((bg, markmask))
        cv2.imwrite(os.path.join(path, 'mask.png'), bgra)


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
    only01 = np.where(img>=1, 255, 0).astype(np.uint8)
    block = int(np.floor(img.shape[0]/5))
    radius = int(block*1.5*math.sqrt(2))
    center = int(np.floor(img.shape[0]/2))
    mask = cv2.circle(np.zeros_like(only01), (center, center), radius, (255, 255, 255), -1)
    masked = cv2.bitwise_and(only01, mask)
    return masked


def preprocess_rare(img: np.ndarray, small_object: int, clipLimit= CLIP_LIMIT, tileGridSize= TILEGRIDSIZE, blur_kernal= BLUR_KERNAL):

    clahe = cv2.createCLAHE(clipLimit= clipLimit, tileGridSize= (tileGridSize, tileGridSize))

    img_clahe = clahe.apply(img)
    ret, a = otsu_th(img_clahe, blur_kernal)                                        # use otsu's threshold but use original image for thresholding
    _, th = cv2.threshold(img, ret, 255, cv2.THRESH_BINARY)
    labeled = measure.label(th, connectivity= 2)
    labeled = morphology.remove_small_objects(labeled, min_size= small_object, connectivity= 2, out= labeled)
    fin = crop(labeled)
    
    return fin


def preprocess_full(img: np.ndarray, small_object: int, clipLimit= CLIP_LIMIT, tileGridSize= TILEGRIDSIZE, blur_kernal= BLUR_KERNAL):

    clahe = cv2.createCLAHE(clipLimit= clipLimit, tileGridSize= (tileGridSize, tileGridSize))

    split = [np.array_split(_, SPLIT, 1) for _ in np.array_split(img, SPLIT)]       # list comprehension

    for iter in np.ndindex((len(split), len(split[:]))):
        subimg = split[iter[0]][iter[1]]
        subimg_clahe = clahe.apply(subimg)
        ret, subimg_th = otsu_th(subimg_clahe, blur_kernal)
        labeled = measure.label(subimg_th, connectivity= 2)
        split[iter[0]][iter[1]] = morphology.remove_small_objects(labeled, min_size= small_object, connectivity= 2)
    fin = crop(np.block(split))

    return fin


# def preprocess_rare(img: np.ndarray, clipLimit= CLIP_LIMIT, tileGridSize= TILEGRIDSIZE, blur_kernal= BLUR_KERNAL):    # old method

#     clahe = cv2.createCLAHE(clipLimit= clipLimit, tileGridSize= (tileGridSize, tileGridSize))

#     img_clahe = clahe.apply(img)
#     ret, a = otsu_th(img_clahe, blur_kernal)                                        # use otsu's threshold but use original image for thresholding
#     _, th = cv2.threshold(img, ret, 255, cv2.THRESH_BINARY)
#     a = erode_dilate(th)
#     fin = crop(a)
    
#     return fin


# def preprocess_full(img: np.ndarray, clipLimit= CLIP_LIMIT, tileGridSize= TILEGRIDSIZE, blur_kernal= BLUR_KERNAL):    # old method

#     clahe = cv2.createCLAHE(clipLimit= clipLimit, tileGridSize= (tileGridSize, tileGridSize))

#     split = [np.array_split(_, SPLIT, 1) for _ in np.array_split(img, SPLIT)]       # list comprehension

#     for iter in np.ndindex((len(split), len(split[:]))):
#         subimg = split[iter[0]][iter[1]]
#         subimg_clahe = clahe.apply(subimg)
#         ret, subimg_th = otsu_th(subimg_clahe, blur_kernal)
#         split[iter[0]][iter[1]] = erode_dilate(subimg_th)
#     fin = crop(np.block(split))

#     return fin

if __name__ == '__main__':

    DATADIRECTORY = "data"
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
    os.chdir(root_dir)
    data_dir = os.path.join(os.getcwd(), DATADIRECTORY)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    img_list = glob.glob(os.path.join(DATADIRECTORY, "*.jpg"))

    for i in img_list:
        if '_0.jpg' in i:
            hct = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        elif '_1.jpg' in i:
            epcam = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        elif '_3.jpg' in i:
            wbc = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
    
    pre_0 = preprocess_full(hct, 0, imwrite= False, path= DATADIRECTORY)
    pre_1 = preprocess_rare(epcam, 1, imwrite= False, path= DATADIRECTORY)
    pre_3 = preprocess_full(wbc, 3, imwrite= False, path= DATADIRECTORY)

    df = img2dataframe(pre_1, pre_0, pre_3)
    start_time = time.time()
    api = Cv_api(None)
    api.analysis(df)
    end_time = time.time()
    print('analysis time = ', end_time-start_time)

    cv2.waitKey(0)
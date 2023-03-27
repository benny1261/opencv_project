import math
import glob
import cv2
import os
import numpy as np
from threading import Thread
import pandas as pd
from skimage import measure, morphology

# preprocess parameters
BLUR_KERNAL = (5, 5)
CLIP_LIMIT = 4
TILEGRIDSIZE = 8
SPLIT = 5
ELIM_HCT_SIZE = 16
ELIM_EPCAM_SIZE = 81
ELIM_WBC_SIZE = 30
BETA = 0.4
# analysis parameters
HCT_AREA = 42
WBC_AREA = 60
HCT_THRESHOLD = 0.9                                                                 # ratio, epcam-hct intersection/average hct area
WBC_THRESHOLD = 0.3                                                                 # ratio, epcam-wbc intersection/average wbc area
SHARPNESS_THRESHOLD = 14000                                                         # laplace blurness detection of roi in wbc
ROUNDNESS_THRESHOLD = 0.7
DIAMETER_THRESHOLD = (10, 27)
# postprocessing parameters
CTC_MARK = (0,0,255)
NONCTC_MARK = (18,153,255)
MARKFONT = cv2.FONT_HERSHEY_TRIPLEX
MARKCOORDINATE = (-30, -45)         # (x, y)

class Import_thread(Thread):                                                        # define a class that inherits from 'Thread' class
    def __init__(self, path: str):
        super().__init__()                                                          # run __init__ of parent class
        self.img_list = glob.glob(os.path.join(path, "*.jpg"))
        self.img_0, self.img_1, self.img_2, self.img_3 = None, None, None, None
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
        else:
            self.flag = True


class Preprocess_thread(Thread):                                                    # define a class that inherits from 'Thread' class
    def __init__(self, cell_type, *imgs):
        super().__init__()                                                          # run __init__ of parent class
        self.img_0, self.img_1, self.img_2, self.img_3 = imgs
        self.pre_0, self.pre_1, self.pre_2, self.pre_3 = None, None, None, None
        self.df: pd.DataFrame
        self.flag = False
        self.cell_type = cell_type

    def run(self):                                                                  # overwrites run() method from parent class

        if self.cell_type == 'CTC':
            self.pre_0 = preprocess(self.img_0, ELIM_HCT_SIZE)
            self.pre_1 = preprocess(self.img_1, ELIM_EPCAM_SIZE)
            self.pre_2 = preprocess(self.img_2, ELIM_EPCAM_SIZE)
            self.pre_3 = preprocess(self.img_3, ELIM_WBC_SIZE)

        if any(x is None for x in [self.pre_0, self.pre_1, self.pre_2, self.pre_3]):
            print("Error in preprocessing")
            return
        else:
            self.df = img2dataframe(self.pre_1, self.pre_0, self.pre_3)     # need to pass in cell type as well
            self.flag = True


class Cv_api:
    def __init__(self, master):
        self.master = master
        self.busy_flag = False

    def export_td(self):                                                            # needs to be able to thread repeatedly
        if self.master.preprocess_flag:
            if not self.busy_flag:                                                  # block creating new thread before previous one terminates
                self.busy_flag = True
                # establish export thread
                thread = Thread(target= self.export)
                thread.start()
    
    def export(self):

        if self.master.export_frame.binary0_switch.get():
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary0.jpg"), self.master.pre_0)
        if self.master.export_frame.binary1_switch.get():
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary1.jpg"), self.master.pre_1)
        if self.master.export_frame.binary3_switch.get():
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary3.jpg"), self.master.pre_3)

        if self.master.home_frame_type.get() == 'CTC':

            image_postprocessing(self.master.pre_0, self.master.pre_1, self.master.pre_3,
            self.master.df, self.master.result, path= self.master.export_dir.get(),
            mark= self.master.export_frame.mark_switch.get(),
            mask= self.master.export_frame.mask_switch.get(), beta= BETA)

            if self.master.export_frame.raw_data_switch.get():
                with pd.ExcelWriter(os.path.join(self.master.export_dir.get(), 'data.xlsx')) as writer:
                    self.master.df.to_excel(writer)
            if self.master.export_frame.result_data_switch.get():
                with pd.ExcelWriter(os.path.join(self.master.export_dir.get(), 'result.xlsx')) as writer:
                    self.master.result.to_excel(writer)

        self.busy_flag = False
    
def analysis(data:pd.DataFrame, hct_thres = HCT_THRESHOLD, wbc_thres = WBC_THRESHOLD, roundness_thres = ROUNDNESS_THRESHOLD,
            sharpness_thres = SHARPNESS_THRESHOLD, diameter_thres = DIAMETER_THRESHOLD) -> pd.DataFrame:
    '''Quick analysis for GUI feedback'''

    # True represents pass
    result = pd.DataFrame()
    result['hoechst'] = data['hct_intersect']/HCT_AREA >= hct_thres
    result['wbc'] = data['wbc_intersect']/WBC_AREA < wbc_thres
    result['roundness'] = data['roundness'] >= roundness_thres
    result['sharpness'] = data['wbc_sharpness'] >= sharpness_thres
    result['size'] = (data['max_diameter'] >= diameter_thres[0]) & (data['max_diameter'] <= diameter_thres[1])
    result['target'] = result.all(axis= 'columns')

    return result

def count_target(dataframe:pd.DataFrame) -> int:
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

def image_slice(orig_hct: np.ndarray, orig_ep: np.ndarray, orig_wbc: np.ndarray, df: pd.DataFrame, index, pixel_scale:int, canv_len:int)-> tuple:
    '''image slicing for toplevel viewer'''
    UV_COLOR = (0, 92, 255)     # RGB
    FITC_COLOR = (45, 255, 0)   # RGB
    APC_COLOR = (243, 255, 0)   # RGB
    PE_COLOR = (255, 0, 0)      # RGB
    RADIUS: int = 10
    THICKNESS: int = 1
    CIRCLE_COLOR = (255, 255, 255)

    half_canv = int(canv_len/2)
    half_img = int(half_canv/pixel_scale)
    center = df.at[index, 'center']         # (x, y)

    # slicing
    hct_slice = orig_hct[center[1]-half_img:center[1]+half_img, center[0]-half_img:center[0]+half_img].copy()
    ep_slice = orig_ep[center[1]-half_img:center[1]+half_img, center[0]-half_img:center[0]+half_img].copy()
    wbc_slice = orig_wbc[center[1]-half_img:center[1]+half_img, center[0]-half_img:center[0]+half_img].copy()

    # scale sliced image back to canv_length
    hct_slice = cv2.resize(hct_slice, (canv_len, canv_len), cv2.INTER_CUBIC)
    ep_slice = cv2.resize(ep_slice, (canv_len, canv_len), cv2.INTER_CUBIC)
    wbc_slice = cv2.resize(wbc_slice, (canv_len, canv_len), cv2.INTER_CUBIC)

    # normalize 255 to 1 then int(norm*COLOR), have to devide first to prevent uint8 overflow
    hct_slice = np.dstack((hct_slice/255*UV_COLOR[0], hct_slice/255*UV_COLOR[1], hct_slice/255*UV_COLOR[2])).astype(np.uint8)
    ep_slice = np.dstack((ep_slice/255*FITC_COLOR[0], ep_slice/255*FITC_COLOR[1], ep_slice/255*FITC_COLOR[2])).astype(np.uint8)
    wbc_slice = np.dstack((wbc_slice/255*PE_COLOR[0], wbc_slice/255*PE_COLOR[1], wbc_slice/255*PE_COLOR[2])).astype(np.uint8)

    # add circle
    cv2.circle(hct_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)
    cv2.circle(ep_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)
    cv2.circle(wbc_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)

    return hct_slice, ep_slice, None, wbc_slice

def image_postprocessing(hct_img: np.ndarray, ep_img: np.ndarray, wbc_img: np.ndarray, df: pd.DataFrame, result: pd.DataFrame,
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
            cv2.putText(final, f'{_}', (center[0]+MARKCOORDINATE[0], center[1]+MARKCOORDINATE[1]),        # label index starts from 0
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

def preprocess(img: np.ndarray, small_object: int, clipLimit= CLIP_LIMIT, tileGridSize= TILEGRIDSIZE, blur_kernal= BLUR_KERNAL):

    clahe = cv2.createCLAHE(clipLimit= clipLimit, tileGridSize= (tileGridSize, tileGridSize))
    block = int(np.floor(img.shape[0]/5))
    radius = int(block*1.5*math.sqrt(2))
    center = int(np.floor(img.shape[0]/2))

    # Create a meshgrid of pixel coordinates
    y, x = np.ogrid[:img.shape[0], :img.shape[1]]
    # Create a boolean mask for pixels within the circle
    mask = (x - center)**2 + (y - center)**2 <= radius**2

    if process_type(img, mask):
        split = [np.array_split(_, SPLIT, 1) for _ in np.array_split(img, SPLIT)]       # list comprehension

        for iter in np.ndindex((len(split), len(split[:]))):
            subimg = split[iter[0]][iter[1]]
            subimg_clahe = clahe.apply(subimg)
            ret, subimg_th = otsu_th(subimg_clahe, blur_kernal)
            labeled = measure.label(subimg_th, connectivity= 2)
            split[iter[0]][iter[1]] = morphology.remove_small_objects(labeled, min_size= small_object, connectivity= 2)
        fin = crop(np.block(split), mask)

    else:
        img_clahe = clahe.apply(img)
        ret, a = otsu_th(img_clahe, blur_kernal)                                        # use otsu's threshold but use original image for thresholding
        _, th = cv2.threshold(img, ret, 255, cv2.THRESH_BINARY)
        labeled = measure.label(th, connectivity= 2)
        labeled = morphology.remove_small_objects(labeled, min_size= small_object, connectivity= 2)
        fin = crop(labeled, mask)

    return fin

def process_type(img: np.ndarray, mask: np.ndarray):
    '''True for 'full', False for 'rare'.'''

    FULL_RARE_THRES = 46
    # calculate mean of pixels in the circle
    avg = np.mean(img, where= mask)
    print(avg > FULL_RARE_THRES)
    return avg > FULL_RARE_THRES

def crop(img: np.ndarray, mask: np.ndarray):
    '''only used in cropping labeled image (by measure.label)'''

    label_to_white = np.where(img>=1, 255, 0).astype(np.uint8)
    masked = np.where(mask, label_to_white, 0)
    return masked


if __name__ == '__main__':

    DATADIRECTORY = "data"
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(os.getcwd(), DATADIRECTORY)
    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)
    img_list = glob.glob(os.path.join(DATADIRECTORY, "*.jpg"))

    for i in img_list:
        if '_0.jpg' in i:
            img_0 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        elif '_1.jpg' in i:
            img_1 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        elif '_2.jpg' in i:
            img_2 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
        elif '_3.jpg' in i:
            img_3 = cv2.imread(i, cv2.IMREAD_GRAYSCALE)


    pre_0 = preprocess(img_0, ELIM_HCT_SIZE)
    pre_1 = preprocess(img_1, ELIM_EPCAM_SIZE)
    pre_2 = preprocess(img_2, ELIM_EPCAM_SIZE)
    pre_3 = preprocess(img_3, ELIM_WBC_SIZE)

    # df = img2dataframe(pre_1, pre_0, pre_3)
    # result = analysis(df)

    show(pre_0, '0')
    show(pre_1, '1')
    show(pre_2, '2')
    show(pre_3, '3')
    # show(pre_0[3000:3600, 3000:3600], '0_mag')
    # show(pre_0_t[3000:3600, 3000:3600], '0t_mag')

    cv2.waitKey(0)
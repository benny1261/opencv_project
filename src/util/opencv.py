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
DISTANCE_ELIM = 10
PROTOCOL_PRE = {'CTC':(ELIM_HCT_SIZE, ELIM_EPCAM_SIZE, None, ELIM_WBC_SIZE),
                'CTC(vimentin)':(ELIM_HCT_SIZE, ELIM_EPCAM_SIZE, ELIM_EPCAM_SIZE, ELIM_WBC_SIZE),
                'CTC(cd11b-)':(ELIM_HCT_SIZE, ELIM_EPCAM_SIZE, ELIM_WBC_SIZE, ELIM_WBC_SIZE),
                'CTC(cd11b+)':(ELIM_HCT_SIZE, ELIM_EPCAM_SIZE, ELIM_WBC_SIZE, ELIM_WBC_SIZE),
                'MDSC':(ELIM_HCT_SIZE, ELIM_EPCAM_SIZE, ELIM_WBC_SIZE, ELIM_WBC_SIZE),
                'T cell':(ELIM_HCT_SIZE, ELIM_EPCAM_SIZE, ELIM_WBC_SIZE, ELIM_WBC_SIZE)}
PROTOCOL_DF = {'CTC': (False, True, None, False),                                   # True= candidate, False= campare
               'CTC(vimentin)': (False, True, True, False),
               'CTC(cd11b-)': (False, True, False, False),
               'CTC(cd11b+)': (False, True, False, False),
               'MDSC': (False, True, False, False),
               'T cell':(False, True, False, False)}
PROTOCOL_NAME = {'CTC':('hct', 'epcam', None, 'cd45'),
                 'CTC(vimentin)':('hct', 'epcam', 'vimentin', 'cd45'),
                 'CTC(cd11b-)':('hct', 'epcam', 'cd11b', 'cd45'),
                 'CTC(cd11b+)':('hct', 'epcam', 'cd11b', 'cd45'),
                 'MDSC':('hct', 'epcam', 'cd11b', 'cd14'),
                 'T cell':('hct', 'epcam', 'cd25', 'cd4')}
# analysis parameters
HCT_AREA = 42
WBC_AREA = 60
HCT_THRESHOLD = 0.9                                                                 # ratio, epcam-hct intersection/average hct area
WBC_THRESHOLD = 0.3                                                                 # ratio, epcam-wbc intersection/average wbc area
SHARPNESS_THRESHOLD = 14000                                                         # laplace blurness detection of roi in wbc
ROUNDNESS_THRESHOLD = 0.7
DIAMETER_THRESHOLD = (10, 27)
PROTOCOL_PN = {'CTC':(True, None, None, False),                                     # True= positive index, False= negative index
               'CTC(vimentin)':(True, None, None, False),
               'CTC(cd11b-)':(True, None, False, False),
               'CTC(cd11b+)':(True, None, True, False),
               'MDSC':(True, None, True, True),
               'T cell':(True, None, True, True)}
PROTOCOL_THRES = {'CTC':(HCT_THRESHOLD, None, None, WBC_THRESHOLD),
                  'CTC(vimentin)':(HCT_THRESHOLD, None, None, WBC_THRESHOLD),
                  'CTC(cd11b-)':(HCT_THRESHOLD, None, WBC_THRESHOLD, WBC_THRESHOLD),
                  'CTC(cd11b+)':(HCT_THRESHOLD, None, WBC_THRESHOLD, WBC_THRESHOLD),
                  'MDSC':(HCT_THRESHOLD, None, WBC_THRESHOLD, WBC_THRESHOLD),
                  'T cell':(HCT_THRESHOLD, None, WBC_THRESHOLD, WBC_THRESHOLD)}
PROTOCOL_AREA = {'CTC':(HCT_AREA, None, None, WBC_AREA),
                 'CTC(vimentin)':(HCT_AREA, None, None, WBC_AREA),
                 'CTC(cd11b-)':(HCT_AREA, None, WBC_AREA, WBC_AREA),
                 'CTC(cd11b+)':(HCT_AREA, None, WBC_AREA, WBC_AREA),
                 'MDSC':(HCT_AREA, None, WBC_AREA, WBC_AREA),
                 'T cell':(HCT_AREA, None, WBC_AREA, WBC_AREA)}
# postprocessing parameters
TARGET_MARK = (0,0,255)
NONTARGET_MARK = (18,153,255)
MARKFONT = cv2.FONT_HERSHEY_TRIPLEX
MARKCOORDINATE = (-30, -45)         # (x, y)

class Import_thread(Thread):                                                        # define a class that inherits from 'Thread' class
    def __init__(self, path: str):
        super().__init__()                                                          # run __init__ of parent class
        self.img_list = glob.glob(os.path.join(path, "*.jpg"))
        self.imgs = (None, None, None, None)
        self.flag = False

    def run(self):                                                                  # overwrites run() method from parent class
        temp = [None, None, None, None]
        for i in self.img_list:
            if '_0.jpg' in i:
                temp[0] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
            elif '_1.jpg' in i:
                temp[1] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
            elif '_2.jpg' in i:
                temp[2] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)
            elif '_3.jpg' in i:
                temp[3] = cv2.imread(i, cv2.IMREAD_GRAYSCALE)

        if any(x is None for x in temp):
            raise IOError(FileNotFoundError, "insufficient required image")
        else:
            self.imgs = tuple(temp)
            self.flag = True


class Preprocess_thread(Thread):                                                    # define a class that inherits from 'Thread' class
    def __init__(self, cell_type, *imgs):
        super().__init__()                                                          # run __init__ of parent class
        self.imgs = imgs
        self.pres = (None, None, None, None)
        self.df: pd.DataFrame
        self.flag = False
        self.cell_type = cell_type

    def run(self):                                                          # overwrites run() method from parent class

        temp = preprocess(self.cell_type, *self.imgs)
        # exclude elements where it is None in protocal
        if any(ai is None and bi is not None for ai, bi in zip(temp, PROTOCOL_PRE.values())):
            print("Error in preprocessing")
            return
        else:
            self.pres = temp
            self.df = img2dataframe(self.cell_type, *self.pres)
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
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary0.jpg"), self.master.pres[0])
        if self.master.export_frame.binary1_switch.get():
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary1.jpg"), self.master.pres[1])
        if self.master.export_frame.binary2_switch.get():
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary2.jpg"), self.master.pres[2])
        if self.master.export_frame.binary3_switch.get():
            cv2.imwrite(os.path.join(self.master.export_dir.get(), "binary3.jpg"), self.master.pres[3])

        if self.master.export_frame.mask_switch.get():
            mask = image_postprocessing(self.master.df, self.master.result, *self.master.pres)
            cv2.imwrite(os.path.join(self.master.export_dir.get(), 'mask.png'), mask)

        if self.master.export_frame.raw_data_switch.get():
            with pd.ExcelWriter(os.path.join(self.master.export_dir.get(), 'data.xlsx')) as writer:
                self.master.df.to_excel(writer)
        if self.master.export_frame.result_data_switch.get():
            with pd.ExcelWriter(os.path.join(self.master.export_dir.get(), 'result.xlsx')) as writer:
                self.master.result.to_excel(writer)

        self.busy_flag = False

def analysis(cell_type: str, data:pd.DataFrame, intersec_thres: tuple, roundness_thres = ROUNDNESS_THRESHOLD, sharpness_thres = SHARPNESS_THRESHOLD,
            diameter_thres = DIAMETER_THRESHOLD) -> pd.DataFrame:
    '''Quick analysis for GUI feedback\n
    @param intersec_thres: (thres_0, thres_1...), element can be None'''

    index_intersec = [i for i in range(4) if PROTOCOL_PN[cell_type][i] is not None]
    # True represents pass
    result = pd.DataFrame()
    result['roundness'] = data['roundness'] >= roundness_thres
    result['sharpness'] = data['sharpness'] >= sharpness_thres
    result['diameter'] = (data['diameter'] >= diameter_thres[0]) & (data['diameter'] <= diameter_thres[1])

    for i in index_intersec:
        if PROTOCOL_PN[cell_type][i]:
            result['intersec_'+PROTOCOL_NAME[cell_type][i]] = data['intersec_'+PROTOCOL_NAME[cell_type][i]]/PROTOCOL_AREA[cell_type][i] >= intersec_thres[i]
        else:
            result['intersec_'+PROTOCOL_NAME[cell_type][i]] = data['intersec_'+PROTOCOL_NAME[cell_type][i]]/PROTOCOL_AREA[cell_type][i] < intersec_thres[i]
    result['target'] = result.all(axis= 'columns')

    return result

def count_target(dataframe:pd.DataFrame) -> int:
    '''A 'target' column in dataframe required'''
    target_amount = dataframe['target'].sum()
    nontarget_amount = (~dataframe['target']).sum()
    return target_amount, nontarget_amount

def img2dataframe(cell_type: str, *pres: np.ndarray) -> pd.DataFrame:
    '''find contours from epcam img, calculate properties of each one and store in dataframe,\n
    also optional marks on exported image, parameter img should be grayscale'''

    index_true = [i for i in range(4) if PROTOCOL_DF[cell_type][i]== True]          # these are channels of suspicious cells
    index_false = [i for i in range(4) if PROTOCOL_DF[cell_type][i]== False]        # these are channels for cell mark camparison
    ROI = 60

    counter = 0

    for i in index_true:
        counter+=1
        labeled = measure.label(pres[i], connectivity= 2)
        properties = measure.regionprops(labeled)

        basic_cols = []
        inter_cols = {}
        for channel_inter in index_false:
            inter_cols[channel_inter] = []

        for prop in properties:

            cy, cx = map(round, prop.centroid)          # cv2.circle uses (x, y)
            roundness = 4*math.pi*prop.area/prop.perimeter_crofton**2
            fuzzyroi = pres[3][cy-int(ROI/2):cy+int(ROI/2), cx-int(ROI/2):cx+int(ROI/2)]    # check if channel_3 too fuzzy
            sharpness = cv2.Laplacian(fuzzyroi, cv2.CV_64F).var()

            basic_cols.append(pd.DataFrame({'center_y': [cy], 'center_x': [cx], 'flourescent': [PROTOCOL_NAME[cell_type][i]], 'area': [prop.area],
                                            'roundness': [roundness], 'diameter': [prop.feret_diameter_max], 'sharpness': [sharpness]}))
            
            # detection of intersection in ROI
            roi_self = prop.image

            for channel_inter in index_false:
                roi_inter = pres[channel_inter][prop.slice]
                bits_inter = np.count_nonzero(np.where((roi_self>0) & (roi_inter>0), 1, 0))
                inter_cols[channel_inter].append(pd.DataFrame({'intersec_'+PROTOCOL_NAME[cell_type][channel_inter]: [bits_inter]}))

        subdf = pd.concat(basic_cols, axis= 0).reset_index(drop= True)
        for channel_inter in index_false:
            subdf = pd.concat([subdf, pd.concat(inter_cols[channel_inter], axis= 0).reset_index(drop= True)], axis= 1)
        
        if counter == 1:
            df = subdf
        else:
            # eliminate repeated data
            for sub_index in range(subdf.shape[0]):
                for main_index in range(df.shape[0]):
                    if abs(subdf.iloc[sub_index,0]-df.iloc[main_index,0])<=DISTANCE_ELIM and abs(subdf.iloc[sub_index,1]-df.iloc[main_index,1])<=DISTANCE_ELIM:
                        subdf.drop(sub_index, inplace= True)

            df = pd.concat([df, subdf], axis= 0).reset_index(drop= True)
    df.sort_values(['center_y', 'center_x'], inplace= True)
    return df.reset_index(drop= True)

def image_slice(df: pd.DataFrame, index, pixel_scale:int, canv_len:int, *imgs: np.ndarray)-> tuple:
    '''image slicing for toplevel viewer'''
    UV_COLOR = (0, 92, 255)     # RGB
    FITC_COLOR = (45, 255, 0)   # RGB
    PE_COLOR = (243, 255, 0)    # RGB
    APC_COLOR = (255, 0, 0)     # RGB
    
    RADIUS: int = 10
    THICKNESS: int = 1
    CIRCLE_COLOR = (255, 255, 255)

    half_canv = int(canv_len/2)
    half_img = int(half_canv/pixel_scale)
    cy = df.at[index, 'center_y']
    cx = df.at[index, 'center_x']

    # slicing
    uv_slice = imgs[0][cy-half_img: cy+half_img, cx-half_img: cx+half_img].copy()
    fitc_slice = imgs[1][cy-half_img: cy+half_img, cx-half_img: cx+half_img].copy()
    pe_slice = imgs[2][cy-half_img: cy+half_img, cx-half_img: cx+half_img].copy()
    apc_slice = imgs[3][cy-half_img: cy+half_img, cx-half_img: cx+half_img].copy()

    # scale sliced image back to canv_length
    uv_slice = cv2.resize(uv_slice, (canv_len, canv_len), cv2.INTER_CUBIC)
    fitc_slice = cv2.resize(fitc_slice, (canv_len, canv_len), cv2.INTER_CUBIC)
    pe_slice = cv2.resize(pe_slice, (canv_len, canv_len), cv2.INTER_CUBIC)
    apc_slice = cv2.resize(apc_slice, (canv_len, canv_len), cv2.INTER_CUBIC)

    # normalize 255 to 1 then int(norm*COLOR), have to devide first to prevent uint8 overflow
    uv_slice = np.dstack((uv_slice/255*UV_COLOR[0], uv_slice/255*UV_COLOR[1], uv_slice/255*UV_COLOR[2])).astype(np.uint8)
    fitc_slice = np.dstack((fitc_slice/255*FITC_COLOR[0], fitc_slice/255*FITC_COLOR[1], fitc_slice/255*FITC_COLOR[2])).astype(np.uint8)
    pe_slice = np.dstack((pe_slice/255*PE_COLOR[0], pe_slice/255*PE_COLOR[1], pe_slice/255*PE_COLOR[2])).astype(np.uint8)
    apc_slice = np.dstack((apc_slice/255*APC_COLOR[0], apc_slice/255*APC_COLOR[1], apc_slice/255*APC_COLOR[2])).astype(np.uint8)

    # add circle, note that cv2 uses (x, y) instead
    cv2.circle(uv_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)
    cv2.circle(fitc_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)
    cv2.circle(pe_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)
    cv2.circle(apc_slice, center= (half_canv, half_canv), radius= RADIUS*pixel_scale, color= CIRCLE_COLOR, thickness= THICKNESS)

    return uv_slice, fitc_slice, pe_slice, apc_slice

def image_postprocessing(df: pd.DataFrame, result: pd.DataFrame, *pres: np.ndarray):
    '''takes both information and result dataframe as input\n
    mask -> only mark no background'''

    bg = np.dstack((np.zeros_like(pres[0]), np.zeros_like(pres[0]), np.zeros_like(pres[0])))

    for _ in df.index:
        cx, cy = df['center_x'][_], df['center_y'][_]
        e = df['roundness'][_]
        if result['target'][_]:
            color = TARGET_MARK
        else:
            color = NONTARGET_MARK

        cv2.circle(bg, (cx, cy), 30, color, 2)
        cv2.putText(bg, f'{_}', (cx+MARKCOORDINATE[0], cy+MARKCOORDINATE[1]),       # label index starts from 0
        fontFace= MARKFONT, fontScale= 1,color= color, thickness= 1)
        cv2.putText(bg, f'e={round(e,3)}', (cx+MARKCOORDINATE[0], cy+MARKCOORDINATE[1]+12),
        fontFace= MARKFONT, fontScale= 0.5,color= color, thickness= 1)

    markgray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
    _, markmask = cv2.threshold(markgray, 1, 255, cv2.THRESH_BINARY)
    bgra = np.dstack((bg, markmask))                                                # make 4th alpha channel

    return bgra

def show(img: np.ndarray, name: str):

    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.imshow(name, img)

def otsu_th(img: np.ndarray, kernal_size: tuple):
    blur = cv2.GaussianBlur(img, kernal_size, 0)
    ret, th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return ret, th

def preprocess(cell_type: str, *imgs: np.ndarray, clipLimit= CLIP_LIMIT, tileGridSize= TILEGRIDSIZE, blur_kernal= BLUR_KERNAL)-> tuple:
    '''pass in image in tuple ex: (img_0, img_1...)'''

    clahe = cv2.createCLAHE(clipLimit= clipLimit, tileGridSize= (tileGridSize, tileGridSize))
    block = int(np.floor(imgs[0].shape[0]/5))
    radius = int(block*1.5*math.sqrt(2))
    center = int(np.floor(imgs[0].shape[0]/2))

    # Create a meshgrid of pixel coordinates
    y, x = np.ogrid[:imgs[0].shape[0], :imgs[0].shape[1]]
    # Create a boolean mask for pixels within the circle
    mask = (x - center)**2 + (y - center)**2 <= radius**2
    pres = []

    for _ in range(len(imgs)):
        if PROTOCOL_PRE[cell_type][_] == None:
            fin = None

        elif process_type(imgs[_], mask):
            split = [np.array_split(i, SPLIT, 1) for i in np.array_split(imgs[_], SPLIT)]       # list comprehension

            for iter in np.ndindex((len(split), len(split[:]))):
                subimg = split[iter[0]][iter[1]]
                subimg_clahe = clahe.apply(subimg)
                ret, subimg_th = otsu_th(subimg_clahe, blur_kernal)
                labeled = measure.label(subimg_th, connectivity= 2)
                split[iter[0]][iter[1]] = morphology.remove_small_objects(labeled, min_size= PROTOCOL_PRE[cell_type][_], connectivity= 2)
            fin = crop(np.block(split), mask)

        else:
            img_clahe = clahe.apply(imgs[_])
            ret, a = otsu_th(img_clahe, blur_kernal)                                        # use otsu's threshold but use original image for thresholding
            b, th = cv2.threshold(imgs[_], ret, 255, cv2.THRESH_BINARY)
            labeled = measure.label(th, connectivity= 2)
            labeled = morphology.remove_small_objects(labeled, min_size= PROTOCOL_PRE[cell_type][_], connectivity= 2)
            fin = crop(labeled, mask)
        
        pres.append(fin)

    return tuple(pres)

def process_type(img: np.ndarray, mask: np.ndarray):
    '''True for 'full', False for 'rare'.'''

    FULL_RARE_THRES = 46
    # calculate mean of pixels in the circle
    avg = np.mean(img, where= mask)
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

    imgs = (img_0, img_1, img_2, img_3)
    pres = preprocess('CTC(vimentin)', *imgs)

    def img2dataframe_ttt(cell_type: str, *pres: np.ndarray) -> pd.DataFrame:
        '''find contours from epcam img, calculate properties of each one and store in dataframe,\n
        also optional marks on exported image, parameter img should be grayscale'''

        index_true = [i for i in range(4) if PROTOCOL_DF[cell_type][i]== True]          # these are channels of suspicious cells
        index_false = [i for i in range(4) if PROTOCOL_DF[cell_type][i]== False]        # these are channels for cell mark camparison
        ROI = 60

        counter = 0

        for i in index_true:
            counter+=1
            labeled = measure.label(pres[i], connectivity= 2)
            properties = measure.regionprops(labeled)

            basic_cols = []
            inter_cols = {}
            for channel_inter in index_false:
                inter_cols[channel_inter] = []

            for prop in properties:

                cy, cx = map(round, prop.centroid)          # cv2.circle uses (x, y)
                roundness = 4*math.pi*prop.area/prop.perimeter_crofton**2
                fuzzyroi = pres[3][cy-int(ROI/2):cy+int(ROI/2), cx-int(ROI/2):cx+int(ROI/2)]    # check if channel_3 too fuzzy
                sharpness = cv2.Laplacian(fuzzyroi, cv2.CV_64F).var()

                basic_cols.append(pd.DataFrame({'center_y': [cy], 'center_x': [cx], 'flourescent': [PROTOCOL_NAME[cell_type][i]], 'area': [prop.area],
                                                'roundness': [roundness], 'diameter': [prop.feret_diameter_max], 'sharpness': [sharpness]}))
                
                # detection of intersection in ROI
                roi_self = prop.image

                for channel_inter in index_false:
                    roi_inter = pres[channel_inter][prop.slice]
                    bits_inter = np.count_nonzero(np.where((roi_self>0) & (roi_inter>0), 1, 0))
                    inter_cols[channel_inter].append(pd.DataFrame({'intersec_'+PROTOCOL_NAME[cell_type][channel_inter]: [bits_inter]}))

            subdf = pd.concat(basic_cols, axis= 0).reset_index(drop= True)
            for channel_inter in index_false:
                subdf = pd.concat([subdf, pd.concat(inter_cols[channel_inter], axis= 0).reset_index(drop= True)], axis= 1)
            
            if counter == 1:
                df = subdf
            else:
                # eliminate repeated data
                for sub_index in range(subdf.shape[0]):
                    for main_index in range(df.shape[0]):
                        if abs(subdf.iloc[sub_index,0]-df.iloc[main_index,0])<=DISTANCE_ELIM and abs(subdf.iloc[sub_index,1]-df.iloc[main_index,1])<=DISTANCE_ELIM:
                            subdf.drop(sub_index, inplace= True)

                df = pd.concat([df, subdf], axis= 0).reset_index(drop= True)
        df.sort_values(['center_y', 'center_x'], inplace= True)
        return df.reset_index(drop= True)

    def analysis_ttt(cell_type: str, data:pd.DataFrame, intersec_thres: tuple, roundness_thres = ROUNDNESS_THRESHOLD, sharpness_thres = SHARPNESS_THRESHOLD,
                     diameter_thres = DIAMETER_THRESHOLD) -> pd.DataFrame:
        '''Quick analysis for GUI feedback\n
        @param intersec_thres: (thres_0, thres_1...), element can be None'''

        index_intersec = [i for i in range(4) if PROTOCOL_PN[cell_type][i] is not None]
        # True represents pass
        result = pd.DataFrame()
        result['roundness'] = data['roundness'] >= roundness_thres
        result['sharpness'] = data['sharpness'] >= sharpness_thres
        result['diameter'] = (data['diameter'] >= diameter_thres[0]) & (data['diameter'] <= diameter_thres[1])

        for i in index_intersec:
            if PROTOCOL_PN[cell_type][i]:
                result['intersec_'+PROTOCOL_NAME[cell_type][i]] = data['intersec_'+PROTOCOL_NAME[cell_type][i]]/PROTOCOL_AREA[cell_type][i] >= intersec_thres[i]
            else:
                result['intersec_'+PROTOCOL_NAME[cell_type][i]] = data['intersec_'+PROTOCOL_NAME[cell_type][i]]/PROTOCOL_AREA[cell_type][i] < intersec_thres[i]
        result['target'] = result.all(axis= 'columns')

        return result

    df = img2dataframe_ttt('CTC(vimentin)', *pres)
    print(df)

    result = analysis_ttt('CTC(vimentin)', df, PROTOCOL_THRES['CTC(vimentin)'])
    print(result)

    # show(pres[0], '0')
    # show(pres[1], '1')
    # # show(pres[2], '2')
    # show(pres[3], '3')
    # # show(pre_0[3000:3600, 3000:3600], '0_mag')
    # # show(pre_0_t[3000:3600, 3000:3600], '0t_mag')

    # cv2.waitKey(0)
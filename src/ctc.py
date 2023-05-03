import os
import cv2
import tkinter as tk
from tkinter import messagebox
import numpy as np
import time
from skimage import measure, morphology
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

'''Image sequence must be: hoechst -> epcam -> CD45'''

class MyHandler(FileSystemEventHandler):
    def __init__(self, tk) -> None:
        super().__init__()
        self.queue = []
        self.img_queue = []
        self.tk = tk

    def on_created(self, event):
        # Handle file creation event here
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            print(f"{filename} has been created")
            # self.counter = int(re.search(r"(\d+)\.jpg", filename).group(1))

            # update queues
            self.queue.append(event.src_path)
            if len(self.queue)%3 == 0:
                self.import_img(self.queue[-3:])
                self.preprocess()

                logic = cv2.bitwise_and(self.img_queue[1], cv2.bitwise_not(self.img_queue[2]), mask= self.img_queue[1])
                logic = cv2.bitwise_and(logic, self.img_queue[0])
                logic_new = self.check_logic(logic)
                # original result with small island will be preserved if no large island found
                if logic_new is None:
                    self.tk.after(0, lambda: messagebox.showinfo('Message', 'Finished', parent = self.tk))
                else:
                    logic = logic_new
                    self.tk.after(0, lambda: messagebox.showwarning('Message', 'CTC', parent = self.tk))                    
                cv2.imwrite('logic.jpg', logic)
    
    def import_img(self, img_paths):
        self.img_queue = []
        for path in img_paths:
            self.img_queue.append(cv2.imread(path, cv2.IMREAD_GRAYSCALE))

    def preprocess(self):
        'overwrites img queue'
        for _ in range(3):
            ret, masked = cv2.threshold(self.img_queue[_], 0, 255, cv2.THRESH_TRIANGLE)
            labeled = np.array(measure.label(masked, connectivity= 2), bool)
            labeled = morphology.remove_small_holes(labeled, area_threshold = 30, connectivity= 2, out = labeled)
            labeled = morphology.remove_small_objects(labeled, min_size= 16, connectivity= 2, out = labeled)
            npimg = np.where(labeled > 0, 255, 0).astype(np.uint8)
            # cv2.imwrite(f'{_}.jpg', npimg)
            self.img_queue[_] = npimg

    def check_logic(self, logic):
        '''determines whether the result is suspicious, returns RGB image if true'''

        labeled = measure.label(logic, connectivity= 2)
        labeled = morphology.remove_small_objects(labeled, min_size= 20, connectivity= 2, out = labeled)
        labeled, label_num = measure.label(labeled, return_num = True, connectivity= 2)
        print('number of suspicious cells: ', label_num)
        if label_num:
            npimg = np.where(labeled > 0, 255, 0)
            stacked = np.dstack((np.zeros_like(npimg), np.zeros_like(npimg), npimg)).astype(np.uint8)       # BGR
            return stacked
        

if __name__ == "__main__":
    watchpath = r'C:/Users/ohyea/OneDrive/Desktop/SGImage'
    resultpath = watchpath+r'/result'
    if not os.path.isdir(resultpath):
        os.mkdir(resultpath)
    os.chdir(resultpath)

    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    root.withdraw()

    event_handler = MyHandler(root)
    observer = Observer()
    observer.schedule(event_handler, path= watchpath, recursive=False)
    observer.start()
    root.mainloop()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

# cv2.waitKey(0)
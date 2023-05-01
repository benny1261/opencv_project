import os
import cv2
import re
import numpy as np
import time
from skimage import measure, morphology
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.queue = []
        self.img_queue = []

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
            labeled = morphology.remove_small_holes(labeled, area_threshold = 30, connectivity= 2)
            labeled = morphology.remove_small_objects(labeled, min_size= 16, connectivity= 2)
            npimg = np.where(labeled > 0, 255, 0).astype(np.uint8)
            # cv2.imwrite(f'{_}.jpg', npimg)
            self.img_queue[_] = npimg
        

if __name__ == "__main__":
    os.chdir(r'C:\Users\ohyea\OneDrive\Desktop')
    watchpath = r'C:\Users\ohyea\OneDrive\Desktop\SGImage'
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path= watchpath, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

# cv2.waitKey(0)
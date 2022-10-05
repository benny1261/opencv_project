# opencv_project

a project assisting senier

## description

use opencv [youtube](https://www.youtube.com/watch?v=xjrykYpaBBM)

or imageJ2 [doc](https://github.com/imagej/pyimagej/blob/master/doc/README.md)

## github marks

U:新建檔案

A:加入追蹤

M:與上個commit有差異

## opencv commands

img_gray = cv2.imread('image.jpg', cv2.IMREAD_GRAYSCALE)     #只讀灰階值

cv2.namedWindow('My Image', cv2.WINDOW_NORMAL)               #讓圖片視窗可調整大小

## instance function

initailize:

```python
def __init__(self):
    self.var = []
```

## image properties

* grayscale: 0(black)----255(white)
* default opencv channel: BGR
* shape(y, x, c)

## useful plots

line plot:

```python
hist = cv2.calcHist([img], [0], None, [256], [0, 256])
plt.plot(hist)                              # "label = ..." is an optional param, then plt.legend()
plt.show()
```

bar plot:

```python
plt.hist(img.ravel(), 256, [0, 256])        # ravel turn into 1d array
plt.show()
```

## Roundness detection

e = 4pi*A/P^2

## Future Works:

* change contour in epcam to colors
* delete or ignore low roundness signal
* read method(batches, filename)
* variation in epcam pre-processing
* GUI

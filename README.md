# opencv_project

a project assisting senier

## description

use opencv [youtube](https://www.youtube.com/watch?v=xjrykYpaBBM)

## github marks

U:新建檔案

A:加入追蹤

M:與上個commit有差異

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

## Cell properties

hoechst ~ 40-45 pixels
cellsize = 12^2~25^2

## custom tkinter

Source [link](https://github.com/TomSchimansky/CustomTkinter)

Wiki [link](https://github.com/TomSchimansky/CustomTkinter/wiki)

## flourescent criterions

below are in sequence: UV, FITC, PE, APC

* untransformed CTC: Hoechst+, Epcam+, X, CD45-
* CTC: Hoechst+, Epcam+(or)Vimentin+, CD45-
* M-MDSC/PMN-MDSC: Hoechst? Epcam? CD11b+ CD14+
* t-cell: Hoechst? Epcam? CD25+ CD4+

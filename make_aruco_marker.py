import cv2
import cv2.aruco as aruco
import numpy as np

idnum = 100
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
marker = aruco.drawMarker(aruco_dict, idnum, 1000)
path = '/home/duke/Documents/aruco/'
cv2.imwrite(str(path) + "marker" + str(idnum) +  ".jpg", marker)




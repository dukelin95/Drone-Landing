import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from Tkinter import *
import cv2.aruco as aruco
import sys
from time import gmtime, strftime
import math

def distance(x1, y1, x2, y2):
	return math.hypot(x2-x1, y2-y1)
	
def take_pic(event):

	rawCapt = PiRGBArray(camera, size = (640, 480))
	time.sleep(0.1)
	camera.capture(rawCapt, format = "bgr", use_video_port = True)
	vid = rawCapt.array
	rawCapt.truncate(0)
	
	corners, ids, rejects = aruco.detectMarkers(vid, aruco_dic)

	if len(corners) is not 0: 
		side1 = distance(corners[0][0][0][0], corners[0][0][0][1], corners[0][0][1][0], corners[0][0][1][1]) 
		side2 = distance(corners[0][0][0][0], corners[0][0][0][1], corners[0][0][2][0], corners[0][0][2][1])
		
		print side1
		print side2
		
		area = side1 * side2
		area_str = "Area in pixels: " + str(area)

		cv2.putText(vid, area_str, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)

	found = aruco.drawDetectedMarkers(vid, corners, ids)	
	
	cv2.imshow('vid',vid)
	
	if cv2.waitKey(0) & 0xFF == ord('s'):
		path = sys.path[0]
		cv2.imwrite(str(path) + "/" + strftime("%Y_%m_%d__%I_%M_%S", gmtime()) + "_DistPic.jpg" , found)
		print "Picture saved"
		cv2.destroyAllWindows()
	else:
		cv2.destroyAllWindows()

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.meter_mode = 'matrix'
camera.shutter_speed = 6000
camera.ISO = 800

aruco_dic = aruco.Dictionary_get(aruco.DICT_6X6_250)

master = Tk()
master.title("Get Area")

instr = Label(master, text = "Press t to take a picture \n Press s on the pictures window to save picture \n Press any other letter on pictures window to close window")
instr.pack()

master.bind("<KeyRelease-t>", take_pic)

close = input("Insert E to end ")
if close == 'E':
	camera.close()
	cv2.destroyAllWindows()

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from Tkinter import *
import cv2.aruco as aruco
import sys
from time import gmtime, strftime

def on_key_release(event):
	path = sys.path[0]
	cv2.putText(found, iso_str, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.putText(found, shutter_str, (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.putText(found, awb_str, (30, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.imwrite(str(path) + "/" + strftime("%Y_%m_%d__%I_%M_%S", gmtime()) + "_test.jpg" , found)
	print "Picture saved"
	

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
camera.awb_mode = 'off'
#camera.awb_mode = 'sunlight'

aruco_dic = aruco.Dictionary_get(aruco.DICT_6X6_250)

master = Tk()
master.title("Adjust")

awbgain_r = Scale(master, from_=0.1, to=8, orient=HORIZONTAL, label = 'awb_gain red', length = 300, resolution = 0.1, showvalue = 0.1)
awbgain_r.set(1.5)
awbgain_r.pack()

awbgain_b = Scale(master, from_=0.1, to=8, orient=HORIZONTAL, label = 'awb_gain blue', length = 300, resolution = 0.1, showvalue = 0.1)
awbgain_b.set(1.5)
awbgain_b.pack()

iso = Scale(master, from_=100, to=800, orient=HORIZONTAL, label = 'ISO', length = 300, resolution = 100, showvalue = 100)
iso.set(800)
iso.pack()

shutter = Scale(master, from_=100, to=6000, orient=HORIZONTAL, label = 'shutter speed', length = 300, resolution = 100, showvalue = 100)
shutter.set(4000)
shutter.pack()

master.bind("<KeyRelease-s>", on_key_release)

while (1):
	master.update_idletasks()
	master.update()
	
	camera.iso = iso.get()
	iso_str = "ISO: " + str(camera.iso)
	#print("ISO: " + str(camera.iso))

	camera.shutter_speed = shutter.get()
	shutter_str = "SS: " + str(camera.shutter_speed)
	#print("Shutter speed: " + str(camera.shutter_speed))

	camera.awb_gains = (awbgain_r.get(), awbgain_b.get())
	awb_str = "AWB_G: " + str(float(camera.awb_gains[0])) + ", " + str(float(camera.awb_gains[1]))
	#print("awb_gain: " + str(camera.awb_gains))

	rawCapt = PiRGBArray(camera, size = (640, 480))
	time.sleep(0.1)
	camera.capture(rawCapt, format = "bgr", use_video_port = True)
	vid = rawCapt.array
	rawCapt.truncate(0)
	
	corners, ids, rejects = aruco.detectMarkers(vid, aruco_dic)
	
	found = aruco.drawDetectedMarkers(vid, corners, ids)
	#cv2.putText(found, iso_str, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	#cv2.putText(found, shutter_str, (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	#cv2.putText(found, awb_str, (30, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	
	cv2.imshow('vid', found)
	
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

camera.close()
cv2.destroyAllWindows()

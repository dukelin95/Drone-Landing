import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from Tkinter import *
import cv2.aruco as aruco
import sys
from time import gmtime, strftime

def save_pic():
	path = sys.path[0]
	cv2.imwrite(str(path) + "/" + strftime("%Y_%m_%d__%I_%M_%S", gmtime()) + "_test.jpg" , found)
	print "Picture saved"
	
def take_pic(event):
	#master.update_idletasks()
	#master.update()
	camera.meter_mode = m_mode.get()
	meter_str = "MM: " + str(camera.meter_mode)

	camera.iso = iso.get()
	iso_str = "ISO: " + str(camera.iso)
	#print("ISO: " + str(camera.iso))

	camera.shutter_speed = shutter.get()
	shutter_str = "SS: " + str(camera.shutter_speed)
	#print("Shutter speed: " + str(camera.shutter_speed))

	camera.awb_gains = (awbgain_r.get(), awbgain_b.get())
	awb_str = "AWB_G: " + str(awbgain_r.get()) + ", " + str(awbgain_b.get())
	#print("awb_gain: " + str(camera.awb_gains))

#	camera.exposure_compensation = expo_comp.get()
	expo_comp_str = "EC: " + str(camera.exposure_compensation)

	rawCapt = PiRGBArray(camera, size = (640, 480))
	time.sleep(0.1)
	camera.capture(rawCapt, format = "bgr", use_video_port = True)
	vid = rawCapt.array
	rawCapt.truncate(0)
	
	if (g_mode.get() == "True"):
		vid = cv2.cvtColor(vid, cv2.COLOR_BGR2GRAY)

	corners, ids, rejects = aruco.detectMarkers(vid, aruco_dic)
	
	found = aruco.drawDetectedMarkers(vid, corners, ids)
	cv2.putText(found, iso_str, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.putText(found, shutter_str, (250, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.putText(found, awb_str, (30, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.putText(found, meter_str, (250, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.putText(found, expo_comp_str, (420, 475), cv2.FONT_HERSHEY_SIMPLEX, 0.75, 255, 2)
	cv2.imshow('vid', found)
	
	if cv2.waitKey(0) & 0xFF == ord('s'):
		path = sys.path[0]
		cv2.imwrite(str(path) + "/" + strftime("%Y_%m_%d__%I_%M_%S", gmtime()) + "_test.jpg" , found)
		print "Picture saved"
		cv2.destroyAllWindows()
	

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
#camera.awb_mode = 'off'
#camera.awb_mode = 'sunlight'
camera.awb_mode = 'auto'

aruco_dic = aruco.Dictionary_get(aruco.DICT_6X6_250)

master = Tk()
master.title("Adjust")

Instructions = Label(master, text = "\n Press SPACE to take picture \n Press S on pictures window to save \n")
Instructions.pack()

grayTitle = Label(master, text = "Gray Scale: ")
grayTitle.pack()

g_mode = StringVar()
g_mode.set('False')

a = Radiobutton(master, text = "Yes", variable = g_mode, value = "True")
a.pack()

c = Radiobutton(master, text = "No", variable = g_mode, value = "False")
c.pack()

awbgain_r = Scale(master, from_=0.1, to=8, orient=HORIZONTAL, label = 'awb_gain red', length = 300, resolution = 0.1, showvalue = 0.1)
awbgain_r.set(1.5)
awbgain_r.pack()

awbgain_b = Scale(master, from_=0.1, to=8, orient=HORIZONTAL, label = 'awb_gain blue', length = 300, resolution = 0.1, showvalue = 0.1)
awbgain_b.set(1.5)
awbgain_b.pack()

iso = Scale(master, from_=100, to=800, orient=HORIZONTAL, label = 'ISO', length = 300, resolution = 100, showvalue = 100)
iso.set(100)
iso.pack()

shutter = Scale(master, from_=100, to=6000, orient=HORIZONTAL, label = 'shutter speed', length = 300, resolution = 100, showvalue = 100)
shutter.set(1100)
shutter.pack()

#expo_comp = Scale(master, from_=-25, to=25, orient=HORIZONTAL, label = 'exposure compensation', length = 300, resolution = 1, showvalue = 1)
#expo_comp.set(0)
#expo_comp.pack()

meterTitle = Label(master, text = "Meter Modes: ")
meterTitle.pack()

METER_MODES = ('average', 'spot', 'backlit', 'matrix')
m_mode = StringVar()
m_mode.set('average')

for mode in METER_MODES:
	b = Radiobutton(master, text = mode, variable = m_mode, value = mode)
	b.pack()

#update = Button(master, text = "Take picture", command = update_val)
#update.pack()
master.bind("<space>", take_pic)
#master.bind("<KeyRelease-s>", on_key_release)
#iso_val = iso.get()
#awbgains_val = (awbgain_r.get(), awbgain_b.get())
#shutter_val = shutter.get()

close = input("Insert E to end ")
if close == 'E':
	camera.close()
	cv2.destroyAllWindows()

import cv2
import math
import cv2.aruco as aruco
from dronekit import connect, VehicleMode
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

WIDTH = 640
HEIGHT = 480

TEMPLATE_L = .07					#in meters
TEMPLATE_H = .07				#in meters

CENTER_X_px = 334				#cam center in pixels
CENTER_Y_px = 275	

xfov = 62.2 * math.pi/180			# pi camera v2's field of view in radians
yfov = 48.8 * math.pi/180

def send_land_message(x, y):
	message = drone.message_factory.landing_target_encode(
		0,	# ms since boot, a time stamp
		0,	# target ID for case of multiple targets
		0,	# MAV_FRAME enum specifying frame
		x,	# X-axis angular offset in radians of target from center of image	
		y,	# Y-axis angular offset
		0,	# distance to the target from vehicle in meters
		0,	# size of target in radians along x-axis
		0)	# size along y-axis
	drone.send_mavlink(message)
	drone.flush()

def calculate_dist(corners):
	sumx = 0
	sumy = 0
	
	for x in corners[0][0]:
		sumx = sumx + x[0]
		sumy = sumy + x[1]
	
	avgx = sumx/4
	avgy = sumy/4

	#PIC_TEMP_L = distance(corners[0][0][0][0], corners[0][0][0][1], corners[0][0][1][0], corners[0][0][1][1])
	#PIC_TEMP_H = distance(corners[0][0][1][0], corners[0][0][1][1], corners[0][0][2][0], corners[0][0][2][1])

	#if (PIC_TEMP_L < PIC_TEMP_H):
	#	temp = PIC_TEMP_H
	#	PIC_TEMP_H = PIC_TEMP_L
	#	PIC_TEMP_L = temp

	#PIX_L_m = TEMPLATE_L/PIC_TEMP_L 		#pixel length in meters
	#PIX_H_m = TEMPLATE_H/PIC_TEMP_H		#pixel height in meters
	
	#CENTER_X_m = CENTER_X_px * PIX_L_m		#cam center in meters
	#CENTER_Y_m = CENTER_Y_px * PIX_H_m

	#xpoint = avg_x * PIX_L_m
	#ypoint = avg_y * PIX_H_m

	x = (avgx - WIDTH/2)*xfov/WIDTH
	y = (avgy - HEIGHT/2)*yfov/HEIGHT

	return (x, y)

#
#	MAIN
#
try:
	connection_str = "tcp:127.0.0.1:57600"
	drone = connect(connection_str ,wait_ready=True)	
	connected = True
except:
	connected = False

if not connected:
	print ("Unable to connect to drone")
	
else:
	print ("Connected to drone")
	
	# set parameters 
	drone.parameters['PLND_ENABLED'] = 1
	drone.parameters['PLND_TYPE'] = 1

	#TODO load pi camera and aruco library
	aruco_dic = aruco.Dictionary_get(aruco.DICT_6X6_250)
	camera = PiCamera()
	camera.resolution = (WIDTH, HEIGHT)
	camera.framerate = 30
	camera.shutter_speed = 5000

	while(1):
		A = time.time()
		rawCapt = PiRGBArray(camera, size = (WIDTH, HEIGHT))
		time.sleep(0.1)
		camera.capture(rawCapt, format = "bgr", use_video_port = True)
		vid = rawCapt.array
		rawCapt.truncate(0)
		corners, ids, rejects = aruco.detectMarkers(vid, aruco_dic)
		
		if len(corners) is not 0:
			print(corners)
			(x, y) = calculate_dist(corners)
			send_land_message(x, y)
			#print (x, y)
			B = time.time()
			print "Time: %0.3f" % (B-A)
			
		else:
			path = '/home/pi/drone_scripts/fail.jpg'
			cv2.imwrite(str(path), vid)
			#print ("Target not in frame, use default RTL")
			#vehicle.mode = VehicleMode("RTL")
			#print ("END")
			#break
		
	camera.close()
	drone.close()	
	print("Done")		

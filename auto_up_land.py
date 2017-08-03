#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
import cv2
import math
import cv2.aruco as aruco
from dronekit import connect, VehicleMode
from picamera.array import PiRGBArray
from picamera import PiCamera

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
	
	x = (avgx - WIDTH/2)*xfov/WIDTH
	y = (avgy - HEIGHT/2)*yfov/HEIGHT

	return (x, y)


# Connect to the Vehicle
connection_string = "tcp:127.0.0.1:57600"
print('Connecting to vehicle on: %s' % connection_string)
drone = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not drone.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    drone.mode = VehicleMode("GUIDED")
    drone.armed = True

    # Confirm vehicle armed before attempting to take off
    while not drone.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    drone.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the drone reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", drone.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if drone.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


arm_and_takeoff(3)

print("Set default/target airspeed to 3")
drone.airspeed = 3

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
		print ("Target not in frame, use default RTL")
		break

	if drone.location.global_relative_frame.alt <= 0.7:
		print ("Too close to ground, use default RTL")
		break

vehicle.mode = VehicleMode("RTL")
	
camera.close()
drone.close()
print ("Done")

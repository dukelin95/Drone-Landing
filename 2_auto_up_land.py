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
from pymavlink import mavutil
import math

WIDTH = 640
HEIGHT = 480

TEMPLATE_L = .07					#in meters
TEMPLATE_H = .07				#in meters

CENTER_X_px = 334				#cam center in pixels
CENTER_Y_px = 275	

xfov = 62.2 * math.pi/180			# pi camera v2's field of view in radians
yfov = 48.8 * math.pi/180

def get_z_7x7(area):
	return (4201.1 * (area ** -0.496))

def get_z_20x20(area):
	return (12632 * (area ** -0.502))

def send_land_message(x, y, z):
	message = drone.message_factory.landing_target_encode(
		0,	# ms since boot, a time stamp
		0,	# target ID for case of multiple targets
		mavutil.mavlink.MAV_FRAME_BODY_NED,	# MAV_FRAME enum specifying frame, try mavutil.mavlink.MAV_FRAME_BODY_NED
		x,	# X-axis angular offset in radians of target from center of image	
		y,	# Y-axis angular offset
		z,	# distance to the target from vehicle in meters
		0,	# size of target in radians along x-axis
		0)	# size along y-axis
	drone.send_mavlink(message)
	drone.flush()

def distance(x1, y1, x2, y2):
	return math.hypot(x2-x1, y2-y1)

def calculate_xyz(corners, flag):
	sumx = 0
	sumy = 0
	
	for x in corners:
		sumx = sumx + x[0]
		sumy = sumy + x[1]
	
	avgx = sumx/4
	avgy = sumy/4
	
	x = (avgx - WIDTH/2)*xfov/WIDTH
	y = (avgy - HEIGHT/2)*yfov/HEIGHT

	side1 = distance(corners[0][0], corners[0][1], corners[1][0], corners[1][1]) 
	side2 = distance(corners[0][0], corners[0][1], corners[2][0], corners[2][1])
	area = side1 * side2

	if flag is .07:
		z = get_z_7x7(area)
	else:
		z = get_z_20x20(area)

	return (x, y, z)


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
        if drone.location.global_relative_frame.alt >= aTargetAltitude * 0.9:
            print("Rea ched target altitude")
            break
        time.sleep(1)


arm_and_takeoff(4)

print("Begin camera, dictionary, params")

print("Set default/target airspeed to 3")
drone.airspeed = 3

print("Set parameters") 
drone.parameters['PLND_ENABLED'] = 1
drone.parameters['PLND_TYPE'] = 1

print("Set dictionary")
#TODO load pi camera and aruco library
aruco_dic = aruco.Dictionary_get(aruco.DICT_6X6_250)
print("Open camera")
camera = PiCamera()
camera.resolution = (WIDTH, HEIGHT)
camera.framerate = 30
camera.shutter_speed = 1100
camera.ISO = 100
camera.meter_mode = 'matrix'

#print(drone.battery)

print("Start landing")
count = 1

while(1):
	
	print("Count: " + str(count))
	rawCapt = PiRGBArray(camera, size = (WIDTH, HEIGHT))
	time.sleep(0.1)
	camera.capture(rawCapt, format = "bgr", use_video_port = True)
	vid = rawCapt.array
	rawCapt.truncate(0)
	time.sleep(0.1)
	corners, ids, rejects = aruco.detectMarkers(vid, aruco_dic)
	time.sleep(0.1)

	numMarkers = len(corners)
	print("Number of Markers: " + str(numMarkers))

	if numMarkers is 1:
		if ids[0][0] is 100:
			(x, y, z) = calculate_xyz(corners[0][0], 0.20)
		else:
			(x, y, z) = calculate_xyz(corners[0][0], 0.07)
		send_land_message(x, y, z)
		print ("Landing message for " + str(ids[0][0]))

	elif numMarkers is 2:
		(x, y, z) = calculate_xyz(corners[1][0], 0.07)
		print ("Landing message for 101")
	
	else:
		path = '/home/pi/drone_scripts/fail' + str(count) + '.jpg'
		cv2.imwrite(str(path), vid)
		if count == 10:
			print ("Target not in frame, use default RTL")
			break

		
	count = count + 1

	#if drone.location.global_relative_frame.alt <= 0.7:
	#	print ("Too close to ground, use default RTL")
	#	break

drone.mode = VehicleMode("RTL")
	
camera.close()
drone.close()
print ("Done")

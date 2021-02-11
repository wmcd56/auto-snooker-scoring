"""
Automatic Snooker Scoring System
Undertaken as part of the Masters of Engineering at Maynooth University
Started    - September 2020
Completed  -


Author: William McDonnell
Specific code segments sourced from others are cited with the url from where they were obtained
Further information on the operation  of this system can be found in the accompanying class and sequence diagrams
"""
# ======================================================================================================================
# This file runs the main program for the system and utilises all classes and functions included in this directory
# ======================================================================================================================

from Classes.Player import Player
from Classes.Ball import Ball
from Classes.Frame import Frame
# from CVFunctions.FindBalls import find_balls

import cv2
import numpy as np
import time
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.FindBalls import find_balls
from CVFunctions.BGRtoHSV import bgr_to_hsv
from CVFunctions.ClassifyHSV import classify_hsv
from CVFunctions.ClassifyBGR import classify_bgr

from Functions.CalibrateColours import calibrate_colours

# For different lighting conditions the colours should be calibrated first
# This function requests the user to place balls of a certain colour within view of the camera
# Can be run separately from the main file if calibrating once before multiple games
print("starting...")
# colours = calibrate_colours()

print("place all balls in position")
# time.sleep(10)
# ----------------------------------------------------------------------------------------------------------------------
# access a web cam

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 640)
cap.set(4, 480)
success, img = cap.read()
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# load a picture from 'Resources'

# path = 'Resources/snooker.png'
# img = cv2.imread(path)
# ----------------------------------------------------------------------------------------------------------------------


circles = find_balls(img)
# print(circles)
# print(circles[0][1])
i = 0
colour_circles = []
for (x, y, r) in circles:
    # print('x: ', x)  # debugging
    # print('y: ', y)  # debugging
    # print('Radius is: ', r)  # debugging
    half_width = np.floor(np.sqrt((r**2)/2))
    # print('half-width: ', half_width)  # debugging
    roi = img[int(y-half_width):int(y+half_width), int(x-half_width):int(x+half_width)]
    bgr_colour = get_ball_colour(roi)
    # hsv_colour = bgr_to_hsv(bgr_colour)
    temp_colour_circles = (circles[i][:], bgr_colour)
    # print("Temp colour: ", temp_colour_circles)  # debugging
    colour_circles.append(temp_colour_circles)
    # cv2.imshow("ROI", roi)  # debugging
    # cv2.waitKey(1000)  # debugging
    i += 1
"""
colour_circles is of the form [[[x, y, r],[h, s, v]],[[x, y, r],[h, s, v]], ...] 
or [[[x, y, r],[b, g, r]],[[x, y, r],[b, g, r]], ...]
where each element of the outer array represents a ball
"""

for circle in colour_circles:
    ball_colour = classify_bgr(circle[1])
    print(ball_colour)

# print("GetBallColour:", get_ball_colour(roi))

# frame = Frame(colour_circles)

# print(frame.player1.cue_colour)





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


# ======================================================================================================================
# FRAME SET-UP

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

# TODO: Make the following code a single function
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
balls = []
for i in range(len(colour_circles)):
    ball_colour = classify_bgr(colour_circles[i][1])
    # print(ball_colour)
    colour_circles[i] = list(colour_circles[i])
    colour_circles[i].append(ball_colour)
    # print(colour_circles[i][0][1])  # = ball_colour
    location = (colour_circles[i][0][0], colour_circles[i][0][1])
    balls.append(Ball(loc=location, colour=ball_colour))


frame = Frame(balls)  # frame is now set up
temp_balls = frame.balls
print(frame.balls)

cv2.imshow("window", img)
cv2.waitKey(0)

while True:

    success, img = cap.read()
    # print("At start: ", frame.balls)

    # TODO: Replace the following code with a function call
    circles = find_balls(img, False)
    i = 0
    colour_circles = []
    for (x, y, r) in circles:
        # print('x: ', x)  # debugging
        # print('y: ', y)  # debugging
        # print('Radius is: ', r)  # debugging
        half_width = np.floor(np.sqrt((r ** 2) / 2))
        # print('half-width: ', half_width)  # debugging
        roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
        bgr_colour = get_ball_colour(roi)
        if bgr_colour is False:
            continue
        # hsv_colour = bgr_to_hsv(bgr_colour)
        temp_colour_circles = (circles[i][:], bgr_colour)
        # print("Temp colour: ", temp_colour_circles)  # debugging
        colour_circles.append(temp_colour_circles)
        # cv2.imshow("ROI", roi)  # debugging
        # cv2.waitKey(1000)  # debugging
        cv2.circle(img, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        i += 1
    cv2.imshow("Video", img)

    # print("Colour circles: ", colour_circles)

    balls = []
    for i in range(len(colour_circles)):
        ball_colour = classify_bgr(colour_circles[i][1])
        # print(ball_colour)
        colour_circles[i] = list(colour_circles[i])
        colour_circles[i].append(ball_colour)
        location = (colour_circles[i][0][0], colour_circles[i][0][1])
        balls.append(Ball(loc=location, colour=ball_colour))

    additional_points = 0
    num_reds = 0
    temp_num_reds = 0
    frame_reds = 0
    updated_ball_colours = []
    temp_ball_colours = []

    for i in range(len(balls)):
        updated_ball_colours.append(balls[i].colour)
    # print("Updated colours: ", updated_ball_colours)
    for i in range(len(temp_balls)):
        temp_ball_colours.append(temp_balls[i].colour)

    # temp_ball_colours is used to check if the ball is missing from two consecutive frames
    for ball in frame.balls:
        if ball.colour != 'red':
            if ball.colour not in updated_ball_colours and ball.colour not in temp_ball_colours:  # and
                additional_points += Ball.colour_point_list[ball.colour]
        elif ball.colour == 'red':
            frame_reds += 1
        i += 1
    for colour in updated_ball_colours:
        if colour == 'red':
            num_reds += 1
    for colour in temp_ball_colours:
        if colour == 'red':
            temp_num_reds += 1

    reds_gone = max((frame_reds-temp_num_reds), (frame_reds-num_reds))
    additional_points = additional_points + reds_gone
    frame.update_score(additional_points)
    frame.balls = temp_balls
    temp_balls = balls

    print("Player 1's current score is: ", frame.obtain_scores())
    # print("At end: ", frame.balls)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

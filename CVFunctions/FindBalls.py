import json

from Classes.Ball import Ball
from Classes.WhiteBall import WhiteBall
from .FindCircles import find_circles
from .GetBallColour import get_ball_colour
from .ClassifyBGR import classify_bgr
from .ClassifyHSV import classify_hsv

import numpy as np


def find_balls(img, hough_param1, hough_param2, min_radius=20, max_radius=30, show_image=True, pockets=None, mode='Normal'):
    if pockets is None:
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/pockets.txt', 'r') as file:
            pockets = json.load(file)

    circles = find_circles(img, show_image, hough_param1=hough_param1, hough_param2=hough_param2, pockets=pockets,
                           hough_min_radius=min_radius, hough_max_radius=max_radius)

    i = 0
    colour_circles = []
    for (x, y, r) in circles:
        # print('x: ', x)  # debugging
        # print('y: ', y)  # debugging
        # print('Radius is: ', r)  # debugging
        half_width = np.floor(np.sqrt((r ** 2) / 2))
        # print('half-width: ', half_width)  # debugging
        # roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
        roi = img[int(y - r):int(y + r), int(x - r):int(x + r)]
        bgr_colour = get_ball_colour(roi)
        if bgr_colour is False:
            continue
        # hsv_colour = bgr_to_hsv(bgr_colour)
        #TODO: Revise below
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
    white_ball = None
    for i in range(len(colour_circles)):
        # print(colour_circles[i][1])
        ball_colour = classify_bgr(colour_circles[i][1])
        colour_circles[i] = list(colour_circles[i])
        colour_circles[i].append(ball_colour)
        location = (colour_circles[i][0][0], colour_circles[i][0][1])
        radius = colour_circles[i][0][2]
        if mode == 'Initial':
            if ball_colour == 'white':
                white_ball = WhiteBall(location, radius, ball_colour)
            else:
                balls.append(Ball(location, radius, ball_colour))
        else:
            balls.append(Ball(location, radius, ball_colour))
    if mode == 'Initial':
        return white_ball, balls
    else:
        return balls

# TODO: path needs to be altered to be versatile for any user and system

import numpy as np
import cv2
import time
import json
from CVFunctions.FindBalls import find_balls
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.BGRtoHSV import bgr_to_hsv

'''
# inputs: colours: empty dict with keys, colour: current key, mode: BGR or HSV
def calibrate(colours, colour, mode=None):
    """
    if mode=None, default of BGR format is returned
    if mode='HSV', values returned are HSV
    """
    # input('Press Enter to continue...')
    time.sleep(5)

    ball_colour = [0, 0, 0]
    for i in range(5):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 640)
        cap.set(4, 480)
        success, img = cap.read()

        circles = find_balls(img)
        (x, y, r) = circles[0][0], circles[0][1], circles[0][2]
        half_width = np.floor(np.sqrt((r ** 2) / 2))
        roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
        temp_ball_colour = get_ball_colour(roi)  # returns bgr value of square within ball

        # adding new values onto existing for averaging
        for j in range(len(temp_ball_colour)):
            ball_colour[j] = ball_colour[j] + temp_ball_colour[j]

    for i in range(len(ball_colour)):
        ball_colour[i] = ball_colour[i]/5  # get average of five frames in bgr

    print(colour, ': ', ball_colour)

    if mode is None or mode == 'BGR':
        colours[colour] = ball_colour
    elif mode == 'HSV':
        colours[colour] = bgr_to_hsv(ball_colour)
'''

def calibrate_colours(mode=None):
    colours = {
        'red': [],
        'white': [],
        'blue': [],
        'yellow': [],
        'green': [],
        'brown': [],
        'pink': [],
        'black': [],
    }

    for colour in colours:
        print("Place a single ", colour, " ball in view of the camera.")
        # calibrate(colours, colour, mode)
        time.sleep(5)

        ball_colour = [0, 0, 0]
        for i in range(5):
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(3, 640)
            cap.set(4, 480)
            success, img = cap.read()

            circles = find_balls(img)
            (x, y, r) = circles[0][0], circles[0][1], circles[0][2]
            half_width = np.floor(np.sqrt((r ** 2) / 2))
            roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
            temp_ball_colour = get_ball_colour(roi)  # returns bgr value of square within ball

            # adding new values onto existing for averaging
            for j in range(len(temp_ball_colour)):
                ball_colour[j] = ball_colour[j] + temp_ball_colour[j]

        for i in range(len(ball_colour)):
            ball_colour[i] = ball_colour[i] / 5  # get average of five frames in bgr

        print(colour, ': ', ball_colour)

        if mode is None or mode == 'BGR':
            colours[colour] = ball_colour
        elif mode == 'HSV':
            colours[colour] = bgr_to_hsv(ball_colour)

    # print(colours)
    if mode is None or mode == 'BGR':
        # FIXME: Fix path so that it works for any user on any system
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr.txt', 'w') as file:
            file.write(json.dumps(colours))
    elif mode == 'HSV':
        # FIXME: Fix path so that it works for any user on any system
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_hsv.txt', 'w') as file:
            file.write(json.dumps(colours))
    return colours


# colour_dict = calibrate_colours()


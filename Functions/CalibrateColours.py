# TODO: path needs to be altered to be versatile for any user and system

import numpy as np
import statistics as st
import cv2
import time
import json
from CVFunctions.FindCircles import find_circles
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.BGRtoHSV import bgr_to_hsv
from CVFunctions.CaptureFrame import capture_frame


def calibrate_colours(mode=None, cap_res=(1280, 960), L=0.9, a=1.25):
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

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, cap_res[0])
    cap.set(4, cap_res[1])
    success, img = cap.read()

    for colour in colours:
        print("Place a single ", colour, " ball in view of the camera.")
        cv2.imshow("delay", img)
        cv2.waitKey(0)
        # time.sleep(5)

        ball_colour = [0, 0, 0]
        loop_number = 100
        temp_colour_list = []
        for i in range(loop_number):
            img = capture_frame(cap)
            circles = find_circles(img, False, 3, 90)
            (x, y, r) = circles[0][0], circles[0][1], circles[0][2]
            # half_width = np.floor(np.sqrt((r ** 2) / 2))
            # roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
            roi = img[int(y - r):int(y + r), int(x - r):int(x + r)]
            temp_ball_colour = get_ball_colour(roi)  # returns bgr value of square within ball

            temp_colour_list.append(temp_ball_colour)

        #     # adding new values onto existing for averaging
        #     for j in range(len(temp_ball_colour)):
        #         ball_colour[j] = ball_colour[j] + temp_ball_colour[j]
        #
        # for i in range(len(ball_colour)):
        #     ball_colour[i] = ball_colour[i] / loop_number  # get average of five frames in bgr

        temp_bgr = [[], [], []]
        for i in range(len(temp_colour_list[0])):
            for j in range(len(temp_colour_list)):
                temp_bgr[i].append(temp_colour_list[j][i])
            ball_colour[i] = st.median(temp_bgr[i])
        # print(temp_bgr)
        print(colour, ': ', ball_colour)

        if mode is None or mode == 'BGR':
            colours[colour] = ball_colour
        elif mode == 'HSV':
            colours[colour] = bgr_to_hsv(ball_colour)

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


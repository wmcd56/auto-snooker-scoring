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
from CVFunctions.FindPockets import find_pockets


def calibrate_colours(mode=None, cap_res=(1280, 960), L=0.9, a=1.25, pockets=None):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, cap_res[0])
    cap.set(4, cap_res[1])

    img, original = capture_frame(cap)

    if pockets is None:
        pockets = find_pockets(cap, show_image=False)
    for pocket in pockets:
        centre = (int(pocket[0][0]), int(pocket[0][1]))
        radius = int(pocket[1])
        cv2.circle(original, centre, radius, (0, 255, 0), 2)
    cv2.imshow('pockets', original)
    cv2.waitKey(0)

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

    colours_original = {
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
        time.sleep(10)

        ball_colour = [0, 0, 0]
        ball_colour_original = [0, 0, 0]
        loop_number = 100
        temp_colour_list = []
        temp_colour_list_original = []
        for i in range(loop_number):
            img, original = capture_frame(cap)
            circles = find_circles(img, show_image=False, hough_param1=4, pockets=pockets)
            print('circles: ', circles)
            if circles is None:
                continue
            if len(circles) == 0:
                continue
            print('circles:', circles)
            (x, y, r) = circles[0][0], circles[0][1], circles[0][2]
            print(f"X: {x}, Y: {y}, R:{r}")
            # half_width = np.floor(np.sqrt((r ** 2) / 2))
            # roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
            roi = img[int(y - r):int(y + r), int(x - r):int(x + r)]
            roi_original = original[int(y - r):int(y + r), int(x - r):int(x + r)]
            temp_ball_colour = get_ball_colour(roi)  # returns bgr value of square within ball
            temp_ball_colour_original = get_ball_colour(roi_original)  # returns bgr value of square within ball

            temp_colour_list.append(list(temp_ball_colour))
            temp_colour_list_original.append(list(temp_ball_colour_original))
        #     # adding new values onto existing for averaging
        #     for j in range(len(temp_ball_colour)):
        #         ball_colour[j] = ball_colour[j] + temp_ball_colour[j]
        #
        # for i in range(len(ball_colour)):
        #     ball_colour[i] = ball_colour[i] / loop_number  # get average of five frames in bgr

        temp_bgr = [[], [], []]
        temp_bgr_original = [[], [], []]
        print('temp_colour_list: ', temp_colour_list)
        for i in range(len(temp_colour_list[0])):
            for j in range(len(temp_colour_list)):
                temp_bgr[i].append(temp_colour_list[j][i])
                temp_bgr_original[i].append(temp_colour_list_original[j][i])
            ball_colour[i] = int(st.median(temp_bgr[i]))
            ball_colour_original[i] = int(st.median(temp_bgr_original[i]))
        print(colour, ': ', ball_colour)

        if mode is None or mode == 'BGR':
            colours[colour] = ball_colour
            colours_original[colour] = ball_colour_original
    if mode is None or mode == 'BGR':
        # FIXME: Fix path so that it works for any user on any system
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr.txt', 'w') as file:
            file.write(json.dumps(colours))

        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr_original.txt', 'w') as file:
            file.write(json.dumps(colours_original))

    return colours


#colour_dict = calibrate_colours()


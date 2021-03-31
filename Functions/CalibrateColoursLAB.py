import numpy as np
import cv2
import time
import json
from CVFunctions.FindCircles import find_circles
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.BGRtoHSV import bgr_to_hsv


def calibrate_colours_lab(mode=None, cap_res=(1280, 960)):
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
            cap.set(3, cap_res[0])
            cap.set(4, cap_res[1])
            success, img = cap.read()

            circles = find_circles(img, show_image=False)
            (x, y, r) = circles[0][0], circles[0][1], circles[0][2]
            half_width = np.floor(np.sqrt((r ** 2) / 2))
            roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
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
    if mode is None or mode == 'LAB':
        # FIXME: Fix path so that it works for any user on any system
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_lab.txt', 'w') as file:
            file.write(json.dumps(colours))
    elif mode == 'HSV':
        # FIXME: Fix path so that it works for any user on any system
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_hsv.txt', 'w') as file:
            file.write(json.dumps(colours))
    return colours


#colour_dict = calibrate_colours_lab()
#print(colour_dict)

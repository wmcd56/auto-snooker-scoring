import cv2
import numpy as np
import PySimpleGUI as sg
import json
from Classes.Ball import Ball
from Classes.WhiteBall import WhiteBall
from CVFunctions.FindBalls import find_balls
from CVFunctions.FindCircles import find_circles
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.BGRtoHSV import bgr_to_hsv
from CVFunctions.ClassifyBGR import classify_bgr
from CVFunctions.CaptureFrame import capture_frame
from CVFunctions.FindPockets import find_pockets

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # comment out for small set up
cap.set(3, 1280)
cap.set(4, 960)

img, original = capture_frame(cap)
with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/pockets.txt', 'r') as file:
    pockets = json.load(file)
# pockets = find_pockets(cap)
circles = find_circles(original,  show_image=True, pockets=pockets)

number_of_tests = 100
L = 0.9
a = 1.25
mode = 'BGR'
# mode = 'LAB'
all_tests_colours = []

totals = {
        "white": 0,
        "red": 0,
        "yellow": 0,
        "green": 0,
        "brown": 0,
        "blue": 0,
        "pink": 0,
        "black": 0
    }

# j = 0
# while j < number_of_tests:
for j in range(number_of_tests):
    sg.OneLineProgressMeter('Progress', j, number_of_tests, 'key')

    colours_found = []
    img, original = capture_frame(cap)

    circles = find_circles(img, show_image=False, hough_param1=4.4, hough_param2=15, hough_min_radius=20,
                           hough_max_radius=30, pockets=pockets)

    i = 0
    colour_circles = []
    if circles is not None:
        for (x, y, r) in circles:
            half_width = np.floor(np.sqrt((r ** 2) / 2))
            # roi = img[int(y - half_width):int(y + half_width), int(x - half_width):int(x + half_width)]
            roi = img[int(y - r):int(y + r), int(x - r):int(x + r)]
            if mode == 'LAB':
                roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
                lab_colour = get_ball_colour(roi)
                print('LAB: ', lab_colour)
                # bgr_colour = cv2.cvtColor(np.uint8([[lab_colour]]), cv2.COLOR_LAB2BGR)
                bgr_colour = cv2.cvtColor(np.uint8([[lab_colour]]), cv2.COLOR_BGR2HSV)
                # print('HSV: ', hsv_colour)
                # bgr_colour = cv2.cvtColor(hsv_colour, cv2.COLOR_HSV2BGR)
            elif mode == 'HSV':
                roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
                hsv_colour = get_ball_colour(roi)
                print('HSV: ', hsv_colour)
                bgr_colour = cv2.cvtColor(np.uint8([[hsv_colour]]), cv2.COLOR_HSV2BGR)
            elif mode == 'BGR':
                bgr_colour = np.uint8([[get_ball_colour(roi)]])
            print('BGR: ', bgr_colour)
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
    else:
        print(j)
        continue
    # print(colour_circles)
    # TODO: change data type to suit method classify BGR()
    temp_colour_circles = []
    for i in range(len(circles)):
        temp_colour_circles.append(colour_circles[i][1][0][0].tolist())
    colour_circles = temp_colour_circles
    # print(type(colour_circles))

    print('colour circles: ', colour_circles)

    balls = []
    white_ball = None
    for i in range(len(colour_circles)):
        ball_colour = classify_bgr(colour_circles[i])
        colour_circles[i] = list(colour_circles[i])
        colour_circles[i].append(ball_colour)
        # location = (colour_circles[i][0][0], colour_circles[i][0][1])
        location = 50, 50
        # radius = colour_circles[i][0][2]
        radius = 55
        if ball_colour == 'white':
            white_ball = WhiteBall(location, radius, ball_colour)
        else:
            balls.append(Ball(location, radius, ball_colour))

    if len(balls) > 0:
        for ball in balls:
            colours_found.append(ball.colour)
            all_tests_colours.append(ball.colour)
        print(f'The colour balls found on test number {j+1}: ', colours_found)
    #j += 1

    # if mode is None or mode == 'BGR':
    #     # mode 'a' is append, mode 'w' is write (overwrite)
    #     with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr_test.txt', 'a') as file:
    #         for colour in colours_found:
    #             file.write(f'{colour},')  # write to file as comma separated values

for colour in all_tests_colours:
    totals[colour] += 1

for colour in totals:
    print(f'Total {colour}s: {totals[colour]}')

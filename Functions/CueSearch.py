"""
cue_search takes an image as input and returns the colour (and therefore player shooting) and the location of the
cue tip

"""

import cv2
import numpy as np
import time
import json
from CVFunctions.GetBallColour import get_ball_colour
from CVFunctions.CaptureFrame import capture_frame
from Functions.CueTipVelocity import cue_tip_velocity


def cue_colour_calibration(img):
    print('place a single cue on the table...')
    time.sleep(5)
    print('select the region within the coloured cue tip and hit enter...')
    (x, y, w, h) = cv2.selectROI('Cue 1', img)
    roi = img[y:y + h, x:x + w]
    p1_cue_colour = get_ball_colour(roi)
    p1_cue_colour = [int(p1_cue_colour[0]), int(p1_cue_colour[1]), int(p1_cue_colour[2])]
    print('place the other cue on the table...')
    time.sleep(5)
    print('select the region within the coloured cue tip and hit enter...')
    (x, y, w, h) = cv2.selectROI('Cue 2', img)
    roi = img[y:y + h, x:x + w]
    p2_cue_colour = get_ball_colour(roi)
    p2_cue_colour = [int(p2_cue_colour[0]), int(p2_cue_colour[1]), int(p2_cue_colour[2])]
    print(f'P2 cue colour: {p2_cue_colour}')
    cue_colours = {
        'P1 cue colour': p1_cue_colour,
        'P2 cue colour': p2_cue_colour
    }

    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/cue_colours.txt', 'w') as file:
        file.write(json.dumps(cue_colours))


def cue_search(img):
    box1 = None
    box2 = None
    box1_centre = None
    box2_centre = None

    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/cue_colours.txt', 'r') as file:
        cue_colours = json.load(file)

    p1_cue_colour = cue_colours['P1 cue colour']
    p2_cue_colour = cue_colours['P2 cue colour']
    cv2.imshow('img', img)

    b_1 = p1_cue_colour[0]
    g_1 = p1_cue_colour[1]
    r_1 = p1_cue_colour[2]
    b_2 = p2_cue_colour[0]
    g_2 = p2_cue_colour[1]
    r_2 = p2_cue_colour[2]

    lower1 = np.array([b_1-15, g_1-15, r_1-15])
    upper1 = np.array([b_1 + 15, g_1 + 15, r_1 + 15])
    mask1 = cv2.inRange(img, lower1, upper1)


    lower2 = np.array([b_2 - 15, g_2 - 15, r_2 - 15])
    upper2 = np.array([b_2 + 15, g_2 + 15, r_2 + 15])
    mask2 = cv2.inRange(img, lower2, upper2)
    cv2.imshow('mask', mask2)


    blur1 = cv2.GaussianBlur(mask1, (5, 5), 2)
    ret, otsu1 = cv2.threshold(blur1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((3, 3), np.uint8)
    otsu1 = cv2.dilate(otsu1, kernel, iterations=1)
    canny1 = cv2.Canny(otsu1, 100, 200)
    cv2.imshow('dilated otsu', otsu1)
    # cv2.waitKey(0)
    blur2 = cv2.GaussianBlur(mask2, (5, 5), 2)
    ret, otsu2 = cv2.threshold(blur2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # kernel = np.ones((3, 3), np.uint8)
    otsu2 = cv2.dilate(otsu2, kernel, iterations=2)
    canny2 = cv2.Canny(otsu2, 100, 200)
    cv2.imshow('canny', canny2)
    cv2.imshow('dilated otsu', otsu2)

    contours1, hierarchy1 = cv2.findContours(canny1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours2, hierarchy2 = cv2.findContours(canny2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    # for cnt in contours2:
    #     cv2.drawContours(image_for_show, cnt, -1, [0, 255, 0], thickness=4)
    # cv2.imshow('cnts', image_for_show)
    # cv2.waitKey(0)

    if len(contours1) > 0:
        min_rect = [None] * len(contours1)

        for i, c in enumerate(contours1):
            min_rect[i] = cv2.minAreaRect(c)

        for i, c in enumerate(contours1):
            if cv2.contourArea(cv2.boxPoints(min_rect[i])) >= 200:
                box1 = cv2.boxPoints(min_rect[i])
                box1 = np.intp(box1)

        if box1 is not None:
            x1 = 0
            y1 = 0
            for i in range(len(box1)):
                x1 = x1 + box1[i][0]
                y1 = y1 + box1[i][1]
            box1_centre = [x1/len(box1), y1/len(box1)]

    if len(contours2) > 0:
        min_rect = [None] * len(contours2)

        for i, c in enumerate(contours2):
            min_rect[i] = cv2.minAreaRect(c)

        for i, c in enumerate(contours2):
            if cv2.contourArea(cv2.boxPoints(min_rect[i])) >= 200:
                box2 = cv2.boxPoints(min_rect[i])
                box2 = np.intp(box2)  # np.intp: Integer used for indexing (same as C ssize_t; normally either int32 or int64)

        if box2 is not None:
            x2 = 0
            y2 = 0
            for i in range(len(box2)):
                x2 = x2 + box2[i][0]
                y2 = y2 + box2[i][1]
            box2_centre = [x2 / len(box2), y2 / len(box2)]
    return [box1, box1_centre], [box2, box2_centre]


# cap_res = (1920, 1080)
cap_res = (1280, 960)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # comment out for small set up
cap.set(3, cap_res[0])
cap.set(4, cap_res[1])
img, original = capture_frame(cap)
cv2.imshow('cue tips', original)
cv2.waitKey(0)
# cue_colour_calibration(original)
p1_cue_tip_list = []
p2_cue_tip_list = []
frames = 0
max_frames = 50

while True:
    # time.sleep(1)
    img, original = capture_frame(cap)

    b1, b2 = cue_search(original)
    if b1[0] is not None:
        b1_area = cv2.contourArea(b1[0], False)
    if b2[0] is not None:
        b2_area = cv2.contourArea(b2[0], False)


    colour = [0, 0, 255]

    if b1[0] is not None and (b1_area >= 200):
        p1_cue_tip_list.append(b1)
        cv2.drawContours(original, [b1[0]], 0, colour, thickness=3)
        # print(f'cue tip list: {p1_cue_tip_list[-1]}')
        # print(f'cue tip box x y: {p1_cue_tip_list[-1][0][0]}')
        if len(p1_cue_tip_list) > 10:
            c1_velocity = cue_tip_velocity(p1_cue_tip_list)
            print(f'cue speed: {c1_velocity[0]}, direction: {c1_velocity[1]}')

    if b2[0] is not None and (b2_area >= 200):
        p2_cue_tip_list.append(b2)
        cv2.drawContours(original, [b2[0]], 0, colour, thickness=3)
        if len(p2_cue_tip_list) > 10:
            c2_velocity = cue_tip_velocity(p2_cue_tip_list)
            print(f'cue speed: {c2_velocity[0]}, direction: {c2_velocity[1]}')
    cv2.imshow('cue tips', original)

    frames += 1
    if cv2.waitKey(0) & 0xFF == ord('q'):
        break
#cv2.waitKey(0)




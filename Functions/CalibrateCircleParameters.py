import cv2
import numpy as np
import time
import json
import PySimpleGUI as sg
from CVFunctions.FindCircles import find_circles
from CVFunctions.CaptureFrame import capture_frame


def calibrate_circle_params(cap_res):
    all_successes = []
    successful_combinations = []
    cap = cv2.VideoCapture(0)  # comment out for small set up
    cap.set(3, cap_res[0])  # medium set up
    cap.set(4, cap_res[1])  # medium set up

    hough_min_radius = 15
    hough_max_radius = 30

    for i in range(1, 6):
        successful_combinations = []
        print(f"Place {i} ball(s) on the table.")
        time.sleep(5)
        img = capture_frame(cap)

        cimg = cv2.medianBlur(img, 5)
        cimg = cv2.cvtColor(cimg, cv2.COLOR_BGR2GRAY)
        cimg = cv2.adaptiveThreshold(cimg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        cv2.imshow('cimg', cimg)
        cv2.waitKey(0)

        for hough_param1 in range(1, 6):
            sg.OneLineProgressMeter('Hough Param 1', hough_param1, 5, 'key')
            for hough_param2 in range(50, 151):
                sg.OneLineProgressMeter('Hough Param 2', hough_param2, 150, 'key')
                circles = cv2.HoughCircles(cimg, cv2.HOUGH_GRADIENT, hough_param1, hough_param2,
                                           minRadius=hough_min_radius, maxRadius=hough_max_radius)
                if circles is not None:
                    if len(circles[0, :]) == i:
                        successful_combinations.append([hough_param1, hough_param2])

        all_successes.append(successful_combinations)
        print(f"Successful combinations for {i} ball(s): ", successful_combinations)

    lengths = []
    for i in range(len(all_successes)):
        lengths.append(len(all_successes[i]))
    min_len_index = lengths.index(min(lengths))

    # TODO: can improve this search algorithm
    usable_values = []
    for elem in all_successes[min_len_index]:
        count = 0
        for i in range(len(all_successes)):
            if elem not in all_successes[i]:
                break
            else:
                count += 1
        if count == len(all_successes):
            usable_values.append(elem)

    print(f"Usable values: {usable_values}")

    counts = [0]*len(usable_values)
    i = 0
    j = 0
    while i < len(usable_values):
        if usable_values[i][0] == usable_values[j][0]:
            counts[usable_values[i][0]] += 1
        else:
            j = i
            i -= 1
        i += 1
    max_counts = max(counts)
    hough_param1 = counts.index(max_counts)
    hough2 = []
    for i in range(len(usable_values)):
        if usable_values[i][0] == hough_param1:
            hough2.append(usable_values[i][1])
    max_hough2 = max(hough2)
    min_hough2 = min(hough2)
    # hough_param2 = min_hough2 + ((max_hough2-min_hough2)/2)
    hough_param2 = max_hough2

    return hough_param1, hough_param2


cap_res = (1280, 960)
# print(f"{calibrate_circle_params(cap_res)}")

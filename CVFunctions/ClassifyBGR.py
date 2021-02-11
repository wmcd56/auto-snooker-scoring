# TODO: Add functionality for the case where differences are the same for multiple colours

import cv2
import numpy as np
import json
import difflib


def classify_bgr(bgr, colours_bgr=None):

    if colours_bgr is None:
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr.txt', 'r') as file:
            colours_bgr = json.load(file)

    colours_bgr_values = list(colours_bgr.values())
    differences = []
    for colour in colours_bgr_values:
        diff = 0  # difference in bgr colours
        for i in range(len(bgr)):
            diff = diff + np.abs(bgr[i] - colour[i])
        # print('diff: ', diff)
        differences.append(diff)
        # print('differences: ', differences)
    differences = np.array(differences)
    # print(differences)
    index_min = np.argmin(differences)
    # print(index_min)
    # print(colours_bgr[index_min])
    return list(colours_bgr.keys())[list(colours_bgr.values()).index(colours_bgr_values[index_min])]


# print(classify_bgr([242, 246, 247]))

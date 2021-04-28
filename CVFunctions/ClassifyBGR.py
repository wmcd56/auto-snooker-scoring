# TODO: Add functionality for the case where differences are the same for multiple colours

import cv2
import numpy as np
import json
import difflib


def classify(bgr, colours_bgr=None):
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
    colour = list(colours_bgr.keys())[list(colours_bgr.values()).index(colours_bgr_values[index_min])]
    return colour


def classify_bgr(bgr_original, bgr_alt=None, colours_bgr=None):

    colour = classify(bgr_original)
    if colour == 'pink' or colour == 'green':  # or colour == 'yellow'
        # print(f'colour: {colour}')
        with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr_original.txt', 'r') as file:
            colours_bgr = json.load(file)
        if bgr_alt is None:
            colour_alt = cv2.cvtColor(np.uint8([[bgr_original]]), cv2.COLOR_BGR2LAB)
            colour_alt[..., 0] = colour_alt[..., 0] * (1/0.9)
            colour_alt[..., 1] = colour_alt[..., 1] * (1/1.25)  # 1.2
            colour_alt[..., 2] = colour_alt[..., 2] * 1
            colour_alt = list(cv2.cvtColor(colour_alt, cv2.COLOR_LAB2BGR))
            colour = classify(colour_alt[0][0], colours_bgr=colours_bgr)
            return colour
        else:
            colour = classify(bgr_alt, colours_bgr=colours_bgr)
            return colour
    else:
        return colour

# def classify_bgr(bgr, colours_bgr=None):
#
#     if colours_bgr is None:
#         with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr.txt', 'r') as file:
#             colours_bgr = json.load(file)
#
#     colours_bgr_values = list(colours_bgr.values())
#     differences = []
#
#     for colour in colours_bgr_values:
#         diff = 0  # difference in bgr colours
#         for i in range(len(bgr)):
#             # diff = diff + np.abs(bgr[i] - colour[i])
#             diff = diff + (bgr[i]/colour[i])
#         diff = abs(diff/len(bgr) - 1)
#         differences.append(diff)
#
#     differences = np.array(differences)
#
#     index_min = np.argmin(differences)
#
#     return list(colours_bgr.keys())[list(colours_bgr.values()).index(colours_bgr_values[index_min])]


# print(classify_bgr([70, 31, 253]))

import cv2
import time
import numpy as np
import json
from CVFunctions.CaptureFrame import capture_frame
from Functions.PixelsDistance import pixels_distance
from CVFunctions.FindCircles import find_circles


def find_pockets(cap, min_radius=25, max_radius=35, show_image=False):
    print('Remove all the balls from the table.\nFinding pockets...')
    circles = []
    for i in range(0, 100):
        cimg, img = capture_frame(cap)
        pockets = img.copy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 200, 300, None, apertureSize=7)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        blur = cv2.GaussianBlur(gray, (5, 5), 5)
        ret, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # edges = cv2.Canny(thresh, 250, 300, None, apertureSize=7)
        kernel = np.ones((3, 3), np.uint8)
        otsu1 = cv2.dilate(otsu, kernel, iterations=1)
        otsu1 = cv2.cvtColor(otsu1, cv2.COLOR_GRAY2BGR)
        circles_found = find_circles(img, show_image=show_image, hough_param1=4, hough_param2=100)
        # th3 = cv2.erode(th3, kernel, iterations=1)
        contours, hierarchy = cv2.findContours(otsu, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # img = cv2.drawContours(img, contours, -1, (0, 250, 0), 3)
        # cv2.imshow('otsu', th3)
        # cv2.imshow('contours', img)
        # cv2.waitKey(0)

        votes = 0
        # for cnt in contours:
        #     (x, y), radius = cv2.minEnclosingCircle(cnt)
        for (x, y, radius) in circles_found:
            centre = (int(x), int(y))
            radius = int(radius)
            new_circle = (centre, radius, votes)
            if min_radius <= radius <= max_radius:
                if i < 1:
                    circles.append(list(new_circle))
                elif i < 10:
                    # get the distance from the centre of contour to centre of all existing circles
                    distances = []
                    for circle in circles:
                        distances.append(pixels_distance(circle[0], centre))
                    # if the minimum distance is greater than the radius of the contour add the contour to circles list
                    if min(distances) >= radius:
                        circles.append(list(new_circle))
                else:
                    # vote for the most consistently occurring circles
                    for circle in circles:
                        if pixels_distance(circle[0], centre) < 20:  # vote for the pocket
                            circle[2] += 1
        # cv2.circle(pockets, center, radius, (0, 255, 0), 2)
        # cv2.imshow('pockets', pockets)
        # cv2.waitKey(0)

        # sort by votes
        length = len(circles)
        for index in range(0, length):
            for j in range(0, length - index - 1):
                if circles[j][2] > circles[j + 1][2]:
                    temp = circles[j]
                    circles[j] = circles[j + 1]
                    circles[j + 1] = temp

    circles.reverse()  # reverse the list so the circles with the most votes comes first
    return circles[0:6]

# cap_res = (1280, 960)
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # comment out for small set up
# cap.set(3, cap_res[0])
# cap.set(4, cap_res[1])
# cimg, img = capture_frame(cap)
# out = img.copy()
# pockets = find_pockets(cap)
# print(pockets)
# for pocket in pockets:
#     centre = (int(pocket[0][0]), int(pocket[0][1]))
#     radius = int(pocket[1])
#     cv2.circle(out, centre, radius, (0, 255, 0), 2)
# with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/pockets.txt', 'w') as file:
#     file.write(json.dumps(pockets))
#
# cv2.imshow('pockets', out)
# cv2.waitKey(0)




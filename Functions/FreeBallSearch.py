import cv2
import numpy as np
import sympy as sp
import math

from Functions.PixelsDistance import pixels_distance

from Classes.Ball import Ball
from Classes.WhiteBall import WhiteBall


# source from https://www.geeksforgeeks.org/check-line-touches-intersects-circle/
def check_interception(a, b, c, x, y, radius):
    # Finding the distance of line
    # from center.
    dist = ((abs(a * x + b * y + c)) /
            math.sqrt(a * a + b * b))

    # Checking if the distance is less
    # than, greater than or equal to radius

    print('dist: ', dist)
    print('radius: ', radius)
    if radius >= dist:
        snooker_flag = True
    else:
        snooker_flag = False

    return snooker_flag

def line_intersect_check(line1, line2, circle, r_multiplier):
    x = circle[0][0]
    y = circle[0][1]
    r = circle[1]

    lower_x = min(line1[0], line2[0])
    upper_x = max(line1[0], line2[0])
    lower_y = min(line1[1], line2[1])
    upper_y = max(line1[1], line2[1])

    if (lower_x <= x <= upper_x) and (lower_y <= y <= upper_y):
        if line1[0] > line2[0]:
            m = (line1[1]-line2[1]) / (line1[0] - line2[0])
        elif line2[0] > line1[0]:
            m = (line2[1] - line1[1]) / (line2[0] - line1[0])
        else:
            m = 0.00000000000000000000001

        c = line1[1] - (m * line1[0])

        # y = mx + c
        # a*x + b*y + c = 0
        # (a, b, c, x, y, radius)
        snooker_flag = check_interception(m, -1, c, x, y, r*r_multiplier)

        return snooker_flag
    else:
        return False



def circle_intersect_check(circle1, circle2):
    centre1 = circle1[0]
    r1 = circle1[1]

    centre2 = circle2[0]
    r2 = circle2[1]

    if pixels_distance(centre1, centre2) <= (r1 + r2):
        return True
    else:
        return False



# def free_ball_search(white_ball, balls, ball_on, foul_flag=None, img=None):
#     if foul_flag is True or foul_flag is None:  # assume that a fouls has occurred
#         balls_to_search = []
#         x = sp.Symbol('x')
#         f = sp.Function('f')(x)
#         g = sp.Function('g')(x)
#
#         for ball in balls:
#             if ball.colour in ball_on:
#                 balls_to_search.append(ball)
#
#
#         clear_balls = 0
#         for ball in balls_to_search:
#             # create a line function
#             m = (white_ball.ball.loc[0][0] - ball.loc[0][0])/((-white_ball.ball.loc[0][1]) - (-ball.loc[0][1]))
#             c = white_ball.ball.loc[0][1] - (m*white_ball.ball.loc[0][0])
#
#             angle = np.arctan(m)
#             additional_boundary = white_ball.ball.radius/np.sin(angle)
#             # slope intercept form
#             f = (m*x) + c + additional_boundary  # function of upper bounding line
#             g = (m*x) + c - additional_boundary  # function of lower bounding line
#
#             if img is not None:
#                 # cv2.line(img, tuple(white_ball.ball.loc[0]), tuple(ball.loc[0]), (255, 0, 0), 5)
#                 y1 = int((m*(white_ball.ball.loc[0][0])) - (c + additional_boundary))
#                 y2 = int((m*(ball.loc[0][0])) - (c - additional_boundary))
#
#                 cv2.line(img, tuple((white_ball.ball.loc[0][0], y1)),
#                          tuple((ball.loc[0][0], y2)), (255, 0, 0), 5)
#
#                 cv2.imshow('Snooker', img)
#                 cv2.waitKey(0)
#
#             for b in balls:
#                 # do not search white ball or the same ball (itself)
#                 if (ball.colour != 'white') and (ball.loc[0] != b.loc[0]):
#                     # a*x + b*y + c = 0
#                     print(f'checking {b.colour} ball')
#                     snooker1 = checkSnooker(m, -1, (c + additional_boundary), b.loc[0][0], b.loc[0][1], b.radius)
#                     snooker2 = checkSnooker(m, -1, (c - additional_boundary), b.loc[0][0], b.loc[0][1], b.radius)
#                     print(snooker1)
#                     print(snooker2)
#                     if snooker1 or snooker2:
#                         print(f'The {ball.colour} ball is snookered by the {b.colour} ball.')
#                     else:
#                         clear_balls += 1
#
#         if clear_balls > 0:
#             print('no snooker, carry on')
#             return False
#         else:
#             print('Free ball, pick a ball')
#             return True
#     else:
#         return None



def free_ball_search(white_ball, balls, ball_on, foul_flag=None, img=None):
    if foul_flag is True or foul_flag is None:  # assume that a fouls has occurred
        balls_to_search = []
        balls_to_check = []
        snookering_balls = []

        for ball in balls:
            if ball.colour in ball_on:
                balls_to_search.append(ball)
            else:
                balls_to_check.append(ball)

        clear_balls = 0
        for ball in balls_to_search:
            snooker_count = 0
            lines = []
            shapes_to_check = []
            a, b = white_ball.ball.loc[0][0], white_ball.ball.loc[0][1]
            c, d = ball.loc[0][0], ball.loc[0][1]
            r1 = white_ball.ball.radius
            r2 = ball.radius

            if b < d:
                position = ['bottom']
                lm = -1
            else:
                position = ['top']
                lm = 1

            if a < c:
                position.append('left')
            else:
                position.append('right')

            # calculate the intersection point of the two tngent lines
            xp = ((c*r1) + (a*r2)) / (r1 + r2)
            yp = ((d*r1) + (b*r2)) / (r1 + r2)

            x_white1 = ((((r1**2)*(xp-a)) + r1*(yp-b)*np.sqrt(((xp-a)**2) + ((yp-b)**2) - r1**2)) /
                        (((xp-a)**2) + ((yp-b)**2))) + a

            x_white2 = ((((r1 ** 2) * (xp - a)) - r1 * (yp - b) *
                         np.sqrt(((xp - a) ** 2) + ((yp - b) ** 2) - r1 ** 2)) /
                        (((xp - a) ** 2) + ((yp - b) ** 2))) + a

            y_white1 = ((((r1 ** 2) * (yp - b)) + r1 * (xp - a) * np.sqrt(
                ((xp - a) ** 2) + ((yp - b) ** 2) - r1 ** 2)) /
                        (((xp - a) ** 2) + ((yp - b) ** 2))) + b

            y_white2 = ((((r1 ** 2) * (yp - b)) - r1 * (xp - a) * np.sqrt(
                ((xp - a) ** 2) + ((yp - b) ** 2) - r1 ** 2)) /
                        (((xp - a) ** 2) + ((yp - b) ** 2))) + b

            x_object1 = ((((r2 ** 2) * (xp - c)) + r2 * (yp - d) * np.sqrt(
                ((xp - c) ** 2) + ((yp - d) ** 2) - r2 ** 2)) /
                        (((xp - c) ** 2) + ((yp - d) ** 2))) + c

            x_object2 = ((((r2 ** 2) * (xp - c)) - r2 * (yp - d) * np.sqrt(
                ((xp - c) ** 2) + ((yp - d) ** 2) - r2 ** 2)) /
                        (((xp - c) ** 2) + ((yp - d) ** 2))) + c

            y_object1 = ((((r2 ** 2) * (yp - d)) + r2 * (xp - c) * np.sqrt(
                ((xp - c) ** 2) + ((yp - d) ** 2) - r2 ** 2)) /
                        (((xp - c) ** 2) + ((yp - d) ** 2))) + d

            y_object2 = ((((r2 ** 2) * (yp - d)) - r2 * (xp - c) * np.sqrt(
                ((xp - c) ** 2) + ((yp - d) ** 2) - r2 ** 2)) /
                        (((xp - c) ** 2) + ((yp - d) ** 2))) + d


            white1 = [int(x_white1), int(y_white2)]
            white2 = [int(x_white2), int(y_white1)]
            object1 = [int(x_object1), int(y_object2)]
            object2 = [int(x_object2), int(y_object1)]

            lines.append([white1, object1])
            lines.append([white2, object2])

            # find one of the boundary circles
            run = (object1[0] - ball.loc[0][0])
            if run != 0:
                m = (object1[1] - ball.loc[0][1]) / run
            else:
                m = (object1[1] - ball.loc[0][1]) / 0.00000000000000000000001
            theta = np.arctan(m)

            # theta = np.arcsin(np.radians(abs(object1[1] - ball.loc[0][1]) / r1))
            vector1 = [lm*int(np.cos(theta) * (r1+r2)), lm*int(np.sin(theta)*(r1+r2))]
            vector2 = [lm*int(np.cos(theta) * (r1 + r1 + r2)), lm*int(np.sin(theta) * (r1 + r1 + r2))]
            vector3 = [lm*int(np.cos(theta) * r1), lm*int(np.sin(theta) * r1)]
            centre = (int(ball.loc[0][0] + vector1[0]), int(ball.loc[0][1] + vector1[1]))
            outside_line1 = (int(ball.loc[0][0] + vector2[0]), int(ball.loc[0][1] + vector2[1]))
            outside_line2 = (int(white_ball.ball.loc[0][0] + vector3[0]), int(white_ball.ball.loc[0][1] + vector3[1]))
            lines.append([outside_line1, outside_line2])
            circle1 = [centre, white_ball.ball.radius]

            # find another one of the boundary circles
            run = (object2[0] - ball.loc[0][0])
            if run != 0:
                m = (object2[1] - ball.loc[0][1]) / run
            else:
                m = (object2[1] - ball.loc[0][1]) / 0.00000000000000000000001
            theta = np.arctan(m)

            # theta = np.radians(180 - np.arcsin(abs(object2[1] - ball.loc[0][1]) / r1))
            vector1 = [lm*-int(np.cos(theta) * (r1 + r2)), lm*-int(np.sin(theta) * (r1 + r2))]
            vector2 = [lm * -int(np.cos(theta) * (r1 + r1 + r2)), lm * -int(np.sin(theta) * (r1 + r1 + r2))]
            vector3 = [lm * -int(np.cos(theta) * r1), lm * -int(np.sin(theta) * r1)]
            centre = (int(ball.loc[0][0] + vector1[0]), int(ball.loc[0][1] + vector1[1]))
            out_line1 = (int(ball.loc[0][0] + vector2[0]), int(ball.loc[0][1] + vector2[1]))
            out_line2 = (int(white_ball.ball.loc[0][0] + vector3[0]), int(white_ball.ball.loc[0][1] + vector3[1]))
            lines.append([out_line1, out_line2])
            circle2 = [centre, white_ball.ball.radius]






            for check_ball in balls_to_check:
                circle = [(check_ball.loc[0][0], check_ball.loc[0][1]), check_ball.radius]
                if circle_intersect_check(circle, circle1) or circle_intersect_check(circle, circle2):
                    # return [True, f'The {check_ball.colour} ball is snookering the ball on.']
                    snookering_balls.append(check_ball.colour)
                    snooker_count += 1
                for line in lines:
                    if line_intersect_check(line[0], line[1], circle, 1):
                        snookering_balls.append(check_ball.colour)
                        snooker_count += 1

            if snooker_count == 0:
                clear_balls += 1



            if img is not None:
                cv2.line(img, tuple(white1), tuple(object1), (255, 0, 0), 5)  # blue
                cv2.line(img, tuple(outside_line1), tuple(outside_line2), (255, 0, 0), 5)
                cv2.line(img, tuple(white2), tuple(object2), (0, 255, 0), 5)  # green
                cv2.line(img, tuple(out_line1), tuple(out_line2), (0, 255, 0), 5)
                cv2.circle(img, circle1[0], circle1[1], (255, 0, 0), 5)
                cv2.circle(img, circle2[0], circle2[1], (0, 255, 0), 5)

        if clear_balls == 0:
            return [True, f'Free ball. List of snookering balls: {snookering_balls}']






# def free_ball_search(white_ball, balls, ball_on, foul_flag=None, img=None):
#     if foul_flag is True or foul_flag is None:  # assume that a fouls has occurred
#         balls_to_search = []
#         t1 = None
#         t2 = None
#         t1a = None
#         t2a = None
#
#         tan1 = None
#         tan2 = None
#         tan1a = None
#         tan2a = None
#
#
#
#         x = sp.Symbol('x')
#         f = sp.Function('f')(x)
#         g = sp.Function('g')(x)
#
#         for ball in balls:
#             if ball.colour in ball_on:
#                 balls_to_search.append(ball)
#
#         clear_balls = 0
#         for ball in balls_to_search:
#             # if the red ball is above the white ball on the image
#             position_of_cue_ball = [None, None]
#
#             ball_on_radius = white_ball.ball.radius  # FIXME should not be called ball_on
#             if ball.loc[0][1] < white_ball.ball.loc[0][1]:
#                 position_of_cue_ball[0] = 'bottom'
#                 x1, y1 = white_ball.ball.loc[0][0], white_ball.ball.loc[0][1]
#                 x2, y2 = ball.loc[0][0], ball.loc[0][1]
#                 r1, r2 = white_ball.ball.radius, ball.radius
#                 location_multiplier = 1
#             else:
#                 position_of_cue_ball[0] = 'top'
#                 x1, y1 = ball.loc[0][0], ball.loc[0][1]
#                 x2, y2 = white_ball.ball.loc[0][0], white_ball.ball.loc[0][1]
#                 r1, r2 = ball.radius, white_ball.ball.radius
#                 location_multiplier = -1  # this needs to be done to correct the parallel lines
#
#             dM1S = r1 + r2
#             dM1M2 = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
#             dM2S = np.sqrt(dM1S**2 + dM1M2**2)
#             if x1 < x2:
#                 print('this is the case')
#                 alpha = abs(np.degrees(np.arctan((y2-y1)/(x2-x1))))
#             elif x1 == x2:
#                 alpha = 90
#             else:
#                 alpha = 180 - abs(np.degrees(np.arctan((y2-y1)/(x2-x1))))
#
#             print('alpha: ', alpha)
#             beta = abs(np.degrees(np.arcsin(dM1S/dM1M2)))
#             gamma = alpha - beta
#
#             if ball.loc[0][0] <= white_ball.ball.loc[0][0]:  # if the red is to the left of the white
#                 position_of_cue_ball[1] = 'right'
#                 # first interior tangent
#                 xt1 = x1 - r1*(np.sin(np.radians(gamma)))
#                 yt1 = y1 - r1*(np.cos(np.radians(gamma)))
#                 t1 = (int(xt1), int(yt1))
#
#                 xt2 = x2 + r2 * (np.sin(np.radians(gamma)))
#                 yt2 = y2 + r2 * (np.cos(np.radians(gamma)))
#                 t2 = (int(xt2), int(yt2))
#
#                 # first interior tangent's associated outside line
#                 xt1a = x1 - (r1 * (np.sin(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gamma))))
#                 yt1a = y1 - (r1 * (np.cos(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gamma))))
#                 t1a = (int(xt1a), int(yt1a))
#
#                 xt2a = x2 + (r2 * (np.sin(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gamma))))
#                 yt2a = y2 + (r2 * (np.cos(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gamma))))
#                 t2a = (int(xt2a), int(yt2a))
#
#
#                 # second interior tangent
#                 gam = 180 - gamma
#                 xtan1 = x1 + r1 * (np.cos(np.radians(gam)))
#                 ytan1 = y1 - location_multiplier * (r1 * (np.sin(np.radians(gam))))
#                 tan1 = (int(xtan1), int(ytan1))
#
#                 xtan2 = x2 - r2 * (np.cos(np.radians(gam)))
#                 ytan2 = y2 + location_multiplier * (r2 * (np.sin(np.radians(gam))))
#                 tan2 = (int(xtan2), int(ytan2))
#
#
#                 # second interior tangent's associated outside line
#                 xtan1a = x1 + (r1 * (np.cos(np.radians(gam)))) - location_multiplier * (2 * ball_on_radius) * (np.cos(np.radians(gam)))
#                 ytan1a = y1 - (r1 * (np.sin(np.radians(gam)))) + location_multiplier * (2 * ball_on_radius) * (np.sin(np.radians(gam)))
#                 tan1a = (int(xtan1a), int(ytan1a))
#
#                 xtan2a = x2 - (r2 * (np.cos(np.radians(gam)))) - location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gam))))
#                 ytan2a = y2 + (r2 * (np.sin(np.radians(gam)))) + location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gam))))
#                 tan2a = (int(xtan2a), int(ytan2a))
#
#             else:  # if the red is to the right of the white
#                 position_of_cue_ball[1] = 'left'
#                 # first interior tangent
#                 xt1 = x1 + r1 * (np.sin(np.radians(gamma)))
#                 yt1 = y1 + r1 * (np.cos(np.radians(gamma)))
#                 t1 = (int(xt1), int(yt1))
#
#                 xt2 = x2 - r2 * (np.sin(np.radians(gamma)))
#                 yt2 = y2 - r2 * (np.cos(np.radians(gamma)))
#                 t2 = (int(xt2), int(yt2))
#
#                 # first interior tangent's associated outside line
#                 xt1a = x1 + (r1 * (np.sin(np.radians(gamma)))) - location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gamma))))
#                 yt1a = y1 + (r1 * (np.cos(np.radians(gamma)))) - location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gamma))))
#                 t1a = (int(xt1a), int(yt1a))
#
#                 xt2a = x2 - (r2 * (np.sin(np.radians(gamma)))) - location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gamma))))
#                 yt2a = y2 - (r2 * (np.cos(np.radians(gamma)))) - location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gamma))))
#                 t2a = (int(xt2a), int(yt2a))
#
#
#                 # second interior tangent
#                 xtan1 = x1 - r1 * (np.sin(np.radians(gamma)))
#                 ytan1 = y1 - r1 * (np.cos(np.radians(gamma)))
#                 tan1 = (int(xtan1), int(ytan1))
#
#                 xtan2 = x2 + r2 * (np.sin(np.radians(gamma)))
#                 ytan2 = y2 + r2 * (np.cos(np.radians(gamma)))
#                 tan2 = (int(xtan2), int(ytan2))
#
#                 # second interior tangent's associated outside line
#                 xtan1a = x1 - (r1 * (np.sin(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gamma))))
#                 ytan1a = y1 - (r1 * (np.cos(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gamma))))
#                 tan1a = (int(xtan1a), int(ytan1a))
#
#                 xtan2a = x2 + (r2 * (np.sin(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.sin(np.radians(gamma))))
#                 ytan2a = y2 + (r2 * (np.cos(np.radians(gamma)))) + location_multiplier * ((2 * ball_on_radius) * (np.cos(np.radians(gamma))))
#                 tan2a = (int(xtan2a), int(ytan2a))
#
#             # establish the equation of the line connecting t1 and t2; in this form a*x + b*y + c = 0
#             # find a second parallel line from the opposite side of the white ball
#             # remember that for opencv the origin is in the top left corner
#             if t1 is not None and tan1 is not None:
#                 t1 = list(t1)  # first interior tangent
#                 t2 = list(t2)
#
#                 t1a = list(t1a)  # first interior tangent's parallel outside line
#                 t2a = list(t2a)
#
#                 tan1 = list(tan1)  # second interior tangent
#                 tan2 = list(tan2)
#
#                 tan1a = list(tan1a)  # second interior tangent's parallel outside line
#                 tan2a = list(tan2a)
#
#                 # for line connecting t1 and t2 and slope for t1a t2a
#                 if t1[0] < t2[0]:  # if t1's x-value is to the left of t2's x-value
#                     m = (t2[0] - t1[0]) / (t2[1] - t1[1])
#                 else:  # if t1's x-value is greater than t2's x-value
#                     m = (t1[0] - t2[0]) / (t1[1] - t2[1])
#                 a1 = m
#                 b1 = 1
#                 c1 = m*(-t1[0]) + t1[1]
#
#
#
#                 # establish another line the far side of the ball
#
#
#             # for line connecting tan1 and tan2
#
#
#
#             if img is not None:
#                 if t1 is not None:
#                     cv2.line(img, tuple(t1), tuple(t2), (255, 0, 0), 5)  # blue
#                 if t1a is not None:
#                     cv2.line(img, tuple(t1a), tuple(t2a), (255, 0, 0), 5)  # blue
#
#                 if tan1 is not None:
#                     cv2.line(img, tuple(tan1), tuple(tan2), (0, 255, 0), 5)  # green
#                 if tan1a is not None:
#                     cv2.line(img, tuple(tan1a), tuple(tan2a), (0, 255, 0), 5)  # green
#
#                 if t1 is not None:
#                     interior_tangent_1 = [t1, t2]
#                     interior_tangent_2 = [tan1, tan2]
#                     tangent_1_exterior = [t1a, t2a]
#                     tangent_2_exterior = [tan1a, tan2a]
#
#                     lines = [interior_tangent_1, interior_tangent_2, tangent_1_exterior, tangent_2_exterior]
#                     tangent_points = []
#                     # find the lines from the centre of the ball that are perpendicular to the tangents
#                     for line in lines:
#                         a = pixels_distance(line[0], ball.loc[0])
#                         b = pixels_distance(line[1], ball.loc[0])
#                         if a <= ball.radius + 5:
#                             tangent_points.append(a)
#                         elif b <= ball.radius + 5:
#                             tangent_points.append(b)
#
#                     # print(f'length tangent_points: {len(tangent_points)}')
#                     perpendicular_to_tangent_1 = [ball.loc[0], tangent_points[0]]
#                     perpendicular_to_tangent_2 = [ball.loc[0], tangent_points[1]]
#                     line_params = []
#                     # for each line, find the parameters for equation of line
#                     # for line in lines:
#                         # m = (line[1][1]-line[0][1])/(line[1][0]-line[0][0])
#
#                     print(f'location of cue ball: {position_of_cue_ball[0]}, {position_of_cue_ball[1]}')
#                     # find the circle centres for beside object ball
#
#                     # TODO Search for red dotted line collisions



# ball1 = Ball(loc=[100, 100], radius=25, colour='red')
# ball2 = Ball(loc=[90, 80], radius=24, colour='brown')
# white_ball = WhiteBall(loc=[20, 20], radius=28, colour='white')
# ball_on = ['red']
# balls = [ball1, ball2]
#
# free_ball_search(white_ball, balls, ball_on)

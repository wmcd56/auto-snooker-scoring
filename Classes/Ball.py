import numpy as np
import cv2
from matplotlib import pyplot as plt
from collections import deque


class Ball:
    colour_point_list = {
        "white": -4,
        "red": 1,
        "yellow": 2,
        "green": 3,
        "brown": 4,
        "blue": 5,
        "pink": 6,
        "black": 7
    }

    def __init__(self, loc=None, radius=None, colour=None, ball_id=None):

        # self.loc = [None, None, None, None, loc]
        self.loc = deque([], maxlen=256)  # can be changed
        self.loc.appendleft(loc)
        self.loc.appendleft(loc)
        self.radius = radius
        self.colour = colour
        self.points_if_scored = Ball.colour_point_list[colour]
        self.ball_id = ball_id

        print(self.colour, ": ", self.loc[0], ", ", self.loc[1])

    def track_ball(self, loc=None, colour=None):
        # update a buffer of past 64 frame locations
        # return buffer and ball_moving (boolean)
        if colour is not None:
            if colour != self.colour:
                print("Not the same ball, check ball colour first")
                return
        if loc is None:
            loc = self.loc

        # else presume ball colour has been checked
        self.loc.appendleft(loc)

        # if the new centre is less than 5 pixels from the last centre in x and y directions mark the ball as not moving
        if (self.loc[1][0] - 5 <= self.loc[0][0] <= self.loc[1][0] + 5) and \
                (self.loc[1][1] - 5 <= self.loc[0][1] <= self.loc[1][1] + 5):
            ball_moving = False
            print(f"The {colour} ball is not moving")
        # if the new centre is greater than 5 pixels from the last centre in x or y directions mark the ball as moving
        elif (self.loc[0][0] <= self.loc[1][0] - 5) or (self.loc[0][0] >= self.loc[1][0] + 5) or \
                (self.loc[0][1] <= self.loc[1][1] - 5) or (self.loc[0][1] >= self.loc[1][1] + 5):
            ball_moving = True
            print(f"The {colour} ball is moving")
        else:
            print(f"Bug in tracking the {colour} ball, it's probably not moving")

            return
        return ball_moving

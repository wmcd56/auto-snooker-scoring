import numpy as np
import cv2
from matplotlib import pyplot as plt


class Ball:

    def __init__(self, loc=None, colour=None, ball_id=None):
        colour_point_list = {
            "white": 0,
            "red": 1,
            "yellow": 2,
            "green": 3,
            "brown": 4,
            "blue": 5,
            "pink": 6,
            "black": 7
        }

        self.loc = loc
        self.colour = colour
        self.ball_id = ball_id

        print(self.colour, ": ", self.loc)

    def is_ball_moving(self):
        # add code to track ball
        ball_moving = False
        return ball_moving
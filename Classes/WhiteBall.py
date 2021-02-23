import numpy as np
import cv2
from matplotlib import pyplot as plt
from collections import deque
from Functions.PixelsDistance import pixels_distance
from Classes.Ball import Ball


class WhiteBall:

    def __init__(self, loc=None, radius=None, colour=None, ball_id=None):
        if colour == 'white':
            self.ball = Ball(loc, radius, 'white', ball_id)

    def first_collision(self, balls):
        ball_moving = self.ball.track_ball()
        first_ball = None
        while ball_moving:
            distances = []
            for b in balls:
                d = pixels_distance(self.ball.loc, b.loc)
                distances.append((b, d))

            # potentially a place for multiprocessing as it could happen that two balls collide at exactly the same time
            for elem in distances:
                if elem[1] - 5 <= 2*elem[0].radius <= elem[1] + 5:
                    print(f"The white ball is touching the {elem[0].colour} ball")
                    first_ball = elem[0]
                    break

            ball_moving = self.ball.track_ball()
        return first_ball

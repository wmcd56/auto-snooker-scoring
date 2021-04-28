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
        # ball_moving = True
        first_ball = None

        # loop until the white ball has stopped moving or the loop has been broken because the white has hit a ball
        if ball_moving:  # cannot loop because it will prevent the necessary looping in the main()
            distances = []  # empty list to hold the distance values between the white ball and all other balls
            for b in balls:
                d = pixels_distance(self.ball.loc[0], b.loc[0])  # calculate the distance between the white ball and ball b
                distances.append((b, d))
            # print('Distances: ', distances)
            # potentially a place for multiprocessing as it could happen that two balls collide at exactly the same time
            # check to find the first ball whose distance is closer than that of two radii +/-5 pixels
            for elem in distances:
                if elem[1] - 5 <= 2*elem[0].radius <= elem[1] + 5:
                    print(f"The white ball collided with the {elem[0].colour} ball first")
                    first_ball = elem[0]
                    break

            # commented for now because it might interrupt main()
            # check to see if the white ball is still moving so that the loop can run again
            # ball_moving = self.ball.track_ball()
        return first_ball

    def track_white(self, balls_on_table):
        differences = []
        updated_white = []
        white_on_table = True
        for ball in balls_on_table:
            differences.append(pixels_distance(self.ball.loc[0], ball.loc[0]))
        if differences:
            min_diff = min(differences)  # find the minimum difference
            index = differences.index(min_diff)  # find index of minimum difference
            # print(balls_on_table[index].colour)
            # FIXME: pink mistake
            # only update the ball if the minimum distance is less than twice the radius width and same colours
            if balls_on_table[index].colour == 'white':
                self.ball.track_ball(balls_on_table[index].loc[0])  # update the correct ball with the new location
                # updated_white.append(balls_on_table[index])
                white_on_table = True
            elif balls_on_table[index].colour != 'pink':
                white_on_table = False
        return white_on_table

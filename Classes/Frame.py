import cv2
import numpy
from Functions.PixelsDistance import pixels_distance
from .Ball import Ball
from .Player import Player
from .WhiteBall import WhiteBall


class Frame:

    # ==================================================================================================================
    # Frame class
    # -Initialised with an input of an array of *structs, circles, should contain: x, y, r, colour, ball_id
    # -
    # ==================================================================================================================
    def __init__(self, white_ball, balls, mode='practice'):
        # for practice purposes
        p1_colour = 'purple'
        p2_colour = 'orange'

        self.player1 = Player(p1_colour)
        self.player2 = Player(p2_colour)
        self.white_ball = white_ball
        self.balls = balls

        if mode == 'practice':
            print("Mode: Practice Break")
        else:
            print("The players playing include: \nPlayer 1: ", self.player1.cue_colour, "\nPlayer 2: ",
                  self.player2.cue_colour, "\nThe balls on the table are: ")  # update for clearer ball count
        for ball in self.balls:
            print(ball.colour)
        if self.white_ball:
            print(white_ball.ball.colour)

    def get_current_player(self):
        # TODO: add functionality for obtaining the current player for game scenario
        current_player = self.player1
        return current_player

    def obtain_scores(self):
        # return the current points of player
        # TODO: add functionality for game scenario
        return self.player1.current_points  # , self.player2.current_points

    def update_score(self, additional_points):
        current_player = self.player1
        current_player.current_points += additional_points

    def balls_moving(self):
        totals = []
        balls_to_check = []
        balls_moving = None
        # check past five frames to see if balls are all static
        for i in range(5):
            xy_total = 0
            # TODO: review how this works in tandem with the white_ball_moving function
            xy_total = xy_total + self.white_ball.ball.loc[i][0] + self.white_ball.ball.loc[i][1]
            for ball in self.balls:
                if len(ball.loc) >= 5:  # ensure that all balls being checked have enough length in loc deque
                    balls_to_check.append(ball)  # can arise that they do not have enough length when spotted

            for ball in balls_to_check:
                xy_total = xy_total + ball.loc[i][0] + ball.loc[i][1]
            totals.append(xy_total)

        # print('xy_total: ', totals)  # debugging

        # check to see if the totals are similar enough to conclude that the balls are not moving
        sum_xy = 0
        for num in totals:
            sum_xy = sum_xy + num

        # each xy_total for each frame must be within +/-5 of the average of the five frames
        for num in totals:
            if num-5 <= sum_xy/len(totals) <= num+5:
                balls_moving = False
            else:
                balls_moving = True

        if balls_moving is not None:
            return balls_moving

    def collision_check(self):
        balls_touching = []
        for ball in self.balls:
            for b in self.balls:
                if ball.loc[0] == b.loc[0]:
                    continue
                elif (pixels_distance(ball.loc[0], b.loc[0]) <= 2*ball.radius + 2) or (pixels_distance(ball.loc[0], b.loc[0]) <= 2*b.radius + 2):
                    balls_touching.append((ball.loc[0], b.loc[0]))
                    print(f"The {ball.colour} ball is touching the {b.colour} ball")

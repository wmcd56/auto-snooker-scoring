import cv2
import numpy
from Functions.PixelsDistance import pixels_distance
from .Ball import Ball
from .Player import Player


class Frame:

    # ==================================================================================================================
    # Frame class
    # -Initialised with an input of an array of *structs, circles, should contain: x, y, r, colour, ball_id
    # -
    # ==================================================================================================================
    def __init__(self, balls, mode='practice'):
        # for practice purposes
        p1_colour = 'purple'
        p2_colour = 'orange'

        self.player1 = Player(p1_colour)
        self.player2 = Player(p2_colour)
        self.balls = balls

        if mode == 'practice':
            print("Mode: Practice Break")
        else:
            print("The players playing include: \nPlayer 1: ", self.player1.cue_colour, "\nPlayer 2: ",
                  self.player2.cue_colour, "\nThe balls on the table are: ")  # update for clearer ball count
        for ball in self.balls:
            print(ball.colour)

    def get_current_player(self):
        # add code to track ball
        current_player = self.player1
        return current_player

    def obtain_scores(self):
        # add code to track ball
        return self.player1.current_points  # , self.player2.current_points

    def update_score(self, additional_points):
        current_player = self.player1
        current_player.current_points += additional_points

    def collision_check(self):
        balls_touching = []
        for ball in self.balls:
            for b in self.balls:
                if ball.loc[0] == b.loc[0]:
                    continue
                elif (pixels_distance(ball.loc[0], b.loc[0]) <= 2*ball.radius + 2) or (pixels_distance(ball.loc[0], b.loc[0]) <= 2*b.radius + 2):
                    balls_touching.append((ball.loc[0], b.loc[0]))
                    print(f"The {ball.colour} ball is touching the {b.colour} ball")




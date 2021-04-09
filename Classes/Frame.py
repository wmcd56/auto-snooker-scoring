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
    def __init__(self, balls, white_ball=None, mode='practice'):
        # for practice purposes
        p1_colour = 'purple'
        p2_colour = 'orange'

        # TODO remove the following
        # for ball in balls:
        #     if ball.colour == 'white':
        #         white_ball = WhiteBall(ball.loc, ball.radius, ball.colour)
        #         balls.remove(ball)
        #         break

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

    def track_balls(self, balls_on_table):
        # --------------------------------------------------------------------------------------------------------------
        # INPUTS: self: frame object,
        #         balls_on_table: a list of balls found on the table
        #
        # OPERATION: update buffer of past frame locations (ball.loc)
        #
        # RETURN: updated_balls, a list of balls which have been successfully updated
        # --------------------------------------------------------------------------------------------------------------

        reds_on_table = []
        colours_on_table = []
        frame_reds = []
        frame_colours = []
        updated_balls = []
        indexes = []
        frame_balls = self.balls

        # split the balls into colours and reds for loop efficiency
        for b in balls_on_table:
            if b.colour == 'red':
                reds_on_table.append(b)  # make a list of reds from the balls currently on the table
                continue
            else:
                colours_on_table.append(b)

        for b in frame_balls:
            if b.colour == 'red':
                frame_reds.append(b)
                continue
            else:
                frame_colours.append(b)

        for c in colours_on_table:
            differences = []

            # create a list of differences for the location of colour balls on table and saved colour balls
            for colour in frame_colours:
                differences.append(pixels_distance(c.loc[0], colour.loc[0]))
            if differences:
                min_diff = min(differences)  # find the minimum difference
                index = differences.index(min_diff)  # find index of minimum difference
                # print(f'c1: {frame_colours[index].colour}, c2: {c.colour}')
                if (min_diff <= c.radius*3) and (frame_colours[index].colour == c.colour):  # only update if same colour

                    frame_colours[index].track_ball(c.loc[0])  # update the correct red ball with the new location
                    updated_balls.append(frame_colours[index])
                    # indexes.append(index)

        for r in reds_on_table:
            differences = []
            for red in frame_reds:  # create a list of differences for the location of reds on table and previous frame
                differences.append(pixels_distance(r.loc[0], red.loc[0]))
            if differences:
                min_diff = min(differences)  # find the minimum difference
                index = differences.index(min_diff)  # find index of minimum difference
                if min_diff <= r.radius*3:  # only update the ball if the minimum distance is less than the radius width
                    frame_reds[index].track_ball(r.loc[0])  # update the correct red ball with the new location
                    updated_balls.append(frame_reds[index])
                    # indexes.append(index)

        return updated_balls

        # for b in balls_on_table:
        #     differences = []
        #     for ball in frame_balls:
        #         differences.append(pixels_distance(b.loc[0], ball.loc[0]))
        #     if differences:
        #         min_diff = min(differences)  # find the minimum difference
        #         index = differences.index(min_diff)  # find index of minimum difference
        #
        #         # only update the ball if the minimum distance is less than the radius width and same colours
        #         # if (min_diff <= b.radius) and (frame_balls[index].colour == b.colour):
        #         if min_diff <= b.radius:
        #             frame_balls[index]track_ball(b.loc[0])  # update the correct ball with the new location
        #             updated_balls.append(frame_balls[index])
        #             indexes.append(index)
        # return updated_balls

    def balls_moving(self):
        totals = []
        balls_to_check = []
        balls_moving = None
        # check past five frames to see if balls are all static
        for i in range(5):
            xy_total = 0
            balls_to_check = []

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

        # each xy_total for each frame must be within +/-10 of the average of the five frames
        for num in totals:
            if num-10 <= sum_xy/len(totals) <= num+10:
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

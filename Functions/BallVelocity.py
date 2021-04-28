import numpy as np
from .PixelsDistance import pixels_distance
from Classes.Ball import Ball


def ball_velocity(ball, frames=None):
    distance = 0
    if frames is None:
        frames = 10
    for i in range(frames):
        distance += pixels_distance(ball.loc[i], ball.loc[i+1])
    speed_per_frame = distance/frames
    if ball.loc[0][1] != ball.loc[frames-1][1]:
        direction = (ball.loc[0][0] - ball.loc[frames-1][0]) / (ball.loc[0][1] - ball.loc[frames-1][1])  # x2- x1 / y2-y1
    else:
        direction = 0.0

    return [speed_per_frame, direction]

import cv2
import numpy as np
import time
import json
from CVFunctions.CaptureFrame import capture_frame
from CVFunctions.FindBalls import find_balls


def print2app(string, window, num=None):
    if num is None:
        window['print_line_2'].update(string)
    else:
        window[f'print_line_{num}'].update(string)


def save_ball_locations(white_ball, balls):
    ball_positions = [['white', [int(white_ball.ball.loc[0][0]), int(white_ball.ball.loc[0][1])],
                       int(white_ball.ball.radius)]]

    for ball in balls:
        ball_positions.append([ball.colour, [int(ball.loc[0][0]), int(ball.loc[0][1])], int(ball.radius)])

    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/ball_positions.txt', 'w') as file:
        file.write(json.dumps(ball_positions))


def ball_replacement(cap, cv2Window, window, hough_param1, hough_param2, pockets):
    cv2.destroyWindow(cv2Window)
    replaced = False  # this will be true once the correct balls have been placed in the right positions
    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/ball_positions.txt', 'r') as file:
        ball_positions = json.load(file)

    with open('C:/Users/mcdon/Desktop/AutoSnooker/Resources/colours_bgr_original.txt', 'r') as file:
        ball_colours = json.load(file)

    print2app('Place the balls within the circles shown.', window, num=1)
    print2app('', window, num=2)

    while replaced is False:
        img, original = capture_frame(cap)
        for ball in ball_positions:
            cv2.circle(original, tuple(ball[1]), ball[2], ball_colours[ball[0]], 3)

        balls = find_balls(img, hough_param1, hough_param2,
                           show_image=False, pockets=pockets,
                           min_radius=20, max_radius=30)
        count = 0
        for ball in balls:
            for i in range(len(ball_positions)):
                if ball_positions[i][1][0] - 2 <= ball.loc[0][0] <= ball_positions[i][1][0] + 2:
                    if ball_positions[i][1][1] - 2 <= ball.loc[0][1] <= ball_positions[i][1][1] + 2:
                        if ball.colour == ball_positions[i][0]:
                            cv2.circle(original, tuple(ball_positions[i][1]), ball_positions[i][2], (0, 255, 0), 3)
                            count += 1
        print(count)
        if count == len(ball_positions):
            replaced = True
            # print2app('Balls have been successfully replaced.', window)
        cv2.imshow('Ball replacement', original)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print2app('Balls correctly replaced.', window, num=1)
    time.sleep(3)
    cv2.destroyWindow('Ball replacement')

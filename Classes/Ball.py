import numpy as np
import cv2
from matplotlib import pyplot as plt


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

    def __init__(self, loc=None, colour=None, ball_id=None):

        self.loc = loc
        self.colour = colour
        self.points_if_scored = Ball.colour_point_list[colour]
        self.ball_id = ball_id

        print(self.colour, ": ", self.loc)

    def track_ball(self):
        # add code to track ball
        # might not work as while loop needs to be in main
        tracker = cv2.TrackerKCF_create()
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)
        cap.set(4, 480)
        success, frame = cap.read()
        tracker.init(frame, )
        timer = 0

        while True:
            success, frame = cap.read()

            success, bbox = tracker.update(frame)

            if success:
                drawBox(frame, bbox)
            else:
                cv2.putText(frame, "LOST", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
            timer = cv2.getTickCount()
            cv2.putText(frame, str(int(fps)), (75, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow("Tracking", frame)

            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break


        return ball_moving
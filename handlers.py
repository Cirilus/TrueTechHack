import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import speech_recognition as sr

HIST_SIZE = 256
HIST_RANGE = (0, 256)
DELTA_THRESHOLD = 30000

def remove_flicks():
    cap = cv2.VideoCapture("test_ep2.MP4")
    prev_hist = None
    new_fps = 10
    p_f = None
    count = 0
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (width,height))
    while(True):
        ret, frame = cap.read()
        if not ret:
            break
        img = frame
        f = frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [HIST_SIZE], HIST_RANGE)

        if count > 0:

            delta = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_CHISQR)

            print(delta)
            if delta > DELTA_THRESHOLD:
                print("Dangerous moment detected")
                continue
                # eq1 = cv2.equalizeHist(gray)
                # img = cv2.cvtColor(eq1, cv2.COLOR_GRAY2BGR)

        prev_hist = hist

        p_f = f

        out.write(img)

        count += 1

        if cv2.waitKey(int(1000 / 10)) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def make_subtitles():

if __name__ == "__main__":
    make_subtitles()

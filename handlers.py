import cv2
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from pydub.silence import detect_nonsilent

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
    out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (width, height))
    while (True):
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


def is_high_pitched(segment):
    # High-pitched sounds
    threshold_freq = 5000

    noise = WhiteNoise().to_audio_segment(duration=len(segment))
    filtered_segment = segment.high_pass_filter(threshold_freq)
    filtered_noise = noise.high_pass_filter(threshold_freq)
    ratio = filtered_segment.dBFS - filtered_noise.dBFS
    return ratio > -15


def sound():
    audio = AudioSegment.from_file("input_video.mp4", "mp4")
    audio_channels = audio.split_to_mono()

    nonsilent_times = detect_nonsilent(audio_channels[0],
                                       min_silence_len=1000,
                                       silence_thresh=-54)
    start_times = [t[0] for t in nonsilent_times]
    end_times = [t[1] for t in nonsilent_times]

    filtered_audio = AudioSegment.empty()
    for i in range(len(start_times)):
        if i == 0:
            segment = audio[:start_times[i]]
        else:
            segment = audio[end_times[i - 1]:start_times[i]]

        if len(segment) < 1000:
            continue
        # Fast and repetitive sounds
        if segment.dBFS > -35 and not is_high_pitched(segment):
            filtered_audio += segment

    filtered_audio.export("output_video.mp4", format="mp4")


if __name__ == "__main__":
    pass

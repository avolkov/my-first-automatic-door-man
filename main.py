from picamera.array import PiRGBArray
from picamera import PiCamera
from espeak import espeak
import cv2

from datetime import datetime
from random import choice

BLUR = (15, 15)

time_greeting = (
    ((21, 24), "Good Night"),
    ((0, 11), "Good Morning"),
    ((11, 17), "Good Afternoon"),
    ((17, 21), "Good Evening"),
)

message_greeting = (
    "Nice weather today isn't it,",
    "Nice shirt,",
    "Have a wonderful day,",
    "Nice to see you here,",
    "I'm running out of greetings again",
    "I'm not being paid enough for this",
    "Good morning. No.   Wait. Good afternoon. No.   \
Wait. Good morning. No. Wait. Nevermind",
    "I think I've saw you before"
)


def rand_greet():
    """Choose between time-based and randomly selected phrase greeting"""

    def time_greet():
        hour = datetime.now().hour
        for t_range, greet in time_greeting:
            if hour > t_range[0] and hour <= t_range[1]:
                return greet

    def rand_greet():
        return choice(message_greeting)

    return choice((time_greet, rand_greet))()


def blur_gray(in_frame):
    out_frame = cv2.blur(in_frame, BLUR)
    # TODO conver to gray with picam
    out_frame = cv2.cvtColor(out_frame, cv2.COLOR_BGR2GRAY)
    return out_frame


class adjust_threshold(object):
    """Analyse several initial frames and adjust threshold"""

    THRESHOLD_ADJUST_MAX = 60

    def __init__(self):
        self.counter = 0
        self.baseframe = None
        self._adjusted = False
        self._threshold = 0

    def run_adjustment(self, image):
        """
        Run threshold adjustment for THRESHOLD_ADJUST_MAX cycles.
        Here be dragons.
        """
        if self.baseframe is None:
            self.baseframe = blur_gray(image)
            return

        frame = blur_gray(image)
        diff = cv2.absdiff(frame, self.baseframe)
        _, diff = cv2.threshold(diff, self.counter, 255, cv2.THRESH_BINARY)

        if cv2.countNonZero(diff) == 0:
            self._threshold = self.counter + 5
            self.adjustement_complete = True
            return

        if self.counter == self.THRESHOLD_ADJUST_MAX:
            self._threshold = self.counter
            self._adjusted = True

        self.counter += 1

    @property
    def adjusted(self):
        return self._adjusted

    @property
    def threshold(self):
        return self._threshold


class doorman(object):
    """Automatic doorman"""

    def __init__(self, adj):
        """
        Initialize automatic doorman

        :param adj: an instance of adjust_threshold
        """
        self.adj = adj
        self.baseframe = None
        self.sensor_active = False
        self.sensor_activated = False

    def detect(self, image):
        """
        Movement detection code, here be [some] dragons

        :param image: picamera/cv2 image array
        """
        if self.baseframe is None:
            self.baseframe = blur_gray(image)
            return

        frame = blur_gray(image)
        diff_frame = cv2.absdiff(frame, self.baseframe)
        _, diff_frame = cv2.threshold(
            diff_frame, self.adj.threshold, 255, cv2.THRESH_BINARY)

        h, w = diff_frame.shape[:2]
        sensor_frame = diff_frame[
            (h / 5) * 2:(h / 5) * 3,
            (w / 5) * 2:(w / 5) * 3
        ]
        frame_h, frame_w = sensor_frame.shape[:2]
        sensor_frame_px = frame_h * frame_w

        if cv2.countNonZero(sensor_frame) > sensor_frame_px * 0.4:
            self.sensor_active = True
        else:
            self.sensor_active = False

        if self.sensor_active and not self.sensor_activated:
            espeak.synth(rand_greet())

        self.sensor_activated = self.sensor_active

        cv2.rectangle(
            diff_frame,
            ((w / 5) * 2, (h / 5) * 2),
            ((w / 5) * 3, (h / 5) * 3),
            (255, 255, 255), 1
        )
        cv2.imshow('diff', diff_frame)

    def process_frame(self, image):
        """
        Process Frames, run through composited threshold code if threshold
        hasn't been adjusted, then run movement detection method.

        :param image: picamera/cv2 image array
        """
        if not self.adj._adjusted:
            self.adj.run_adjustment(image)
        else:
            self.detect(image)


def init_camera(resolution=(640, 480), framerate=32):
    """
    Initialize a picamera

    :param resolution: tuple of two integers, resolution w x h or None. \
Default 640x480.
    :param framerate: integer or None. Default 32
    :rtype: a tuple of an instance PiCamera and PiRGBArray
    """
    camera = PiCamera()
    camera.resolution = resolution
    camera.framerate = framerate
    camera.vflip = True
    raw_capture = PiRGBArray(camera, size=resolution)
    return (camera, raw_capture)


def frame_loop(camera, capture, func=None):
    """
    Execute picamera frame loop

    :param camera: initialized PiCamera instance
    :param capture: initialized PiRGBArray instance
    :param func: a function to process final image that accepts one param
 -- image or none
    :rtype: None
    """

    for frame in camera.capture_continuous(
                    capture, format="bgr", use_video_port=True):
        image = frame.array
        if func:
            func(image)
        key = cv2.waitKey(1) & 0xFF
        # clear the stream in preparation for the next frame
        capture.truncate(0)
        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break


if __name__ == '__main__':
    camera, capture = init_camera()
    adj = adjust_threshold()
    active_doorman = doorman(adj)
    frame_loop(camera, capture, func=active_doorman.process_frame)

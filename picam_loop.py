from picamera.array import PiRGBArray
from picamera import PiCamera
#import time
import cv2

BLUR = (15, 15)


def blur_gray(in_frame):
    out_frame = cv2.blur(in_frame, BLUR)
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
        if not self.baseframe:
            self.baseframe = blur_gray(image)
            return

        frame = blur_gray(image)
        diff = cv2.absdiff(frame, self.baseframe)
        diff = cv2.threshold(diff, self.counter, 255, cv2.THRESH_BINARY)
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

    def __init__(self):
        pass

    def doorman_detect(self, frame):
        frame = cv2.blur(frame, BLUR)
        # TODO conver to gray with picam
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def process_frame(self, image):
        pass


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
        cv2.imshow("Frame", image)
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame
        capture.truncate(0)

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break


if __name__ == '__main__':
    camera, capture = init_camera()
    frame_loop(camera, capture)
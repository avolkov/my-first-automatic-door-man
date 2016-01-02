from picamera.array import PiRGBArray
from picamera import PiCamera
#import time
import cv2


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
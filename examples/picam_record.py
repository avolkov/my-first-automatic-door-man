from picamera import PiCamera
from time import sleep


if __name__ == "__main__":
    # Record a sample 20 second video
    camera = PiCamera()
    camera.vflip = True
    camera.start_recording('test_video.h264')
    sleep(20)
    camera.stop_recording()

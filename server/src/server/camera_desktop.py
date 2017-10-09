from __future__ import with_statement
import cv2
import time
from threading import Thread
from threading import Lock


class Camera(object):
    stopped = False
    image = None
    camera = None
    lock = Lock()

    def start(self, resolution=(640, 480), framerate=16):
        """
        Starts camera input in a new thread.

        :param resolution Resolution
        :param framerate Framerate
        """
        self.stopped = False

        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.grab_image()

        # Start thread
        thread = Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()

    def stop(self):
        """
        Stops camera input.
        """
        self.stopped = True
        self.camera.release()

    def read(self):
        """
        Returns the most recent image read from the camera input.
        """
        with self.lock:
            return self.image

    def update(self):
        """
        Grabs next image from camera.
        """
        while not self.stopped:
            time.sleep(0.01)
            self.grab_image()

    def grab_image(self):
        """
        Grabs an image from the camera input.
        """
        _, camera_image = self.camera.read()
        with self.lock:
            self.image = camera_image
            self.image = cv2.imread("resources/debug/debug_board.png")  # TODO! Remove! Only for test purposes!

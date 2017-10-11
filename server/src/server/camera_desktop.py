from __future__ import with_statement

import traceback

import cv2
import time
from threading import Thread
from threading import Lock

import sys


class Camera(object):
    delegate = None
    stopped = False
    image = None
    camera = None
    lock = Lock()
    debug_image = None

    def start(self, delegate, resolution=(640, 480), framerate=16):
        """
        Starts camera input in a new thread.

        :param delegate: Delegate that receives new images
        :param resolution Resolution
        :param framerate Framerate
        """
        self.delegate = delegate
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
            current_image = self.grab_image()
            self.call_delegate(current_image)

    def grab_image(self):
        """
        Grabs an image from the camera input.
        """
        _, camera_image = self.camera.read()
        with self.lock:
            if self.debug_image is None:
                self.image = camera_image
            return self.image

    def call_delegate(self, current_image):
        if self.delegate is not None:
            try:
                self.delegate.camera_image_updated(current_image)
            except Exception as e:
                print("Exception in handleMessage: %s" % str(e))
                traceback.print_exc(file=sys.stdout)

    def set_debug_image(self, image):
        """
        Overrides the camera input with the given image. Set to None to revert to camera input.

        :param image: Debug image
        """
        with self.lock:
            if len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)  # Remove alpha channel
            self.debug_image = image
            self.image = image
            self.call_delegate(self.image)

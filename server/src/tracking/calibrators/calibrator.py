import time
from threading import RLock
from util import enum


State = enum.Enum('NOT_DETECTED', 'DETECTED')


class Calibrator(object):
    def __init__(self):

        # Initialize instance variables
        self.lock = RLock()

        self.detect_min_stable_time = 2.0
        self.detect_min_count = 2

        self.detect_history = []

    def reset(self):
        self.detect_history = []

    def update(self, image):
        """
        Updates detection state with image.

        :param image: Input image
        :return: Current detection state
        """

        # Perform detection
        result = self.detect(image)

        # Update history
        if result is not None:
            with self.lock:
                self.detect_history.append({"timestamp": time.time(), "result": result})

        # Return detected state
        return self.get_state()

    def get_state(self):
        with self.lock:

            # Check sufficient amount of detections
            if len(self.detect_history) < self.detect_min_count:
                return State.NOT_DETECTED

            # Check sufficient time ellapsed
            if self.detect_history[-1]["timestamp"] - self.detect_history[0]["timestamp"] < self.detect_min_stable_time:
                return State.NOT_DETECTED

            return State.DETECTED

    def detect(self, image, debug=False):
        """
        Performs a single detection with the given image.

        :param image: Input image
        :param debug: Enable debug output
        :return: Detection result
        """
        pass

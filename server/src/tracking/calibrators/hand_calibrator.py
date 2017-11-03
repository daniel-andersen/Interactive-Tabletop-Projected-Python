import numpy as np
import cv2

from tracking.calibrators.calibrator import Calibrator, State


class HandCalibrator(Calibrator):
    """
    Class capable of calibrating hand detection.
    """
    def __init__(self):
        super().__init__()

    def get_medians(self):
        with self.lock:
            return self.detect_history[-1]["result"] if self.get_state() == State.DETECTED else None

    def detect(self, image, debug=False):
        return None

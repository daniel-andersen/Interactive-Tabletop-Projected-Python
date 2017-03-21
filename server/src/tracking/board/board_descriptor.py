from threading import RLock
from tracking.board.board_snapshot import BoardSnapshot
from tracking.board.board_detector import BoardDetector
from tracking.board.board_detector import State as DetectionState
from util import enum


State = enum.Enum('INITIALIZING', 'DETECTING', 'READY', 'CALIBRATING')


class BoardDescriptor(object):
    """
    Class representing a description of a board.
    """
    def __init__(self):
        self.lock = RLock()

        self.state = State.INITIALIZING

        self.board_snapshot = BoardSnapshot()

        self.board_corners = None

        self.board_detector = BoardDetector(board_image_filename='resources/board_detection.png')
        self.board_calibrator = BoardDetector(board_image_filename='resources/board_calibration.png')

        self.switch_to_detection_state()

    def switch_to_detection_state(self):
        self.state = State.DETECTING

    def switch_to_ready_state(self):
        self.state = State.READY

    def switch_to_calibration_state(self):
        self.state = State.CALIBRATING

    def update(self, image):

        with self.lock:

            # Update detection state
            if self.state == State.DETECTING:
                self.update_detection(image)

            # Update ready state
            if self.state == State.READY:
                self.update_ready(image)

    def update_detection(self, image):

        # Update detection
        detection_state = self.board_detector.update(image)

        # Detected board
        if detection_state == DetectionState.DETECTED:
            self.board_corners = self.board_detector.get_corners()
            self.switch_to_ready_state()

    def update_ready(self, image):
        pass

    def get_snapshot(self):
        with self.lock:
            return self.board_snapshot

    def set_board_snapshot(self, snapshot):
        with self.lock:
            self.board_snapshot = snapshot

    def is_recognized(self):
        with self.lock:
            return self.board_snapshot is not None

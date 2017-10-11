from threading import RLock

from tracking.board.board_detector import BoardDetector
from tracking.board.board_snapshot import BoardSnapshot, SnapshotStatus


class BoardDescriptor(object):
    """
    Class representing a description of a board.
    """
    def __init__(self):
        self.lock = RLock()

        self.board_detector = BoardDetector(board_image_filename='resources/board_calibration.png')

        self.board_snapshot = BoardSnapshot()
        self.board_snapshot.status = SnapshotStatus.NOT_RECOGNIZED

    def update(self, image):
        with self.lock:
            self.board_snapshot = BoardSnapshot(camera_image=image, board_corners=self.board_detector.get_corners())

    def set_board_detector(self, board_detector):
        with self.lock:
            self.board_detector = board_detector

    def get_board_detector(self):
        with self.lock:
            return self.board_detector

    def set_board_snapshot(self, snapshot):
        with self.lock:
            self.board_snapshot = snapshot

    def get_board_snapshot(self):
        with self.lock:
            return self.board_snapshot

    def is_recognized(self):
        with self.lock:
            return self.board_snapshot is not None

from threading import RLock

from tracking.board.board_snapshot import BoardSnapshot, SnapshotStatus
from tracking.calibrators.board_calibrator import BoardCalibrator


class BoardDescriptor(object):
    """
    Class representing a description of a board.
    """
    def __init__(self):
        self.lock = RLock()

        self.board_calibrator = BoardCalibrator(board_image_filename='resources/calibration/board_calibration.png')

        self.board_snapshot = BoardSnapshot()
        self.board_snapshot.status = SnapshotStatus.NOT_RECOGNIZED

    def update(self, image):
        with self.lock:
            self.board_snapshot = BoardSnapshot(camera_image=image, board_corners=self.board_calibrator.get_corners())

    def set_board_calibrator(self, board_calibrator):
        with self.lock:
            self.board_calibrator = board_calibrator

    def get_board_calibrator(self):
        with self.lock:
            return self.board_calibrator

    def set_board_snapshot(self, snapshot):
        with self.lock:
            self.board_snapshot = snapshot

    def get_board_snapshot(self):
        with self.lock:
            return self.board_snapshot

    def is_recognized(self):
        with self.lock:
            return self.board_snapshot is not None

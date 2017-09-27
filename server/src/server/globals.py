from threading import RLock


class GlobalState:

    debug = False

    """
    RGB camera
    """

    _camera = None
    camera_lock = RLock()

    def get_camera(self):
        with self.camera_lock:
            return self._camera

    def set_camera(self, camera):
        with self.camera_lock:
            self._camera = camera

    """
    Board detector
    """

    _board_detector = None
    board_detector_lock = RLock()

    def get_board_detector(self):
        with self.board_detector_lock:
            return self._board_detector

    def set_board_detector(self, board_detector):
        with self.board_detector_lock:
            self._board_detector = board_detector


_global_state_instance = GlobalState()


def get_state():
    return _global_state_instance

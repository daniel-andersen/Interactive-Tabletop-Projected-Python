from threading import RLock
from tracking.board.board_descriptor import BoardDescriptor
from tracking.board.board_area import BoardArea
from tracking.board.board_area import BoardAreaId_FULL_BOARD


class GlobalState:

    debug = False

    def __init__(self):

        # Perform reset
        self.reset_board_descriptor()
        self.reset_board_areas()
        self.reset_detectors()

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

    """
    Board descriptor
    """

    _board_descriptor = None
    board_descriptor_lock = RLock()

    def reset_board_descriptor(self):
        board_descriptor = BoardDescriptor()
        board_descriptor.board_size = [1280, 800]
        board_descriptor.border_percentage_size = [0.0, 0.0]
        self.set_board_descriptor(board_descriptor)

    def get_board_descriptor(self):
        with self.board_descriptor_lock:
            return self._board_descriptor

    def set_board_descriptor(self, board_descriptor):
        with self.board_descriptor_lock:
            self._board_descriptor = board_descriptor

    """
    Board areas
    """

    _board_areas = {}
    board_areas_lock = RLock()

    def reset_board_areas(self):
        with self.board_areas_lock:
            self._board_areas = {}

            # Initialize default board area (full board)
            board_area = BoardArea(
                area_id=BoardAreaId_FULL_BOARD,
                board_descriptor=self.get_board_descriptor(),
                rect=[0.0, 0.0, 1.0, 1.0]
            )
            self.set_board_area(board_area.area_id, board_area)

    def get_board_area(self, area_id):
        with self.board_areas_lock:
            return self._board_areas[area_id] if area_id in self._board_areas else None

    def set_board_area(self, area_id, board_area):
        with self.board_areas_lock:
            self._board_areas[area_id] = board_area

    def remove_board_area(self, area_id):
        with self.board_areas_lock:
            del self._board_areas[area_id]

    """
    Detectors
    """

    _detectors= {}
    detectors_lock = RLock()

    def reset_detectors(self):
        with self.detectors_lock:
            self._detectors = {}

    def get_detector(self, detector_id):
        with self.detectors_lock:
            return self._detectors[detector_id] if detector_id in self._detectors else None

    def set_detector(self, detector_id, detector):
        with self.detectors_lock:
            self._detectors[detector_id] = detector

    def remove_detector(self, detector_id):
        with self.detectors_lock:
            del self._detectors[detector_id]


def reset():
    global _global_state_instance, _global_state_instance_lock
    with _global_state_instance_lock:
        _global_state_instance = GlobalState()


def get_state():
    global _global_state_instance, _global_state_instance_lock
    with _global_state_instance_lock:
        return _global_state_instance


_global_state_instance = None
_global_state_instance_lock = RLock()

reset()

import time

from server import globals
from server.threads.server_thread import ServerThread
from tracking.board.board_area import BoardAreaId_FULL_BOARD
from tracking.calibrators.calibrator import State
from tracking.calibrators.hand_calibrator import HandCalibrator
from tracking.detectors.hand_detector import HandDetector, handDetectorId


class HandDetectorCalibrationThread(ServerThread):
    def __init__(self, request_id, callback_function):
        super().__init__(request_id)
        self.callback_function = callback_function

    def _run(self):

        # Create hand calibrator
        hand_calibrator = HandCalibrator()

        # Update hand calibration
        while True:

            # Sleep a while
            time.sleep(0.01)

            # Check if stopped
            if self.stopped:
                return

            # Get whole board area
            board_area = globals.get_state().get_board_area(BoardAreaId_FULL_BOARD)
            if board_area is None:
                continue

            # Check calibrated
            if hand_calibrator.get_state() == State.DETECTED:

                # Create new hand detector
                hand_detector = HandDetector(detector_id=handDetectorId, medians=hand_calibrator.get_medians())
                globals.get_state().set_detector(hand_detector)

                # Callback
                print('Hand calibrated')
                self.callback_function()
                return

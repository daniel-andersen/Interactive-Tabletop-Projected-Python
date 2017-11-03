import time

from server import globals
from server.threads.server_thread import ServerThread
from tracking.board.board_area import BoardAreaId_FULL_BOARD


class HandDetectorCalibrationThread(ServerThread):
    def __init__(self, request_id, callback_function):
        super().__init__(request_id)
        self.callback_function = callback_function

    def _run(self):

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

            # Detect hand

            # Check calibrated
            #if board_calibrator.get_state() == State.DETECTED:
            #    print('Board calibrated')
            #    self.callback_function()
            #    return

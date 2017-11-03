import time

from server import globals
from server.threads.server_thread import ServerThread
from tracking.board.board_detector import State


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

            # Get board detector
            board_detector = globals.get_state().get_board_descriptor().get_board_detector()

            # Update board calibrator with camera image
            with globals.get_state().camera_lock:
                camera = globals.get_state().get_camera()
                if camera is not None:
                    image = camera.read()
                    if image is not None:
                        board_detector.update(image)

            # Check calibrated
            if board_detector.get_state() == State.DETECTED:
                print('Board calibrated')
                self.callback_function()
                return

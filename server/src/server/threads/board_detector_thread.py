import time

from threading import Thread
from server import globals
from server.threads.server_thread import ServerThread
from tracking.board.board_detector import State


class BoardDetectorThread(ServerThread):
    def __init__(self, callback_function, timeout_function=None, timeout=20.0):
        super().__init__()
        self.timeout_function = timeout_function
        self.callback_function = callback_function
        self.timeout = timeout

    def _run(self):

        # Update board calibration
        start_time = time.time()

        while time.time() < start_time + self.timeout:

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

        # Timeout
        print('Board calibration timed out!')
        if self.timeout_function is not None:
            self.timeout_function()

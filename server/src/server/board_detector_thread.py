import time

from threading import Thread
from server import globals
from tracking.board import board_detector


class BoardDetectorThread(object):
    def __init__(self, callback_function, timeout_function=None, timeout=20.0):
        self.timeout_function = timeout_function
        self.callback_function = callback_function
        self.timeout = timeout

    def start(self):
        thread = Thread(target=self._run, args=())
        thread.start()

    def _run(self):

        # Create board detector
        with globals.get_state().board_detector_lock:
            if globals.get_state().get_board_detector() is None:
                globals.get_state().set_board_detector(board_detector.BoardDetector(board_image_filename='resources/board_calibration.png'))

        # Update board calibration
        start_time = time.time()

        while time.time() < start_time + self.timeout:

            # Sleep a while
            time.sleep(0.01)

            # Update board calibrator with camera image
            with globals.get_state().camera_lock:
                camera = globals.get_state().get_camera()
                if camera is not None:
                    image = camera.read()
                    if image is not None:
                        globals.get_state().get_board_detector().update(image)

            # Check calibrated
            if globals.get_state().get_board_detector().get_state() == board_detector.State.DETECTED:
                print('Board calibrated')
                self.callback_function()
                return

        # Timeout
        print('Board calibration timed out!')
        if self.timeout_function is not None:
            self.timeout_function()

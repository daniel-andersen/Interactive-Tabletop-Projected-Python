import time
from server.threads.server_thread import ServerThread
from tracking.detectors.nonobstructed_area_detector import NonobstructedAreaDetector


class NonobstructedAreaDetectorThread(ServerThread):
    def __init__(self, request_id, board_area, target_size, target_point, keep_running, callback_function):
        super().__init__(request_id)
        self.board_area = board_area
        self.target_size = target_size
        self.target_point = target_point
        self.keep_running = keep_running
        self.callback_function = callback_function

        self.nonobstructedRectangleDetector = NonobstructedAreaDetector(self.target_size, self.target_point)

    def _run(self):

        first_run = True

        while True:

            # Sleep a while
            if not first_run:
                time.sleep(self.fixed_update_delay)

            first_run = True

            # Check if stopped
            if self.stopped:
                return

            # Check if we have a board area image
            if self.board_area.area_image() is not None:

                # Find rectangle
                rect = self.nonobstructedRectangleDetector.detect(board_area=self.board_area)

                if rect is not None or not self.keep_running:
                    self.callback_function(rect)
                    return

            # No board area image
            else:

                # Give up waiting if not keep running
                if not self.keep_running:
                    self.callback_function(None)
                    return

                # Wait for board image
                continue

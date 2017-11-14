import time
from server.threads.server_thread import ServerThread


class ImagesDetectorThread(ServerThread):
    def __init__(self, request_id, detector, board_area, keep_running, callback_function):
        super().__init__(request_id)
        self.detector = detector
        self.board_area = board_area
        self.keep_running = keep_running
        self.callback_function = callback_function

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

                # Update
                result = self.detector.detect(board_area=self.board_area)
                self.callback_function(result)

                # Stop running
                if not self.keep_running:
                    return

            # No board area image
            else:

                # Give up waiting if not keep running
                if not self.keep_running:
                    self.callback_function([])
                    return

                # Wait for board image
                continue

import time
from server.threads.server_thread import ServerThread
from tracking.detectors.nonobstructed_area_detector import NonobstructedAreaDetector


class NonobstructedAreaDetectorThread(ServerThread):
    def __init__(self, request_id, board_area, target_size, target_position, current_position, padding, stable_time, keep_running, callback_function):
        super().__init__(request_id)
        self.board_area = board_area
        self.stable_time = stable_time
        self.keep_running = keep_running
        self.callback_function = callback_function

        self.nonobstructedRectangleDetector = NonobstructedAreaDetector(target_size, target_position, current_position, padding)

    def _run(self):

        detection_history = []
        start_time = time.time()
        last_sent_center = None

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
                result = self.nonobstructedRectangleDetector.detect(board_area=self.board_area)

                # Update history
                if result is not None:
                    detection_history.append({"timestamp": time.time(), "result": result})

                while len(detection_history) > 0 and detection_history[0]["timestamp"] < time.time() - self.stable_time:
                    detection_history.pop(0)

                # Check stable detection
                if time.time() < start_time + self.stable_time:
                    continue

                centers = [result_dict["result"]["matches"][0]["center"] for result_dict in detection_history]
                if len(centers) == 0 or centers.count(centers[0]) != len(centers):
                    continue

                if last_sent_center is None or last_sent_center == centers[0]:
                    last_sent_center = centers[0]
                    self.callback_function(result)

                # Stop running
                if not self.keep_running:
                    return

            # No board area image
            else:

                # Give up waiting if not keep running
                if not self.keep_running:
                    self.callback_function(None)
                    return

                # Wait for board image
                continue

from server.threads.server_thread import ServerThread


class ImagesDetectorThread(ServerThread):
    def __init__(self, request_id, detector, board_area, callback_function):
        super().__init__(request_id)
        self.detector = detector
        self.board_area = board_area
        self.callback_function = callback_function

    def _run(self):
        result = self.detector.detect(board_area=self.board_area)
        self.callback_function(result)

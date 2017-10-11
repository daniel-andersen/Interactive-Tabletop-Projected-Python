from threading import Thread


class ImagesDetectorThread(object):
    def __init__(self, detector, board_area, callback_function):
        self.detector = detector
        self.board_area = board_area
        self.callback_function = callback_function

    def start(self):
        thread = Thread(target=self._run, args=())
        thread.start()

    def _run(self):
        result = self.detector.detect(board_area=self.board_area)
        self.callback_function(result)

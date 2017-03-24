class HandDetector(object):

    def __init__(self, board_area, medians=[]):
        """
        :param board_area: Board area
        :param medians: Medians
        """
        self.board_area = board_area
        self.medians = medians

    def detect_hand(self, debug=False):
        """
        Detects hand in image.

        :param debug: If True, output debug info
        :return: Hand info [[(finger pos x, finger pos y), ...], ...]
        """
        pass

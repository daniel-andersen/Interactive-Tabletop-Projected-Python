from tracking.board.board_snapshot import SnapshotSize


class Detector(object):

    def __init__(self, detector_id=None):
        """
        :param detector_id: Detector ID
        """
        self.detector_id = detector_id

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to medium.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return SnapshotSize.MEDIUM

    def detect(self, image=None, board_area=None):
        """
        Run detector in image or board area.

        :param image: Image
        :param board_area: Board area
        :return: Detector-dependant output
        """
        if image is not None:
            return self.detect_in_image(image)
        if board_area is not None:
            return self.detect_in_board_area(board_area)
        raise Exception("Either 'image' or 'board_area' must be given as input to 'detect'")

    def detect_in_image(self, image):
        raise Exception("Function 'detect_in_image' must be overridden!")

    def detect_in_board_area(self, board_area):
        return self.detect_in_image(board_area.area_image(size=self.preferred_input_image_resolution()))

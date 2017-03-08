import cv2
from board.board_descriptor import BoardDescriptor


class Detector(object):

    def __init__(self, detector_id):
        """
        :param detector_id: Detector ID
        """
        self.detector_id = detector_id

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to medium.

        :return: Input resolution (of type BoardDescriptor.SnapshotSize)
        """
        return BoardDescriptor.SnapshotSize.MEDIUM

    def detect(self, image):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected features each in form {"detectorId", "centerX", "centerY", "width", "height", "angle", ...}
        """
        return []

from tracking.board.snapshot import SnapshotSize


class Detector(object):

    def __init__(self, detector_id):
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

    def detect(self, image):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected features each containing at least {"detectorId", "centerX", "centerY", "width", "height", "angle"}
        """
        return []

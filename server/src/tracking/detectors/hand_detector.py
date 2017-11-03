import cv2
from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector


handDetectorId = "handDetector"


class HandDetector(Detector):
    """
    Class implementing hand detector.
    """
    def __init__(self, detector_id, medians=[]):
        """
        :param detector_id: Detector ID
        :param board_area: Board area
        """
        super().__init__(detector_id)

        self.medians = medians

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to medium.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return SnapshotSize.EXTRA_SMALL

    def detect_in_image(self, image):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected hands each containing {boundingRect: {x1, y1, x2, y2}}
        """

        # Convert image to grayscale
        #grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #blur_image = cv2.GaussianBlur(grayscale_image, ksize=(5, 5), sigmaX=0)

        #_, threshold_image = cv2.threshold(blur_image, 70, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        #cv2.imshow('Area image', threshold_image)
        #cv2.waitKey(0)

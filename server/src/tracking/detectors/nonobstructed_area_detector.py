import cv2
from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector


class NonobstructedAreaDetector(Detector):
    """
    Class implementing nonobstructed area detector.
    """
    def __init__(self, detector_id, rectangle, target_point=None):
        """
        :param detector_id: Detector ID
        :param rectangle: Rectangle to fit
        :param target_point: Optional target point for which to find nonobstructed space
        """
        super().__init__(detector_id)

        self.rectangle = rectangle
        self.target_point = target_point

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
        :return: List of detected nonobstructed areas {detectorId, matches: [{x1, y1, x2, y2}]}
        """

        # Prepare image
        image = self.prepare_image(image)

        # Debug
        if False:
            #debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            debug_image = image
            cv2.imshow("Desk", debug_image)
            cv2.waitKey(0)

        return {"detectorId": self.detector_id,
                "matches": []}

    def prepare_image(self, image):

        # Grayscale image
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Blur image
        blur_image = cv2.GaussianBlur(grayscale_image, (7, 7), 0)

        # Threshold image
        _, threshold_image = cv2.threshold(blur_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Remove noise
        dilate_image = cv2.dilate(threshold_image, (3, 3))
        erode_image = cv2.erode(dilate_image, (3, 3))

        return erode_image

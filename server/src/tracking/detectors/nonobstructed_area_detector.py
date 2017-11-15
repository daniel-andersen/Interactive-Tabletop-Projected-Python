import cv2
import numpy as np

from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector
from tracking.util import misc_math


class NonobstructedAreaDetector(Detector):
    """
    Class implementing nonobstructed area detector.
    """
    def __init__(self, target_size, target_point=[0.5, 0.5]):
        """
        :param size: Size to fit (width, height)
        :param target_point: Optional target point for which to find nonobstructed space
        """
        super().__init__()

        self.target_size = target_size
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

        # Calculate sizes
        image_height, image_width = image.shape[:2]

        rect_width = int(self.target_size[0] * float(image_width))
        rect_height = int(self.target_size[1] * float(image_height))

        # Debug
        if False:
            debug_image = image
            cv2.imshow("Desk", debug_image)
            cv2.waitKey(0)

        # Calculate maximum values
        max_x = image_width - rect_width
        max_y = image_height - rect_height

        # Calculate step
        step_x = int(rect_width / 2)
        step_y = int(rect_height / 2)

        # Calculate target in image
        target_in_image = [int(self.target_point[0] * image_width), int(self.target_point[1] * image_height)]

        # Add points to check
        points_to_check = []

        for i in range(0, max_y, step_y):
            for j in range(0, max_x, step_x):
                center = [j + int(rect_width / 2), i + (rect_height / 2)]
                distance_to_target = misc_math.distance(center, target_in_image)
                points_to_check.append({"rectangle": {"x": j, "y": i, "width": rect_width, "height": rect_height},
                                        "distanceToTarget": distance_to_target})

        # Sort distances
        sorted_points = sorted(points_to_check, key=lambda p: p["distanceToTarget"])

        # Scan through points
        for point in sorted_points:

            # Check if rectangle fits here
            rect = point["rectangle"]
            result = self.check_rectangle(image, rect["x"], rect["y"], rect["width"], rect["height"])
            if result:
                return {"detectorId": self.detector_id,
                        "matches": [{
                            "center": [float(rect["x"] + (rect["width"] / 2.0)) / float(image_width),
                                       float(rect["y"] + (rect["height"] / 2.0)) / float(image_height)],
                            "left": float(rect["x"]) / float(image_width),
                            "top": float(rect["y"]) / float(image_height),
                            "width": float(rect["width"]) / float(image_width),
                            "height": float(rect["height"]) / float(image_height)
                        }]}

        return None

    def prepare_image(self, image):

        image_height, image_width = image.shape[:2]

        # Grayscale image
        grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Blur image
        blur_image = cv2.GaussianBlur(grayscale_image, (7, 7), 0)

        # Threshold image
        _, threshold_image = cv2.threshold(blur_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

        # Remove noise
        dilate_image = cv2.dilate(threshold_image, (3, 3))
        erode_image = cv2.erode(dilate_image, (3, 3))

        # Invert image if necessary
        percentage_white = np.count_nonzero(erode_image) / (image_width * image_height)
        if percentage_white > 0.5:
            corrected_image = np.bitwise_not(erode_image)
        else:
            corrected_image = erode_image

        return corrected_image

    def check_rectangle(self, image, x, y, width, height):

        # Draw rectangle
        rect_image = np.zeros(image.shape[0:2], np.uint8)
        rect_image = cv2.rectangle(rect_image, (x, y), (x + width, y + height), color=(255, 255, 255), thickness=-1)

        # Merge images
        merge_image = np.logical_and(image, rect_image)

        if False:
            print(np.any(merge_image))
            debug_image = image + rect_image
            cv2.imshow("Rect", debug_image)
            cv2.waitKey(0)

        return not np.any(merge_image)

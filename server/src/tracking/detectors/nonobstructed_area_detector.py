import cv2
import numpy as np

from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector
from tracking.util import misc_math


class NonobstructedAreaDetector(Detector):
    """
    Class implementing nonobstructed area detector.
    """
    def __init__(self, target_size, target_position=[0.5, 0.5], current_position=None, padding=[0.0, 0.0]):
        """
        :param target_size: Size to fit (width, height)
        :param target_position: Optional target point for which to find nonobstructed space
        :param current_position: (Optional) Excludes current position area minus half padding
        :param padding: Optional area padding
        """
        super().__init__()

        self.target_size = target_size
        self.target_point = target_position
        self.current_position = current_position
        self.padding = padding

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

        # Calculate sizes
        image_height, image_width = image.shape[:2]

        pct_width = self.target_size[0] + (self.padding[0] * 2.0)
        pct_height = self.target_size[1] + (self.padding[1] * 2.0)

        rect_width = int(pct_width * float(image_width))
        rect_height = int(pct_height * float(image_height))

        # Adjust target point to fit screen
        self.target_point[0] = max(pct_width / 2.0, self.target_point[0])
        self.target_point[0] = min(1.0 - (pct_width / 2.0), self.target_point[0])

        self.target_point[1] = max(pct_height / 2.0, self.target_point[1])
        self.target_point[1] = min(1.0 - (pct_height / 2.0), self.target_point[1])

        # Prepare image
        image = self.prepare_image(image)

        cv2.imwrite("nonobstructed_area_detector.png", image)

        # Debug
        if False:
            debug_image = image
            cv2.imshow("Desk", debug_image)
            cv2.waitKey(0)

        # Calculate maximum values
        max_x = image_width - rect_width
        max_y = image_height - rect_height

        # Calculate step
        step_x = int(rect_width / 4)
        step_y = int(rect_height / 4)

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

        # Threshold image
        threshold_image = cv2.adaptiveThreshold(grayscale_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 5, 7)

        # Remove area itself
        if self.current_position is not None:
            rect_width = int((self.target_size[0] + (self.padding[0] * 1.5)) * float(image_width))
            rect_height = int((self.target_size[1] + (self.padding[1] * 1.5)) * float(image_height))
            rect_x = int((self.current_position[0] * float(image_width)) - (rect_width / 2.0))
            rect_y = int((self.current_position[1] * float(image_height)) - (rect_height / 2.0))
            threshold_image = cv2.rectangle(threshold_image, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), color=(0, 0, 0), thickness=-1)

        return threshold_image

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

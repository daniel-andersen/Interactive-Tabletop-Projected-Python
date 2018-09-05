import cv2
import numpy as np
import math

from skimage.morphology import watershed

from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector
from tracking.util import misc_math


class ColoredBrickDetector(Detector):
    """
    Class implementing simple colored brick detector.
    """
    def __init__(self, detector_id):
        """
        :param detector_id: Detector ID
        """
        super().__init__(detector_id)

        self.classes = {
            "Red": {
                "hue": [0, 179]
            },
            "Yellow": {
                "hue": [27]
            },
            "Green": {
                "hue": [50, 90]
            },
            "Blue": {
                "hue": [110]
            }
        }

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to small.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return SnapshotSize.SMALL

    def detect_in_image(self, image, debug=False):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected bricks {detectorId, bricks: [{class, x, y, radius}]}
        """

        image_height, image_width = image.shape[:2]

        # Meanshift segmentation
        meanshift_image = cv2.pyrMeanShiftFiltering(image, 21, 51)

        # Convert into HSV
        hsv_image = cv2.cvtColor(meanshift_image, cv2.COLOR_BGR2HSV)

        hue_image, saturation_image, value_image = cv2.split(hsv_image)

        # Check if image has black in it
        has_black_in_image = np.max(value_image) - np.min(value_image) > 100

        # Normalize brightness
        cv2.normalize(value_image, value_image,  0, 255, cv2.NORM_MINMAX)

        # Saturation threshold - bricks are saturated
        mask = np.zeros((image_height+2, image_width+2), dtype=np.uint8)

        while True:
            minValue, maxValue, minLoc, maxLoc = cv2.minMaxLoc(saturation_image, mask=~mask[1:image_height + 1, 1:image_width + 1])

            floodflags = 4
            floodflags |= (255 << 8)
            cv2.floodFill(saturation_image, mask, minLoc, 1, 5, 5, flags=floodflags)

            points = np.argwhere(mask==255)
            if len(points) > (image_width*0.75) * (image_height*0.75):
                break

        # Filter contours on properties
        contours = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[1]

        first_pass_valid_contours = [contour for contour in contours if self.is_contour_valid(contour, image, pass_number=1)]

        if len(first_pass_valid_contours) == 0:
            return self.get_result_dict(bricks=[], image=image)

        # Seperate connected "brick contours" by hue
        second_pass_valid_contours = []

        for contour in first_pass_valid_contours:

            # Draw contour mask
            contour_mask = np.zeros(image.shape[:2], np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, 255, -1)

            # Extract hue part
            hue_contour_image = hue_image[np.where(contour_mask == 255)]

            # Calculate histogram of hue
            counts, bins = np.histogram(hue_contour_image, range(257))

            # Sort histogram with most common hue first
            hist = [(i, counts[i]) for i in range(0, len(counts))]
            sorted_hist = sorted(hist, key=lambda e: e[1], reverse=True)

            # Group most common hues in ranges
            hue_ranges = []

            max_hist_count = sorted_hist[0][1]

            range_span = 6
            for i, count in sorted_hist:
                if count < max_hist_count * 0.5:
                    break
                hue_ranges.append((i - range_span, i + range_span))

            # Sort ranges on hue value
            hue_ranges = sorted(hue_ranges, key=lambda e: e[0])

            # Combine overlapping ranges
            combined_ranges = []
            for hue_range in hue_ranges:
                combined = False
                for i in range(0, len(combined_ranges)):
                    other_range = combined_ranges[i]
                    if hue_range[1] >= other_range[0] and hue_range[0] <= other_range[1]:
                        combined_ranges[i] = (min(hue_range[0], other_range[0]), max(hue_range[1], other_range[1]))
                        combined = True
                        break
                if not combined:
                    combined_ranges.append(hue_range)

            # Get valid contours from saturation segmented by hue ranges
            for hue_range in combined_ranges:

                # Segment image with hue range
                hue_mask = cv2.inRange(hue_image, hue_range[0], hue_range[1])
                ranged_mask = cv2.bitwise_and(contour_mask, contour_mask, mask=hue_mask)

                # Add all resulting valid contours
                _, other_contours, other_hierarchy = cv2.findContours(ranged_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                for other_contour in other_contours:
                    if self.is_contour_valid(other_contour, image, pass_number=2):
                        second_pass_valid_contours.append(other_contour)

        # Detect bricks among contours
        found_bricks = []

        for contour in second_pass_valid_contours:

            # Find minimum enclosing circle of contour
            (x, y), radius = cv2.minEnclosingCircle(contour)

            # Calculate the "quality" of the contour compared to the detected circle
            quality = self.get_contour_quality(contour, radius)

            # Check if quality passes quality control ;)
            if quality < 0.3:
                continue

            # Draw mask from contour
            contour_mask = np.zeros(image.shape[:2], np.uint8)
            cv2.drawContours(contour_mask, [contour], -1, 255, -1)

            # Get masked hue
            hue_contour_image = hue_image[np.where(contour_mask == 255)]

            # Calculate histogram from hue
            counts, bins = np.histogram(hue_contour_image, range(257))

            # Sort with most common hue value first
            hist = [(i, counts[i]) for i in range(0, len(counts))]
            sorted_hist = sorted(hist, key=lambda e: e[1], reverse=True)

            brick_hue = sorted_hist[0][0]

            # Calculate "blackness" of brick from brightness
            value_contour_image = value_image[np.where(contour_mask == 255)]
            counts, bins = np.histogram(value_contour_image, range(257))

            hist = [(i, counts[i]) for i in range(0, len(counts))]
            sorted_value_hist = sorted(hist, key=lambda e: e[1], reverse=True)

            brick_value = sorted_value_hist[0][0]

            # Calculate propability of black brick
            propability_black = 1.0 - (brick_value / 255.0)

            # Make guess at brick class
            best_class_name = "Black"

            if propability_black < 0.95 or not has_black_in_image:
                best_hue_dist = None

                # Run through all classes
                for class_name, class_dict in self.classes.items():

                    # Run through all hues valid for this class
                    for hue in class_dict["hue"]:

                        # Calculate distance to class hue
                        hue_dist = abs(hue - brick_hue)

                        if best_hue_dist is None or hue_dist < best_hue_dist:
                            best_hue_dist = hue_dist
                            best_class_name = class_name

            # Register found brick
            found_bricks.append({
                "class": best_class_name,
                "hue": brick_hue,
                "center": (int(x), int(y)),
                "radius": int(radius),
                "quality": quality,
                "propabilityBlack": propability_black
            })

        # Return result
        return self.get_result_dict(found_bricks, image)

    def get_result_dict(self, bricks, image):
        image_height, image_width = image.shape[:2]

        return {
            "detectorId": self.detector_id,
            "bricks": [
                {
                    "class": brick["class"],
                    "x": float(brick["center"][0]) / float(image_width),
                    "y": float(brick["center"][1]) / float(image_height),
                    "radius": float(brick["radius"]) / float(max(image_width, image_height))
                 }
            for brick in bricks]
        }

    def is_contour_valid(self, contour, image, pass_number):
        image_height, image_width = image.shape[:2]

        min_area = 100 if pass_number == 1 else 50

        area = cv2.contourArea(contour)
        return area >= min_area and area <= 100*2 * 8

    def get_contour_quality(self, contour, circle_radius):

        # Calculate difference between circle radius and contour area - this is the "quality" of the detection
        circle_area = circle_radius * circle_radius * math.pi
        contour_area = cv2.contourArea(contour, False)

        return min(circle_area, contour_area) / max(circle_area, contour_area)

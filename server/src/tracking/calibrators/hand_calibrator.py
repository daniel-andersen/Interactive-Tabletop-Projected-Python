import cv2
import numpy as np

from tracking.calibrators.calibrator import Calibrator, State


class HandCalibrator(Calibrator):
    """
    Class capable of calibrating hand detection.
    """
    def __init__(self):
        super().__init__()

        self.center_extract_pct = [0.7, 0.8]
        self.thresholds = [
            [{"lower": (0, 10, 60), "upper": (20, 150, 255)}],
            #[{"lower": (0, 48, 80), "upper": (20, 150, 255)}],
            #[{"lower": (0, 55, 90), "upper": (28, 175, 230)}],
        ]

    def get_medians(self):
        with self.lock:
            return self.detect_history[-1]["result"] if self.get_state() == State.DETECTED else None

    def detect(self, image, debug=False):

        # Prepare image
        image = self.prepare_image(image)

        image_height, image_width = image.shape[:2]

        # Try different thresholds one after one
        for hand_thresholds in self.thresholds:

            # Threshold image
            threshold_image = self.threshold_image(image, hand_thresholds)

            # Find contours
            contours, hierarchy = cv2.findContours(threshold_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
            if len(contours) == 0:
                continue

            # Find hands in contours
            hands = []
            for contour in contours:
                if self.are_hand_conditions_satisfied_for_contour(contour, threshold_image):
                    hands.append(contour)

            #cv2.imshow("debug_board %s" % hand_thresholds, threshold_image)

        #cv2.waitKey(0)

        return None

    def threshold_image(self, image, hand_thresholds):

        image_height, image_width = image.shape[:2]

        # Merge colorspaces into one mask
        mask_image = np.zeros((image_height, image_width, 1), np.uint8)

        for threshold_dict in hand_thresholds:
            lower_bounds = threshold_dict["lower"]
            upper_bounds = threshold_dict["upper"]

            threshold_image = cv2.inRange(image, lower_bounds, upper_bounds)
            dilate_image = cv2.dilate(threshold_image, (3, 3))
            erode_image = cv2.erode(dilate_image, (3, 3))

            mask_image = cv2.bitwise_or(mask_image, erode_image)

        return mask_image

    def prepare_image(self, image):

        # Extract center area
        image_height, image_width = image.shape[:2]

        image = cv2.resize(image, (320, int(320.0 * image_height / image_width)))
        image_height, image_width = image.shape[:2]

        # Extract area image
        x1 = int(float(image_width) * ((1.0 - self.center_extract_pct[0]) / 2.0))
        y1 = int(float(image_height) * ((1.0 - self.center_extract_pct[1]) / 2.0))
        x2 = int(float(image_width) * ((1.0 + self.center_extract_pct[0]) / 2.0))
        y2 = int(float(image_height) * ((1.0 + self.center_extract_pct[1]) / 2.0))

        center_extract_image = image[y1:y2, x1:x2]

        # Blur image
        blur_image = cv2.GaussianBlur(center_extract_image, (5, 5), 0)

        # Extract HSV image
        hsv_image = cv2.cvtColor(blur_image, cv2.COLOR_BGR2HSV)

        return hsv_image

    def are_hand_conditions_satisfied_for_contour(self, contour, image):

        image_height, image_width = image.shape[:2]

        # Simplify contour
        approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.02, True)

        # Check area
        area = cv2.contourArea(approxed_contour, False)

        min_hand_area = (image_width * 0.2) * (image_height * 0.2)
        max_hand_area = (image_width * 0.5) * (image_height * 0.5)

        if area < min_hand_area:
            #print("Area too small: %f vs %f" % (area, min_marker_size))
            return False

        if area > max_hand_area:
            #print("Area too big: %f vs %f" % (area, max_marker_size))
            return False

        # Convex hulled contour must be approximately twice as big
        convex_hull_contour = cv2.convexHull(approxed_contour, returnPoints=False)
        if len(convex_hull_contour) == 0:
            print("No convex hulls")
            return False

        # Get convexity defects
        convexity_defects = cv2.convexityDefects(approxed_contour, convex_hull_contour)

        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        #cv2.drawContours(image, [approxed_contour], -1, (255, 0, 255), 2)
        for i in range(convexity_defects.shape[0]):
            s, e, f, d = convexity_defects[i, 0]
            start = tuple(approxed_contour[s][0])
            end = tuple(approxed_contour[e][0])
            far = tuple(approxed_contour[f][0])
            cv2.line(image, start, end, [0, 255, 0], 2)
            cv2.circle(image, far, 5, [0, 0, 255], -1)

        cv2.destroyAllWindows()
        cv2.imshow("Contour", image)
        cv2.waitKey(0)

        return True

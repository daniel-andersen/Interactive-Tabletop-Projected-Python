import cv2
import numpy as np

from tracking.calibrators.calibrator import Calibrator, State
from tracking.util import misc_math


class HandCalibrator(Calibrator):
    """
    Class capable of calibrating hand detection.
    """
    def __init__(self):
        super().__init__()

        self.detect_min_stable_time = 1.0

        self.center_extract_pct = [0.7, 0.8]
        self.thresholds = [
            [{"lower": (0, 10, 60), "upper": (20, 255, 255)}],
            #[{"lower": (0, 10, 60), "upper": (20, 180, 255)}],
            #[{"lower": (0, 48, 80), "upper": (20, 150, 255)}],
        ]

    def get_medians(self):
        with self.lock:
            return self.detect_history[-1]["result"] if self.get_state() == State.DETECTED else None

    def detect(self, image, debug=False):

        cv2.imwrite("debug_hand_calibration.png", image)

        #image = cv2.imread("debug.png")
        #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #_, threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        #cv2.imshow("test", threshold_image)
        #cv2.waitKey(0)

        # Prepare image
        image = self.prepare_image(image)

        # Try different thresholds one after one
        for hand_thresholds in self.thresholds:

            # Threshold image
            threshold_image = self.threshold_image(image, hand_thresholds)

            # Debug
            if False:
                cv2.imshow("Image", threshold_image)
                cv2.waitKey(0)

            # Find contours
            contours, hierarchy = cv2.findContours(threshold_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
            if len(contours) == 0:
                continue

            # Find hands in contours
            for i in range(0, len(contours)):
                if self.are_hand_conditions_satisfied_for_contour(i, contours, hierarchy, threshold_image):
                    return True

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
        blur_image = cv2.GaussianBlur(center_extract_image, (7, 7), 0)

        # Extract HSV image
        hsv_image = cv2.cvtColor(blur_image, cv2.COLOR_BGR2HSV)

        return hsv_image

    def are_hand_conditions_satisfied_for_contour(self, index, contours, hierarchy, image):

        # Check hierarchy
        if hierarchy[0][index][3] != -1:
            #print("Contour cannot have a parent!")
            return False

        # Extract contour
        contour = contours[index]

        # Simplify contour
        approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.01, True)

        # Prepare constants
        image_height, image_width = image.shape[:2]

        calibration_center_point = [image_width / 2.0, image_height / 2.0]
        calibration_center_max_distance = min(image_width, image_height) * 0.1
        calibration_convexity_defect_max_length = min(image_width, image_height) * 0.7

        # Check area
        area = cv2.contourArea(approxed_contour, False)

        min_hand_area = (image_width * 0.2) * (image_height * 0.2)
        max_hand_area = (image_width * 0.75) * (image_height * 0.75)

        if area < min_hand_area:
            #print("Area too small: %f vs %f" % (area, min_hand_area))
            return False

        if area > max_hand_area:
        #    #print("Area too big: %f vs %f" % (area, max_hand_area))
            return False

        # Check convexity defects
        convex_hull_contour = cv2.convexHull(approxed_contour, returnPoints=False)
        if convex_hull_contour is None or len(convex_hull_contour) == 0:
            return False

        convexity_defects = cv2.convexityDefects(approxed_contour, convex_hull_contour)
        if convexity_defects is None or len(convexity_defects) == 0:
            return False

        # Find finger by averating convexity defects nearby center
        finger_positions = []

        for i in range(0, len(convexity_defects)):
            s, e, f, d = convexity_defects[i, 0]
            start = tuple(approxed_contour[s][0])
            end = tuple(approxed_contour[e][0])

            # Check convexity defect length
            if misc_math.line_length(start, end) > calibration_convexity_defect_max_length:
                #print("Convexity defect length too large: %s vs %s" % (misc_math.line_length(start, end), calibration_convexity_defect_max_length))
                continue

            # Check convexity defect start/end distance from calibration center
            dist_start = misc_math.distance(calibration_center_point, start)
            dist_end = misc_math.distance(calibration_center_point, end)

            if min(dist_start, dist_end) > calibration_center_max_distance:
                #print("Convexity defect distance to center too large: %s vs %s" % (min(dist_start, dist_end), calibration_center_max_distance))
                continue

            # Finger detected
            finger_positions.append(start if dist_start < dist_end else end)

        # Finger detected
        if len(finger_positions) > 0:
            finger_position = (int(sum([p[0] for p in finger_positions]) / float(len(finger_positions))),
                               int(sum([p[1] for p in finger_positions]) / float(len(finger_positions))))

            # Debug
            if False:
                debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                for i in range(convexity_defects.shape[0]):
                    s, e, f, d = convexity_defects[i, 0]
                    start = tuple(approxed_contour[s][0])
                    end = tuple(approxed_contour[e][0])
                    far = tuple(approxed_contour[f][0])
                    cv2.line(debug_image, start, end, [0, 255, 0], 2)
                    cv2.circle(debug_image, far, 2, [0, 0, 255], -1)
                cv2.circle(debug_image, finger_position, 5, [255, 0, 255], -1)

                cv2.imshow("Convexity hulls", debug_image)
                cv2.waitKey(0)

            return True

        return False

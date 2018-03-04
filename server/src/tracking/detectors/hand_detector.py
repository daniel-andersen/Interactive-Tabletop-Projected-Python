import cv2
import numpy as np

from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector
from tracking.util import misc_math
from util import enum


HandGesture = enum.Enum('UNKNOWN', 'POINTING', 'OPEN_HAND')

handDetectorId = "handDetector"


class HandDetector(Detector):
    """
    Class implementing hand detector.
    """
    def __init__(self, detector_id, thresholds=[{"lower": (0, 10, 60), "upper": (20, 255, 255)}]):
        """
        :param detector_id: Detector ID
        :param thresholds: List of thresholds to apply of type {lower: (h, s, v), upper: (h, s, v)}
        """
        super().__init__(detector_id)

        self.thresholds = thresholds

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
        :return: List of detected hands each containing {gesture, boundingRect: {x1, y1, x2, y2}}
        """

        # Prepare image
        #cv2.imwrite("debug/hand_detector.png", image)

        image = self.prepare_image(image)

        #cv2.imshow("Thresholded", image)
        #cv2.waitKey(0)

        # Find contours
        contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        if len(contours) == 0:
            return None

        # Find gestures
        hands = []
        for i in range(0, len(contours)):

            # Find finger positions
            finger_positions = self.finger_positions_from_contour(i, contours, hierarchy, image)
            if finger_positions is not None:

                # Find gesture
                gesture = self.gesture_from_finger_positions(finger_positions)

                # Find palm center
                palm_center = self.palm_center(contours[i], image)

                # Add hand
                hands.append({"fingerPositions": finger_positions,
                              "gesture": gesture,
                              "palmCenter": palm_center})

        if len(hands) == 0:
            return None

        return {"detectorId": self.detector_id,
                "hands": hands}

    def prepare_image(self, image):
        image_height, image_width = image.shape[:2]

        # Blur image
        image = cv2.GaussianBlur(image, (7, 7), 0)

        # Extract HSV image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Merge colorspaces into one mask
        mask_image = np.zeros((image_height, image_width, 1), np.uint8)

        for threshold_dict in self.thresholds:
            lower_bounds = threshold_dict["lower"]
            upper_bounds = threshold_dict["upper"]

            threshold_image = cv2.inRange(image, lower_bounds, upper_bounds)
            dilate_image = cv2.dilate(threshold_image, (3, 3))
            erode_image = cv2.erode(dilate_image, (3, 3))

            mask_image = cv2.bitwise_or(mask_image, erode_image)

        return mask_image

    def finger_positions_from_contour(self, index, contours, hierarchy, image):

        # Check hierarchy
        if hierarchy[0][index][3] != -1:
            #print("Contour cannot have a parent!")
            return None

        # Extract contour
        contour = contours[index]

        # Simplify contour
        approxed_contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.01, True)

        # Prepare constants
        image_height, image_width = image.shape[:2]

        calibration_convexity_defect_min_length = min(image_width, image_height) * 0.05
        calibration_convexity_defect_max_length = min(image_width, image_height) * 0.7
        calibration_convexity_defect_min_angle = 0.0
        calibration_convexity_defect_min_dist_to_other_finger = min(image_width, image_height) * 0.1

        # Check area
        area = cv2.contourArea(approxed_contour, False)

        min_hand_area = (image_width * 0.2) * (image_height * 0.2)
        max_hand_area = (image_width * 0.75) * (image_height * 0.75)

        if area < min_hand_area:
            #print("Area too small: %f vs %f" % (area, min_hand_area))
            return None

        if area > max_hand_area:
            #print("Area too big: %f vs %f" % (area, max_hand_area))
            return None

        # Check convexity defects
        convex_hull_contour = cv2.convexHull(approxed_contour, returnPoints=False)
        if convex_hull_contour is None or len(convex_hull_contour) == 0:
            return None

        convexity_defects = cv2.convexityDefects(approxed_contour, convex_hull_contour)
        if convexity_defects is None or len(convexity_defects) == 0:
            return None

        # Find finger by averating convexity defects nearby center
        finger_positions = []

        # Debug
        if False:
            debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            for i in range(convexity_defects.shape[0]):
                s, e, f, d = convexity_defects[i, 0]
                start = tuple(approxed_contour[s][0])
                end = tuple(approxed_contour[e][0])
                far = tuple(approxed_contour[f][0])
                cv2.line(debug_image, start, end, [255, 0, 255], 2)
                cv2.circle(debug_image, far, 2, [0, 0, 255], -1)

            cv2.imshow("Convexity hulls", debug_image)
            cv2.waitKey(0)

        for i in range(0, len(convexity_defects)):
            s, e, f, d = convexity_defects[i, 0]
            start = tuple(approxed_contour[s][0])
            end = tuple(approxed_contour[e][0])
            far = tuple(approxed_contour[f][0])

            # Check convexity defect length
            if misc_math.line_length(start, end) < calibration_convexity_defect_min_length:
                #print("Convexity defect length too small: %s vs %s" % (misc_math.line_length(start, end), calibration_convexity_defect_min_length))
                continue

            if misc_math.line_length(start, end) > calibration_convexity_defect_max_length:
                #print("Convexity defect length too large: %s vs %s" % (misc_math.line_length(start, end), calibration_convexity_defect_max_length))
                continue

            # Check angle of defect
            if False:
                debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                cv2.line(debug_image, start, end, [255, 0, 255], 2)
                cv2.circle(debug_image, far, 2, [0, 0, 255], -1)
                cv2.imshow("Convexity hull", debug_image)
                cv2.waitKey(0)

            if misc_math.angle(start, far, end) < calibration_convexity_defect_min_angle:
                #print("Convexity defect angle too small: %s vs %s" % (misc_math.angle(start, far, end), calibration_convexity_defect_min_angle))
                continue

            # Add start of convexity defect
            if len(finger_positions) > 0:
                dist_to_prev_finger = misc_math.distance(finger_positions[-1], start)
                if dist_to_prev_finger < calibration_convexity_defect_min_dist_to_other_finger:
                    finger_positions[-1] = (int((finger_positions[-1][0] + start[0]) / 2), int((finger_positions[-1][1] + start[1]) / 2))  # Average finger position
                else:
                    finger_positions.append(start)
            else:
                finger_positions.append(start)

            # Add end of convexity defect
            if len(finger_positions) > 0:
                dist_to_first_finger = misc_math.distance(finger_positions[0], end)
                if dist_to_first_finger < calibration_convexity_defect_min_dist_to_other_finger:
                    finger_positions[0] = (int((finger_positions[0][0] + end[0]) / 2), int((finger_positions[0][1] + end[1]) / 2))  # Average finger position
                else:
                    finger_positions.append(end)
            else:
                finger_positions.append(end)

        # Check if any fingers detected
        if len(finger_positions) == 0:
            return None

        if False:
            debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            for finger_pos in finger_positions:
                cv2.circle(debug_image, finger_pos, 2, [0, 0, 255], -1)
            cv2.imshow("Fingers", debug_image)
            cv2.waitKey(0)

        # Generate output
        finger_positions = [{"x": float(x) / float(image_width),
                             "y": float(y) / float(image_height)} for x, y in finger_positions]

        return finger_positions

    def gesture_from_finger_positions(self, finger_positions):
        if len(finger_positions) >= 5:
            return HandGesture.OPEN_HAND

        if len(finger_positions) == 1:
            return HandGesture.POINTING

        return HandGesture.UNKNOWN

    def palm_center(self, contour, image):
        image_height, image_width = image.shape[:2]

        M = cv2.moments(contour)

        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])

        return {"x": float(x) / float(image_width),
                "y": float(y) / float(image_height)}

from random import randint

import cv2
import numpy as np

from test.base_test import BaseTest
from tracking.board.board_descriptor import BoardDescriptor
from tracking.board.tiled_board_area import TiledBoardArea
from tracking.calibrators.board_calibrator import BoardCalibrator, State
from tracking.detectors.tiled_brick_detector import TiledBrickDetector


class ColoredBrickDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        classes = {
            "green": {"ranges": [{"hue": [45, 93],
                                  "saturation": [150, 255],
                                  "value": [0, 255]}]}
        }
        tests = [  # [Filename prefix, [x, y], [width, height]]
            {"image": "test/resources/colored_brick_detection/test_1", "position": [0.0, 0.0], "size": [0.1, 0.1], "class": "green"},
            {"image": "test/resources/colored_brick_detection/test_2", "position": [0.0, 0.0], "size": [0.1, 0.1], "class": "green"},
            {"image": "test/resources/colored_brick_detection/test_3", "position": [0.0, 0.0], "size": [0.1, 0.1], "class": "green"},
            {"image": "test/resources/colored_brick_detection/test_4", "position": [0.0, 0.0], "size": [0.1, 0.1], "class": "green"},
            {"image": "test/resources/colored_brick_detection/test_5", "position": [0.0, 0.0], "size": [0.1, 0.1], "class": "green"},
            {"image": "test/resources/colored_brick_detection/test_6", "position": [0.0, 0.0], "size": [0.1, 0.1], "class": "green"},
        ]

        # Run tests
        success_count = 0
        failed_count = 0
        i = 0

        for test_dict in tests:
            self.print_number(current=i + 1, total=len(tests))

            class_name = test_dict["class"]
            class_dict = classes[class_name]

            test_filename = "%s.png" % test_dict["image"]
            image = cv2.imread(test_filename)

            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            height, width = image.shape[:2]

            mask = np.zeros((height, width, 1), np.uint8)

            for a_range in class_dict["ranges"]:
                range_lower = np.array([a_range["hue"][0], a_range["saturation"][0], a_range["value"][0]])
                range_upper = np.array([a_range["hue"][1], a_range["saturation"][1], a_range["value"][1]])

                range_mask = cv2.inRange(hsv_image, range_lower, range_upper)
                mask = cv2.bitwise_or(mask, range_mask)

            cv2.imshow("HSV", mask)
            cv2.waitKey(0)

            i += 1

        return success_count, failed_count

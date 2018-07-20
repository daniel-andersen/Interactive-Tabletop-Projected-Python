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
            "Red": {
                "color": (0, 0, 255),
                "ranges": [
                    [
                        {
                            "hue": [0, 10],
                            "saturation": [150, 255],
                            "value": [0, 255]
                        }, {
                            "hue": [170, 180],
                            "saturation": [150, 255],
                            "value": [0, 255]
                        }
                    ]
                ]
            },
            "Blue": {
                "color": (255, 0, 0),
                "ranges": [
                    [
                        {
                            "hue": [100, 130],
                            "saturation": [50, 255],
                            "value": [75, 150]
                        }
                    ],
                    [
                        {
                            "hue": [100, 130],
                            "saturation": [100, 255],
                            "value": [75, 150]
                        }
                    ],
                    [
                        {
                            "hue": [100, 130],
                            "saturation": [200, 255],
                            "value": [150, 255]
                        }
                    ]
                ]
            },
            "Green": {
                "color": (0, 255, 0),
                "ranges": [
                    [
                        {
                            "hue": [50, 100],
                            "saturation": [50, 255],
                            "value": [0, 220]
                        }
                    ]
                ]
            },
            "Yellow": {
                "color": (0, 255, 255),
                "ranges": [
                    [
                        {
                            "hue": [12, 30],
                            "saturation": [100, 255],
                            "value": [150, 220]
                        }
                    ],
                    [
                        {
                            "hue": [12, 30],
                            "saturation": [120, 255],
                            "value": [150, 255]
                        }
                    ]
                ]
            },
            "Black": {
                "color": (0, 0, 0),
                "ranges": [
                    [
                        {
                            "hue": [0, 180],
                            "saturation": [0, 255],
                            "value": [0, 80]
                        }
                    ]
                ]
            }
        }
        tests = [
            {
                "image": "test/resources/colored_brick_detection/test_1.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Blue"},
                    {"position": [0.0, 0.0], "class": "Yellow"},
                    {"position": [0.0, 0.0], "class": "Black"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_2.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Black"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_3.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Yellow"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_4.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Yellow"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_5.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Blue"},
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Black"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_6.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Red"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_7.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Yellow"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_8.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Blue"},
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Yellow"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_9.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Black"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_10.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Yellow"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_11.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Yellow"},
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Black"},
                ]
            },
            {
                "image": "test/resources/colored_brick_detection/test_12.jpg",
                "bricks": [
                    {"position": [0.0, 0.0], "class": "Yellow"},
                    {"position": [0.0, 0.0], "class": "Red"},
                    {"position": [0.0, 0.0], "class": "Green"},
                    {"position": [0.0, 0.0], "class": "Black"},
                    {"position": [0.0, 0.0], "class": "Blue"},
                ]
            },
        ]

        # Run tests
        success_count = 0
        failed_count = 0
        i = 0

        for test_dict in tests:
            self.print_number(current=i + 1, total=len(tests))

            found_bricks = []

            image = cv2.imread(test_dict["image"])
            image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

            output_image = image.copy()

            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            image_height, image_width = image.shape[:2]

            for class_name, class_dict in classes.items():
                class_color = class_dict["color"]

                #if class_name != "Blue":
                #    continue

                for ranges in class_dict["ranges"]:

                    mask = np.zeros((image_height, image_width, 1), np.uint8)

                    for a_range in ranges:
                        range_lower = np.array([a_range["hue"][0], a_range["saturation"][0], a_range["value"][0]])
                        range_upper = np.array([a_range["hue"][1], a_range["saturation"][1], a_range["value"][1]])

                        range_mask = cv2.inRange(hsv_image, range_lower, range_upper)
                        mask = cv2.bitwise_or(mask, range_mask)

                    mask = cv2.bilateralFilter(mask.copy(), 11, 17, 17)

                    #cv2.imshow("Mask", mask)

                    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:2]

                    if len(contours) == 0:
                        continue
                    if len(contours) > 0 and not self.are_contour_properties_satisfied(contours[0], image_width, image_height):
                        continue
                    if len(contours) > 1:
                        if self.are_contour_properties_satisfied(contours[1], image_width, image_height):
                            continue
                        area1 = cv2.contourArea(contours[0])
                        area2 = cv2.contourArea(contours[1])
                        if area2 > area1 / 2:
                            continue

                    x, y, w, h = cv2.boundingRect(contours[0])
                    cv2.rectangle(output_image, (x - 2, y - 2), (x + w + 2, y + h + 2), class_color, 2)

                    found_bricks.append(class_name)

                    break

            for brick_dict in test_dict["bricks"]:
                if brick_dict["class"] not in found_bricks:
                    print("%s missing!" % brick_dict["class"])

            for found_brick in found_bricks:
                found = False
                for brick_dict in test_dict["bricks"]:
                    if found_brick == brick_dict["class"]:
                        found = True
                if not found:
                    print("%s wrongly found!" % found_brick)

            cv2.imshow("Output", output_image)
            cv2.waitKey(0)

            i += 1

        return success_count, failed_count

    def are_contour_properties_satisfied(self, contour, image_width, image_height):
        area = cv2.contourArea(contour)
        return area >= (image_width * 0.015) * (image_height * 0.015) and area <= (image_width * 0.05) * (image_height * 0.05)

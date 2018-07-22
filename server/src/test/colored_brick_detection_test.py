from random import randint

import cv2
import numpy as np
import json

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
                    ],
                    [
                        {
                            "hue": [0, 10],
                            "saturation": [200, 255],
                            "value": [75, 255]
                        }, {
                            "hue": [170, 180],
                            "saturation": [200, 255],
                            "value": [75, 255]
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
                            "saturation": [50, 255],
                            "value": [75, 250]
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
                    ],
                    [
                        {
                            "hue": [50, 100],
                            "saturation": [50, 255],
                            "value": [50, 220]
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
                    ],
                    [
                        {
                            "hue": [12, 30],
                            "saturation": [200, 255],
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

        with open('test/resources/colored_brick_detection/tests.json') as f:
            tests = json.load(f)

        # Run tests
        success_count = 0
        failed_count = 0
        i = 0

        for test_dict in tests:
            self.print_number(current=i + 1, total=len(tests))

            found_bricks = []

            image = cv2.imread(test_dict["image"])

            image = cv2.resize(image, (320, int(320 * image.shape[:2][0] / image.shape[:2][1])))
            image = cv2.normalize(image, image, 0, 255, cv2.NORM_MINMAX)

            if debug:
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

                    mask = cv2.erode(mask, (5, 5), iterations=1)
                    mask = cv2.dilate(mask, (5, 5), iterations=1)
                    #mask = cv2.bilateralFilter(mask.copy(), 11, 17, 17)

                    if debug:
                        cv2.imshow("Mask", mask)

                    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours = sorted(contours, key=cv2.contourArea, reverse=True)

                    if class_name != "Black" and not self.is_mask_valid(contours, image_width, image_height):
                        continue

                    first_valid_contour_index = self.get_first_valid_contour_index(contours, hierarchy, image_width, image_height)
                    if first_valid_contour_index >= len(contours):
                        continue

                    if not self.are_contour_properties_satisfied(contours, hierarchy, first_valid_contour_index, image_width, image_height):
                        continue

                    if first_valid_contour_index + 1 < len(contours):
                        if self.are_contour_properties_satisfied(contours, hierarchy, first_valid_contour_index + 1, image_width, image_height):
                            continue

                        area1 = cv2.contourArea(contours[first_valid_contour_index])
                        area2 = cv2.contourArea(contours[first_valid_contour_index + 1])
                        if area2 > area1 / 2:
                            continue

                    if debug:
                        x, y, w, h = cv2.boundingRect(contours[first_valid_contour_index])
                        cv2.rectangle(output_image, (x - 2, y - 2), (x + w + 2, y + h + 2), class_color, 2)

                    found_bricks.append(class_name)

                    break

            success = True

            for brick_dict in test_dict["bricks"]:
                if brick_dict["class"] not in found_bricks:
                    success = False
                    if debug:
                        print("%s missing!" % brick_dict["class"])

            for found_brick in found_bricks:
                found = False
                for brick_dict in test_dict["bricks"]:
                    if found_brick == brick_dict["class"]:
                        found = True
                if not found:
                    success = False
                    if debug:
                        print("%s wrongly found!" % found_brick)

            if success:
                success_count += 1
            else:
                failed_count += 1

            if debug and not success:
                cv2.imshow("Output", output_image)
                cv2.waitKey(0)

            i += 1

        return success_count, failed_count

    def is_mask_valid(self, contours, image_width, image_height):
        if len(contours) == 0:
            return False

        area = cv2.contourArea(contours[0])
        if area > self.contour_max_area(image_width, image_height):
            return False

        return True

    def get_first_valid_contour_index(self, contours, hierarchy, image_width, image_height):

        # Skip to first valid contour, if any
        index = 0
        while index < len(contours):
            if cv2.contourArea(contours[index]) < self.contour_min_area(image_width, image_height):
                break
            if self.are_contour_properties_satisfied(contours, hierarchy, index, image_width, image_height):
                break

            index += 1

        return index

    def are_contour_properties_satisfied(self, contours, hierarchy, contour_index, image_width, image_height):

        contour = contours[contour_index]

        # Can not have no parent
        if hierarchy[0][contour_index][3] != -1:
            return False

        # Check area
        area = cv2.contourArea(contour)
        if area < self.contour_min_area(image_width, image_height) or area > self.contour_max_area(image_width, image_height):
            return False

        # Check bounding box size
        x, y, w, h = cv2.boundingRect(contour)
        if w > self.contour_max_width(image_width) or h > self.contour_max_height(image_height):
            return False

        # Check area compared to contour bounding box
        if area < (w * 0.5) * (h * 0.5):
            return False

        return True

    def contour_min_area(self, image_width, image_height):
        return self.contour_min_width(image_width) * self.contour_min_height(image_height)

    def contour_max_area(self, image_width, image_height):
        return self.contour_max_width(image_width) * self.contour_max_height(image_height)

    def contour_min_width(self, image_width):
        return image_width * 0.015

    def contour_min_height(self, image_height):
        return image_height * 0.015

    def contour_max_width(self, image_width):
        return image_width * 0.075

    def contour_max_height(self, image_height):
        return image_height * 0.075

import cv2
import json
import os

from test.base_test import BaseTest
from tracking.detectors.colored_brick_detector import ColoredBrickDetector


class ColoredBrickDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):

        # Load tests from JSON
        with open('test/resources/colored_brick_detection/tests.json') as f:
            tests = json.load(f)

        # Run tests
        success_count = 0
        failed_count = 0
        i = 0

        tests = [{
            "image": "/Users/daniel/Desktop/training/images/train/" + f,
            "bricks": []
        } for f in os.listdir('/Users/daniel/Desktop/training/images/train/') if f.endswith(".jpg")]

        for test_dict in tests:
            #if test_dict["image"] != "/Users/daniel/Desktop/training/images/train/image_20180614_1616_38.jpg":
            #    continue

            print(test_dict["image"])
            self.print_number(current=i + 1, total=len(tests))

            # Load test image
            image = cv2.imread(test_dict["image"])

            # Detect bricks
            colored_brick_detector = ColoredBrickDetector(detector_id=0)

            result = colored_brick_detector.detect_in_image(image, debug)
            found_bricks = result["bricks"]

            # Check if success
            success = True

            for brick_dict in test_dict["bricks"]:
                found = False
                for found_brick in found_bricks:
                    if found_brick["class"] == brick_dict["class"]:
                        found = True
                if not found:
                    success = False
                    if debug:
                        print("%s missing!" % brick_dict["class"])

            for found_brick in found_bricks:
                found = False
                for brick_dict in test_dict["bricks"]:
                    if found_brick["class"] == brick_dict["class"]:
                        found = True
                if not found:
                    success = False
                    if debug:
                        print("%s wrongly found!" % found_brick["class"])

            if not success and debug:
                class_color = {"Red": (0, 0, 255), "Blue": (255, 0, 0), "Yellow": (0, 255, 255), "Green": (0, 255, 0), "Black": (0, 0, 0)}
                for brick in found_bricks:
                    image_height, image_width = image.shape[:2]
                    cv2.circle(image, (int(brick["x"] * image_width), int(brick["y"] * image_height)), int(brick["radius"] * image_width), class_color[brick["class"]], 2)
                cv2.imshow("Image", image)
                cv2.waitKey(0)

            if success:
                success_count += 1
            else:
                failed_count += 1

            i += 1

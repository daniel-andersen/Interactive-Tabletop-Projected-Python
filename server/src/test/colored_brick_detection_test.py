import cv2
import json

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

        for test_dict in tests:
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
                for brick in found_bricks:
                    image_height, image_width = image.shape[:2]
                    cv2.circle(image, (int(brick["x"] * image_width), int(brick["y"] * image_height)), int(brick["radius"] * image_width), (255, 0, 255), 2)
                cv2.imshow("Image", image)
                cv2.waitKey(0)

            if success:
                success_count += 1
            else:
                failed_count += 1

            i += 1

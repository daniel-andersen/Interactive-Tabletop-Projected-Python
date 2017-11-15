import cv2

from test.base_test import BaseTest
from tracking.detectors.nonobstructed_area_detector import NonobstructedAreaDetector


class NonobstructedAreaDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, [{}, ...]]
            ['test/resources/nonobstructed_area_detection/image_detection_1', []],
        ]

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, expected_matches) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            test_filename = "%s_test.png" % image_filename
            test_image = cv2.imread(test_filename)

            # Find nonobstructed area
            nonobstructed_area_detector = NonobstructedAreaDetector(0, [0.0, 0.0, 1.0, 1.0])

            rectangle = nonobstructed_area_detector.detect(test_image)
            if rectangle is None:
                failed_count += 1
                print('%s FAILED. Did not find nonobstructed area!' % image_filename)
                continue

            # Success
            success_count += 1

        return success_count, failed_count

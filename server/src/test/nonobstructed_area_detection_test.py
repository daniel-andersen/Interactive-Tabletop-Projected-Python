import cv2

from test.base_test import BaseTest
from tracking.detectors.nonobstructed_area_detector import NonobstructedAreaDetector
from tracking.util import misc_math


class NonobstructedAreaDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [
            ['test/resources/nonobstructed_area_detection/image_detection_1', [0.2, 0.2], [0.3, 0.5], {"shouldFindArea": True, "center": [0.3, 0.5]}],
            ['test/resources/nonobstructed_area_detection/image_detection_2', [0.2, 0.2], [0.5, 0.8], {"shouldFindArea": True, "center": [0.5, 0.8]}],
            ['test/resources/nonobstructed_area_detection/image_detection_3', [0.2, 0.2], [0.5, 0.0], {"shouldFindArea": True, "center": [0.5, 0.7]}],
        ]

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, target_size, target_point, expected_result) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            test_filename = "%s_test.png" % image_filename
            test_image = cv2.imread(test_filename)

            # Find nonobstructed area
            nonobstructed_area_detector = NonobstructedAreaDetector(0, target_size, target_point)

            result = nonobstructed_area_detector.detect(test_image)
            if result is None and expected_result["shouldFindArea"]:
                failed_count += 1
                print('%s FAILED. Did not find nonobstructed area!' % image_filename)
                continue

            # Verify result
            matches = result["matches"]
            if len(matches) != 1:
                failed_count += 1
                print('%s FAILED. Did not find single nonobstructed area, but found %s' % (image_filename, len(matches)))
                continue

            match = matches[0]
            if misc_math.distance(match["center"], expected_result["center"]) > 0.1:
                failed_count += 1
                print('%s FAILED. Found nonobstructed area at unexpected position: (%f, %f). Distance: %f' % (image_filename, match["center"][0], match["center"][1], misc_math.distance(match["center"], expected_result["center"])))
                continue


            # Success
            success_count += 1

        return success_count, failed_count

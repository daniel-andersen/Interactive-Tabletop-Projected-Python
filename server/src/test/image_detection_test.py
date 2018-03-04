import cv2

from test.base_test import BaseTest
from tracking.board import board_snapshot
from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.image_detector import ImageDetector


class ImageDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, [{expected x, expected y, expected width, expected height, expected angle}, ...]]
            ['test/resources/image_detection/image_detection_1', SnapshotSize.SMALL, [{"x": 0.4000, "y": 0.3650, "width": 0.1562, "height": 0.1675, "angle": 30.0}]],
            ['test/resources/image_detection/image_detection_2', SnapshotSize.LARGE, [{"x": 0.8039, "y": 0.7662, "width": 0.0742, "height": 0.1875, "angle": -73.0}]],
            ['test/resources/image_detection/image_detection_3', SnapshotSize.LARGE, [{"x": 0.3390, "y": 0.5400, "width": 0.0742, "height": 0.1875, "angle": 67.0}]],
        ]

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, input_resolution, expected_matches) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            source_filename = "%s_source.png" % image_filename
            source_image = cv2.imread(source_filename)

            test_filename = "%s_test.png" % image_filename
            test_image = cv2.imread(test_filename)

            # Find image
            image_detector = ImageDetector(0, source_image, input_resolution=input_resolution)

            test_image = self.resize_image_to_detector_default_size(test_image, image_detector)

            result = image_detector.detect(test_image)

            matches = result["matches"]
            matches_count = len(matches)

            # Verify result
            if matches_count != len(expected_matches):
                failed_count += 1
                print('%s FAILED. %i images out of %i not detected!' % (image_filename, len(expected_matches) - matches_count, len(expected_matches) - matches_count))
                continue

            for i in range(0, matches_count):
                actual_match = matches[i]
                expected_match = expected_matches[i]

                if abs(actual_match["x"] - expected_match["x"]) > 0.01 or abs(actual_match["y"] - expected_match["y"]) > 0.01:
                    failed_count += 1
                    print('%s FAILED. Incorrect position: (%s, %s). Should be (%s, %s).' % (image_filename, actual_match["x"], actual_match["y"], expected_match["x"], expected_match["y"]))
                    continue

                if abs(actual_match["width"] - expected_match["width"]) > 0.01 or abs(actual_match["height"] - expected_match["height"]) > 0.01:
                    failed_count += 1
                    print('%s FAILED. Incorrect size: (%s, %s). Should be (%s, %s).' % (image_filename, actual_match["width"], actual_match["height"], expected_match["width"], expected_match["height"]))
                    continue

                if abs(actual_match["angle"] - expected_match["angle"]) > 3.0:
                    failed_count += 1
                    print('%s FAILED. Incorrect angle: %s. Should be %s.' % (image_filename, actual_match["angle"], expected_match["angle"]))
                    continue

            # Success
            success_count += 1

        return success_count, failed_count

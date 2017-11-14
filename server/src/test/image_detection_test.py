import cv2

from test.base_test import BaseTest
from tracking.board.board_area import BoardArea
from tracking.board.board_descriptor import BoardDescriptor
from tracking.calibrators.board_calibrator import BoardCalibrator, State
from tracking.calibrators.hand_calibrator import HandCalibrator
from tracking.detectors.hand_detector import HandDetector
from tracking.detectors.image_detector import ImageDetector


class ImageDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, [{expected x, expected y, expected width, expected height, expected angle}, ...]]
            ['test/resources/image_detection/image_detection_1', [{"x": 0.4000, "y": 0.3650, "width": 0.1562, "height": 0.1675, "angle": 30.0}]],
            ['test/resources/image_detection/image_detection_2', [{"x": 0.8039, "y": 0.7662, "width": 0.0742, "height": 0.1875, "angle": -73.0}]],
            ['test/resources/image_detection/image_detection_3', [{"x": 0.3390, "y": 0.5400, "width": 0.0742, "height": 0.1875, "angle": 67.0}]],
        ]

        # Initial board detection
        board_calibrator = BoardCalibrator(board_image_filename='test/resources/hand_detection/board_detection_source.png')
        board_descriptor = BoardDescriptor()

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, expected_matches) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            board_filename = "%s_board.png" % image_filename
            board_image = cv2.imread(board_filename)

            source_filename = "%s_source.png" % image_filename
            source_image = cv2.imread(source_filename)

            test_filename = "%s_test.png" % image_filename
            test_image = cv2.imread(test_filename)

            # Create board area
            board_area = BoardArea(0, board_descriptor)

            # Detect board
            corners = board_calibrator.detect(board_image)
            if corners is None:
                failed_count += 1
                print('%s FAILED. Could not detect board' % image_filename)
                continue

            # Force update board descriptor to recognize board immediately
            board_descriptor.get_board_calibrator().update(board_image)
            board_descriptor.get_board_calibrator().state = State.DETECTED

            # Update board descriptor with test image
            board_descriptor.update(test_image)

            # Find image
            image_detector = ImageDetector(0, source_image)
            result = image_detector.detect(test_image, board_area)

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

                if abs(actual_match["angle"] - expected_match["angle"]) > 2.0:
                    failed_count += 1
                    print('%s FAILED. Incorrect angle: %s. Should be %s.' % (image_filename, actual_match["angle"], expected_match["angle"]))
                    continue

            # Success
            success_count += 1

        return success_count, failed_count

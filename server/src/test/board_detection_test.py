import sys
import cv2
from test.base_test import BaseTest
from tracking.board import detector


class BoardDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self):
        board_detector = detector.Detector(board_image_filename='test/resources/board_detection_source.png')

        test_images = [
            ['test/resources/board_detection_source.png', detector.State.DETECTED],
            ['test/resources/board_detection_black.png', detector.State.NOT_DETECTED],
            ['test/resources/board_detection_1.jpg', detector.State.DETECTED],
            ['test/resources/board_detection_2.jpg', detector.State.DETECTED],
            ['test/resources/board_detection_3.jpg', detector.State.DETECTED],
            ['test/resources/board_detection_4.jpg', detector.State.DETECTED]
        ]

        success_count = 0
        failed_count = 0

        for i, (image_filename, expected_state) in enumerate(test_images):
            self.print_number(current=i + 1, total=len(test_images))

            image = cv2.imread(image_filename)
            corners = board_detector.detect_corners(image, debug=True)
            detected_state = detector.State.DETECTED if corners is not None else detector.State.NOT_DETECTED

            if detected_state == expected_state:
                success_count += 1
            else:
                failed_count += 1
                print('%s FAILED. Should be %s but was %s!' % (image_filename, 'DETECTED' if expected_state == detector.State.DETECTED else 'NOT DETECTED', 'NOT DETECTED' if expected_state == detector.State.DETECTED else 'DETECTED'))

        return success_count, failed_count

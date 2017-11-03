import cv2

from test.base_test import BaseTest
from tracking.calibrators.board_calibrator import BoardCalibrator, State


class BoardDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        test_images = [
            ['test/resources/board_detection/board_detection_source.png', State.DETECTED],
            ['test/resources/board_detection/board_detection_black.png', State.NOT_DETECTED],
            ['test/resources/board_detection/board_detection_1.jpg', State.DETECTED],
            ['test/resources/board_detection/board_detection_2.jpg', State.DETECTED],
            ['test/resources/board_detection/board_detection_3.jpg', State.DETECTED],
            ['test/resources/board_detection/board_detection_4.jpg', State.DETECTED]
        ]

        board_calibrator = BoardCalibrator(board_image_filename='test/resources/board_detection/board_detection_source.png')

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, expected_state) in enumerate(test_images):
            self.print_number(current=i + 1, total=len(test_images))

            image = cv2.imread(image_filename)
            corners = board_calibrator.detect(image, debug=debug)
            detected_state = State.DETECTED if corners is not None else State.NOT_DETECTED

            if detected_state == expected_state:
                success_count += 1
            else:
                failed_count += 1
                print('%s FAILED. Should be %s but was %s!' % (image_filename, 'DETECTED' if expected_state == State.DETECTED else 'NOT DETECTED', 'NOT DETECTED' if expected_state == State.DETECTED else 'DETECTED'))

        return success_count, failed_count

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
            ['test/resources/board_detection_black.png', detector.State.NOT_DETECTED]
        ]

        success = 0
        failed = 0

        for image_filename, expected_state in test_images:
            image = cv2.imread(image_filename)

            state = board_detector.detect(image)

            if state == expected_state:
                success += 1
            else:
                failed += 1

        return success, failed

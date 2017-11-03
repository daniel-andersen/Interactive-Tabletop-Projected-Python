import cv2

from test.base_test import BaseTest
from tracking.board.board_area import BoardArea
from tracking.board.board_descriptor import BoardDescriptor
from tracking.calibrators.board_calibrator import BoardCalibrator, State
from tracking.detectors.hand_detector import HandDetector


class HandDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, [(expected x, expected y), ...]]
            ['test/resources/hand_detection/hand_detection_1', [(0.5, 0.5)]],
            ['test/resources/hand_detection/hand_detection_2', [(0.5, 0.5)]],
        ]

        # Initial board detection
        board_calibrator = BoardCalibrator(board_image_filename='test/resources/hand_detection/board_detection_source.png')
        board_descriptor = BoardDescriptor()

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, expected_positions) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            board_filename = "%s_board.png" % image_filename
            test_filename = "%s_test.png" % image_filename

            # Create board area
            board_area = BoardArea(0, board_descriptor)
            hand_detector = HandDetector(0, board_area)

            # Detect board
            board_image = cv2.imread(board_filename)
            corners = board_calibrator.detect(board_image)
            if corners is None:
                failed_count += 1
                print('%s FAILED. Could not detect board' % image_filename)
                continue

            # Force update board descriptor to recognize board immediately
            board_descriptor.get_board_calibrator().update(board_image)
            board_descriptor.get_board_calibrator().state = State.DETECTED

            # Update board descriptor with test image
            test_image = cv2.imread(test_filename)
            board_descriptor.update(test_image)

            # Detect hands
            detected_positions = hand_detector.detect_in_image(test_image)

            # Print result
            """
            if detected_count == len(expected_positions):
                success_count += 1
            else:
                failed_count += 1
                print('%s FAILED. %i bricks out of %i not detected!' % (image_filename, len(expected_positions) - detected_count, len(expected_positions) - detected_count))
            """

        return success_count, failed_count

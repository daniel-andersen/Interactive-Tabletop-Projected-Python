import cv2

from test.base_test import BaseTest
from tracking.board.board_area import BoardArea
from tracking.board.board_descriptor import BoardDescriptor
from tracking.calibrators.board_calibrator import BoardCalibrator, State
from tracking.calibrators.hand_calibrator import HandCalibrator
from tracking.detectors.hand_detector import HandDetector


class HandDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, board calibration successful, [{expected x, expected y}, ...]]
            ['test/resources/hand_detection/hand_detection_1', True, [{"gesture": "OPEN_PALM", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_2', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_3', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_4', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_5', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_6', False, []],
            ['test/resources/hand_detection/hand_detection_7', False, []],
        ]

        # Initial board detection
        board_calibrator = BoardCalibrator(board_image_filename='test/resources/hand_detection/board_detection_source.png')
        board_descriptor = BoardDescriptor()

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, board_calibration_success, expected_positions) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            board_filename = "%s_board.png" % image_filename
            board_image = cv2.imread(board_filename)

            calibrator_filename = "%s_calibration.png" % image_filename
            calibrator_image = cv2.imread(calibrator_filename)

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

            # Calibrate hand detector
            hand_detector_calibrator = HandCalibrator()
            medians = hand_detector_calibrator.detect(calibrator_image)

            if medians is None and not board_calibration_success:
                success_count += 1
                continue

            if medians is None and board_calibration_success:
                failed_count += 1
                print('%s FAILED. Could not calibrate hand' % image_filename)
                continue

            if medians is not None and not board_calibration_success:
                failed_count += 1
                print('%s FAILED. Hand calibration mistakely found hand!' % image_filename)
                continue

            # Update board descriptor with calibrator image
            #board_descriptor.update(calibrator_image)

            # Detect hands
            hand_detector = HandDetector(0, medians)
            #result = hand_detector.detect_in_image(test_image)

            # Success
            success_count += 1

        return success_count, failed_count

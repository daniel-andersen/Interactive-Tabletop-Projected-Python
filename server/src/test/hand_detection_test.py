import cv2

from test.base_test import BaseTest
from tracking.calibrators.hand_calibrator import HandCalibrator
from tracking.detectors.hand_detector import HandDetector


class HandDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, board calibration successful, [{expected x, expected y}, ...]]
            #['test/resources/hand_detection/hand_detection_1', True, [{"gesture": "OPEN_PALM", "x": 0.5, "y": 0.5}]],
            #['test/resources/hand_detection/hand_detection_2', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_3', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_4', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            ['test/resources/hand_detection/hand_detection_5', True, [{"gesture": "POINTING", "x": 0.5, "y": 0.5}]],
            #['test/resources/hand_detection/hand_detection_6', False, []],
            #['test/resources/hand_detection/hand_detection_7', False, []],
            #['test/resources/hand_detection/hand_detection_8', False, []],
            #['test/resources/hand_detection/hand_detection_9', False, []],
            #['test/resources/hand_detection/hand_detection_10', False, []],
        ]

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, board_calibration_success, expected_positions) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            calibrator_filename = "%s_calibration.png" % image_filename
            calibrator_image = cv2.imread(calibrator_filename)

            test_filename = "%s_test.png" % image_filename
            test_image = cv2.imread(test_filename)

            # Calibrate hand detector
            hand_calibrator = HandCalibrator()
            thresholds = hand_calibrator.detect(calibrator_image)

            if thresholds is None and not board_calibration_success:
                success_count += 1
                continue

            if thresholds is None and board_calibration_success:
                failed_count += 1
                print('%s FAILED. Could not calibrate hand' % image_filename)
                continue

            if thresholds is not None and not board_calibration_success:
                failed_count += 1
                print('%s FAILED. Hand calibration mistakely found hand!' % image_filename)
                continue

            # Update board descriptor with calibrator image
            #board_descriptor.update(calibrator_image)

            # Detect hands
            hand_detector = HandDetector(0, thresholds)
            test_image = self.resize_image_to_detector_default_size(test_image, hand_detector)
            result = hand_detector.detect_in_image(test_image)

            # Success
            success_count += 1

        return success_count, failed_count

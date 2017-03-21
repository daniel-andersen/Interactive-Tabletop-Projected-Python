import cv2
from test.base_test import BaseTest
from tracking.board.board_detector import BoardDetector, State
from tracking.board.board_snapshot import BoardSnapshot, SnapshotSize
from tracking.board.tiled_board_area import TiledBoardArea


class TiledBrickDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [
            ['test/resources/tiled_brick_detection/brick_detection_1', [(1, 1)]]
        ]

        # Initial board detection
        board_detector = BoardDetector(board_image_filename='test/resources/tiled_brick_detection/board_detection_source.png')
        tiled_board_area = TiledBoardArea(0, [32, 20])

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, expected_positions) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            board_filename = "%s_board.png" % image_filename
            test_filename = "%s_test.png" % image_filename

            # Detect board
            board_image = cv2.imread(board_filename)
            corners = board_detector.detect_corners(board_image)
            if corners is None:
                failed_count += 1
                print('%s FAILED. Could not detect board' % image_filename)
                continue

            # Create board snapshot
            test_image = cv2.imread(test_filename)
            board_snapshot = BoardSnapshot(board_image, corners)

            # Detect bricks
            detected_count = 0

            for x, y in expected_positions:
                detected_count += 1

            # Print result
            if detected_count == len(expected_positions):
                success_count += 1
            else:
                failed_count += 1
                print('%s FAILED. %i bricks out of %i not detected!' % (image_filename, detected_count, len(expected_positions) - detected_count))

        return success_count, failed_count

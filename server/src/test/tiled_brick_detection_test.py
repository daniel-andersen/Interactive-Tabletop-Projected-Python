import cv2
from random import randint
from test.base_test import BaseTest
from tracking.board.board_detector import BoardDetector
from tracking.board.board_descriptor import BoardDescriptor
from tracking.board.board_snapshot import BoardSnapshot
from tracking.board.tiled_board_area import TiledBoardArea
from tracking.detectors.tiled_brick_detector import TiledBrickDetector


class TiledBrickDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [
            ['test/resources/tiled_brick_detection/brick_detection_1', [32, 20], [(1, 1)]]
        ]

        # Initial board detection
        board_detector = BoardDetector(board_image_filename='test/resources/tiled_brick_detection/board_detection_source.png')
        tiled_brick_detector = TiledBrickDetector()
        board_descriptor = BoardDescriptor()

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, tile_count, expected_positions) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            board_filename = "%s_board.png" % image_filename
            test_filename = "%s_test.png" % image_filename

            # Create board area
            tiled_board_area = TiledBoardArea(0, tile_count, board_descriptor)

            # Detect board
            board_image = cv2.imread(board_filename)
            corners = board_detector.detect_corners(board_image)
            if corners is None:
                failed_count += 1
                print('%s FAILED. Could not detect board' % image_filename)
                continue

            # Create board snapshot
            test_image = cv2.imread(test_filename)
            board_snapshot = BoardSnapshot(test_image, corners)

            # Update board descriptor
            board_descriptor.set_board_snapshot(board_snapshot)

            # Detect bricks
            detected_count = 0

            for expected_position in expected_positions:

                # Find all positions with no expected bricks
                no_brick_positions = []
                for y in range(0, tile_count[1]):
                    for x in range(0, tile_count[0]):
                        position = (x, y)
                        if position not in expected_positions:
                            no_brick_positions.append(position)

                # Pick a random number of positions with no bricks
                positions = []
                for _ in range(5, 10):
                    random_index = randint(0, len(no_brick_positions))
                    positions.append(no_brick_positions[random_index])
                    no_brick_positions.pop(random_index)

                # Insert expected position
                expected_index = randint(0, len(positions))
                positions.insert(expected_index, expected_position)

                # Detect brick
                detected_position = tiled_brick_detector.find_brick_among_tiles(tiled_board_area, positions, debug)
                detected_position = detected_position[0] if detected_position is not None else None

                if detected_position == expected_position:
                    detected_count += 1
                else:
                    print('Brick supposed to be at %s but was found at %s!' % (expected_position, detected_position))

            # Print result
            if detected_count == len(expected_positions):
                success_count += 1
            else:
                failed_count += 1
                print('%s FAILED. %i bricks out of %i not detected!' % (image_filename, len(expected_positions) - detected_count, len(expected_positions) - detected_count))

        return success_count, failed_count

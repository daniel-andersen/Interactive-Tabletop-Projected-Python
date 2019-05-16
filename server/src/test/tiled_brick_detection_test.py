from random import randint

import cv2

from test.base_test import BaseTest
from tracking.board.board_descriptor import BoardDescriptor
from tracking.board.tiled_board_area import TiledBoardArea
from tracking.calibrators.board_calibrator import BoardCalibrator, State
from tracking.detectors.tiled_brick_detector import TiledBrickDetector
from tracking.detectors.tiled_brick_detector import BrickColor


class TiledBrickDetectionTest(BaseTest):
    def get_tests(self):
        return [
            self.detection_test
        ]

    def detection_test(self, debug=False):
        tests = [  # [Filename prefix, [tile count x, tile count y], [padding horizontal, padding vertical], [((expected x, expected y), brick color), ...]]
            #['test/resources/tiled_brick_detection/brick_detection_1', [32, 20], [0.1, 0.1], [((1, 1), BrickColor.BLACK), ((10, 7), BrickColor.BLACK), ((15, 5), BrickColor.BLACK), ((29, 17), BrickColor.BLACK)]],
            #['test/resources/tiled_brick_detection/brick_detection_2', [32, 20], [0.2, 0.2], [((1, 7), BrickColor.BLACK), ((14, 8), BrickColor.BLACK), ((20, 12), BrickColor.BLACK), ((24, 18), BrickColor.BLACK), ((30, 1), BrickColor.BLACK)]],
            #['test/resources/tiled_brick_detection/brick_detection_3', [32, 20], [0.1, 0.1], [((13, 12), BrickColor.RED), ((25, 15), BrickColor.YELLOW), ((26, 15), BrickColor.BLUE), ((27, 16), BrickColor.BLACK)]],
            #['test/resources/tiled_brick_detection/brick_detection_4', [32, 20], [0.1, 0.1], [((6, 0), BrickColor.GREEN), ((7, 4), BrickColor.BLUE), ((7, 13), BrickColor.RED), ((26, 19), BrickColor.YELLOW)]],
            ['test/resources/tiled_brick_detection/brick_detection_5', [32, 20], [0.1, 0.1], [((0, 13), BrickColor.GREEN), ((3, 10), BrickColor.BLACK), ((10, 4), BrickColor.YELLOW), ((11, 9), BrickColor.RED), ((22, 0), BrickColor.BLUE)]],
        ]

        # Initial board detection
        board_descriptor = BoardDescriptor()
        board_descriptor.set_board_calibrator(BoardCalibrator(board_image_filename="test/resources/tiled_brick_detection/board_detection_source.png"))
        board_descriptor.get_board_calibrator().detect_min_count = 1
        board_descriptor.get_board_calibrator().detect_min_stable_time = 0.0

        # Run tests
        success_count = 0
        failed_count = 0

        for i, (image_filename, tile_count, tile_padding, bricks) in enumerate(tests):
            self.print_number(current=i + 1, total=len(tests))

            board_filename = "%s_board.png" % image_filename
            test_filename = "%s_test.png" % image_filename

            # Create board area
            tiled_board_area = TiledBoardArea(0, tile_count, tile_padding, board_descriptor)

            # Create detector
            tiled_brick_detector = TiledBrickDetector(tiled_board_area)

            # Detect board
            board_image = cv2.imread(board_filename)
            corners = board_descriptor.get_board_calibrator().detect(board_image)
            if corners is None:
                failed_count += 1
                self.error(0, '%s FAILED. Could not detect board' % image_filename)
                continue

            # Force update board descriptor to recognize board immediately
            board_descriptor.get_board_calibrator().update(board_image)
            board_descriptor.get_board_calibrator().state = State.DETECTED

            # Update board descriptor with test image
            test_image = cv2.imread(test_filename)
            board_descriptor.update(test_image)

            # Detect bricks
            detected_count = 0

            expected_positions = [position for position, color in bricks]

            for j, brick in enumerate(bricks):
                expected_position = brick[0]
                brick_color = brick[1]

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
                    random_index = randint(0, len(no_brick_positions) - 1)
                    positions.append(no_brick_positions[random_index])
                    no_brick_positions.pop(random_index)

                # Insert expected position
                expected_index = randint(0, len(positions) - 1)
                positions.insert(expected_index, expected_position)

                error = False

                # Detect brick with specific color
                result = tiled_brick_detector.find_brick_among_tiles(positions, brick_color, debug)
                if result is not None:
                    detected_position, detected_color = result
                else:
                    detected_position, detected_color = None, None

                if detected_position != expected_position:
                    self.error(j, 'Brick with color %s supposed to be at %s but was found at %s!' % (BrickColor.names[brick_color], expected_position, detected_position))
                    error = True

                # Find brick color
                result = tiled_brick_detector.find_brick_among_tiles(positions, color=None, debug=debug)
                if result is not None:
                    detected_position, detected_color = result
                else:
                    detected_position, detected_color = None, None

                if detected_position != expected_position:
                    self.error(j, 'Brick with color %s supposed to be at %s but was found at %s!' % (BrickColor.names[brick_color], expected_position, detected_position))
                    error = True
                if detected_position == expected_position and detected_color != brick_color:
                    self.error(j, 'Found wrong color for brick at position %s. Expected %s but found %s!' % (expected_position, BrickColor.names[brick_color], BrickColor.names[detected_color]))
                    error = True

                # Check success
                if not error:
                    detected_count += 1

                if error and debug:
                    cv2.waitKey(0)

            # Print result
            if detected_count == len(expected_positions):
                success_count += 1
            else:
                failed_count += 1
                self.error(-1, '%s FAILED. %i bricks out of %i not detected!' % (image_filename, len(expected_positions) - detected_count, len(expected_positions)))

        return success_count, failed_count

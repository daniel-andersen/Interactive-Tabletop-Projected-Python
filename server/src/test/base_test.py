import sys
import cv2

from tracking.board import board_snapshot
from tracking.board.board_area import BoardArea
from tracking.board.board_descriptor import BoardDescriptor
from tracking.calibrators.board_calibrator import BoardCalibrator
from tracking.calibrators.calibrator import State


class BaseTest(object):
    current_test_output_string = None
    current_test_name = ''

    default_board_image = None
    default_board_calibrator = None
    default_board_descriptor = None
    default_board_area = None
    default_board_corners = None

    def run(self, debug=False):
        print('\nTest class: %s' % type(self).__name__)

        #self.prepare_defaults()

        total_failed_count = 0
        total_success_count = 0

        for f in self.get_tests():
            self.current_test_name = f.__name__
            self.current_test_output_string = None

            success_count, failed_count = f(debug=debug)

            total_success_count += success_count
            total_failed_count += failed_count

        print('\n%i/%i test%s completed successfully' % (total_success_count, total_success_count + total_failed_count, 's' if total_success_count > 1 else ''), end='')
        if total_failed_count > 0:
            print('. %i test%s FAILED!' % (total_failed_count, 's' if total_failed_count > 1 else ''), end='')
        print()

        return total_success_count, total_failed_count

    def get_tests(self):
        return []

    def print_number(self, current, total):
        if self.current_test_output_string is not None:
            print(('\b' * len(self.current_test_output_string)), end='')

        self.current_test_output_string = 'Running test: %s... %i/%i ' % (self.current_test_name, current, total)

        print(self.current_test_output_string, end='')
        sys.stdout.flush()

    def prepare_defaults(self):

        # Initial board detection
        self.default_board_image = cv2.imread("test/resources/test_base/default_board_detection_source.png")

        self.default_board_calibrator = BoardCalibrator(board_image_filename="test/resources/test_base/default_board_detection_source.png")
        self.default_board_descriptor = BoardDescriptor()

        self.default_board_descriptor.get_board_calibrator().update(self.default_board_image)
        self.default_board_descriptor.get_board_calibrator().state = State.DETECTED

        self.default_board_area = BoardArea(0, self.default_board_descriptor)

        # Detect board
        self.default_board_corners = self.default_board_calibrator.detect(self.default_board_image)
        if self.default_board_corners is not None:
            self.default_board_descriptor.get_board_calibrator().update(self.default_board_image)
            self.default_board_descriptor.get_board_calibrator().state = State.DETECTED

    def resize_image_to_detector_default_size(self, image, detector):
        image_height, image_width = image.shape[:2]

        # Calculate output aspect ratio
        aspect_ratio = float(image_height) / float(image_width)

        # Find output width
        dest_width = board_snapshot.get_snapshot_width(detector.preferred_input_image_resolution(), default=image_width)

        # Resize image
        if dest_width < image_width:
            return cv2.resize(image, (int(dest_width), int(dest_width * aspect_ratio)))
        else:
            return image

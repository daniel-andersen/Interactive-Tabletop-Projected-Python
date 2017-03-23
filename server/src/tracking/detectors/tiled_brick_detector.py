import cv2
import numpy as np
import heapq
from tracking.util import histogram_util


class TiledBrickDetector(object):
    """
    Class capable of recognizing tile bricks on a board.
    """

    def __init__(self):
        self.brick_detection_minimum_median_delta = 20.0
        self.brick_detection_minimum_probability = 0.15
        self.brick_detection_minimum_probability_delta = 0.30

    def find_brick_among_tiles(self, tiled_board_area, coordinates, debug=False):
        """
        Returns the coordinate of a brick from one of the given tile coordinates.

        :param tiled_board_area: Tiled board area
        :param coordinates: Coordinates [(x, y), ...] on which to search for a brick
        :param debug: If True outputs debug information
        :return: (x, y), [probabilities...] - where (x, y) is position of brick, or None if no brick is found, followed by list of probabilities
        """

        # Extract tile strip
        tile_strip_image = tiled_board_area.tile_strip(coordinates, grayscaled=True)

        # Calculate medians
        medians = self.medians_of_tiles(tile_strip_image, coordinates, tiled_board_area)
        min_median, second_min_median = heapq.nsmallest(2, medians)[:2]

        # Check medians
        if debug:
            print("Min median: %f - second min median: %f - delta: %f" % (min_median, second_min_median, second_min_median - min_median))
            cv2.imshow('Area image', tiled_board_area.board_descriptor.get_snapshot().board_image('MEDIUM'))
            cv2.imshow('Tile stip image', tile_strip_image)
            cv2.waitKey(0)

        if second_min_median - min_median < self.brick_detection_minimum_median_delta:
            return None, [0.0 for _ in medians]

        # OTSU strip
        _, tile_strip_image = cv2.threshold(tile_strip_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Calculate probabilities
        probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates, tiled_board_area)
        max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]

        # Check probabilities
        if debug:
            print("2) %f - %f = %f" % (max_probability, second_max_probability, max_probability - second_max_probability))
            print(probabilities)

        if max_probability < self.brick_detection_minimum_probability:
            return None, probabilities

        if max_probability - second_max_probability < self.brick_detection_minimum_probability_delta:
            return None, probabilities

        return coordinates[np.argmin(medians)], probabilities

    def find_bricks_among_tiles(self, tiled_board_area, coordinates, debug=False):
        """
        Returns the coordinates of bricks from any of the given tile coordinates.

        :param tiled_board_area: Tiled board area
        :param coordinates: Coordinates [(x, y), ...] on which to search for bricks
        :param debug: If True outputs debug information
        :return: [((x, y), hasBrick, probability), ...] - where (x, y) is position of brick and hasBrick is True if brick is detected and otherwise false
        """

        # Extract tile strip
        tile_strip_image = tiled_board_area.tile_strip(coordinates, grayscaled=True)

        # Calculate medians
        medians = self.medians_of_tiles(tile_strip_image, coordinates, tiled_board_area)
        min_median, second_min_median = heapq.nsmallest(2, medians)[:2]

        # Check medians
        if second_min_median - min_median < self.brick_detection_minimum_median_delta:
            return None, [0.0 for _ in medians]

        # OTSU strip
        _, tile_strip_image = cv2.threshold(tile_strip_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Calculate probabilities
        probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates, tiled_board_area)

        # Calculate and return brick positions
        return [(coordinates[i], probabilities[i] < self.brick_detection_minimum_probability, probabilities[i]) for i in range(0, len(coordinates))]

    def medians_of_tiles(self, tile_strip_image, coordinates, tiled_board_area):
        return [self.median_of_tile(i, tile_strip_image, tiled_board_area) for i in range(0, len(coordinates))]

    def median_of_tile(self, index, tile_strip_image, tiled_board_area):

        # Extract brick image
        brick_image = tiled_board_area.tile_from_strip_image(index, tile_strip_image)

        # Remove border
        tile_width, tile_height = tiled_board_area.tile_size()
        border_width = int(float(tile_width) * 0.1)
        border_height = int(float(tile_height) * 0.1)
        brick_image = brick_image[border_height:int(tile_height) - border_height, border_width:int(tile_width) - border_width]

        # Calculate histogram from b/w image
        histogram = histogram_util.histogram_from_bw_image(brick_image)

        # Return median and black percentage
        return histogram_util.histogram_median(histogram, ((tile_width - (border_width * 2)) * (tile_height - (border_height * 2))))

    def probabilities_of_bricks(self, tile_strip_image, coordinates, tiled_board_area):
        return [self.probability_of_brick(i, tile_strip_image, tiled_board_area) for i in range(0, len(coordinates))]

    def probability_of_brick(self, index, tile_strip_image, tiled_board_area):

        # Extract brick image
        brick_image = tiled_board_area.tile_from_strip_image(index, tile_strip_image)

        # Remove border
        tile_width, tile_height = tiled_board_area.tile_size()
        border_width = int(float(tile_width) * 0.1)
        border_height = int(float(tile_height) * 0.1)
        brick_image = brick_image[border_height:int(tile_height) - border_height, border_width:int(tile_width) - border_width]

        # Calculate histogram from b/w image
        histogram = histogram_util.histogram_from_bw_image(brick_image)

        # Return black percentage
        return histogram[0][0] / (tile_width * tile_height)

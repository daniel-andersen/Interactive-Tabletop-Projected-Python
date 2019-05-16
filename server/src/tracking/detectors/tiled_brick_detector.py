import cv2
import numpy as np
import heapq

from tracking.util import histogram_util
from util import enum


BrickColor = enum.Enum('BLACK', 'RED', 'BLUE', 'GREEN', 'YELLOW')


class TiledBrickDetector(object):
    """
    Class capable of recognizing tile bricks on a board.
    """

    def __init__(self, tiled_board_area):
        """
        :param tiled_board_area: Tiled board area
        """
        self.tiled_board_area = tiled_board_area

        self.black_brick_detection_minimum_median_delta = 20.0
        self.black_brick_detection_minimum_probability = 0.15
        self.black_brick_detection_minimum_probability_delta = 0.30

        self.colored_brick_detection_minimum_median_delta = 20.0

        self.hue_ranges = {
            BrickColor.RED: [
                {"min": 0, "max": 10},
                {"min": 160, "max": 180}
            ],
            BrickColor.GREEN: [
                {"min": 32, "max": 100}
            ],
            BrickColor.BLUE: [
                {"min": 100, "max": 130}
            ],
            BrickColor.YELLOW: [
                {"min": 20, "max": 40}
            ],
        }

    def find_brick_among_tiles(self, coordinates, color=None, debug=False):
        """
        Returns the coordinate of a brick from one of the given tile coordinates.

        :param coordinates: Coordinates [(x, y), ...] on which to search for a brick
        :param color: (Optional) Brick color
        :param debug: If True outputs debug information
        :return: (x, y), color - where (x, y) is position of brick, or None if no brick is found
        """

        # Detect both black and colored bricks
        black_brick = self.find_black_brick_among_tiles(coordinates, debug)
        colored_brick = self.find_colored_brick_among_tiles(color, coordinates, debug)

        # Black brick
        if color == BrickColor.BLACK and black_brick is not None:
            if colored_brick is not None and colored_brick[0] == black_brick[0]:  # There must be no colored brick detected at same position!
                return None
            return black_brick

        # Specific colored brick other than black
        if color is not None and color != BrickColor.BLACK and colored_brick is not None:
            return colored_brick

        # Any color brick
        if color is None:

            # A black and a colored brick is found
            if colored_brick is not None and black_brick is not None:

                # Cannot have different positions
                if colored_brick[0] != black_brick[0]:
                    return None

                # Return colored brick if same position
                return colored_brick

            if colored_brick is not None:
                return colored_brick

            if black_brick is not None:
                return black_brick

        return None

    def find_bricks_among_tiles(self, coordinates, debug=False):
        """
        Returns the coordinates of bricks from any of the given tile coordinates.

        :param coordinates: Coordinates [(x, y), ...] on which to search for bricks
        :param debug: If True outputs debug information
        :return: [((x, y), color), ...]
        """

        with self.tiled_board_area.lock:

            # Extract tile strip
            tile_strip_image = self.tiled_board_area.tile_strip(coordinates, grayscaled=True)

            # Calculate medians
            medians = self.medians_of_tiles(tile_strip_image, coordinates)
            min_median, second_min_median = heapq.nsmallest(2, medians)[:2]

            # Check medians
            if second_min_median - min_median < self.black_brick_detection_minimum_median_delta:
                return []

            # OTSU strip
            _, tile_strip_image = cv2.threshold(tile_strip_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # Calculate probabilities
            probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates)

            # Calculate and return brick positions
            return [(coordinates[i], probabilities[i] < self.black_brick_detection_minimum_probability, probabilities[i]) for i in range(0, len(coordinates))]

    def find_black_brick_among_tiles(self, coordinates, debug=False):
        with self.tiled_board_area.lock:

            # Extract tile strip
            tile_strip_image = self.tiled_board_area.tile_strip(coordinates, grayscaled=True)

            # Calculate medians
            medians = self.medians_of_tiles(tile_strip_image, coordinates)
            min_median, second_min_median = heapq.nsmallest(2, medians)[:2]

            # Check medians
            if debug:
                print("Min median: %f - second min median: %f - delta: %f" % (min_median, second_min_median, second_min_median - min_median))
                cv2.imshow('Area image', self.tiled_board_area.board_descriptor.get_board_snapshot().board_image('MEDIUM'))
                cv2.imshow('Tile stip image', tile_strip_image)

            if second_min_median - min_median < self.black_brick_detection_minimum_median_delta:
                return None

            # OTSU strip
            _, tile_strip_image = cv2.threshold(tile_strip_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            # Calculate probabilities
            probabilities = self.probabilities_of_bricks(tile_strip_image, coordinates)
            max_probability, second_max_probability = heapq.nlargest(2, probabilities)[:2]

            # Check probabilities
            if debug:
                print("Max probability: %f - second max probability: %f - delta: %f" % (max_probability, second_max_probability, max_probability - second_max_probability))
                print(probabilities)

            if max_probability < self.black_brick_detection_minimum_probability:
                return None

            if max_probability - second_max_probability < self.black_brick_detection_minimum_probability_delta:
                return None

            return coordinates[np.argmin(medians)], BrickColor.BLACK

    def find_colored_brick_among_tiles(self, color, coordinates, debug=False):
        with self.tiled_board_area.lock:

            # Extract tile strip
            tile_strip_image = self.tiled_board_area.tile_strip(coordinates, grayscaled=False)

            if debug:
                cv2.imshow('Area image', self.tiled_board_area.board_descriptor.get_board_snapshot().board_image('MEDIUM'))
                cv2.imshow('Tile stip image', tile_strip_image)

            # Extract HSV
            hsv_image = cv2.cvtColor(tile_strip_image, cv2.COLOR_BGR2HSV)
            hue_image, saturation_image, value_image = cv2.split(hsv_image)

            if debug:
                cv2.imshow('Hue', hue_image)
                cv2.imshow('Saturation', saturation_image)
                #cv2.imshow('Value', value_image)

            # Calculate saturation medians
            medians = self.medians_of_tiles(saturation_image, coordinates)
            max_median, second_max_median = heapq.nlargest(2, medians)[:2]
            min_median, second_min_median = heapq.nsmallest(2, medians)[:2]
            if debug:
                print("Max median: %f - second max median: %f - delta: %f" % (max_median, second_max_median, max_median - second_max_median))
                print("Min median: %f - max median: %f - delta: %f" % (min_median, max_median, max_median - min_median))

            # Check medians
            if max_median - min_median < self.colored_brick_detection_minimum_median_delta:
                return None

            # Find all colored bricks
            colored_bricks = {color: [] for color in BrickColor.names}
            bricks = []

            for index in range(0, len(coordinates)):

                # Ignore less saturated tiles
                if max_median - medians[index] > self.colored_brick_detection_minimum_median_delta:
                    continue

                # Extract tile
                brick_hue_image = self.tiled_board_area.tile_from_strip_image(index, hue_image)
                brick_saturation_image = self.tiled_board_area.tile_from_strip_image(index, saturation_image)

                # Extract color from hue
                tile_color = self.brick_color_from_image(brick_hue_image, brick_saturation_image)

                if tile_color is not None:
                    colored_bricks[BrickColor.names[tile_color]].append((index, tile_color))
                    bricks.append((index, tile_color))

            if debug:
                print(colored_bricks)

            # If a specific color is given, return the unique tile containing the colored brick
            if color is not None:
                bricks = colored_bricks[BrickColor.names[color]]

            # Check if the tile is unique
            if len(bricks) != 1:
                return None

            # Return tile
            index, color = bricks[0]
            return coordinates[index], color

    def brick_color_from_image(self, hue_image, saturation_image):

        # Extract saturated part of hue image
        saturated_hue_image = hue_image[np.where(saturation_image > 50)]

        # Calculate histogram of hue
        counts, bins = np.histogram(saturated_hue_image, range(181))

        # Sort histogram with most common hue first
        hist = [(i, counts[i]) for i in range(0, len(counts))]
        sorted_hist = sorted(hist, key=lambda e: e[1], reverse=True)

        hue = sorted_hist[0][0]

        # Get color
        for color, hue_ranges in self.hue_ranges.items():
            for hue_range in hue_ranges:
                if hue >= hue_range["min"] and hue <= hue_range["max"]:
                    return color

        return None


    def medians_of_tiles(self, tile_strip_image, coordinates):
        return [self.median_of_tile(i, tile_strip_image) for i in range(0, len(coordinates))]

    def median_of_tile(self, index, tile_strip_image):

        with self.tiled_board_area.lock:

            # Extract brick image
            brick_image = self.tiled_board_area.tile_from_strip_image(index, tile_strip_image)

            # Remove border
            tile_width, tile_height = self.tiled_board_area.tile_size()
            border_width = int(float(tile_width) * 0.1)
            border_height = int(float(tile_height) * 0.1)
            brick_image = brick_image[border_height:int(tile_height) - border_height, border_width:int(tile_width) - border_width]

            # Calculate histogram from b/w image
            histogram = histogram_util.histogram_from_bw_image(brick_image)

            # Return median and black percentage
            return histogram_util.histogram_median(histogram, ((tile_width - (border_width * 2)) * (tile_height - (border_height * 2))))

    def probabilities_of_bricks(self, tile_strip_image, coordinates):
        return [self.probability_of_brick(i, tile_strip_image) for i in range(0, len(coordinates))]

    def probability_of_brick(self, index, tile_strip_image):

        with self.tiled_board_area.lock:

            # Extract brick image
            brick_image = self.tiled_board_area.tile_from_strip_image(index, tile_strip_image)

            # Calculate histogram from b/w image
            histogram = histogram_util.histogram_from_bw_image(brick_image)

            # Return black percentage
            tile_width, tile_height = self.tiled_board_area.tile_size_padded()

            return histogram[0][0] / (tile_width * tile_height)

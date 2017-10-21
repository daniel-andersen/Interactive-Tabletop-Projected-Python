import cv2
import numpy as np
from tracking.board.board_area import BoardArea, SnapshotSize
from tracking.detectors.tiled_brick_detector import TiledBrickDetector


class TiledBoardArea(BoardArea):
    """
    Represents a description of a tiled board area.

    Field variables:
    tile_count -- [width, height]
    """
    def __init__(self, area_id, tile_count, padding, rect=[0.0, 0.0, 1.0, 1.0]):
        """
        Initializes a tiled board area.

        :param tile_count: Tile count [tile_count_x, tile_count_y]
        :param padding: Tile padding in percentage [horizontal, vertical]
        """
        super(TiledBoardArea, self).__init__(area_id, rect)

        self.tile_count = tile_count
        self.padding = padding
        self.brick_detector = TiledBrickDetector(tiled_board_area=self)

    def tile_size(self, size=SnapshotSize.ORIGINAL):
        """
        Calculates the size of a single tile.

        :param size: Snapshot size
        :return: Tile (width, height)
        """
        image = self.area_image(size)
        image_height, image_width = image.shape[:2]

        return (float(image_width) / float(self.tile_count[0]),
                float(image_height) / float(self.tile_count[1]))

    def tile_size_padded(self, size=SnapshotSize.ORIGINAL):
        """
        Calculates the size of a single tile minus padding.

        :param size: Snapshot size
        :return: Tile (width, height)
        """
        tile_width, tile_height = self.tile_size(size)
        padding_width, padding_height = self.padding_size(size)

        return (int(tile_width) - (padding_width * 2),
                int(tile_height) - (padding_height * 2))

    def padding_size(self, size=SnapshotSize.ORIGINAL):
        """
        Calculates the size of the padding in whole pixels.

        :param size: Snapshot size
        :return: Padding size (width, height)
        """
        tile_width, tile_height = self.tile_size(size)

        return (int(tile_width * self.padding[0]),
                int(tile_height * self.padding[1]))

    def tile_region(self, x, y, size=SnapshotSize.ORIGINAL):
        """
        Calculates the tile region for tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :param size: Snapshot size
        :return: The (x1, y1, x2, y2, width, height) tile region
        """
        tile_width, tile_height = self.tile_size(size)
        tile_width_padded, tile_height_padded = self.tile_size_padded(size)

        padding_width, padding_height = self.padding_size(size)

        offset_x = int(float(x) * tile_width) + padding_width
        offset_y = int(float(y) * tile_height) + padding_height

        return (offset_x,
                offset_y,
                offset_x + tile_width_padded,
                offset_y + tile_height_padded,
                tile_width_padded,
                tile_height_padded)

    def tile(self, x, y, grayscaled=False, size=SnapshotSize.ORIGINAL):
        """
        Returns the tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :param grayscaled: If true, use grayscaled image as source
        :param size: Snapshot size
        :return: The tile at x, y
        """
        source_image = self.area_image(size) if not grayscaled else self.grayscaled_area_image(size)
        x1, y1, x2, y2 = self.tile_region(x, y, size)[:4]
        return source_image[y1:y2, x1:x2]

    def tile_strip(self, coordinates, grayscaled=False, size=SnapshotSize.ORIGINAL):
        """
        Returns the tiles at the specified coordinates.

        :param coordinates: List of coordinates [(x, y), ...]
        :param grayscaled: If true and source_image is None, use grayscaled image as source
        :param size: Snapshot size
        :return: The tiles in a single horizontal image strip
        """
        source_image = self.area_image(size) if not grayscaled else self.grayscaled_area_image(size)

        tile_width, tile_height = self.tile_size_padded(size)

        image_width = len(coordinates) * tile_width
        image_height = tile_height

        channels = source_image.shape[2] if len(source_image.shape) > 2 else 1
        if channels > 1:
            size = (image_height, image_width, channels)
        else:
            size = (image_height, image_width)

        strip_image = np.zeros(size, source_image.dtype)

        offset = 0.0
        for (x, y) in coordinates:
            tile_image = self.tile(x, y, grayscaled, size)
            strip_image[0:image_height, int(offset):min(int(offset) + int(tile_width), image_width)] = tile_image
            offset += tile_width

        return strip_image

    def tile_from_strip_image(self, index, tile_strip_image, size=SnapshotSize.ORIGINAL):
        """
        Returns the tile at the given index from the given tile strip image.

        :param index: Tile index
        :param tile_strip_image: Tile strip image
        :param size: Snapshot size
        :return: The tile at the given index
        """
        tile_width, tile_height = self.tile_size_padded(size)
        x1 = int(float(index) * tile_width)
        x2 = x1 + int(tile_width)
        return tile_strip_image[0:int(tile_height), x1:x2]

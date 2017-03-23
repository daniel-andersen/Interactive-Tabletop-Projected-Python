import cv2
import numpy as np
from tracking.board.board_area import BoardArea, SnapshotSize


class TiledBoardArea(BoardArea):
    """
    Represents a description of a tiled board area.

    Field variables:
    tile_count -- [width, height]
    """
    def __init__(self, area_id, tile_count, board_descriptor, rect=[0.0, 0.0, 1.0, 1.0]):
        """
        Initializes a tiled board area.

        :param tile_count: Tile count [tile_count_x, tile_count_y]
        """
        super(TiledBoardArea, self).__init__(area_id, board_descriptor, rect)

        self.tile_count = tile_count

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

    def tile_region(self, x, y, size=SnapshotSize.ORIGINAL):
        """
        Calculates the tile region for tile at x, y.

        :param x: X coordinate
        :param y: Y coordinate
        :param size: Snapshot size
        :return: The (x1, y1, x2, y2, width, height) tile region
        """
        tile_width, tile_height = self.tile_size(size)

        return (int(float(x) * tile_width),
                int(float(y) * tile_height),
                int((float(x) * tile_width)) + int(tile_width),
                int((float(y) * tile_height)) + int(tile_height),
                int(tile_width),
                int(tile_height))

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

        tile_width, tile_height = self.tile_size(size)

        image_width = int(float(len(coordinates)) * tile_width)
        image_height = int(tile_height)

        channels = source_image.shape[2] if len(source_image.shape) > 2 else 1
        if channels > 1:
            size = (image_height, image_width, channels)
        else:
            size = (image_height, image_width)

        image = np.zeros(size, source_image.dtype)

        offset = 0.0
        for (x, y) in coordinates:
            x1, y1, x2, y2 = self.tile_region(x, y, size)[:4]
            tile_image = source_image[y1:y2, x1:x2]
            image[0:image_height, int(offset):min(int(offset) + int(tile_width), image_width)] = tile_image
            offset += tile_width

        return image

    def tile_from_strip_image(self, index, tile_strip_image, size=SnapshotSize.ORIGINAL):
        """
        Returns the tile at the given index from the given tile strip image.

        :param index: Tile index
        :param tile_strip_image: Tile strip image
        :param size: Snapshot size
        :return: The tile at the given index
        """
        tile_width, tile_height = self.tile_size(size)
        x1 = int(float(index) * tile_width)
        x2 = x1 + int(tile_width)
        return tile_strip_image[0:int(tile_height), x1:x2]

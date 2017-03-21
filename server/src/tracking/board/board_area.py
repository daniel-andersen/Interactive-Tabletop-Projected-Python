from threading import RLock

import cv2
from random import randint
from tracking.board.board_snapshot import SnapshotSize


class BoardArea(object):
    """
    Represents a description of a board area.
    """
    cached_area_images = {}
    cached_grayscaled_area_images = {}

    def __init__(self, area_id, rect=[0.0, 0.0, 1.0, 1.0]):
        """
        Initializes a board area.

        :param area_id: Area id
        :param rect: Board rect in percentage of board [x1, y1, x2, y2]
        """
        self.area_id = area_id if area_id is not None else randint(0, 100000)
        self.rect = rect
        self.current_board_snapshot_id = None

        self.lock = RLock()

    def area_image(self, board_snapshot, size=SnapshotSize.SMALL):
        """
        Extracts area image from board snapshot.

        :param board_snapshot: Board snapshot
        :param size: Size to return
        :return Extracted area image
        """

        with self.lock:

            # Check if board is recognized
            if not board_snapshot.is_recognized():
                return None

            # Check if snapshot has changed
            if self.current_board_snapshot_id != board_snapshot.id:

                # Remove cached images
                self.cached_area_images = {}
                self.cached_grayscaled_area_images = {}

                # Save snapshot ID
                self.current_board_snapshot_id = board_snapshot.id

            # Return cached area image
            if size in self.cached_area_images:
                return self.cached_area_images[size]

            # Get board image
            board_image = board_snapshot.board_image(size)
            image_height, image_width = board_image.shape[:2]

            # Extract area image
            x1 = int(float(image_width) * self.rect[0])
            y1 = int(float(image_height) * self.rect[1])
            x2 = int(float(image_width) * self.rect[2])
            y2 = int(float(image_height) * self.rect[3])

            self.cached_area_images[size] = board_image[y1:y2, x1:x2]

            return self.cached_area_images[size]

    def grayscaled_area_image(self, board_snapshot, size=SnapshotSize.SMALL):
        """
        Extracts grayscaled area image from board snapshot.

        :param board_snapshot: Board snapshot
        :param size: Size to return
        :return Extracted grayscaled area image
        """

        with self.lock:

            # Check if board is recognized
            if not board_snapshot.is_recognized():
                return None

            # Check if already extracted image
            if self.current_board_snapshot_id == board_snapshot.id:
                if size in self.cached_grayscaled_area_images:
                    return self.cached_grayscaled_area_images[size]

            # Extract image
            image = self.area_image(board_snapshot, size)

            # Grayscale image
            self.cached_grayscaled_area_images[size] = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            return self.cached_grayscaled_area_images[size]
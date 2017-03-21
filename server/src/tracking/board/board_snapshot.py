import cv2
from random import randint
from threading import RLock
from util import enum
from tracking.util import transform


SnapshotStatus = enum.Enum('NOT_RECOGNIZED', 'RECOGNIZED')
SnapshotSize = enum.Enum('EXTRA_SMALL', 'SMALL', 'MEDIUM', 'LARGE', 'ORIGINAL')


class BoardSnapshot:
    """
    Class representing a snapshot (including current camera feed image) of a board.

    Field variables (READ-ONLY!):
    status -- Recognition status (of type SnapshotStatus enum) of snapshot
    camera_image -- Original camera image
    board_images -- The recognized and transformed images in all sizes (dict of type SnapshotSize enum)
    grayscaled_board_images -- A grayscaled version of the board images in all sizes (dict of type SnapshotSize enum)
    board_corners -- The four points in the source image representing the corners of the recognized board
    id -- Random ID for the actual snapshot. Is set automatically when created
    """

    def __init__(self, camera_image, board_corners, status=SnapshotStatus.RECOGNIZED):
        self.camera_image = camera_image
        self.board_corners = board_corners
        self.status = status

        self.id = randint(0, 1000000)

        self.lock = RLock()

        self.board_images = {}
        self.grayscaled_board_images = {}

        if camera_image is not None:
            self.board_images[SnapshotSize.ORIGINAL] = transform.transform_image(camera_image, board_corners)

    def is_recognized(self):
        """
        Returns True if board is recognized in this snapshot or else False.

        :return: True if board is recognized or else False.
        """
        return self.status is SnapshotStatus.RECOGNIZED

    def board_image(self, image_size=SnapshotSize.SMALL):
        """
        Returns the board image in the given size.

        :param image_size:
        :return: Board image in given size
        """

        with self.lock:

            # Check if image already exists
            if image_size in self.board_images:
                return self.board_images[image_size]

            # Get original board image
            if SnapshotSize.ORIGINAL not in self.board_images:
                return None

            original_image = self.board_images[SnapshotSize.ORIGINAL]

            original_height, original_width = original_image.shape[:2]

            # Calculate output aspect ratio
            aspect_ratio = float(original_height) / float(original_width)

            # Find output width
            dest_width = original_width

            if image_size is SnapshotSize.EXTRA_SMALL:
                dest_width = 320.0
            elif image_size is SnapshotSize.SMALL:
                dest_width = 640.0
            elif image_size is SnapshotSize.MEDIUM:
                dest_width = 800.0
            elif image_size is SnapshotSize.LARGE:
                dest_width = 1200.0

            # Resize image
            if dest_width < original_width:
                self.board_images[image_size] = cv2.resize(original_image, (int(dest_width), int(dest_width * aspect_ratio)))
            else:
                self.board_images[image_size] = original_image

            return self.board_images[image_size]

    def grayscaled_board_image(self, image_size=SnapshotSize.SMALL):
        """
        Returns the grayscaled board image in the given size.

        :param image_size: Image size
        :return: Grayscaled board image in given size
        """

        with self.lock:

            # Check if image already exists
            if image_size in self.grayscaled_board_images:
                return self.grayscaled_board_images[image_size]

            # Check for original board image
            if SnapshotSize.ORIGINAL not in self.board_images:
                return None

            # Grayscale imagae
            self.grayscaled_board_images[image_size] = cv2.cvtColor(self.board_image(image_size), cv2.COLOR_BGR2GRAY)

            return self.grayscaled_board_images[image_size]

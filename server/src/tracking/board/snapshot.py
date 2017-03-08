import numpy as np
import cv2
from random import randint
from threading import RLock
from util import enum
from tracking.board.detector import Detector


class Snapshot:
    """
    Class representing a snapshot (including current camera feed image) of a board.

    Field variables:
    status -- Recognition status of snapshot
    camera_image -- Original camera image
    board_images -- The recognized and transformed images in all sizes
    grayscaled_board_images -- A grayscale version of the board images in all sizes
    board_corners -- The four points in the source image representing the corners of the recognized board
    missing_corners -- Dictionary of missing corners, if board was not recognized. {topLeft, topRight, bottomLeft, bottomRight}
    id -- Random ID for the actual snapshot. Is set automatically when created
    """

    SnapshotStatus = enum.Enum('NOT_RECOGNIZED', 'RECOGNIZED')
    SnapshotSize = enum.Enum('EXTRA_SMALL', 'SMALL', 'MEDIUM', 'LARGE', 'ORIGINAL')

    def __init__(self, status=SnapshotStatus.NOT_RECOGNIZED, camera_image=None, board_image=None, board_corners=None, missing_corners=None):
        self.status = status
        self.camera_image = camera_image
        self.board_images = {}
        self.grayscaled_board_images = {}
        self.board_canvas_images = {}
        self.board_corners = board_corners
        self.missing_corners = missing_corners

        self.id = randint(0, 100000)

        self.lock = RLock()

        if board_image is not None:
            self.board_images[BoardDescriptor.SnapshotSize.ORIGINAL] = board_image

    def board_image(self, image_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Returns the board image in the given size.

        :param image_size:
        :return: Board image in given size
        """

        with self.lock:

            # Check if image already exists
            if image_size in self.board_images:
                return self.board_images[image_size]

            if BoardDescriptor.SnapshotSize.ORIGINAL not in self.board_images:
                return None

            # Original image measurements
            original_image = self.board_images[BoardDescriptor.SnapshotSize.ORIGINAL]
            original_height, original_width = original_image.shape[:2]
            aspect_ratio = float(original_height) / float(original_width)

            # Find scaled width
            dest_width = original_width
            if image_size is BoardDescriptor.SnapshotSize.EXTRA_SMALL:
                dest_width = 320.0
            elif image_size is BoardDescriptor.SnapshotSize.SMALL:
                dest_width = 640.0
            elif image_size is BoardDescriptor.SnapshotSize.MEDIUM:
                dest_width = 800.0
            elif image_size is BoardDescriptor.SnapshotSize.LARGE:
                dest_width = 1200.0

            # Resize image
            if dest_width < original_width:
                self.board_images[image_size] = cv2.resize(original_image, (int(dest_width), int(dest_width * aspect_ratio)))
            else:
                self.board_images[image_size] = original_image

            return self.board_images[image_size]

    def grayscaled_board_image(self, image_size=BoardDescriptor.SnapshotSize.SMALL):
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
            if BoardDescriptor.SnapshotSize.ORIGINAL not in self.board_images:
                return None

            # Grayscale imagae
            self.grayscaled_board_images[image_size] = cv2.cvtColor(self.board_image(image_size), cv2.COLOR_BGR2GRAY)
            return self.grayscaled_board_images[image_size]

    def board_canvas_image(self, canvas_region, image_size=BoardDescriptor.SnapshotSize.SMALL):
        """
        Returns the grayscaled board image in the given size.

        :param canvas_region: Canvas region (x1, y1, x2, y2)
        :param image_size: Image size
        :return: Grayscaled board image in given size
        """

        with self.lock:

            # Check if already present
            if image_size not in self.board_canvas_images:

                # Extract board image
                board_image = self.board_image(image_size)
                if board_image is None:
                    return None

                # Extract region
                self.board_canvas_images[image_size] = board_image[
                                                       int(canvas_region[1]):int(canvas_region[3]),
                                                       int(canvas_region[0]):int(canvas_region[2])]

            return self.board_canvas_images[image_size]

import numpy as np
import cv2
from threading import RLock
from util import enum


State = enum.Enum('NOT_DETECTED', 'DETECTED')


class Detector(object):
    """
    Class capable of detecting board.
    """
    def __init__(self, board_image_filename, min_matches=20):

        self.min_matches = min_matches

        self.lock = RLock()

        self.state = State.NOT_DETECTED
        self.corners = None

        # Load board calibrator image
        self.board_image = cv2.imread(board_image_filename)

        if self.board_image is None:
            raise Exception('Could not load board calibrator image: %s' % board_image_filename)

        # Get aspect ratio of board image
        image_height, image_width = self.board_image.shape[:2]
        self.aspect_ratio = image_height / image_width

        # Initialize SIFT detector
        self.sift = cv2.xfeatures2d.SIFT_create()

        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find features in marker image
        self.kp1, self.des1 = self.sift.detectAndCompute(self.board_image, None)

    def update(self, image):
        """
        Updates detection state with image.

        :param image: Input image
        :return: Current detection state
        """

        # Perform detection
        new_state = self.detect(image)

        # Update state
        with self.lock:
            self.corners = None
            self.state = new_state
            return self.state

    def detect(self, image):
        """
        Performs a single detection with the given image.

        :param image: Input image
        :return: Detection status
        """

        # Detect image
        with self.lock:

            # Find features in image
            kp2, des2 = self.sift.detectAndCompute(image, None)

            if len(self.kp1) < 2 or len(kp2) < 2:
                return State.NOT_DETECTED

            # Find matches
            matches = self.flann.knnMatch(self.des1, des2, k=2)

        # Sort out bad matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.65 * n.distance:
                good_matches.append(m)

        matchesMask = [[0, 0] for i in range(0, len(matches))]

        # ratio test as per Lowe's paper
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.65 * n.distance:
                matchesMask[i] = [1, 0]

        draw_params = dict(matchColor=(0, 255, 0),
                           singlePointColor=(255, 0, 0),
                           matchesMask=matchesMask,
                           flags=0)

        print("Matches: %i" % len(good_matches))
        img3 = cv2.drawMatchesKnn(self.board_image, self.kp1, image, kp2, matches, None, **draw_params)
        cv2.imshow('frame', img3)

        # Check number of matches
        if len(good_matches) < self.min_matches:
            return State.NOT_DETECTED

        # Catch potential transformation exceptions
        try:

            # Find homography between matches
            src_pts = np.float32([self.kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Transform points to image
            _, image_width = image.shape[:2]

            src_points = np.float32([[0, 0],
                                     [0, (image_width * self.aspect_ratio) - 1],
                                     [image_width - 1, (image_width * self.aspect_ratio) - 1],
                                     [image_width - 1, 0]]).reshape(-1, 1, 2)
            dst_points = cv2.perspectiveTransform(src_points, M)

            with self.lock:
                self.corners = [[int(p[0][0]), int(p[0][1])] for p in dst_points]

            print("Corners: %s" % self.corners)
            img4 = image.copy()
            cv2.drawContours(img4, [np.int32(self.corners).reshape(-1, 1, 2)], -1, (255, 0, 255), 2)
            cv2.imshow('frame 2', img4)
            cv2.waitKey(0)

            return State.DETECTED

        except Exception as e:
            print("Exception in Detector: %s" % str(e))
            return State.NOT_DETECTED

    def get_corners(self):
        with self.lock:
            return self.corners

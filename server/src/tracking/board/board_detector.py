import time
import numpy as np
import cv2
from threading import RLock
from util import enum


State = enum.Enum('NOT_DETECTED', 'DETECTED')


class BoardDetector(object):
    """
    Class capable of detecting board.
    """
    def __init__(self, board_image_filename, min_matches=50):

        self.min_matches = min_matches

        # Initialize instance variables
        self.lock = RLock()

        self.detect_min_stable_time = 2.0
        self.detect_min_count = 2

        self.tracking_accept_distance_ratio = 1.0

        self.detect_history = []  # {timestamp, corners}

        # Load board calibrator image
        self.board_image = cv2.imread(board_image_filename)

        if self.board_image is None:
            raise Exception('Could not load board calibrator image: %s' % board_image_filename)

        # Initialize SIFT detector
        self.sift = cv2.xfeatures2d.SIFT_create()

        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find features in marker image
        self.kp1, self.des1 = self.sift.detectAndCompute(self.board_image, None)

    def reset(self):
        self.detect_history = []

    def update(self, image):
        """
        Updates detection state with image.

        :param image: Input image
        :return: Current detection state
        """

        # Perform detection
        corners = self.detect_corners(image)

        # Update history
        if corners is not None:
            with self.lock:
                self.detect_history.append((time.time(), corners))

        # Return detected state
        return self.get_state()

    def get_state(self):
        with self.lock:

            # Check sufficient amount of detections
            if len(self.detect_history) < self.detect_min_count:
                return State.NOT_DETECTED

            # Check sufficient time ellapsed
            if self.detect_history[-1]["timestamp"] - self.detect_history[0]["timestamp"] < self.detect_min_stable_time:
                return State.NOT_DETECTED

            # Check corner deviation
            #corner_deviation = [[0.0, 0.0] for _ in range(0, 4)]
            #for _, state, corners in self.detect_history:
            #    for i, p in enumerate(corners):
            #        corner_deviation[i][0] += p[0]
            #        corner_deviation[i][1] += p[1]

            return State.DETECTED

    def get_corners(self):
        with self.lock:
            return self.detect_history[-1]["corners"] if self.get_state() == State.DETECTED else None

    def detect_corners(self, image, debug=False):
        """
        Performs a single detection of corners with the given image.

        :param image: Input image
        :param debug: Enable debug output
        :return: Detected corners, if any
        """

        # Detect image
        with self.lock:

            # Find features in image
            kp2, des2 = self.sift.detectAndCompute(image, None)

            if len(self.kp1) < 2 or len(kp2) < 2:
                return None

            # Find matches
            matches = self.flann.knnMatch(self.des1, des2, k=2)

        # Find homography between matches
        src_pts = np.float32([self.kp1[m.queryIdx].pt for m, n in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m, n in matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matches_mask = mask.ravel().tolist()

        # Sort out outliers and bad matches
        good_matches = []
        for i, (m, n) in enumerate(matches):
            if matches_mask[i] == 1 and m.distance < self.tracking_accept_distance_ratio * n.distance:
                good_matches.append(m)

        # Debug output
        if debug:
            draw_mask = [[0, 0] for i in range(0, len(matches))]
            for i, (m, n) in enumerate(matches):
                if matches_mask[i] == 1 and m.distance < self.tracking_accept_distance_ratio * n.distance:
                    draw_mask[i] = [1, 0]

            draw_params = dict(matchColor=(0, 255, 0), singlePointColor=(255, 0, 0), matchesMask=draw_mask, flags=0)
            img = cv2.drawMatchesKnn(self.board_image, self.kp1, image, kp2, matches, None, **draw_params)
            cv2.imshow('All matches', img)

        # Check number of matches
        if len(good_matches) < self.min_matches:
            return None

        # Catch potential transformation exceptions
        try:

            # Find homography between matches
            src_pts = np.float32([self.kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Transform points to image
            image_height, image_width = self.board_image.shape[:2]

            src_points = np.float32([[0, 0],
                                     [0, image_height - 1],
                                     [image_width - 1, image_height - 1],
                                     [image_width - 1, 0]]).reshape(-1, 1, 2)
            dst_points = cv2.perspectiveTransform(src_points, M)

            # Get corners
            detected_corners = [[int(p[0][0]), int(p[0][1])] for p in dst_points]

            # Debug output
            if debug:
                img = image.copy()
                cv2.drawContours(img, [np.int32(detected_corners).reshape(-1, 1, 2)], -1, (255, 0, 255), 2)
                cv2.imshow('Corners', img)
                cv2.waitKey(0)

            return detected_corners

        except Exception as e:
            print("Exception in Detector: %s" % str(e))
            return None

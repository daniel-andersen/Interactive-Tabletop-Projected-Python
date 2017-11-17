import cv2
import numpy as np
import math
from threading import RLock
from tracking.board.board_snapshot import SnapshotSize
from tracking.detectors.detector import Detector
from tracking.util import misc_math


class ImageDetector(Detector):
    """
    Class implementing hand detector.
    """
    def __init__(self, detector_id, source_image, min_matches=20, input_resolution=SnapshotSize.ORIGINAL):
        """
        :param detector_id: Detector ID
        :param source_image: Image to detect
        :param min_matches: Minimum number of matches for detection to be considered successful
        """
        super().__init__(detector_id)

        self.source_image = source_image
        self.min_matches = min_matches
        self.input_resolution = input_resolution

        self.lock = RLock()

        # Get size of query image
        self.query_image_height, self.query_image_width = self.source_image.shape[:2]

        # Initialize SIFT detector
        self.sift = cv2.xfeatures2d.SIFT_create()

        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find features in marker image
        self.kp1, self.des1 = self.sift.detectAndCompute(self.source_image, None)

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to medium.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return self.input_resolution

    def detect_in_image(self, image):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected images {detectorId, matches: [{x, y, width, height, angle}]}
        """

        # TODO! Multiple matches!

        # Find features in image
        with self.lock:
            kp2, des2 = self.sift.detectAndCompute(image, None)

        if len(self.kp1) < 2 or len(kp2) < 2:
            return None

        # Find matches
        with self.lock:
            matches = self.flann.knnMatch(self.des1, des2, k=2)

        # Sort out bad matches
        good_matches = []
        for m, n in matches:
            if m.distance < 0.666 * n.distance:
                good_matches.append(m)

        # Check number of matches
        if len(good_matches) < self.min_matches:
            cv2.imwrite("debug_image_detector.png", image)
            return None

        try:
            # Find homography between matches
            src_pts = np.float32([self.kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([     kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Transform points to board area
            pts = np.float32([[0, 0], [0, self.query_image_height - 1], [self.query_image_width - 1, self.query_image_height - 1], [self.query_image_width - 1, 0]]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts, M)
            contour = np.int32(dst)

        except Exception as e:
            print("Exception in image detector: %s" % str(e))
            return None

        # Calculate width and height
        size_1 = misc_math.line_length(contour[1][0], contour[0][0])
        size_2 = misc_math.line_length(contour[2][0], contour[1][0])

        max_size = max(size_1, size_2)
        min_size = min(size_1, size_2)

        if self.query_image_width > self.query_image_height:
            width = max_size
            height = min_size
        else:
            width = min_size
            height = max_size

        # Sanity check
        image_height, image_width = image.shape[:2]
        box = cv2.minAreaRect(contour)

        if width > image_width or height > image_height:
            return None

        # Return result
        return {"detectorId": self.detector_id,
                "matches": [
                    {"x": float(box[0][0]) / float(image_width),
                     "y": float(box[0][1]) / float(image_height),
                     "width": float(width) / float(image_width),
                     "height": float(height) / float(image_height),
                     "angle": misc_math.angle_from_homography_matrix(M) * 180.0 / math.pi
                     }]}

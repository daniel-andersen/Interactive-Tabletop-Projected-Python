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
    def __init__(self, detector_id, source_images, min_matches=8, input_resolution=SnapshotSize.LARGE):
        """
        :param detector_id: Detector ID
        :param source_images: List of image to detect
        :param min_matches: Minimum number of matches for detection to be considered successful
        """
        super().__init__(detector_id)

        self.source_images = source_images
        self.min_matches = min_matches
        self.input_resolution = input_resolution

        self.lock = RLock()

        # Initialize SIFT detector
        self.sift = cv2.xfeatures2d.SIFT_create()

        # Initialize FLANN matcher
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=4)
        search_params = dict(checks=32)

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Find features in marker image
        self.descriptors = []
        for source_image in self.source_images:
            kp, des = self.sift.detectAndCompute(source_image, None)
            height, width = source_image.shape[:2]
            self.descriptors.append({"kp": kp,
                                     "des": des,
                                     "width": width,
                                     "height": height})

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

        #cv2.imwrite("debug_image_detector.png", image)

        # Find features in image
        with self.lock:
            kp, des = self.sift.detectAndCompute(image, None)

        if len(kp) < 2:
            return None

        # Find matches in all images
        best_matches = None
        best_descriptor = None

        for descriptor in self.descriptors:
            source_kp = descriptor["kp"]
            source_des = descriptor["des"]

            with self.lock:
                matches = self.flann.knnMatch(des, source_des, k=2)

            # Sort out bad matches
            good_matches = []
            for m, n in matches:
                if m.distance < 0.6 * n.distance:
                    good_matches.append(m)

            # Find inliers
            try:
                src_pts = np.float32([       kp[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([source_kp[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

                matches_mask = mask.ravel().tolist()
            except Exception:
                matches_mask = [0 for i in range(0, len(matches))]

            inliers_count = sum([i for i in matches_mask])

            # Check number of matches
            if inliers_count < 4:
                #print("Inliers count too low!")
                continue

            if len(good_matches) < self.min_matches:
                #print("Not enough matches!")
                continue

            # Check if best match
            if best_matches is None or len(good_matches) > len(best_matches):
                best_matches = good_matches
                best_descriptor = descriptor

        # Check if any matches
        if best_matches is None:
            #print("No best match!")
            return None

        # Extract best match
        source_kp = best_descriptor["kp"]
        source_des = best_descriptor["des"]
        source_width = best_descriptor["width"]
        source_height = best_descriptor["height"]

        try:
            # Find homography between matches
            src_pts = np.float32([source_kp[m.trainIdx].pt for m in best_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([       kp[m.queryIdx].pt for m in best_matches]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # Transform points to board area
            pts = np.float32([[0, 0], [0, source_height - 1], [source_width - 1, source_height - 1], [source_width - 1, 0]]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts, M)
            contour = np.int32(dst)

            # Calculate width and height
            size_1 = misc_math.line_length(contour[1][0], contour[0][0])
            size_2 = misc_math.line_length(contour[2][0], contour[1][0])

            max_size = max(size_1, size_2)
            min_size = min(size_1, size_2)

            if source_width > source_height:
                width = max_size
                height = min_size
            else:
                width = min_size
                height = max_size

        except Exception as e:
            print("Exception in image detector: %s" % str(e))
            return None

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

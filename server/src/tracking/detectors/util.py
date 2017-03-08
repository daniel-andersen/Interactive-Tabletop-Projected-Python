import cv2


def contour_to_detector_result(detector, image, contour):
    """
    Extracts detection result from contour.

    :param detector: Detector used
    :param image: Image
    :param contour: Contour
    :return: Result in form {"detectorId", "centerX", "centerY", "width", "height", "angle", "contour"}
    """
    image_height, image_width = image.shape[:2]
    box = cv2.minAreaRect(contour)

    return {"detectorId": detector.detector_id,
            "x": (float(box[0][0]) + (float(box[1][0]) / 2.0)) / float(image_width),
            "y": (float(box[0][1]) + (float(box[1][1]) / 2.0)) / float(image_height),
            "width": float(box[1][0]) / float(image_width),
            "height": float(box[1][1]) / float(image_height),
            "angle": box[2],
            "contour": [[float(p[0][0]) / float(image_width), float(p[0][1]) / float(image_height)] for p in contour]}


def contours_to_marker_result(detector, image, contours):
    """
    Extracts marker results from contours.

    :param detector: Detector used
    :param image: Image
    :param contours: Contours
    :return: List of markers each in form {"detectorId", "centerX", "centerY", "width", "height", "angle", "contour"}
    """
    return [contour_to_detector_result(detector, image, contour) for contour in contours]

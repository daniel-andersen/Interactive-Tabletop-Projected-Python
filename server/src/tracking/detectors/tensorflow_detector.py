import cv2
import numpy as np
import tensorflow as tf

from tracking.detectors.detector import Detector
from tracking.board.board_snapshot import SnapshotSize


class TensorflowDetector(Detector):
    """
    Class implementing image detector using tensorflow.
    """

    detection_graph = None

    def __init__(self, detector_id, model_name, min_score=0.9):
        """
        :param detector_id: Detector ID
        :param model_name: Name of model to use
        """
        super().__init__(detector_id)

        self.model_name = model_name
        self.min_score = min_score

        self.load_model()

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to medium.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return SnapshotSize.EXTRA_SMALL

    def detect_in_image(self, image):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected features each containing {detectorId, class, score, centerX, centerY, width, height, angle}
        """
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as session:

                # Definite input and output Tensors for detection_graph
                image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

                # Each box represents a part of the image where a particular object was detected.
                detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

                # Each score represent how level of confidence for each of the objects.
                # Score is shown on the result image, together with the class label.
                detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
                detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_expanded = np.expand_dims(image, axis=0)

                # Actual detection.
                (boxes, scores, classes, num) = session.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_expanded})

                return [{"detectorId": self.detector_id,
                         "class": int(classes[0][i]),
                         "score": float(scores[0][i]),
                         "centerX": float(boxes[0][i][1] + boxes[0][i][3]) / 2.0,
                         "centerY": float(boxes[0][i][0] + boxes[0][i][2]) / 2.0,
                         "width": float(boxes[0][i][3] - boxes[0][i][1]),
                         "height": float(boxes[0][i][2] - boxes[0][i][0]),
                         "angle": 0.0} for i in range(0, len(scores[0])) if scores[0][i] >= self.min_score]

    def load_model(self):
        path_to_ckpt = 'resources/tensorflow/%s_frozen_inference_graph.pb' % self.model_name

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

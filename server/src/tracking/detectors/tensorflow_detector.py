import numpy as np
import tensorflow as tf

from tracking.detectors.detector import Detector
from tracking.board.board_snapshot import SnapshotSize


class TensorflowDetector(Detector):
    """
    Class implementing image detector using tensorflow.
    """

    detection_graph = None

    def __init__(self, detector_id, model_name):
        """
        :param detector_id: Detector ID
        :param model_name: Name of model to use
        """
        super().__init__(detector_id)
        self.model_name = model_name

        self.load_model()

    def preferred_input_image_resolution(self):
        """
        Returns the preferred input resolution for this detector. Defaults to medium.

        :return: Input resolution (of type SnapshotSize enum)
        """
        return SnapshotSize.MEDIUM

    def detect(self, image):
        """
        Run detector in image.

        :param image: Image
        :return: List of detected features each containing at least {"detectorId", "centerX", "centerY", "width", "height", "angle"}
        """
        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:

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
                (boxes, scores, classes, num) = sess.run(
                    [detection_boxes, detection_scores, detection_classes, num_detections],
                    feed_dict={image_tensor: image_expanded})

                # Visualization of the results of a detection.
                """
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=2)
                plt.figure(figsize=IMAGE_SIZE)
                plt.imshow(image_np)
                plt.show()
                """

        return []

    def load_model(self):
        path_to_ckpt = 'resources/%s_frozen_inference_graph.pb' % self.model_name

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

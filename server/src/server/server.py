from __future__ import with_statement

import base64
import json
import sys
import time
import traceback
from random import randint
from threading import RLock

import cv2
import numpy as np
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

from server import globals
from server.threads.board_calibration_thread import BoardCalibrationThread
from server.threads.hand_detector_calibration_thread import HandDetectorCalibrationThread
from server.threads.images_detector_thread import ImagesDetectorThread
from server.threads.tiled_brick_detector_threads import TiledBrickDetectorThread, TiledBrickMovementDetectorThread, \
    TiledBricksDetectorThread
from tracking.board.board_area import BoardArea
from tracking.board.tiled_board_area import TiledBoardArea
from tracking.detectors.tensorflow_detector import TensorflowDetector
from util import misc_util

if misc_util.module_exists("picamera"):
    print("Using Raspberry Pi camera")
    from server.camera_pi import Camera
else:
    print("Using desktop camera")
    from server.camera_desktop import Camera


class Server(WebSocket):
    """
    Server which communicates with the client library.
    """
    def __init__(self, server, sock, address):
        super().__init__(server, sock, address)

        self.action_to_function_dict = {'cancelRequest': self.cancel_request,
                                        'cancelRequests': self.cancel_requests,
                                        'reset': self.reset,
                                        'clearState': self.clear_state,
                                        'enableDebug': self.enable_debug,
                                        'takeScreenshot': self.take_screenshot,
                                        'setDebugCameraImage': self.set_debug_camera_image,
                                        'calibrateBoard': self.calibrate_board,
                                        'calibrateHandDetection': self.calibrate_hand_detection,
                                        'initializeTiledBoardArea': self.initialize_tiled_board_area,
                                        'detectTiledBrick': self.detect_tiled_brick,
                                        'detectTiledBricks': self.detect_tiled_bricks,
                                        'detectTiledBrickMovement': self.detect_tiled_brick_movement,
                                        'setupTensorflowDetector': self.setup_tensorflow_detector,
                                        'detectImages': self.detect_images}

        self.detectors = {}
        self.detectors_lock = RLock()

        self.threads = {}
        self.threads_lock = RLock()

    def handleMessage(self):
        """
        Handles incoming message.
        """
        try:
            print("Got message: %s" % self.data)
            json_dict = json.loads(self.data)

            if "action" in json_dict:
                action = json_dict["action"]

                result = self.handle_action(action, json_dict["payload"])

                if result is not None:
                    self.send_message(result=result[0], action=action, payload=result[1], request_id=result[2])

        except Exception as e:
            print("Exception in handleMessage: %s" % str(e))
            traceback.print_exc(file=sys.stdout)

    def handle_action(self, action, payload):
        if action in self.action_to_function_dict:
            return self.action_to_function_dict[action](payload)
        else:
            return "UNDEFINED_ACTION", {}, self.request_id_from_payload(payload)

    def initialize_video(self, resolution):
        with globals.get_state().camera_lock:
            if globals.get_state().get_camera() is not None:
                return
            globals.get_state().set_camera(Camera())
            globals.get_state().get_camera().start(delegate=self, resolution=resolution)

    def cancel_request(self, payload):
        """
        Cancels a request made to the server.

        id: Request ID
        """
        self.cancel_thread(request_id=payload["id"])
        return "OK", {}, self.request_id_from_payload(payload)

    def cancel_requests(self, payload):
        """
        Cancels all requests made to the server.
        """
        self.cancel_threads()
        return "OK", {}, self.request_id_from_payload(payload)

    def reset(self, payload):
        """
        Resets to initial state.

        requestId: (Optional) Request ID
        cameraResolution: (Optional) Camera resolution in [width, height]. Default: [640, 480].
        """
        resolution = payload["resolution"] if "resolution" in payload else [640, 480]

        self.cancel_threads()
        globals.reset()
        self.initialize_video(resolution)

        return "OK", {}, self.request_id_from_payload(payload)

    def clear_state(self, payload):
        """
        Cancels all requests, resets board areas, etc., but does not clear board detection and camera state.

        requestId: (Optional) Request ID
        """
        self.cancel_threads()

        globals.get_state().reset_board_areas()
        globals.get_state().reset_detectors()

        return "OK", {}, self.request_id_from_payload(payload)

    def enable_debug(self, payload):
        """
        Enables debug output.

        requestId: (Optional) Request ID
        """
        globals.get_state().debug = True

        return "OK", {}, self.request_id_from_payload(payload)

    def take_screenshot(self, payload):
        """
        Takes a screenshot and saves it to disk.

        requestId: (Optional) Request ID
        filename: (Optional) Screenshot filename
        """
        camera = globals.get_state().get_camera()
        if camera is not None:
            image = camera.read()
            if image is not None:
                filename = payload["filename"] if "filename" in payload else\
                    "debug/board_{0}.png".format(time.strftime("%Y-%m-%d-%H%M%S"))
                cv2.imwrite(filename, image)
                return "OK", {}, self.request_id_from_payload(payload)

        return "CAMERA_NOT_READY", {}, self.request_id_from_payload(payload)

    def set_debug_camera_image(self, payload):
        """
        Overriden the camera input with the given image.

        imageBase64: Image as base 64 encoded PNG
        """
        raw_image = base64.b64decode(payload["imageBase64"])
        raw_bytes = np.asarray(bytearray(raw_image), dtype=np.uint8)
        image = cv2.imdecode(raw_bytes, cv2.IMREAD_UNCHANGED)

        camera = globals.get_state().get_camera()
        if camera is None:
            return "CAMERA_NOT_READY", {}, self.request_id_from_payload(payload)

        camera.set_debug_image(image)

        cv2.imwrite("debug.png", image)

        return "OK", {}, self.request_id_from_payload(payload)

    def calibrate_board(self, payload):
        """
        Calibrates board.

        requestId: (Optional) Request ID
        """
        thread = BoardCalibrationThread(self.request_id_from_payload(payload),
                                        callback_function=lambda: self.stop_thread(thread,
                                                                                   result="OK",
                                                                                   action="calibrateBoard",
                                                                                   payload={}),
                                        timeout_function=lambda: self.stop_thread(thread,
                                                                                  result="CALIBRATION TIMEOUT",
                                                                                  action="calibrateBoard",
                                                                                  payload={}))
        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def calibrate_hand_detection(self, payload):
        """
        Calibrates hand detection.

        requestId: (Optional) Request ID
        """
        thread = HandDetectorCalibrationThread(self.request_id_from_payload(payload),
                                               callback_function=lambda: self.stop_thread(thread,
                                                                                          result="OK",
                                                                                          action="calibrateHandDetection",
                                                                                          payload={}))
        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def setup_tensorflow_detector(self, payload):
        """
        Sets up a tensorflow detector.

        detectorId: Detector ID to use as a reference
        modelName: Name of model to use
        requestId: (Optional) Request ID
        """
        detector = TensorflowDetector(detector_id=payload["detectorId"], model_name=payload["modelName"])

        globals.get_state().set_detector(detector.detector_id, detector)

        return "OK", {}, self.request_id_from_payload(payload)

    def initialize_board_area(self, payload):
        """
        Initializes board area with given parameters.

        requestId: (Optional) Request ID
        id: (Optional) Area id
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        """
        with globals.get_state().board_descriptor_lock:
            board_descriptor = globals.get_state().get_board_descriptor()

            board_area = BoardArea(
                area_id=payload["id"] if "id" in payload else None,
                board_descriptor=board_descriptor,
                rect=[payload["x1"], payload["y1"], payload["x2"], payload["y2"]]
            )
            globals.get_state().set_board_area(board_area.area_id, board_area)

            return "OK", {"id": board_area.area_id}, self.request_id_from_payload(payload)

    def initialize_tiled_board_area(self, payload):
        """
        Initializes tiled board area with given parameters.

        requestId: (Optional) Request ID
        id: (Optional) Area id
        tileCountX: Number of horizontal tiles.
        tileCountY: Number of vertical tiles.
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        """
        with globals.get_state().board_descriptor_lock, globals.get_state().board_areas_lock:
            board_descriptor = globals.get_state().get_board_descriptor()

            board_area = TiledBoardArea(
                payload["id"] if "id" in payload else None,
                [payload["tileCountX"], payload["tileCountY"]],
                [payload["x1"], payload["y1"], payload["x2"], payload["y2"]],
                board_descriptor
            )

            globals.get_state().set_board_area(board_area.area_id, board_area)

            return "OK", {"id": board_area.area_id}, self.request_id_from_payload(payload)

    def remove_board_areas(self, payload):
        """
        Removes all board areas.

        requestId: (Optional) Request ID
        """
        globals.get_state().reset_board_areas()

        return "OK", {}, self.request_id_from_payload(payload)

    def remove_board_area(self, payload):
        """
        Removes the given board area.

        requestId: (Optional) Request ID
        id: Area ID.
        """
        area_id = payload["id"]

        globals.get_state().remove_board_area(area_id)

        return "OK", {}, self.request_id_from_payload(payload)

    def detect_images(self, payload):
        """
        Detects images on the board using the given detector.

        areaId: ID of area to detect images in
        detectorId: Detector ID to use as a reference
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        if board_area is None:
            return "BOARD_AREA_NOT_FOUND", {}, self.request_id_from_payload(payload)

        detector = globals.get_state().get_detector(payload["detectorId"])
        if detector is None:
            return "DETECTOR_NOT_FOUND", {}, self.request_id_from_payload(payload)

        thread = ImagesDetectorThread(self.request_id_from_payload(payload),
                                      detector, board_area,
                                      callback_function=lambda result: self.stop_thread(thread,
                                                                                        result="OK",
                                                                                        action="detectImages",
                                                                                        payload=result))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_tiled_brick(self, payload):
        """
        Detects tiled brick at any of the given positions.

        areaId: Tiled board area id
        validPositions: Positions to search for brick in.
        targetPosition: (Optional) Target position for brick to be placed. Use fx. for initial brick positioning.
        waitForPosition: (Optional) If True, waits for brick to be detected.
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        valid_positions = payload["validPositions"]
        target_position = payload["targetPosition"]
        wait_for_position = payload["waitForPosition"] if "waitForPosition" in payload else False

        thread = TiledBrickDetectorThread(
            self.request_id_from_payload(payload),
            board_area,
            valid_positions,
            target_position,
            wait_for_position,
            callback_function=lambda tile: self.stop_thread(thread,
                                                            result="OK",
                                                            action="detectTiledBrick",
                                                            payload={"tile": tile} if tile else {}))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_tiled_bricks(self, payload):
        """
        Detects tiled bricks at the given positions.

        areaId: Tiled board area id
        validPositions: Positions to search for brick in.
        waitForPosition: (Optional) If True, waits for bricks to be detected.
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        valid_positions = payload["validPositions"]
        wait_for_position = payload["waitForPosition"] if "waitForPosition" in payload else False

        thread = TiledBricksDetectorThread(
            self.request_id_from_payload(payload),
            board_area,
            valid_positions,
            wait_for_position,
            callback_function=lambda tiles: self.stop_thread(thread,
                                                             result="OK",
                                                             action="detectTiledBricks",
                                                             payload={"tiles": tiles}))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_tiled_brick_movement(self, payload):
        """
        Reports back when brick is found in any of the given positions other than the initial position.

        areaId: Tiled board area id
        validPositions: Positions to search for object in.
        initialPosition: (Optional) Initial position.
        targetPosition: (Optional) Target position.
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        valid_positions = payload["validPositions"]
        initial_position = payload["initialPosition"] if "initialPosition" in payload else None
        target_position = payload["targetPosition"] if "targetPosition" in payload else None

        thread = TiledBrickMovementDetectorThread(
            self.request_id_from_payload(payload),
            board_area,
            valid_positions,
            initial_position,
            target_position,
            callback_function=lambda to_position, from_position: self.stop_thread(thread,
                                                                                  result="OK",
                                                                                  action="detectTiledBrickMovement",
                                                                                  payload={"position": to_position,
                                                                                           "initialPosition": from_position}))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def send_message(self, result, action, payload={}, request_id=None):
        """
        Sends a new message to the client.

        :param result Result code
        :param action Client action from which the message originates
        :param payload Payload
        :param request_id: Request ID
        """
        message = {"result": result,
                   "action": action,
                   "payload": payload,
                   "requestId": request_id}
        self.sendMessage(json.dumps(message, ensure_ascii=False))

        print("Sent message: %s" % message)

    def handleConnected(self):
        print(self.address, "connected")

    def handleClose(self):
        print(self.address, "closed")

    def pick_request_id(self):
        return randint(0, 1000000)

    def request_id_from_payload(self, payload):
        """
        Returns payload from request. If no payload given, a random ID is generated.

        :param payload: Payload
        :return: Request ID from payload, or random if none given
        """
        return payload["requestId"] if "requestId" in payload else self.pick_request_id()

    def camera_image_updated(self, image):
        board_descriptor = globals.get_state().get_board_descriptor()
        if board_descriptor is not None:
            board_descriptor.update(image)

    def start_thread(self, request_id, thread):
        with self.threads_lock:
            self.threads[request_id] = thread

        try:
            thread.start()
        except Exception as e:
            print("Exception in start_thread: %s" % str(e))
            traceback.print_exc(file=sys.stdout)

    def stop_thread(self, thread, result, action, payload):
        self.cancel_thread(thread.request_id)
        self.send_message(result, action, payload, thread.request_id)

    def cancel_thread(self, request_id):
        with self.threads_lock:
            thread = self.threads.pop(request_id, None)
            if thread:
                thread.stop()

    def cancel_threads(self):
        with self.threads_lock:
            thread_keys = list(self.threads.keys())  # Original dict modified during iteration
            for request_id in thread_keys:
                self.cancel_thread(request_id)
            self.threads = {}


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()

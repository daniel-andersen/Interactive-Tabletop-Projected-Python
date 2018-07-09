from __future__ import with_statement

import base64
import json
import sys
import time
import traceback
from random import randint

from threading import Thread, RLock

import cv2
import numpy as np

import asyncio
import websockets

from server import globals
from server.threads.board_calibration_thread import BoardCalibrationThread
from server.threads.gesture_detector_thread import GestureDetectorThread
from server.threads.hand_detector_calibration_thread import HandDetectorCalibrationThread
from server.threads.images_detector_thread import ImagesDetectorThread
from server.threads.nonobstructed_area_detector_thread import NonobstructedAreaDetectorThread
from server.threads.tiled_brick_detector_threads import TiledBrickDetectorThread, TiledBrickMovementDetectorThread, TiledBricksDetectorThread
from tracking.board.board_area import BoardArea
from tracking.board.board_snapshot import SnapshotSize
from tracking.board.tiled_board_area import TiledBoardArea
from tracking.detectors.hand_detector import handDetectorId
from tracking.detectors.image_detector import ImageDetector
from tracking.detectors.tensorflow_detector import TensorflowDetector
from util import misc_util

if misc_util.module_exists("picamera"):
    print("Using Raspberry Pi camera")
    from server.camera_pi import Camera
else:
    print("Using desktop camera")
    from server.camera_desktop import Camera


class Server(object):
    """
    Server which communicates with the client library.
    """
    def __init__(self):
        self.action_to_function_dict = {'cancelRequest': self.cancel_request,
                                        'cancelRequests': self.cancel_requests,
                                        'reset': self.reset,
                                        'clearState': self.clear_state,
                                        'enableDebug': self.enable_debug,
                                        'takeScreenshot': self.take_screenshot,
                                        'setDebugCameraImage': self.set_debug_camera_image,
                                        'writeTextToFile': self.write_text_to_file,
                                        'calibrateBoard': self.calibrate_board,
                                        'calibrateHandDetection': self.calibrate_hand_detection,
                                        'initializeTiledBoardArea': self.initialize_tiled_board_area,
                                        'detectTiledBrick': self.detect_tiled_brick,
                                        'detectTiledBricks': self.detect_tiled_bricks,
                                        'detectTiledBrickMovement': self.detect_tiled_brick_movement,
                                        'setupImageDetector': self.setup_image_detector,
                                        'setupTensorflowDetector': self.setup_tensorflow_detector,
                                        'detectImages': self.detect_images,
                                        'detectNonobstructedArea': self.detect_nonobstructed_area,
                                        'detectGestures': self.detect_gestures}

        self.detectors = {}
        self.detectors_lock = RLock()

        self.threads = {}
        self.threads_lock = RLock()

    def start(self):
        thread = Thread(target=self.run, args=())
        thread.start()

    def run(self):
        print("Starting server...")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        asyncio.get_event_loop().run_until_complete(
            websockets.serve(self.handleMessage, "localhost", 9001)
        )
        asyncio.get_event_loop().run_forever()

    async def handleMessage(self, websocket, path):
        """
        Handles incoming messages.
        """
        try:
            async for data in websocket:
                #message = ("%s" % data)[:128]
                #print("Got message: %s" % message)

                json_dict = json.loads(data)

                if "action" in json_dict:
                    action = json_dict["action"]

                    result = self.handle_action(action, json_dict["payload"], websocket)

                    if result is not None:
                        await self.send_message(websocket, result=result[0], action=action, payload=result[1], request_id=result[2])

        except Exception as e:
            print("Exception in handleMessage: %s" % str(e))
            traceback.print_exc(file=sys.stdout)

    def handle_action(self, action, payload, websocket):
        if action in self.action_to_function_dict:
            return self.action_to_function_dict[action](websocket, payload)
        else:
            return "UNDEFINED_ACTION", {}, self.request_id_from_payload(payload)

    def initialize_video(self, resolution):
        with globals.get_state().camera_lock:
            if globals.get_state().get_camera() is not None:
                return
            globals.get_state().set_camera(Camera())
            globals.get_state().get_camera().start(delegate=self, resolution=resolution)

    def cancel_request(self, websocket, payload):
        """
        Cancels a request made to the server.

        id: Request ID
        """
        self.cancel_thread(request_id=payload["id"])
        return "OK", {}, self.request_id_from_payload(payload)

    def cancel_requests(self, websocket, payload):
        """
        Cancels all requests made to the server.
        """
        self.cancel_threads()
        return "OK", {}, self.request_id_from_payload(payload)

    def reset(self, websocket, payload):
        """
        Resets to initial state.

        cameraResolution: (Optional) Camera resolution in [width, height]. Default: [640, 480].
        requestId: (Optional) Request ID
        """
        resolution = payload["resolution"] if "resolution" in payload else [640, 480]

        self.cancel_threads()
        globals.reset()
        self.initialize_video(resolution)

        return "OK", {}, self.request_id_from_payload(payload)

    def clear_state(self, websocket, payload):
        """
        Cancels all requests, resets board areas, etc., but does not clear board detection and camera state.

        requestId: (Optional) Request ID
        """
        self.cancel_threads()

        globals.get_state().reset_board_areas()
        globals.get_state().reset_detectors()

        return "OK", {}, self.request_id_from_payload(payload)

    def enable_debug(self, websocket, payload):
        """
        Enables debug output.

        requestId: (Optional) Request ID
        """
        globals.get_state().debug = True

        return "OK", {}, self.request_id_from_payload(payload)

    def take_screenshot(self, websocket, payload):
        """
        Takes a screenshot and saves it to disk.

        areaId: (Optional) ID of area to detect images in
        size: (Optional) Size of image
        filename: (Optional) Screenshot filename
        requestId: (Optional) Request ID
        """
        filename = payload["filename"] if "filename" in payload else "resources/screenshots/board_{0}.png".format(time.strftime("%Y-%m-%d-%H%M%S"))
        area_id = payload["areaId"] if "areaId" in payload else None
        size = payload["size"] if "size" in payload else None
        image = None

        if area_id is not None:
            board_area = globals.get_state().get_board_area(area_id)
            if board_area is not None:
                image = board_area.area_image(size=SnapshotSize.ORIGINAL)
        else:
            camera = globals.get_state().get_camera()
            if camera is not None:
                image = camera.read()

        if image is not None:
            if size is not None:
                image = cv2.resize(image, (size[0], size[1]))
            cv2.imwrite(filename, image)
            return "OK", {}, self.request_id_from_payload(payload)

        return "ERROR", {}, self.request_id_from_payload(payload)

    def set_debug_camera_image(self, websocket, payload):
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

        return "OK", {}, self.request_id_from_payload(payload)

    def write_text_to_file(self, websocket, payload):
        """
        Writes the given text to the filesystem.

        textBase64: Base 64 encoded text
        filename: Output filename
        """
        filename = payload["filename"]
        text = base64.b64decode(bytes(payload["textBase64"], 'utf-8')).decode("utf-8", "ignore")

        with open(filename, "w") as text_file:
            text_file.write(text)

        return "OK", {}, self.request_id_from_payload(payload)

    def calibrate_board(self, websocket, payload):
        """
        Calibrates board.

        requestId: (Optional) Request ID
        """
        thread = BoardCalibrationThread(self.request_id_from_payload(payload),
                                        callback_function=lambda: self.send_thread_result(websocket,
                                                                                          thread,
                                                                                          result="OK",
                                                                                          action="calibrateBoard",
                                                                                          payload={}),
                                        timeout_function=lambda: self.send_thread_result(websocket,
                                                                                         thread,
                                                                                         result="CALIBRATION TIMEOUT",
                                                                                         action="calibrateBoard",
                                                                                         payload={}))
        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def calibrate_hand_detection(self, websocket, payload):
        """
        Calibrates hand detection.

        requestId: (Optional) Request ID
        """
        thread = HandDetectorCalibrationThread(self.request_id_from_payload(payload),
                                               callback_function=lambda: self.send_thread_result(websocket,
                                                                                                 thread,
                                                                                                 result="OK",
                                                                                                 action="calibrateHandDetection",
                                                                                                 payload={}))
        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def setup_image_detector(self, websocket, payload):
        """
        Sets up an image detector. Either imageBase64 or imagesBase64 must be used.

        detectorId: Detector ID to use as a reference
        imageBase64: (Optional) Source image to detect
        imageResolution: Image resolution to use when detecting (of type tracking.board.board_snapshot.SnapshotSize)
        minMatches: (Optional) Minimum number of matches for detection to be considered successful
        requestId: (Optional) Request ID
        """
        raw_image = base64.b64decode(payload["imageBase64"])
        raw_bytes = np.asarray(bytearray(raw_image), dtype=np.uint8)
        image = cv2.imdecode(raw_bytes, cv2.IMREAD_UNCHANGED)

        detector = ImageDetector(detector_id=payload["detectorId"], source_image=image)
        if "imageResolution" in payload:
            detector.input_resolution = payload["imageResolution"]
        if "minMatches" in payload:
            detector.min_matches = payload["minMatches"]

        globals.get_state().set_detector(detector)

        return "OK", {}, self.request_id_from_payload(payload)

    def setup_tensorflow_detector(self, websocket, payload):
        """
        Sets up a tensorflow detector.

        detectorId: Detector ID to use as a reference
        modelName: Name of model to use
        requestId: (Optional) Request ID
        """
        detector = TensorflowDetector(detector_id=payload["detectorId"], model_name=payload["modelName"])

        globals.get_state().set_detector(detector)

        return "OK", {}, self.request_id_from_payload(payload)

    def initialize_board_area(self, websocket, payload):
        """
        Initializes board area with given parameters.

        id: (Optional) Area id
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        requestId: (Optional) Request ID
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

    def initialize_tiled_board_area(self, websocket, payload):
        """
        Initializes tiled board area with given parameters.

        id: (Optional) Area id
        tileCountX: Number of horizontal tiles.
        tileCountY: Number of vertical tiles.
        x1: X1 in percentage of board size.
        y1: Y1 in percentage of board size.
        x2: X2 in percentage of board size.
        y2: Y2 in percentage of board size.
        requestId: (Optional) Request ID
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

    def remove_board_areas(self, websocket, payload):
        """
        Removes all board areas.

        requestId: (Optional) Request ID
        """
        globals.get_state().reset_board_areas()

        return "OK", {}, self.request_id_from_payload(payload)

    def remove_board_area(self, websocket, payload):
        """
        Removes the given board area.

        requestId: (Optional) Request ID
        id: Area ID.
        """
        area_id = payload["id"]

        globals.get_state().remove_board_area(area_id)

        return "OK", {}, self.request_id_from_payload(payload)

    def detect_images(self, websocket, payload):
        """
        Detects images on the board using the given detector.

        areaId: ID of area to detect images in
        detectorId: ID of detector to use
        keepRunning: (Optional) Keep returning results. Defaults to False
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        if board_area is None:
            return "BOARD_AREA_NOT_FOUND", {}, self.request_id_from_payload(payload)

        detector = globals.get_state().get_detector(payload["detectorId"])
        if detector is None:
            return "DETECTOR_NOT_FOUND", {}, self.request_id_from_payload(payload)

        thread = ImagesDetectorThread(self.request_id_from_payload(payload),
                                      detector,
                                      board_area,
                                      keep_running=payload["keepRunning"] if "keepRunning" in payload else False,
                                      callback_function=lambda result: self.send_thread_result(websocket,
                                                                                               thread,
                                                                                               result="OK",
                                                                                               action="detectImages",
                                                                                               payload=result,
                                                                                               keep_alive=thread.keep_running))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_nonobstructed_area(self, websocket, payload):
        """
        Detects nonobstructed area on the board.

        areaId: ID of area to detect nonobstructed area in
        targetSize: Size of area to fit (width, height)
        targetPosition: (Optional) Find area closest possible to target position (x, y). Defaults to [0.5, 0.5].
        currentPosition: (Optional) Excludes current position area minus half padding.
        stableTime: (Optional) Time to wait for result to stabilize. Defaults to 0.5.
        padding: (Optional) Area padding.
        keepRunning: (Optional) Keep returning results. Defaults to False
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        if board_area is None:
            return "BOARD_AREA_NOT_FOUND", {}, self.request_id_from_payload(payload)

        thread = NonobstructedAreaDetectorThread(self.request_id_from_payload(payload),
                                                 board_area,
                                                 payload["targetSize"],
                                                 target_position=payload["targetPosition"] if "targetPosition" in payload else [0.5, 0.5],
                                                 current_position=payload["currentPosition"] if "currentPosition" in payload else None,
                                                 padding=payload["padding"] if "padding" in payload else [0.0, 0.0],
                                                 stable_time=payload["stableTime"] if "stableTime" in payload else 0.5,
                                                 keep_running=payload["keepRunning"] if "keepRunning" in payload else False,
                                                 callback_function=lambda result: self.send_thread_result(websocket,
                                                                                                          thread,
                                                                                                          result="OK",
                                                                                                          action="detectNonobstructedArea",
                                                                                                          payload=result,
                                                                                                          keep_alive=thread.keep_running))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_gestures(self, websocket, payload):
        """
        Detects hand gestures.

        areaId: ID of area to detect images in
        gesture: (Optional) Gesture to detect
        keepRunning: (Optional) Keep returning results. Defaults to False
        requestId: (Optional) Request ID
        """
        board_area = globals.get_state().get_board_area(payload["areaId"])
        if board_area is None:
            return "BOARD_AREA_NOT_FOUND", {}, self.request_id_from_payload(payload)

        detector = globals.get_state().get_detector(handDetectorId)
        if detector is None:
            return "HAND_DETECTOR_NOT_INITIALIZED", {}, self.request_id_from_payload(payload)

        thread = GestureDetectorThread(self.request_id_from_payload(payload),
                                       detector,
                                       board_area,
                                       keep_running=payload["keepRunning"] if "keepRunning" in payload else False,
                                       callback_function=lambda result: self.send_thread_result(websocket,
                                                                                                thread,
                                                                                                result="OK",
                                                                                                action="detectGestures",
                                                                                                payload=result,
                                                                                                keep_alive=thread.keep_running))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_tiled_brick(self, websocket, payload):
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
            callback_function=lambda tile: self.send_thread_result(websocket,
                                                                   thread,
                                                                   result="OK",
                                                                   action="detectTiledBrick",
                                                                   payload={"tile": tile} if tile else {}))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_tiled_bricks(self, websocket, payload):
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
            callback_function=lambda tiles: self.send_thread_result(websocket,
                                                                    thread,
                                                                    result="OK",
                                                                    action="detectTiledBricks",
                                                                    payload={"tiles": tiles}))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    def detect_tiled_brick_movement(self, websocket, payload):
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
            callback_function=lambda to_position, from_position: self.send_thread_result(websocket,
                                                                                         thread,
                                                                                         result="OK",
                                                                                         action="detectTiledBrickMovement",
                                                                                         payload={"position": to_position,
                                                                                                  "initialPosition": from_position}))

        self.start_thread(self.request_id_from_payload(payload), thread)

        return None

    async def send_message(self, websocket, result, action, payload={}, request_id=None):
        """
        Sends a new message to the client.

        :param websocket Websocket instance
        :param result Result code
        :param action Client action from which the message originates
        :param payload Payload
        :param request_id: Request ID
        """
        message = {"result": result,
                   "action": action,
                   "payload": payload if payload is not None else {},
                   "requestId": request_id}

        messageJsonStr = json.dumps(message, ensure_ascii=False)
        await websocket.send(messageJsonStr)

        print("Sent message: %s" % messageJsonStr[:128])

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

    async def send_thread_result(self, websocket, thread, result, action, payload, keep_alive=False):
        if not keep_alive:
            self.cancel_thread(thread.request_id)
        await self.send_message(websocket, result, action, payload, thread.request_id)

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

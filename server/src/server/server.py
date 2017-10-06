from __future__ import with_statement

import json
import sys
import time
import traceback
import base64
import cv2
import numpy as np
from threading import Thread
from threading import RLock
from random import randint

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

from server import globals
from server.board_detector_thread import BoardDetectorThread
from util import misc_util

from tracking.detectors.tensorflow_detector import TensorflowDetector

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

        self.action_to_function_dict = {'enableDebug': self.enable_debug,
                                        'takeScreenshot': self.take_screenshot,
                                        'reset': self.reset,
                                        'calibrateBoard': self.calibrate_board,
                                        'setupTensorflowDetector': self.setup_tensorflow_detector}

        self.detectors = {}
        self.detectors_lock = RLock()

        random_id_lock = RLock()

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
            globals.get_state().get_camera().start(resolution)

    def reset(self, payload):
        """
        Resets the board.

        requestId: (Optional) Request ID
        cameraResolution: (Optional) Camera resolution in [width, height]. Default: [640, 480].
        """
        resolution = payload["resolution"] if "resolution" in payload else [640, 480]

        self.initialize_video(resolution)

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
        with globals.get_state().camera_lock:
            camera = globals.get_state().get_camera()
            if camera is not None:
                image = camera.read()
                if image is not None:
                    filename = payload["filename"] if "filename" in payload else\
                        "debug/board_{0}.png".format(time.strftime("%Y-%m-%d-%H%M%S"))
                    cv2.imwrite(filename, image)
                    return "OK", {}, self.request_id_from_payload(payload)

        return "CAMERA_NOT_READY", {}, self.request_id_from_payload(payload)

    def calibrate_board(self, payload):
        """
        Calibrates board.

        requestId: (Optional) Request ID
        """
        BoardDetectorThread(callback_function=lambda: self.send_message(result="OK",
                                                                        action="calibrateBoard",
                                                                        payload={},
                                                                        request_id=self.request_id_from_payload(payload)),
                            timeout_function=lambda: self.send_message(result="CALIBRATION TIMEOUT",
                                                                       action="calibrateBoard",
                                                                       payload={},
                                                                       request_id=self.request_id_from_payload(payload))
                            ).start()

        return None

    def setup_tensorflow_detector(self, payload):
        """
        Sets up a tensorflow detector.

        detectorId: Detector ID to use as a reference
        modelName: Name of model to use
        requestId: (Optional) Request ID
        """
        detector = TensorflowDetector(detector_id=payload["detectorId"], model_name=payload["modelName"])

        with self.detectors_lock:
            self.detectors[payload["detectorId"]] = detector

        return "OK", {}, self.request_id_from_payload(payload)

    def send_message(self, result, action, payload={}, request_id=None):
        """
        Sends a new message to the client.

        :param result Result code
        :param action Client action from which the message originates
        :param payload Payload
        :param request_id: Request ID. If none given, random ID is generated
        """
        message = {"result": result,
                   "action": action,
                   "payload": payload,
                   "requestId": request_id if request_id is not None else self.random_id()}
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


def start_server():
    print("Starting server...")
    server = SimpleWebSocketServer('', 9001, Server)
    server.serveforever()

var Client;

Client = (function() {
  function Client(port) {
    this.port = port != null ? port : 9001;
    this.debug_textField = null;
    this.debug_log = [];
    this.socket = void 0;
    this.socketOpen = false;
    this.requests = {};
    this.boardCalibrationDiv = void 0;
    this.boardAreaId_fullImage = -2;
    this.boardAreaId_fullBoard = -1;
  }

  "connect: Establishes a websocket connection to the server.\n\nTakes two callback parameters.\nonSocketOpen: onSocketOpen() is called when socket connection has been established.\nonMessage: onMessage(json) is called with json response from server. The json consists of the following mandatory fields:\n  - result: Fx. \"OK\" or \"BOARD_NOT_RECOGNIZED\"\n  - action: Action which message is a reply to, fx. \"reset\" or \"initializeBoard\"\n  - payload: The actual payload. Varies from response to response.\n  - requestId: Unique request id for which this is a response to.";

  Client.prototype.connect = function(onSocketOpen, onMessage) {
    this.disconnect();
    this.socket = new WebSocket("ws://localhost:" + this.port + "/");
    this.socket.onopen = (function(_this) {
      return function(event) {
        return onSocketOpen();
      };
    })(this);
    return this.socket.onmessage = (function(_this) {
      return function(event) {
        var json;
        json = JSON.parse(event.data);
        console.log(json);
        _this.performCompletionCallbackForRequest(json);
        onMessage(json);
        if (_this.debug_textField != null) {
          _this.debug_log.splice(0, 0, JSON.stringify(json));
          return _this.debug_textField.text = _this.debug_log.slice(0, 6).join("<br/>");
        }
      };
    })(this);
  };

  "disconnect: Disconnects from the server.";

  Client.prototype.disconnect = function() {
    if (this.socket != null) {
      this.socket.close();
      return this.socket = void 0;
    }
  };

  "enableDebug: Enables server debug.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.enableDebug = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    this.sendMessage("enableDebug", {
      "requestId": requestId
    });
    return requestId;
  };

  "cancelRequest: Cancels a request.\n\nid: Request ID of request to cancel.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.cancelRequest = function(id, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("cancelRequest", {
      "id": id,
      "requestId": requestId
    });
  };

  "cancelRequests: Cancels all requests made to server.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.cancelRequests = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("cancelRequests", {
      "requestId": requestId
    });
  };

  "reset: Resets the server to initial state.\n\nresolution: (Optional) Camera resolution to use in form [width, height].\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.reset = function(resolution, completionCallback) {
    var json, requestId;
    if (resolution == null) {
      resolution = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    this.requests = {};
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    if (resolution != null) {
      json["resolution"] = resolution;
    }
    this.sendMessage("reset", json);
    return requestId;
  };

  "clearState: Cancels all requests, resets board areas, etc., but does not clear board detection and camera state.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.clearState = function(completionCallback) {
    var json, requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    this.requests = {};
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    this.sendMessage("clearState", json);
    return requestId;
  };

  "takeScreenshot: Takes and stores a screenshot from the camera.\n\nfilename: (Optional) Screenshot filename.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.takeScreenshot = function(filename, completionCallback) {
    var json, requestId;
    if (filename == null) {
      filename = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    if (filename != null) {
      json["filename"] = filename;
    }
    this.sendMessage("takeScreenshot", json);
    return requestId;
  };

  "setDebugCameraImage: Uploads debug camera image.\n\nimage: Debug image.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.setDebugCameraImage = function(image, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    ClientUtil.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "imageBase64": base64Image
        };
        return _this.sendMessage("setDebugCameraImage", json);
      };
    })(this));
    return requestId;
  };

  "setDebugCameraCanvas: Uploads debug camera canvas.\n\ncanvas: Debug canvas.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.setDebugCameraCanvas = function(canvas, completionCallback) {
    var base64Image, dataURL, json, requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    dataURL = canvas.toDataURL("image/png");
    base64Image = dataURL.replace(/^.*;base64,/, "");
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "imageBase64": base64Image
    };
    this.sendMessage("setDebugCameraImage", json);
    return requestId;
  };

  "calibrateBoard: Calibrates the board.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.calibrateBoard = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback((function(_this) {
      return function() {
        return _this.hideBoardCalibratorImage(completionCallback);
      };
    })(this));
    this.showBoardCalibratorImage((function(_this) {
      return function() {
        var json;
        json = {
          "requestId": requestId
        };
        return _this.sendMessage("calibrateBoard", json);
      };
    })(this));
    return requestId;
  };

  Client.prototype.showBoardCalibratorImage = function(completionCallback) {
    var image;
    this.boardCalibrationDiv = document.createElement('div');
    this.boardCalibrationDiv.style.background = '#000000';
    this.boardCalibrationDiv.style.position = 'fixed';
    this.boardCalibrationDiv.style.left = '0%';
    this.boardCalibrationDiv.style.top = '0%';
    this.boardCalibrationDiv.style.width = '100%';
    this.boardCalibrationDiv.style.height = '100%';
    this.boardCalibrationDiv.style.opacity = '0';
    this.boardCalibrationDiv.style.transition = 'opacity 1s linear';
    this.boardCalibrationDiv.style.zIndex = 1000;
    document.body.appendChild(this.boardCalibrationDiv);
    image = document.createElement('img');
    image.src = 'assets/images/calibration/board_calibration.png';
    image.style.objectFit = 'contain';
    image.style.position = 'fixed';
    image.style.left = '0%';
    image.style.top = '0%';
    image.style.width = '100%';
    image.style.height = '100%';
    this.boardCalibrationDiv.appendChild(image);
    setTimeout((function(_this) {
      return function() {
        return _this.boardCalibrationDiv.style.opacity = '1';
      };
    })(this), 100);
    return setTimeout((function(_this) {
      return function() {
        if (completionCallback != null) {
          return completionCallback();
        }
      };
    })(this), 1100);
  };

  Client.prototype.hideBoardCalibratorImage = function(completionCallback) {
    this.boardCalibrationDiv.style.opacity = '0';
    return setTimeout((function(_this) {
      return function() {
        document.body.removeChild(_this.boardCalibrationDiv);
        _this.boardCalibrationDiv = void 0;
        if (completionCallback != null) {
          return completionCallback();
        }
      };
    })(this), 1000);
  };

  "calibrateHandDetection: Calibrates the hand detection algorithm by presenting user with touch point.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.calibrateHandDetection = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback((function(_this) {
      return function() {
        return _this.hideHandDetectionCalibratorImage(completionCallback);
      };
    })(this));
    this.showHandDetectionCalibratorImage((function(_this) {
      return function() {
        var json;
        json = {
          "requestId": requestId
        };
        return _this.sendMessage("calibrateHandDetection", json);
      };
    })(this));
    return requestId;
  };

  Client.prototype.showHandDetectionCalibratorImage = function(completionCallback) {
    var image;
    this.handDetectionCalibrationDiv = document.createElement('div');
    this.handDetectionCalibrationDiv.style.background = '#000000';
    this.handDetectionCalibrationDiv.style.position = 'fixed';
    this.handDetectionCalibrationDiv.style.left = '0%';
    this.handDetectionCalibrationDiv.style.top = '0%';
    this.handDetectionCalibrationDiv.style.width = '100%';
    this.handDetectionCalibrationDiv.style.height = '100%';
    this.handDetectionCalibrationDiv.style.opacity = '0';
    this.handDetectionCalibrationDiv.style.transition = 'opacity 1s linear';
    this.handDetectionCalibrationDiv.style.zIndex = 1000;
    document.body.appendChild(this.handDetectionCalibrationDiv);
    image = document.createElement('img');
    image.src = 'assets/images/calibration/hand_calibration.png';
    image.style.objectFit = 'contain';
    image.style.position = 'fixed';
    image.style.left = '0%';
    image.style.top = '0%';
    image.style.width = '100%';
    image.style.height = '100%';
    this.handDetectionCalibrationDiv.appendChild(image);
    setTimeout((function(_this) {
      return function() {
        return _this.handDetectionCalibrationDiv.style.opacity = '1';
      };
    })(this), 100);
    return setTimeout((function(_this) {
      return function() {
        if (completionCallback != null) {
          return completionCallback();
        }
      };
    })(this), 1100);
  };

  Client.prototype.hideHandDetectionCalibratorImage = function(completionCallback) {
    this.handDetectionCalibrationDiv.style.transition = 'opacity 0.3s linear';
    this.handDetectionCalibrationDiv.style.opacity = '0';
    return setTimeout((function(_this) {
      return function() {
        document.body.removeChild(_this.handDetectionCalibrationDiv);
        _this.handDetectionCalibrationDiv = void 0;
        if (completionCallback != null) {
          return completionCallback();
        }
      };
    })(this), 1000);
  };

  "setupImageDetector: Sets up an image detector.\n\ndetectorId: Detector ID to use as a reference.\nsourceImage: Image to detect\nminMatches: (Optional) Minimum number of matches for detection to be considered successful\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.setupImageDetector = function(detectorId, sourceImage, minMatches, completionCallback) {
    var requestId;
    if (minMatches == null) {
      minMatches = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    ClientUtil.convertImageToDataURL(sourceImage, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "detectorId": detectorId,
          "imageBase64": base64Image
        };
        if (minMatches != null) {
          json["minMatches"] = minMatches;
        }
        return _this.sendMessage("setupImageDetector", json);
      };
    })(this));
    return requestId;
  };

  "setupTensorflowDetector: Sets up a tensorflow detector.\n\ndetectorId: Detector ID to use as a reference.\nmodelName: Name of model to use.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.setupTensorflowDetector = function(detectorId, modelName, completionCallback) {
    var json, requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "detectorId": detectorId,
      "modelName": modelName
    };
    this.sendMessage("setupTensorflowDetector", json);
    return requestId;
  };

  "initializeBoardArea: Initializes an area of the board. Is used to search for markers in a specific region, etc.\n\nx1: Left coordinate in percentage [0..1] of board width.\ny1: Top in percentage [0..1] of board height.\nx2: Right coordinate in percentage [0..1] of board width.\ny2: Bottom coordinate in percentage [0..1] of board height.\nareaId: (Optional) Area ID to use. If none is given, a random area ID is generated and returned from the server.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeBoardArea = function(x1, y1, x2, y2, areaId, completionCallback) {
    var json, requestId;
    if (x1 == null) {
      x1 = 0.0;
    }
    if (y1 == null) {
      y1 = 0.0;
    }
    if (x2 == null) {
      x2 = 1.0;
    }
    if (y2 == null) {
      y2 = 1.0;
    }
    if (areaId == null) {
      areaId = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "x1": x1,
      "y1": y1,
      "x2": x2,
      "y2": y2
    };
    if (areaId != null) {
      json["id"] = areaId;
    }
    this.sendMessage("initializeBoardArea", json);
    return requestId;
  };

  "initializeTiledBoardArea: Initializes a tiled board area, ie. an area which is divided into equally sized tiles.\n\ntileCountX: Number of tiles horizontally.\ntileCountY: Number of tiles vertically.\nx1: Left coordinate in percentage [0..1] of board width.\ny1: Top in percentage [0..1] of board height.\nx2: Right coordinate in percentage [0..1] of board width.\ny2: Bottom coordinate in percentage [0..1] of board height.\nareaId: (Optional) Area ID to use. If none is given, a random area ID is generated and returned from the server.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeTiledBoardArea = function(tileCountX, tileCountY, x1, y1, x2, y2, areaId, completionCallback) {
    var json, requestId;
    if (x1 == null) {
      x1 = 0.0;
    }
    if (y1 == null) {
      y1 = 0.0;
    }
    if (x2 == null) {
      x2 = 1.0;
    }
    if (y2 == null) {
      y2 = 1.0;
    }
    if (areaId == null) {
      areaId = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "tileCountX": tileCountX,
      "tileCountY": tileCountY,
      "x1": x1,
      "y1": y1,
      "x2": x2,
      "y2": y2
    };
    if (areaId != null) {
      json["id"] = areaId;
    }
    this.sendMessage("initializeTiledBoardArea", json);
    return requestId;
  };

  "removeBoardAreas: Removes all board areas at server end. Maintaining a board area requires some server processing, so\nit is good practice to remove them when not used any longer.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeBoardAreas = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    this.sendMessage("removeBoardAreas", {
      "requestId": requestId
    });
    return requestId;
  };

  "removeBoardArea: Removes a specific board area at server end. Maintaining a board area requires some server processing, so\nit is good practice to remove them when not used any longer.\n\nareaId: Board area ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeBoardArea = function(areaId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    this.sendMessage("removeBoardArea", {
      "requestId": requestId,
      "id": areaId
    });
    return requestId;
  };

  "removeMarkers: Removes all markers from the server.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeMarkers = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    this.sendMessage("removeMarkers", {
      "requestId": requestId
    });
    return requestId;
  };

  "removeMarker: Removes a specific marker from the server.\n\nmarkerId: Marker ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeMarker = function(markerId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    this.sendMessage("removeMarker", {
      "requestId": requestId,
      "id": markerId
    });
    return requestId;
  };

  "detectImages: Detect images in the given area.\n\nareaId: Area ID of tiled board area.\ndetectorId: The ID of the detector to use.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.detectImages = function(areaId, detectorId, keepRunning, completionCallback) {
    var json, requestId;
    if (keepRunning == null) {
      keepRunning = false;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "detectorId": detectorId
    };
    if (keepRunning != null) {
      json["keepRunning"] = keepRunning;
    }
    this.sendMessage("detectImages", json);
    return requestId;
  };

  "detectNonobstructedArea: Detects nonobstructed area on the board.\n\nareaId: ID of area to detect nonobstructed area in.\ntargetSize: Size of area to fit (width, height).\ntargetPoint: (Optional) Find area closest possible to target point (x, y). Defaults to [0.5, 0.5].\nkeepRunning: (Optional) Keep returning results. Defaults to False.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.detectNonobstructedArea = function(areaId, targetSize, targetPoint, keepRunning, completionCallback) {
    var json, requestId;
    if (targetPoint == null) {
      targetPoint = void 0;
    }
    if (keepRunning == null) {
      keepRunning = false;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "targetSize": targetSize
    };
    if (keepRunning != null) {
      json["keepRunning"] = keepRunning;
    }
    if (targetPoint != null) {
      json["targetPoint"] = targetPoint;
    }
    this.sendMessage("detectNonobstructedArea", json);
    return requestId;
  };

  "detectTiledBrick: Returns the position of a brick among the given possible positions in a tiled area.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\ntargetPosition: (Optional) Target position.\nwaitForPosition: (Optional) If true, waits for brick to be detected, else returns immediately.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.detectTiledBrick = function(areaId, validPositions, targetPosition, waitForPosition, completionCallback) {
    var json, requestId;
    if (targetPosition == null) {
      targetPosition = void 0;
    }
    if (waitForPosition == null) {
      waitForPosition = false;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    };
    if (targetPosition != null) {
      json["targetPosition"] = targetPosition;
    }
    if (waitForPosition != null) {
      json["waitForPosition"] = waitForPosition;
    }
    this.sendMessage("detectTiledBrick", json);
    return requestId;
  };

  "detectTiledBricks: Returns the positions of bricks among the given possible positions in a tiled area.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\nwaitForPosition: (Optional) If true, waits for brick to be detected, else returns immediately.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.detectTiledBricks = function(areaId, validPositions, completionCallback) {
    var json, requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    };
    if (typeof waitForPosition !== "undefined" && waitForPosition !== null) {
      json["waitForPosition"] = waitForPosition;
    }
    this.sendMessage("detectTiledBricks", json);
    return requestId;
  };

  "detectTiledBrickMovement: Keeps searching for a brick in the given positions in a tiled area and returns\nthe position when found.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\ninitialPosition: (Optional) Initial position.\ntargetPosition: (Optional) Target position.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.detectTiledBrickMovement = function(areaId, validPositions, initialPosition, targetPosition, completionCallback) {
    var json, requestId;
    if (initialPosition == null) {
      initialPosition = void 0;
    }
    if (targetPosition == null) {
      targetPosition = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    };
    if (initialPosition != null) {
      json["initialPosition"] = initialPosition;
    }
    if (targetPosition != null) {
      json["targetPosition"] = targetPosition;
    }
    this.sendMessage("detectTiledBrickMovement", json);
    return requestId;
  };

  Client.prototype.sendMessage = function(action, payload) {
    var message;
    message = {
      "action": action,
      "payload": payload
    };
    this.socket.send(JSON.stringify(message));
    return payload["requestId"];
  };

  Client.prototype.addCompletionCallback = function(completionCallback) {
    var requestId;
    if (completionCallback != null) {
      requestId = ClientUtil.randomRequestId();
      this.requests[requestId] = {
        "timestamp": Date.now(),
        "completionCallback": completionCallback
      };
      return requestId;
    } else {
      return void 0;
    }
  };

  Client.prototype.performCompletionCallbackForRequest = function(json) {
    var action, completionCallback, payload, requestDict, requestId, shouldRemoveRequest;
    action = json["action"];
    requestId = json["requestId"];
    payload = json["payload"];
    if ((action == null) || (requestId == null) || (payload == null)) {
      return;
    }
    requestDict = this.requests[requestId];
    if (requestDict == null) {
      return;
    }
    completionCallback = requestDict["completionCallback"];
    shouldRemoveRequest = completionCallback(action, payload);
    if ((shouldRemoveRequest == null) || shouldRemoveRequest) {
      return delete this.requests[requestId];
    }
  };

  return Client;

})();

//# sourceMappingURL=clientLibrary.js.map

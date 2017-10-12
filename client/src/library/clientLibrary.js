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
    return this.sendMessage("enableDebug", {
      "requestId": requestId
    });
  };

  "reset: Resets the server.\n\nresolution: (Optional) Camera resolution to use in form [width, height].\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

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
    return this.sendMessage("reset", json);
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
    return this.sendMessage("takeScreenshot", json);
  };

  "setDebugCameraImage: Uploads debug camera image.\n\nimage: Source marker image.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.setDebugCameraImage = function(image, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return ClientUtil.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "imageBase64": base64Image
        };
        return _this.sendMessage("setDebugCameraImage", json);
      };
    })(this));
  };

  "calibrateBoard: Calibrates the board.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.calibrateBoard = function(completionCallback) {
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    return this.showBoardCalibratorImage((function(_this) {
      return function() {
        var json, requestId;
        requestId = _this.addCompletionCallback(function() {
          return _this.hideBoardCalibratorImage(completionCallback);
        });
        json = {
          "requestId": requestId
        };
        return _this.sendMessage("calibrateBoard", json);
      };
    })(this));
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
    image.src = 'assets/images/board_calibration.png';
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
    })(this), 1);
    return setTimeout((function(_this) {
      return function() {
        if (completionCallback != null) {
          return completionCallback();
        }
      };
    })(this), 1000);
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
    return this.sendMessage("setupTensorflowDetector", json);
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
    return this.sendMessage("initializeBoardArea", json);
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
    return this.sendMessage("initializeTiledBoardArea", json);
  };

  "removeBoardAreas: Removes all board areas at server end. Maintaining a board area requires some server processing, so\nit is good practice to remove them when not used any longer.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeBoardAreas = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeBoardAreas", {
      "requestId": requestId
    });
  };

  "removeBoardArea: Removes a specific board area at server end. Maintaining a board area requires some server processing, so\nit is good practice to remove them when not used any longer.\n\nareaId: Board area ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeBoardArea = function(areaId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeBoardArea", {
      "requestId": requestId,
      "id": areaId
    });
  };

  "removeMarkers: Removes all markers from the server.\n\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeMarkers = function(completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeMarkers", {
      "requestId": requestId
    });
  };

  "removeMarker: Removes a specific marker from the server.\n\nmarkerId: Marker ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.removeMarker = function(markerId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("removeMarker", {
      "requestId": requestId,
      "id": markerId
    });
  };

  "requestTiledBrickPosition: Returns the position of a brick among the given possible positions in a tiled area.\n\nareaId: Area ID of tiled board area.\ndetectorId: The ID of the detector to use.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.detectImages = function(areaId, detectorId, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("detectImages", {
      "requestId": requestId,
      "areaId": areaId,
      "detectorId": detectorId
    });
  };

  "requestTiledBrickPosition: Returns the position of a brick among the given possible positions in a tiled area.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestTiledBrickPosition = function(areaId, validPositions, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("requestBrickPosition", {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    });
  };

  "requestTiledBrickPositions: Returns the positions of bricks among the given possible positions in a tiled area.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestTiledBrickPosition = function(areaId, validPositions, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.sendMessage("requestBrickPositions", {
      "requestId": requestId,
      "areaId": areaId,
      "validPositions": validPositions
    });
  };

  "reportBackWhenBrickFoundAtAnyOfPositions: Keeps searching for a brick in the given positions in a tiled area and returns\nthe position when found.\n\nareaId: Area ID of tiled board area.\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.reportBackWhenBrickFoundAtAnyOfPositions = function(areaId, validPositions, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
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
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json);
  };

  "reportBackWhenBrickMovedToAnyOfPositions: Reports back when brick has moved to any of the given positions in a tiled area.\n\nareaId: Area ID of tiled board area.\ninitialPosition: Position where brick is currently located in form [x, y].\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...].\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.reportBackWhenBrickMovedToAnyOfPositions = function(areaId, initialPosition, validPositions, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "initialPosition": initialPosition,
      "validPositions": validPositions
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json);
  };

  "reportBackWhenBrickMovedToPosition: Reports back when brick has moved to the given position in a tiled area.\n\nposition: Target position to trigger the callback in form [x, y].\nvalidPositions: A list of valid positions in the form [[x, y], [x, y], ...] where the brick could be located.\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.reportBackWhenBrickMovedToPosition = function(areaId, position, validPositions, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "position": position,
      "validPositions": validPositions
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenBrickMovedToPosition", json);
  };

  "initializeImageMarker: Initializes an image marker.\n\nmarkerId: Marker ID.\nimage: Source marker image.\nminMatches: (Optional) Minimum number of matches required. (8 is recommended minimum).\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeImageMarker = function(markerId, image, minMatches, completionCallback) {
    var requestId;
    if (minMatches == null) {
      minMatches = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "markerId": markerId,
          "imageBase64": base64Image
        };
        if (minMatches != null) {
          json["minMatches"] = minMatches;
        }
        return _this.sendMessage("initializeImageMarker", json);
      };
    })(this));
  };

  "initializeHaarClassifierMarker: Initializes a Haar Classifier with the given filename.\n\nmarkerId: Marker ID.\nfilename: Filename of Haar Classifier.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeHaarClassifierMarker = function(markerId, filename, completionCallback) {
    var requestId;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.readFileBase64(filename, (function(_this) {
      return function(base64Data) {
        return _this.sendMessage("initializeHaarClassifierMarker", {
          "requestId": requestId,
          "markerId": markerId,
          "dataBase64": base64Data
        });
      };
    })(this));
  };

  "initializeShapeMarkerWithContour: Initializes a shape marker with the given contour.\n\nmarkerId: Marker ID.\ncontour: Contour of shape in form [[x, y], [x, y], ...].\nminArea: (Optional) Minimum area in percentage [0..1] of board area image size.\nmaxArea: (Optional) Maximum area in percentage [0..1] of board area image size.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeShapeMarkerWithContour = function(markerId, contour, minArea, maxArea, completionCallback) {
    var json, requestId;
    if (minArea == null) {
      minArea = void 0;
    }
    if (maxArea == null) {
      maxArea = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "markerId": markerId,
      "shape": contour
    };
    if (minArea != null) {
      json["minArea"] = minArea;
    }
    if (maxArea != null) {
      json["maxArea"] = maxArea;
    }
    return this.sendMessage("initializeShapeMarker", json);
  };

  "initializeShapeMarkerWithImage: Initializes a shape marker with shape extracted from the given image.\n\nmarkerId: Marker ID.\nimage: Marker image. Must be black contour on white image.\nminArea: (Optional) Minimum area in percentage [0..1] of board area image size.\nmaxArea: (Optional) Maximum area in percentage [0..1] of board area image size.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeShapeMarkerWithImage = function(markerId, image, minArea, maxArea, completionCallback) {
    var requestId;
    if (minArea == null) {
      minArea = void 0;
    }
    if (maxArea == null) {
      maxArea = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    return this.convertImageToDataURL(image, (function(_this) {
      return function(base64Image) {
        var json;
        json = {
          "requestId": requestId,
          "markerId": markerId,
          "imageBase64": base64Image
        };
        if (minArea != null) {
          json["minArea"] = minArea;
        }
        if (maxArea != null) {
          json["maxArea"] = maxArea;
        }
        return _this.sendMessage("initializeShapeMarker", json);
      };
    })(this));
  };

  "initializeArUcoMarker: Initializes an ArUco marker with given properties.\n\nmarkerId: Marker ID.\narUcoMarkerId: ArUco marker ID. Number in range [0..dictionarySize-1].\nmarkerSize: Marker size. Any of 4, 5, 6, 7.\ndictionarySize: (Optional) Dictionary size. Any of 100, 250, 1000.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.initializeArUcoMarker = function(markerId, arUcoMarkerId, markerSize, dictionarySize, completionCallback) {
    var json, requestId;
    if (dictionarySize == null) {
      dictionarySize = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "markerId": markerId,
      "arUcoMarkerId": arUcoMarkerId,
      "markerSize": markerSize
    };
    if (dictionarySize != null) {
      json["dictionarySize"] = dictionarySize;
    }
    return this.sendMessage("initializeArUcoMarker", json);
  };

  "reportBackWhenMarkerFound: Keeps searching for marker and reports back when found.\n\nareaId: Area ID to search for marker in.\nmarkerId: Marker ID to search for.\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.reportBackWhenMarkerFound = function(areaId, markerId, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerId": markerId
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("reportBackWhenMarkerFound", json);
  };

  "requestMarkers: Returns which markers among the given list of markers that are currently visible in the given area.\n\nareaId: Area ID to search for markers in.\nmarkerIds: Marker IDs to search for in form [id, id, ...].\nid: (Optional) Reporter ID.\nstabilityLevel: (Optional) Minimum stability level of board area before returning result.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestMarkers = function(areaId, markerIds, id, stabilityLevel, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (stabilityLevel == null) {
      stabilityLevel = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerIds": markerIds
    };
    if (id != null) {
      json["id"] = id;
    }
    if (stabilityLevel != null) {
      json["stabilityLevel"] = stabilityLevel;
    }
    return this.sendMessage("requestMarkers", json);
  };

  "requestArUcoMarkers: Returns a list of all visible ArUco markers of given size in given area.\n\nareaId: Area ID to search for markers in.\nmarkerSize: ArUco marker size. Any of 4, 5, 6, 7.\nid: (Optional) Reporter ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestArUcoMarkers = function(areaId, markerSize, id, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerSize": markerSize
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("requestArUcoMarkers", json);
  };

  "startTrackingMarker: Continously tracks a marker in the given area. Continously reports back.\n\nareaId: Area ID to track marker in.\nmarkerId: Marker ID to track.\nid: (Optional) Reporter ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.startTrackingMarker = function(areaId, markerId, id, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId,
      "markerId": markerId
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("startTrackingMarker", json);
  };

  "requestContours: Returns a list of all visible contours in given area.\n\nareaId: Area ID to search for markers in.\napproximation: (Optional) Contour approximation constant. This is the maximum distance between the original curve and its approximation.\nid: (Optional) Reporter ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestContours = function(areaId, approximation, id, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId,
      "areaId": areaId
    };
    if (id != null) {
      json["id"] = id;
    }
    if (approximation != null) {
      json["approximation"] = approximation;
    }
    return this.sendMessage("requestContours", json);
  };

  "requestHumanHeadPositions: Returns human head positions as a 3D vector with (0, 0, 0) representing board center.\n\nid: (Optional) Reporter ID.\ncompletionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.";

  Client.prototype.requestHumanHeadPositions = function(id, completionCallback) {
    var json, requestId;
    if (id == null) {
      id = void 0;
    }
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    requestId = this.addCompletionCallback(completionCallback);
    json = {
      "requestId": requestId
    };
    if (id != null) {
      json["id"] = id;
    }
    return this.sendMessage("requestHumanHeadPositions", json);
  };

  Client.prototype.sendMessage = function(action, payload) {
    var message;
    message = {
      "action": action,
      "payload": payload
    };
    return this.socket.send(JSON.stringify(message));
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

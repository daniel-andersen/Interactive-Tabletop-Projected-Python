class Client

    constructor: (@port = 9001) ->
        @debug_textField = null
        @debug_log = []
        @socket = undefined

        @socketOpen = false

        @requests = {}

        @boardCalibrationDiv = undefined

        @boardAreaId_fullImage = -2
        @boardAreaId_fullBoard = -1



    """
    connect: Establishes a websocket connection to the server.

    Takes two callback parameters.
    onSocketOpen: onSocketOpen() is called when socket connection has been established.
    onMessage: onMessage(json) is called with json response from server. The json consists of the following mandatory fields:
      - result: Fx. "OK" or "BOARD_NOT_RECOGNIZED"
      - action: Action which message is a reply to, fx. "reset" or "initializeBoard"
      - payload: The actual payload. Varies from response to response.
      - requestId: Unique request id for which this is a response to.
    """
    connect: (onSocketOpen, onMessage) ->
        @disconnect()

        @socket = new WebSocket("ws://localhost:" + @port + "/")

        @socket.onopen = (event) =>
            onSocketOpen()

        @socket.onmessage = (event) =>
            json = JSON.parse(event.data)
            console.log(json)
            @performCompletionCallbackForRequest(json)

            onMessage(json)

            if @debug_textField?
                @debug_log.splice(0, 0, JSON.stringify(json))
                @debug_textField.text = @debug_log[..5].join("<br/>")

    """
    disconnect: Disconnects from the server.
    """
    disconnect: ->
        if @socket?
            @socket.close()
            @socket = undefined

    """
    enableDebug: Enables server debug.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    enableDebug: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("enableDebug", {
            "requestId": requestId
        })
        return requestId

    """
    cancelRequest: Cancels a request.

    id: Request ID of request to cancel.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    cancelRequest: (id, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("cancelRequest", {
            "id": id,
            "requestId": requestId
        })

    """
    cancelRequests: Cancels all requests made to server.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    cancelRequests: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("cancelRequests", {
            "requestId": requestId
        })

    """
    reset: Resets the server to initial state.

    resolution: (Optional) Camera resolution to use in form [width, height].
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    reset: (resolution = undefined, completionCallback = undefined) ->
        @requests = {}
        requestId = @addCompletionCallback(completionCallback)
        json = {"requestId": requestId}
        if resolution? then json["resolution"] = resolution
        @sendMessage("reset", json)
        return requestId

    """
    clearState: Cancels all requests, resets board areas, etc., but does not clear board detection and camera state.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    clearState: (completionCallback = undefined) ->
        @requests = {}
        requestId = @addCompletionCallback(completionCallback)
        json = {"requestId": requestId}
        @sendMessage("clearState", json)
        return requestId

    """
    takeScreenshot: Takes and stores a screenshot from the camera.

    filename: (Optional) Screenshot filename.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    takeScreenshot: (filename = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {"requestId": requestId}
        if filename? then json["filename"] = filename
        @sendMessage("takeScreenshot", json)
        return requestId

    """
    setDebugCameraImage: Uploads debug camera image.

    image: Debug image.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    setDebugCameraImage: (image, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        ClientUtil.convertImageToDataURL(image, (base64Image) =>
            json = {
                "requestId": requestId,
                "imageBase64": base64Image
            }
            @sendMessage("setDebugCameraImage", json)
        )
        return requestId

    """
    setDebugCameraCanvas: Uploads debug camera canvas.

    canvas: Debug canvas.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    setDebugCameraCanvas: (canvas, completionCallback = undefined) ->
        dataURL = canvas.toDataURL("image/png")
        base64Image = dataURL.replace(/^.*;base64,/, "")

        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "imageBase64": base64Image
        }
        @sendMessage("setDebugCameraImage", json)
        return requestId

    """
    calibrateBoard: Calibrates the board.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    calibrateBoard: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(() => @hideBoardCalibratorImage(completionCallback))
        @showBoardCalibratorImage(() =>
            json = {"requestId": requestId}
            @sendMessage("calibrateBoard", json)
        )
        return requestId

    showBoardCalibratorImage: (completionCallback) ->
        @boardCalibrationDiv = document.createElement('div')
        @boardCalibrationDiv.style.background = '#000000'
        @boardCalibrationDiv.style.position = 'fixed'
        @boardCalibrationDiv.style.left = '0%'
        @boardCalibrationDiv.style.top = '0%'
        @boardCalibrationDiv.style.width = '100%'
        @boardCalibrationDiv.style.height = '100%'
        @boardCalibrationDiv.style.opacity = '0'
        @boardCalibrationDiv.style.transition = 'opacity 1s linear'
        @boardCalibrationDiv.style.zIndex = 1000
        document.body.appendChild(@boardCalibrationDiv)

        image = document.createElement('img')
        image.src = 'assets/images/calibration/board_calibration.png'
        image.style.objectFit = 'contain'
        image.style.position = 'fixed'
        image.style.left = '0%'
        image.style.top = '0%'
        image.style.width = '100%'
        image.style.height = '100%'
        @boardCalibrationDiv.appendChild(image)

        setTimeout(() =>
            @boardCalibrationDiv.style.opacity = '1'
        , 100)

        setTimeout(() =>
            if completionCallback?
                completionCallback()
        , 1100)

    hideBoardCalibratorImage: (completionCallback) ->
        @boardCalibrationDiv.style.opacity = '0'

        setTimeout(() =>
            document.body.removeChild(@boardCalibrationDiv)
            @boardCalibrationDiv = undefined
            if completionCallback?
                completionCallback()
        , 1000)

    """
    calibrateHandDetection: Calibrates the hand detection algorithm by presenting user with touch point.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    calibrateHandDetection: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(() => @hideHandDetectionCalibratorImage(completionCallback))
        @showHandDetectionCalibratorImage(() =>
            json = {"requestId": requestId}
            @sendMessage("calibrateHandDetection", json)
        )
        return requestId

    showHandDetectionCalibratorImage: (completionCallback) ->
        @handDetectionCalibrationDiv = document.createElement('div')
        @handDetectionCalibrationDiv.style.background = '#000000'
        @handDetectionCalibrationDiv.style.position = 'fixed'
        @handDetectionCalibrationDiv.style.left = '0%'
        @handDetectionCalibrationDiv.style.top = '0%'
        @handDetectionCalibrationDiv.style.width = '100%'
        @handDetectionCalibrationDiv.style.height = '100%'
        @handDetectionCalibrationDiv.style.opacity = '0'
        @handDetectionCalibrationDiv.style.transition = 'opacity 1s linear'
        @handDetectionCalibrationDiv.style.zIndex = 1000
        document.body.appendChild(@handDetectionCalibrationDiv)

        image = document.createElement('img')
        image.src = 'assets/images/calibration/hand_calibration.png'
        image.style.objectFit = 'contain'
        image.style.position = 'fixed'
        image.style.left = '0%'
        image.style.top = '0%'
        image.style.width = '100%'
        image.style.height = '100%'
        @handDetectionCalibrationDiv.appendChild(image)

        setTimeout(() =>
            @handDetectionCalibrationDiv.style.opacity = '1'
        , 100)

        setTimeout(() =>
            if completionCallback?
                completionCallback()
        , 1100)

    hideHandDetectionCalibratorImage: (completionCallback) ->
        @handDetectionCalibrationDiv.style.transition = 'opacity 0.3s linear'
        @handDetectionCalibrationDiv.style.opacity = '0'

        setTimeout(() =>
            document.body.removeChild(@handDetectionCalibrationDiv)
            @handDetectionCalibrationDiv = undefined
            if completionCallback?
                completionCallback()
        , 1000)

    """
    setupImageDetector: Sets up an image detector.

    detectorId: Detector ID to use as a reference.
    sourceImage: Image to detect
    minMatches: (Optional) Minimum number of matches for detection to be considered successful
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    setupImageDetector: (detectorId, sourceImage, minMatches = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        ClientUtil.convertImageToDataURL(sourceImage, (base64Image) =>
            json = {
                "requestId": requestId,
                "detectorId": detectorId,
                "imageBase64": base64Image
            }
            if minMatches? then json["minMatches"] = minMatches
            @sendMessage("setupImageDetector", json)
        )
        return requestId

    """
    setupTensorflowDetector: Sets up a tensorflow detector.

    detectorId: Detector ID to use as a reference.
    modelName: Name of model to use.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    setupTensorflowDetector: (detectorId, modelName, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "detectorId": detectorId,
            "modelName": modelName
        }
        @sendMessage("setupTensorflowDetector", json)
        return requestId




    """
    initializeBoardArea: Initializes an area of the board. Is used to search for markers in a specific region, etc.

    x1: Left coordinate in percentage [0..1] of board width.
    y1: Top in percentage [0..1] of board height.
    x2: Right coordinate in percentage [0..1] of board width.
    y2: Bottom coordinate in percentage [0..1] of board height.
    areaId: (Optional) Area ID to use. If none is given, a random area ID is generated and returned from the server.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeBoardArea: (x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        if areaId? then json["id"] = areaId
        @sendMessage("initializeBoardArea", json)
        return requestId

    """
    initializeTiledBoardArea: Initializes a tiled board area, ie. an area which is divided into equally sized tiles.

    tileCountX: Number of tiles horizontally.
    tileCountY: Number of tiles vertically.
    x1: Left coordinate in percentage [0..1] of board width.
    y1: Top in percentage [0..1] of board height.
    x2: Right coordinate in percentage [0..1] of board width.
    y2: Bottom coordinate in percentage [0..1] of board height.
    areaId: (Optional) Area ID to use. If none is given, a random area ID is generated and returned from the server.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeTiledBoardArea: (tileCountX, tileCountY, x1 = 0.0, y1 = 0.0, x2 = 1.0, y2 = 1.0, areaId = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "tileCountX": tileCountX,
            "tileCountY": tileCountY,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        }
        if areaId? then json["id"] = areaId
        @sendMessage("initializeTiledBoardArea", json)
        return requestId

    """
    removeBoardAreas: Removes all board areas at server end. Maintaining a board area requires some server processing, so
    it is good practice to remove them when not used any longer.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    removeBoardAreas: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeBoardAreas", {
            "requestId": requestId
        })
        return requestId

    """
    removeBoardArea: Removes a specific board area at server end. Maintaining a board area requires some server processing, so
    it is good practice to remove them when not used any longer.

    areaId: Board area ID.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    removeBoardArea: (areaId, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeBoardArea", {
            "requestId": requestId,
            "id": areaId
        })
        return requestId

    """
    removeMarkers: Removes all markers from the server.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    removeMarkers: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeMarkers", {
            "requestId": requestId
        })
        return requestId

    """
    removeMarker: Removes a specific marker from the server.

    markerId: Marker ID.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    removeMarker: (markerId, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeMarker", {
            "requestId": requestId,
            "id": markerId
        })
        return requestId

    """
    detectImages: Detect images in the given area.

    areaId: Area ID of tiled board area.
    detectorId: The ID of the detector to use.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    detectImages: (areaId, detectorId, keepRunning = false, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "detectorId": detectorId,
        }
        if keepRunning? then json["keepRunning"] = keepRunning
        @sendMessage("detectImages", json)
        return requestId

    """
    detectNonobstructedArea: Detects nonobstructed area on the board.

    areaId: ID of area to detect nonobstructed area in.
    targetSize: Size of area to fit (width, height).
    targetPoint: (Optional) Find area closest possible to target point (x, y). Defaults to [0.5, 0.5].
    keepRunning: (Optional) Keep returning results. Defaults to False.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    detectNonobstructedArea: (areaId, targetSize, targetPoint = undefined, keepRunning = false, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "targetSize": targetSize
        }
        if keepRunning? then json["keepRunning"] = keepRunning
        if targetPoint? then json["targetPoint"] = targetPoint
        @sendMessage("detectNonobstructedArea", json)
        return requestId

    """
    detectTiledBrick: Returns the position of a brick among the given possible positions in a tiled area.

    areaId: Area ID of tiled board area.
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    targetPosition: (Optional) Target position.
    waitForPosition: (Optional) If true, waits for brick to be detected, else returns immediately.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    detectTiledBrick: (areaId, validPositions, targetPosition = undefined, waitForPosition = false, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        }
        if targetPosition? then json["targetPosition"] = targetPosition
        if waitForPosition? then json["waitForPosition"] = waitForPosition
        @sendMessage("detectTiledBrick", json)
        return requestId

    """
    detectTiledBricks: Returns the positions of bricks among the given possible positions in a tiled area.

    areaId: Area ID of tiled board area.
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    waitForPosition: (Optional) If true, waits for brick to be detected, else returns immediately.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    detectTiledBricks: (areaId, validPositions, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        }
        if waitForPosition? then json["waitForPosition"] = waitForPosition
        @sendMessage("detectTiledBricks", json)
        return requestId

    """
    detectTiledBrickMovement: Keeps searching for a brick in the given positions in a tiled area and returns
    the position when found.

    areaId: Area ID of tiled board area.
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    initialPosition: (Optional) Initial position.
    targetPosition: (Optional) Target position.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    detectTiledBrickMovement: (areaId, validPositions, initialPosition = undefined, targetPosition = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        }
        if initialPosition? then json["initialPosition"] = initialPosition
        if targetPosition? then json["targetPosition"] = targetPosition
        @sendMessage("detectTiledBrickMovement", json)
        return requestId



    sendMessage: (action, payload) ->
        message = {
            "action": action,
            "payload": payload
        }
        @socket.send(JSON.stringify(message))
        return payload["requestId"]


    addCompletionCallback: (completionCallback) ->
        if completionCallback?
            requestId = ClientUtil.randomRequestId()
            @requests[requestId] = {"timestamp": Date.now(), "completionCallback": completionCallback}
            return requestId
        else
            return undefined

    performCompletionCallbackForRequest: (json) ->

        # Extract fields
        action = json["action"]
        requestId = json["requestId"]
        payload = json["payload"]

        # Json validation
        if not action? or not requestId? or not payload?
            return

        # Extract request from request dict
        requestDict = @requests[requestId]

        if not requestDict?
            return

        # Fire callback handler
        completionCallback = requestDict["completionCallback"]

        shouldRemoveRequest = completionCallback(action, payload)

        # Delete request if not explicitely specified otherwise by callback handler
        if not shouldRemoveRequest? or shouldRemoveRequest
            delete @requests[requestId]

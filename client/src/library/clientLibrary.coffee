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

    """
    reset: Resets the server.

    resolution: (Optional) Camera resolution to use in form [width, height].
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    reset: (resolution = undefined, completionCallback = undefined) ->
        @requests = {}
        requestId = @addCompletionCallback(completionCallback)
        json = {"requestId": requestId}
        if resolution? then json["resolution"] = resolution
        @sendMessage("reset", json)

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

    """
    setDebugCameraImage: Uploads debug camera image.

    image: Source marker image.
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

    """
    calibrateBoard: Calibrates the board.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    calibrateBoard: (completionCallback = undefined) ->
        @showBoardCalibratorImage(() =>
            requestId = @addCompletionCallback(() => @hideBoardCalibratorImage(completionCallback))
            json = {"requestId": requestId}
            @sendMessage("calibrateBoard", json)
        )

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
        image.src = 'assets/images/board_calibration.png'
        image.style.objectFit= 'contain'
        image.style.position = 'fixed'
        image.style.left = '0%'
        image.style.top = '0%'
        image.style.width = '100%'
        image.style.height = '100%'
        @boardCalibrationDiv.appendChild(image)

        setTimeout(() =>
            @boardCalibrationDiv.style.opacity = '1'
        , 1)

        setTimeout(() =>
            if completionCallback?
                completionCallback()
        , 1000)

    hideBoardCalibratorImage: (completionCallback) ->
        @boardCalibrationDiv.style.opacity = '0'

        setTimeout(() =>
            document.body.removeChild(@boardCalibrationDiv)
            @boardCalibrationDiv = undefined
            if completionCallback?
                completionCallback()
        , 1000)

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

    """
    removeMarkers: Removes all markers from the server.

    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    removeMarkers: (completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("removeMarkers", {
            "requestId": requestId
        })

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

    """
    requestTiledBrickPosition: Returns the position of a brick among the given possible positions in a tiled area.

    areaId: Area ID of tiled board area.
    detectorId: The ID of the detector to use.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    detectImages: (areaId, detectorId, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("detectImages", {
            "requestId": requestId,
            "areaId": areaId,
            "detectorId": detectorId
        })

    """
    requestTiledBrickPosition: Returns the position of a brick among the given possible positions in a tiled area.

    areaId: Area ID of tiled board area.
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    requestTiledBrickPosition: (areaId, validPositions, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("requestBrickPosition", {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        })

    """
    requestTiledBrickPositions: Returns the positions of bricks among the given possible positions in a tiled area.

    areaId: Area ID of tiled board area.
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    requestTiledBrickPosition: (areaId, validPositions, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @sendMessage("requestBrickPositions", {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        })

    """
    reportBackWhenBrickFoundAtAnyOfPositions: Keeps searching for a brick in the given positions in a tiled area and returns
    the position when found.

    areaId: Area ID of tiled board area.
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    id: (Optional) Reporter ID.
    stabilityLevel: (Optional) Minimum stability level of board area before returning result.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    reportBackWhenBrickFoundAtAnyOfPositions: (areaId, validPositions, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickFoundAtAnyOfPositions", json)

    """
    reportBackWhenBrickMovedToAnyOfPositions: Reports back when brick has moved to any of the given positions in a tiled area.

    areaId: Area ID of tiled board area.
    initialPosition: Position where brick is currently located in form [x, y].
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...].
    id: (Optional) Reporter ID.
    stabilityLevel: (Optional) Minimum stability level of board area before returning result.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    reportBackWhenBrickMovedToAnyOfPositions: (areaId, initialPosition, validPositions, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "initialPosition": initialPosition,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickMovedToAnyOfPositions", json)

    """
    reportBackWhenBrickMovedToPosition: Reports back when brick has moved to the given position in a tiled area.

    position: Target position to trigger the callback in form [x, y].
    validPositions: A list of valid positions in the form [[x, y], [x, y], ...] where the brick could be located.
    id: (Optional) Reporter ID.
    stabilityLevel: (Optional) Minimum stability level of board area before returning result.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    reportBackWhenBrickMovedToPosition: (areaId, position, validPositions, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "position": position,
            "validPositions": validPositions
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenBrickMovedToPosition", json)

    """
    initializeImageMarker: Initializes an image marker.

    markerId: Marker ID.
    image: Source marker image.
    minMatches: (Optional) Minimum number of matches required. (8 is recommended minimum).
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeImageMarker: (markerId, image, minMatches = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @convertImageToDataURL(image, (base64Image) =>
            json = {
                "requestId": requestId,
                "markerId": markerId,
                "imageBase64": base64Image
            }
            if minMatches? then json["minMatches"] = minMatches
            @sendMessage("initializeImageMarker", json)
        )

    """
    initializeHaarClassifierMarker: Initializes a Haar Classifier with the given filename.

    markerId: Marker ID.
    filename: Filename of Haar Classifier.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeHaarClassifierMarker: (markerId, filename, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @readFileBase64(filename, (base64Data) =>
            @sendMessage("initializeHaarClassifierMarker", {
                "requestId": requestId,
                "markerId": markerId,
                "dataBase64": base64Data
            })
        )

    """
    initializeShapeMarkerWithContour: Initializes a shape marker with the given contour.

    markerId: Marker ID.
    contour: Contour of shape in form [[x, y], [x, y], ...].
    minArea: (Optional) Minimum area in percentage [0..1] of board area image size.
    maxArea: (Optional) Maximum area in percentage [0..1] of board area image size.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeShapeMarkerWithContour: (markerId, contour, minArea = undefined, maxArea = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "markerId": markerId,
            "shape": contour
        }
        if minArea? then json["minArea"] = minArea
        if maxArea? then json["maxArea"] = maxArea
        @sendMessage("initializeShapeMarker", json)

    """
    initializeShapeMarkerWithImage: Initializes a shape marker with shape extracted from the given image.

    markerId: Marker ID.
    image: Marker image. Must be black contour on white image.
    minArea: (Optional) Minimum area in percentage [0..1] of board area image size.
    maxArea: (Optional) Maximum area in percentage [0..1] of board area image size.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeShapeMarkerWithImage: (markerId, image, minArea = undefined, maxArea = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        @convertImageToDataURL(image, (base64Image) =>
            json = {
                "requestId": requestId,
                "markerId": markerId,
                "imageBase64": base64Image
            }
            if minArea? then json["minArea"] = minArea
            if maxArea? then json["maxArea"] = maxArea
            @sendMessage("initializeShapeMarker", json)
        )

    """
    initializeArUcoMarker: Initializes an ArUco marker with given properties.

    markerId: Marker ID.
    arUcoMarkerId: ArUco marker ID. Number in range [0..dictionarySize-1].
    markerSize: Marker size. Any of 4, 5, 6, 7.
    dictionarySize: (Optional) Dictionary size. Any of 100, 250, 1000.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    initializeArUcoMarker: (markerId, arUcoMarkerId, markerSize, dictionarySize = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "markerId": markerId,
            "arUcoMarkerId": arUcoMarkerId,
            "markerSize": markerSize
        }
        if dictionarySize? then json["dictionarySize"] = dictionarySize
        @sendMessage("initializeArUcoMarker", json)

    """
    reportBackWhenMarkerFound: Keeps searching for marker and reports back when found.

    areaId: Area ID to search for marker in.
    markerId: Marker ID to search for.
    id: (Optional) Reporter ID.
    stabilityLevel: (Optional) Minimum stability level of board area before returning result.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    reportBackWhenMarkerFound: (areaId, markerId, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "markerId": markerId
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("reportBackWhenMarkerFound", json)

    """
    requestMarkers: Returns which markers among the given list of markers that are currently visible in the given area.

    areaId: Area ID to search for markers in.
    markerIds: Marker IDs to search for in form [id, id, ...].
    id: (Optional) Reporter ID.
    stabilityLevel: (Optional) Minimum stability level of board area before returning result.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    requestMarkers: (areaId, markerIds, id = undefined, stabilityLevel = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "markerIds": markerIds
        }
        if id? then json["id"] = id
        if stabilityLevel? then json["stabilityLevel"] = stabilityLevel
        @sendMessage("requestMarkers", json)

    """
    requestArUcoMarkers: Returns a list of all visible ArUco markers of given size in given area.

    areaId: Area ID to search for markers in.
    markerSize: ArUco marker size. Any of 4, 5, 6, 7.
    id: (Optional) Reporter ID.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    requestArUcoMarkers: (areaId, markerSize, id = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "markerSize": markerSize
        }
        if id? then json["id"] = id
        @sendMessage("requestArUcoMarkers", json)

    """
    startTrackingMarker: Continously tracks a marker in the given area. Continously reports back.

    areaId: Area ID to track marker in.
    markerId: Marker ID to track.
    id: (Optional) Reporter ID.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    startTrackingMarker: (areaId, markerId, id = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
            "markerId": markerId
        }
        if id? then json["id"] = id
        @sendMessage("startTrackingMarker", json)

    """
    requestContours: Returns a list of all visible contours in given area.

    areaId: Area ID to search for markers in.
    approximation: (Optional) Contour approximation constant. This is the maximum distance between the original curve and its approximation.
    id: (Optional) Reporter ID.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    requestContours: (areaId, approximation, id = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId,
            "areaId": areaId,
        }
        if id? then json["id"] = id
        if approximation? then json["approximation"] = approximation
        @sendMessage("requestContours", json)

    """
    requestHumanHeadPositions: Returns human head positions as a 3D vector with (0, 0, 0) representing board center.

    id: (Optional) Reporter ID.
    completionCallback: (Optional) completionCallback(action, payload) is called when receiving a respond to the request.
    """
    requestHumanHeadPositions: (id = undefined, completionCallback = undefined) ->
        requestId = @addCompletionCallback(completionCallback)
        json = {
            "requestId": requestId
        }
        if id? then json["id"] = id
        @sendMessage("requestHumanHeadPositions", json)



    sendMessage: (action, payload) ->
        message = {
            "action": action,
            "payload": payload
        }
        @socket.send(JSON.stringify(message))


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

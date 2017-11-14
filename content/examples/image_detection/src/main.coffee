class ImageDetectionExample

    constructor: () ->
        @client = new Client()

    start: ->
        @client.connect(
          (() => @reset()),
          ((json) => @onMessage(json))
        )

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset([1600, 1200], (action, payload) =>
            @client.enableDebug()
            @setDebugCameraImage("calibration/board_calibration.png", (action, payload) =>
                @calibrateBoard()
            )
        )

    onMessage: (json) ->

    setDebugCameraImage: (filename, completionCallback) ->
        image = new Image()
        image.onload = () => @client.setDebugCameraImage(image, completionCallback)
        image.src = "assets/images/" + filename

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) => @setupImageDetector())

    setupImageDetector: ->
        image = new Image()
        image.onload = () => @client.setupImageDetector(0, image, undefined, (action, payload) => @detectImages())
        image.src = "assets/images/image_source.png"

    detectImages: ->
        @setDebugCameraImage("image_detection.png", (action, payload) =>
            @client.detectImages(@client.boardAreaId_fullBoard, 0, (action, payload) =>
                console.log("Images detected!")
                console.log(payload)
            )
        )

class BoardDetectionExample

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
            @setDebugCameraImage("board_calibration.png", (action, payload) =>
                @calibrateBoard()
            )
        )

    onMessage: (json) ->

    setDebugCameraImage: (filename, completionCallback) ->
        image = new Image()
        image.onload = () => @client.setDebugCameraImage(image, completionCallback)
        image.src = "assets/images/" + filename

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) => @setupTensorflowDetector())

    setupTensorflowDetector: ->
        @client.setupTensorflowDetector(0, "brick", (action, payload) => @detectBricks())

    detectBricks: ->
        @setDebugCameraImage("brick_detection.png", (action, payload) =>
            @client.detectImages(@client.boardAreaId_fullBoard, 0, (action, payload) =>
                console.log("Bricks detected!")
                console.log(payload)
            )
        )

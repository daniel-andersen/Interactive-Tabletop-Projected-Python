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
            @calibrateBoard()
        )

    onMessage: (json) ->

    setDebugCameraImage: (filename, completionCallback) ->
        image = new Image()
        image.onload = () => @client.setDebugCameraImage(image, completionCallback)
        image.src = "assets/images/" + filename

    calibrateBoard: ->
        @setDebugCameraImage("calibration/board_calibration.png", (action, payload) =>
            @client.calibrateBoard((action, payload) =>
                console.log('Calibrated board!')
            )
        )

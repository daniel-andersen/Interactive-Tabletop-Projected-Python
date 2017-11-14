class RaspberryPiInstructions

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

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) =>
            @calibrateHandDetection()
        )

    calibrateHandDetection: ->
        @client.calibrateHandDetection((action, payload) =>
            @setupImageDetector()
        )

    setupImageDetector: ->
        @raspberryPiDetectorId = 0

        image = new Image()
        image.onload = () => @client.setupImageDetector(@raspberryPiDetectorId, image, undefined, (action, payload) => @start())
        image.src = "assets/images/raspberry_pi_source.png"

    start: ->
        console.log("Ready!")

class BoardDetectionExample

    constructor: () ->
        @initialize()

        @client = new Client()

    start: ->
        @client.connect(
          (() => @reset()),
          ((json) => @onMessage(json))
        )

    stop: ->
        @client.disconnect()

    initialize: ->
        @ready = undefined
        @cornersVisible = true

        @markerRelaxationTime = 1.0
        @markersHistory = []

        @headHistory = []

        @visibleMarkerPosition = undefined
        @visibleMarkerAngle = undefined

        @wholeBoardArea = [0.3, 0.3, 0.7, 0.7]

        @aspectRatio = screen.width / screen.height

    reset: ->
        @client.reset([1600, 1200], (action, payload) =>
            @client.enableDebug()
            @calibrateBoard()
        )

    onMessage: (json) ->
        switch json["action"]
            when "recognizeBoard"
                if json["result"] is "BOARD_RECOGNIZED"
                    @boardRecognized()

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) =>
            @client.setupTensorflowDetector(0, "brick", (action, payload) =>
                console.log('OK!')
            )
            # @initializeBoardAreas()
        )

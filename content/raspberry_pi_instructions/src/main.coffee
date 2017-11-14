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
            console.log("Hand detection initialized!")
        )

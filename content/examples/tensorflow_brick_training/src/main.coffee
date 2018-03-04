class TensorflowBrickDetectionExample

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
            @ready()
            @calibrateBoard()
        )

    onMessage: (json) ->

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) => @ready())

    ready: ->
        window.addEventListener('keydown', ((event) => @onKeydown(event)), false)

    onKeydown: (event) ->
        console.log('Received keydown event: ' + event.keyCode)

        if event.keyCode == 32  # Space
            @takeScreenshot()

    takeScreenshot: ->
        @client.takeScreenshot(@client.boardAreaId_fullBoard, undefined, () =>
            flashElement = document.getElementById("flash")

            flashElement.style.transition = "opacity 0s"
            flashElement.style.opacity = 1.0

            setTimeout(() =>
                flashElement.style.transition = "opacity 2s"
                flashElement.style.opacity = 0.0
            , 10)
        )

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
            @setupImageDetectors()
        )

    onMessage: (json) ->

    setupImageDetectors: ->
        @raspberry_pi_detector_id = 0

        @image_detectors = []

        raspberry_pi_source_image = new Image()
        raspberry_pi_source_image.onload = () => @client.setupImageDetector(0, raspberry_pi_source_image, undefined, (action, payload) => @didSetupImageDetector(@raspberry_pi_detector_id))
        raspberry_pi_source_image.src = "assets/images/raspberry_pi_source.png"

    didSetupImageDetector: (id) ->
        @image_detectors.push(id)

        return if @raspberry_pi_detector_id not in @image_detectors

        @calibrateBoard()

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) =>
            @calibrateHandDetection()
        )

    calibrateHandDetection: ->
        @client.calibrateHandDetection((action, payload) =>
            @ready()
        )

    ready: ->
        console.log("Ready!")

        @client.cancelRequests((action, payload) ->
            @detectRaspberryPi()
        )

    detectRaspberryPi: ->
        @client.detectImages(@client.boardAreaId_fullBoard, @raspberry_pi_detector_id, true, (action, payload) =>
            console.log(payload)
            if payload?
                document.getElementById('detection_state').style.backgroundColor = 'green'
            else
                document.getElementById('detection_state').style.backgroundColor = 'red'
        )

class RaspberryPiInstructions

    State =
        Initializing: 0
        Ready: 1
        PlaceRaspberryPiOnTable: 2
        Instructions: 3

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
        @initialize()

        @client.reset([1600, 1200], (action, payload) =>
            @client.enableDebug()
            @setupImageDetectors()
        )

    onMessage: (json) ->

    initialize: ->
        @state = State.Initializing

        @instruction_place_raspberry_pi_on_table = document.getElementById('instruction_place_raspberry_pi_on_table')
        @instruction_steps = document.getElementById('instruction_steps')
        @instruction_connect_to_monitor = document.getElementById('instruction_connect_to_monitor')
        @instruction_connect_power = document.getElementById('instruction_connect_power')

        @all_elements = [
            @instruction_place_raspberry_pi_on_table,
            @instruction_steps,
            @instruction_connect_to_monitor,
            @instruction_connect_power
        ]

        @current_instruction = @instruction_connect_to_monitor

        @element_padding = 0.2

        @raspberryPiPosition = undefined


    setupImageDetectors: ->
        @raspberry_pi_detector_id = 0

        @image_detectors = []

        raspberry_pi_source_image = new Image()
        raspberry_pi_source_image.onload = () => @client.setupImageDetector(0, raspberry_pi_source_image, undefined, (action, payload) => @didSetupImageDetector(@raspberry_pi_detector_id))
        raspberry_pi_source_image.src = "assets/images/raspberry_pi_source.png"

    didSetupImageDetector: (id) ->
        @image_detectors.push(id)

        return if @raspberry_pi_detector_id not of @image_detectors

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

        @state = State.Ready

        @raspberryPiDetectionHistory = []

        @client.cancelRequests((action, payload) =>
            @detectRaspberryPi()
        )

    detectRaspberryPi: ->
        @client.detectImages(@client.boardAreaId_fullBoard, @raspberry_pi_detector_id, true, (action, payload) =>
            @updateRaspberryPiDetection(payload)
            return false
        )

    updateRaspberryPiDetection: (payload) ->
        detected = "matches" of payload

        if detected
            @raspberryPiPosition = payload['matches'][0]

        document.getElementById('detection_state').style.backgroundColor = if detected then 'green' else 'red'

        @raspberryPiDetectionHistory.push({
            'timestamp': @currentTimeSeconds(),
            'detected': detected
        })
        while @raspberryPiDetectionHistory.length > 0 and @raspberryPiDetectionHistory[0]['timestamp'] < @currentTimeSeconds() - 1.0
            @raspberryPiDetectionHistory.shift()

        detected_count = 0
        for entry in @raspberryPiDetectionHistory
            if entry['detected']
                detected_count += 1

        if detected_count >= @raspberryPiDetectionHistory.length / 2 and @state != State.Instructions
            @showState(State.Instructions)

        if detected_count == 0 and @state != State.PlaceRaspberryPiOnTable
            @showState(State.PlaceRaspberryPiOnTable)

    showState: (state, completionCallback = () =>) ->
        if (state == @state)
            return

        @state = state

        @hideCurrentState(() =>
            switch @state
                when State.PlaceRaspberryPiOnTable then @showPlaceRaspberryPiOnTable()
                when State.Instructions then @showInstructions()

            setTimeout(() =>
                completionCallback()
            , 300)
        )

    showPlaceRaspberryPiOnTable: ->
        [width, height] = [242.0 / 1280.0, 70.0 / 800.0]
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width + @element_padding, height + @element_padding], [0.5, 0.0], false, (action, payload) =>
            if "matches" of payload
                match = payload['matches'][0]
                @instruction_place_raspberry_pi_on_table.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                @instruction_place_raspberry_pi_on_table.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                @instruction_place_raspberry_pi_on_table.style.opacity = 1
            else
                @showPlaceRaspberryPiOnTable()
        )

    showInstructions: ->
        @updateInstructionStepsPosition()
        @updateCurrentInstructionsPosition()

    updateInstructionStepsPosition: ->
        [width, height] = [223.0 / 1280.0, 78.0 / 800.0]
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width + @element_padding, height + @element_padding], [0.0, 0.0], false, (action, payload) =>
            if @state == State.Instructions
                if "matches" of payload and @raspberryPiDetectionHistory.length > 0 and @raspberryPiDetectionHistory[@raspberryPiDetectionHistory.length - 1]["detected"]
                    match = payload['matches'][0]
                    @instruction_steps.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                    @instruction_steps.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                    @instruction_steps.style.opacity = 1
                @updateInstructionStepsPosition()
        )
    updateCurrentInstructionsPosition: ->
        element_target_position = @elementTargetPosition()

        [width, height] = [250.0 / 1280.0, 150.0 / 800.0]
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width, height], element_target_position, false, (action, payload) =>
            if @state == State.Instructions
                if "matches" of payload and @raspberryPiDetectionHistory.length > 0 and @raspberryPiDetectionHistory[@raspberryPiDetectionHistory.length - 1]["detected"]
                    match = payload['matches'][0]
                    @current_instruction.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                    @current_instruction.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                    @current_instruction.style.opacity = 1
                @updateCurrentInstructionsPosition()
        )

    hideCurrentState: (completionCallback = () =>) ->
        for element in @all_elements
            element.style.opacity = 0

        setTimeout(() =>
            completionCallback()
        , 300)

    elementTargetPosition: -> if @raspberryPiPosition? then [@raspberryPiPosition['x'], @raspberryPiPosition['y']] else [0.5, 0.5]

    currentTimeSeconds: -> new Date().getTime() / 1000.0

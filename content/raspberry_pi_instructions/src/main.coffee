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

        @element_place_raspberry_pi_on_table = document.getElementById('instructions_place_raspberry_pi_on_table')
        @element_gpio_pinout = document.getElementById('instructions_gpio_pinout')
        @element_gpio_pinout_left = document.getElementById('instructions_gpio_pinout_left')
        @element_gpio_pinout_right = document.getElementById('instructions_gpio_pinout_right')
        @element_raspi_overlay = document.getElementById('instructions_raspi_overlay')
        @element_palm_overlay_1 = document.getElementById('instructions_palm_overlay_1')
        @element_palm_overlay_2 = document.getElementById('instructions_palm_overlay_2')
        @all_elements = [
            @element_place_raspberry_pi_on_table,
            @element_gpio_pinout,
            @element_gpio_pinout_left,
            @element_gpio_pinout_right,
            @element_raspi_overlay,
            @element_palm_overlay_1,
            @element_palm_overlay_2,
        ]

        @current_place_raspberry_pi_on_table_position = undefined
        @current_gpio_pinout_position = undefined
        @current_gpio_pinout_left_position = undefined
        @current_gpio_pinout_right_position = undefined

        @element_padding = 0.05

        @raspberry_pi_position = undefined
        @raspberry_pi_position_current = undefined
        @raspberry_pi_size = undefined
        @raspberry_pi_angle = undefined
        @raspberry_pi_angle_current = undefined

    setupImageDetectors: ->
        @raspberry_pi_detector_id = 0

        @image_detectors = []

        raspberry_pi_source_images = []
        loaded_count = 0
        total_count = 1

        for i in [1..total_count]
            raspberry_pi_source_image = new Image()
            raspberry_pi_source_images.push(raspberry_pi_source_image)

            raspberry_pi_source_image.onload = () =>
                loaded_count += 1
                if loaded_count == total_count
                    @client.setupImageDetector(0, undefined, raspberry_pi_source_images, undefined, (action, payload) => @didSetupImageDetector(@raspberry_pi_detector_id))

            raspberry_pi_source_image.src = "assets/images/raspberry_pi_source_" + i +  ".png"

    didSetupImageDetector: (id) ->
        @image_detectors.push(id)

        return if @raspberry_pi_detector_id not of @image_detectors

        @calibrateBoard()

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) =>
            @calibrateHandDetection()
        )

    calibrateHandDetection: ->
        #@ready()
        @client.calibrateHandDetection((action, payload) =>
            @ready()
        )

    ready: ->
        console.log("Ready!")

        @state = State.Ready

        @raspberryPiDetectionHistory = []

        @client.cancelRequests((action, payload) =>
            @detectRaspberryPi()
            @detectGestures()
        )

    detectRaspberryPi: ->
        @client.detectImages(@client.boardAreaId_fullBoard, @raspberry_pi_detector_id, true, (action, payload) =>
            @updateRaspberryPiDetection(payload)
            return false
        )

    detectGestures: ->
        @client.detectGestures(@client.boardAreaId_fullBoard, undefined, true, (action, payload) =>
            @updateGesture(payload)
            return false
        )

    updateRaspberryPiDetection: (payload) ->
        detected = "matches" of payload

        #document.getElementById('detection_state').style.backgroundColor = if detected then 'green' else 'red'

        # Update detection history
        @raspberryPiDetectionHistory.push({
            'timestamp': @currentTimeSeconds(),
            'detected': detected,
            'payload': payload
        })
        while @raspberryPiDetectionHistory.length > 0 and @raspberryPiDetectionHistory[0]['timestamp'] < @currentTimeSeconds() - 1.0
            @raspberryPiDetectionHistory.shift()

        detected_count = 0
        for entry in @raspberryPiDetectionHistory
            if entry['detected']
                detected_count += 1

        # Update position
        position = [0.0, 0.0]
        size = [0.0, 0.0]
        angle = 0
        count = 0

        for entry in @raspberryPiDetectionHistory
            if entry['detected']
                payload = entry['payload']['matches'][0]
                position = [position[0] + payload['x'], position[1] + payload['y']]
                size = [size[0] + payload['width'], size[1] + payload['height']]
                angle = payload['angle']
                count += 1

        if count > 0
            @raspberry_pi_position = [position[0] / count, position[1] / count]
            @raspberry_pi_size = [size[0] / count, size[1] / count]
            @raspberry_pi_angle = Math.round(angle)

            # Snap angle to 90 degrees
            if @raspberry_pi_angle >= 180 - 5
                @raspberry_pi_angle = 180
            if @raspberry_pi_angle <= -180 + 5
                @raspberry_pi_angle = -180

        # Update state
        if detected_count >= @raspberryPiDetectionHistory.length / 2 and @state != State.Instructions
            @showState(State.Instructions)

        if detected_count == 0 and @state != State.PlaceRaspberryPiOnTable
            @showState(State.PlaceRaspberryPiOnTable)

    updateGesture: (payload) ->
        if 'hands' not of payload
            @element_palm_overlay_1.style.opacity = 0
            @element_palm_overlay_2.style.opacity = 0
            return

        hands = payload['hands']

        if hands.length > 0 and hands[0]['gesture'] == 2
            hand = hands[0]
            [width, height] = [45.0 / 1280.0, 44.0 / 800.0]
            @element_palm_overlay_1.style.left = ((hand['palmCenter']['x'] - (width / 2.0)) * 100.0) + '%'
            @element_palm_overlay_1.style.top = ((hand['palmCenter']['y'] - (height / 2.0)) * 100.0) + '%'
            @element_palm_overlay_1.style.opacity = 1
        else
            @element_palm_overlay_1.style.opacity = 0

        if hands.length > 1 and hands[0]['gesture'] == 1
            hand = hands[1]
            [width, height] = [45.0 / 1280.0, 45.0 / 800.0]
            @element_palm_overlay_2.style.left = ((hand['palmCenter']['x'] - (width / 2.0)) * 100.0) + '%'
            @element_palm_overlay_2.style.top = ((hand['palmCenter']['y'] - (height / 2.0)) * 100.0) + '%'
            @element_palm_overlay_2.style.opacity = 1
        else
            @element_palm_overlay_2.style.opacity = 0

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
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width, height], [0.5, 0.0], @current_place_raspberry_pi_on_table_position, [@element_padding, @element_padding], 0.25, false, (action, payload) =>
            if @state == State.PlaceRaspberryPiOnTable
                if "matches" of payload
                    match = payload['matches'][0]
                    @current_place_raspberry_pi_on_table_position = match['center']
                    @element_place_raspberry_pi_on_table.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                    @element_place_raspberry_pi_on_table.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                    @element_place_raspberry_pi_on_table.style.opacity = 1
                @showPlaceRaspberryPiOnTable()
        )

    showInstructions: ->
        @updateInstructionGpioPinoutPosition()
        @updateRaspiOverlayPosition()

    updateInstructionGpioPinoutPosition: ->
        [width, height] = [640.0 / 1280.0, 208.0 / 800.0]
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width, height], [0.5, 0.0], @current_gpio_pinout_position, [@element_padding, @element_padding], 0.25, false, (action, payload) =>
            if @state == State.Instructions
                if "matches" of payload
                    match = payload['matches'][0]
                    @current_gpio_pinout_position = match['center']
                    @element_gpio_pinout.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                    @element_gpio_pinout.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                    @element_gpio_pinout.style.opacity = 1
                    @element_gpio_pinout_left.style.opacity = 0
                    @element_gpio_pinout_right.style.opacity = 0
                    setTimeout(() =>
                        @updateInstructionGpioPinoutPosition()
                    , 150)
                else
                    @current_gpio_pinout_position = undefined
                    @element_gpio_pinout.style.opacity = 0
                    setTimeout(() =>
                        @updateInstructionGpioPinoutLeftPosition()
                    , 150)
        )

    updateInstructionGpioPinoutLeftPosition: ->
        [width, height] = [232.0 / 1280.0, 150.0 / 800.0]
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width, height], [0.0, 0.0], @current_gpio_pinout_left_position, [@element_padding, @element_padding], 0.25, false, (action, payload) =>
            if @state == State.Instructions
                if "matches" of payload
                    match = payload['matches'][0]
                    @current_gpio_pinout_left_position = match['center']
                    @element_gpio_pinout_left.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                    @element_gpio_pinout_left.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                    @element_gpio_pinout_left.style.opacity = 1
                else
                    @current_gpio_pinout_left_position = undefined
                    @element_gpio_pinout_left.style.opacity = 0
            setTimeout(() =>
                @updateInstructionGpioPinoutRightPosition()
            , 150)
        )

    updateInstructionGpioPinoutRightPosition: ->
        [width, height] = [230.0 / 1280.0, 150.0 / 800.0]
        @client.detectNonobstructedArea(@client.boardAreaId_fullBoard, [width, height], [1.0, 0.0], @current_gpio_pinout_right_position, [@element_padding, @element_padding], 0.25, false, (action, payload) =>
            if @state == State.Instructions
                if "matches" of payload
                    match = payload['matches'][0]
                    @current_gpio_pinout_right_position = match['center']
                    @element_gpio_pinout_right.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%'
                    @element_gpio_pinout_right.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%'
                    @element_gpio_pinout_right.style.opacity = 1
                else
                    @current_gpio_pinout_right_position = undefined
                    @element_gpio_pinout_right.style.opacity = 0
            setTimeout(() =>
                @updateInstructionGpioPinoutPosition()
            , 150)
        )

    updateRaspiOverlayPosition: ->
        if @state != State.Instructions
            return

        if @raspberry_pi_position?
            [width, height] = [580.0 / 1280.0, 280.0 / 800.0]

            if @isNewPosition(@raspberry_pi_position_current, @raspberry_pi_position)
                @raspberry_pi_position_current = @raspberry_pi_position
                @element_raspi_overlay.style.left = ((@raspberry_pi_position[0] - (width * 0.5)) * 100.0) + 'vw'
                @element_raspi_overlay.style.top = ((@raspberry_pi_position[1] - (height * 0.5)) * 100.0) + 'vh'

            if @isNewAngle(@raspberry_pi_angle_current, @raspberry_pi_angle)
                @raspberry_pi_angle_current = @raspberry_pi_angle
                @element_raspi_overlay.style.transform = 'rotate(' + (@raspberry_pi_angle + 180.0) + 'deg)'

            @element_raspi_overlay.style.opacity = 1

        setTimeout(() =>
            @updateRaspiOverlayPosition()
        , 100)

    hideCurrentState: (completionCallback = () =>) ->
        for element in @all_elements
            element.style.opacity = 0

        @current_place_raspberry_pi_on_table_position = undefined
        @current_gpio_pinout_position = undefined
        @current_gpio_pinout_left_position = undefined
        @current_gpio_pinout_right_position = undefined

        @raspberry_pi_position = undefined
        @raspberry_pi_position_current = undefined

        setTimeout(() =>
            completionCallback()
        , 300)

    isNewPosition: (currentPosition, newPosition) ->
        if not currentPosition? or not newPosition?
            return true

        return Math.abs(currentPosition[0] - newPosition[0]) > 10.0 / 1280.0 or Math.abs(currentPosition[1] - newPosition[1]) > 10.0 / 800.0

    isNewAngle: (currentAngle, newAngle) ->
        if not currentAngle? or not newAngle?
            return true

        angle_diff = Math.abs(currentAngle - newAngle)
        return angle_diff >= 5.0 and angle_diff <= 360.0 - 5.0

    currentTimeSeconds: -> new Date().getTime() / 1000.0

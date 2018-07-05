class TensorflowBrickDetectionExample

    constructor: () ->
        @client = new Client()

        @figures = ["Black", "Red", "Blue", "Green"]

        @backgroundCount = 2

        @tileCount =
            x: 32
            y: 20

        @tileSize =
            width: window.innerWidth / @tileCount.x
            height: window.innerHeight / @tileCount.y

        @aspectRatio = (640 / window.innerWidth)
        @screenshotSize =
            width: 640
            height: @aspectRatio * window.innerHeight

        @tiles = [
            {
                "filename": "tiles1.png",
                "tilemap": [
                    "      ",
                    " ***  ",
                    " **** ",
                    " ***  ",
                    "      ",
                ]
            },
            {
                "filename": "tiles2.png",
                "tilemap": [
                    "         ",
                    "   ****  ",
                    " ******* ",
                    "   ****  ",
                    "   ****  ",
                    "     *   ",
                    "         ",
                ]
            },
            {
                "filename": "tiles3.png",
                "tilemap": [
                    "     ",
                    " *** ",
                    " *** ",
                    " *** ",
                    " *   ",
                    "     ",
                ]
            },
            {
                "filename": "tiles4.png",
                "tilemap": [
                    "      ",
                    " **** ",
                    "  *** ",
                    "  *** ",
                    "      ",
                ]
            },
            {
                "filename": "tiles5.png",
                "tilemap": [
                    "       ",
                    "    *  ",
                    "   *** ",
                    " ***** ",
                    "   *** ",
                    "       ",
                ]
            },
            {
                "filename": "tiles6.png",
                "tilemap": [
                    "        ",
                    " ****   ",
                    " ****** ",
                    " ****   ",
                    " ****   ",
                    "  *     ",
                    "  *     ",
                    "        ",
                ]
            },
            {
                "filename": "tiles7.png",
                "tilemap": [
                    "     ",
                    "  *  ",
                    "  *  ",
                    " *** ",
                    " *** ",
                    " *** ",
                    "     ",
                ]
            },
            {
                "filename": "tiles8.png",
                "tilemap": [
                    "      ",
                    " **** ",
                    " **   ",
                    " **   ",
                    " **   ",
                    " *    ",
                    " *    ",
                    "      ",
                ]
            },
            {
                "filename": "tiles9.png",
                "tilemap": [
                    "      ",
                    " **** ",
                    " **** ",
                    " **** ",
                    " **** ",
                    "  *   ",
                    "      ",
                ]
            },
            {
                "filename": "tiles10.png",
                "tilemap": [
                    "     ",
                    " *** ",
                    " *** ",
                    " *** ",
                    "     ",
                ]
            },
            {
                "filename": "tiles11.png",
                "tilemap": [
                    "   ",
                    " * ",
                    " * ",
                    " * ",
                    " * ",
                    "   ",
                ]
            },
            {
                "filename": "tiles12.png",
                "tilemap": [
                    "     ",
                    " *** ",
                    " *   ",
                    " *   ",
                    "     ",
                ]
            }
        ]

        @backgroundDiv = document.getElementById("background")
        @markersDiv = document.getElementById("markers")
        @tilesDiv = document.getElementById("tiles")
        @flashDiv = document.getElementById("flash")
        @maskElement = document.getElementById("mask")

        @trainNumber = 0

        @readyForScreenshot = false

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
            @client.setDebugCameraImageFilename("assets/images/calibration/board_calibration.png", (action, payload) =>
                @calibrateBoard()
            )
        )

    onMessage: (json) ->

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) => @ready())

    ready: ->
        window.addEventListener('keydown', ((event) => @onKeydown(event)), false)

        # Write label map
        @writeLabelMap()

        # Present first background
        @presentNewBackground()

    presentNewBackground: ->

        # Hide currently visible markers and tiles
        if @markersDiv.firstChild?
            @backgroundDiv.style.opacity = '0'

            setTimeout(() =>
                @markersDiv.removeChild(@markersDiv.firstChild) while @markersDiv.firstChild?
                @tilesDiv.removeChild(@tilesDiv.firstChild) while @tilesDiv.firstChild?
                @maskElement.removeChild(@maskElement.firstChild) while @maskElement.firstChild?
                @presentNewBackground()
            , 1000)
            return

        if Math.random() <= 0.75
            @presentRandomTiles()
        else
            @presentRandomBackground()

        @pickRandomPositions()

        setTimeout(() =>
            @markersDiv.style.opacity = '1'
            @backgroundDiv.style.opacity = '1'
            setTimeout(() =>
                @readyForScreenshot = true
            , 1000)
        , 100)

        @trainNumber += 1

    presentRandomTiles: ->

        # Generate tile map
        @tilePositions = []

        tilemap = ((false for j in [0...@tileCount.x]) for i in [0...@tileCount.y])

        for k in [0...@randomInRange(3, 6)]
            tileNumber = @randomInRange(0, @tiles.length)
            tile = @tiles[tileNumber]

            tileCount =
                x: tile["tilemap"][0].length
                y: tile["tilemap"].length

            # Find valid position not occupied by other tiles
            positionValid = false
            while not positionValid
                tilePosition =
                    x: @randomInRange(0, @tileCount.x - tileCount.x)
                    y: @randomInRange(0, @tileCount.y - tileCount.y)

                positionValid = true
                for i in [0...tileCount.y]
                    for j in [0...tileCount.x]
                        if tilemap[i + tilePosition.y][j + tilePosition.x]
                            positionValid = false

            # Mark tiles as used
            for i in [0...tileCount.y]
                for j in [0...tileCount.x]
                    tilemap[i + tilePosition.y][j + tilePosition.x] = true
                    if tile["tilemap"][i][j] == "*"
                        @tilePositions.push({
                            "x": j + tilePosition.x,
                            "y": i + tilePosition.y,
                            "masked": false
                        })

            # Create img
            tileImg = document.createElement('img')
            tileImg.src = 'assets/images/' + tile["filename"]
            tileImg.style.position = 'fixed'
            tileImg.style.left = (tilePosition.x * @tileSize.width) + 'px'
            tileImg.style.top = (tilePosition.y * @tileSize.height) + 'px'
            tileImg.style.width = (tileCount.x * @tileSize.width) + 'px'
            tileImg.style.height = (tileCount.y * @tileSize.height) + 'px'

            @tilesDiv.appendChild(tileImg)

    presentRandomBackground: ->

        useMask = @randomInRange(0, 3) > 0

        # All tile positions are valid for background images
        @tilePositions = []
        for i in [0...@tileCount.y]
            for j in [0...@tileCount.x]
                @tilePositions.push({
                    "x": j,
                    "y": i,
                    "masked": useMask
                })

        # Create img
        number = @randomInRange(0, @backgroundCount)

        tileImg = document.createElement('img')
        tileImg.src = 'assets/images/background' + (number + 1) + '.png'
        tileImg.style.position = 'fixed'
        tileImg.style.left = '0%'
        tileImg.style.top = '%0'
        tileImg.style.width = '100%'
        tileImg.style.height = '100%'

        @tilesDiv.appendChild(tileImg)

    pickRandomPositions: ->

        # Pick random figures
        @choosenFigures = []

        availableFigures = (figure for figure in @figures)

        count = @randomInRange(1, @figures.length + 1)
        for i in [0...count]
            figureIndex = @randomInRange(0, availableFigures.length)
            @choosenFigures.push(availableFigures[figureIndex])
            availableFigures.splice(figureIndex, 1)

        # Pick random positions
        @positions = []

        for figure in @choosenFigures

            # Pick random tile position
            positionIndex = @randomInRange(0, @tilePositions.length)
            position = @tilePositions[positionIndex]
            @tilePositions.splice(positionIndex, 1)

            @positions.push(position)

            console.log("Place figure '" + figure + "' at (" + position.x + ", " + position.y + ")")

        # Place markers
        for position in @positions

            # Create img
            markerImg = document.createElement('img')
            markerImg.src = 'assets/images/figure_marker.png'
            markerImg.style.position = 'fixed'
            markerImg.style.left = ((position.x * @tileSize.width) - (@tileSize.width * 0.25)) + 'px'
            markerImg.style.top = ((position.y * @tileSize.height) - (@tileSize.height * 0.25)) + 'px'
            markerImg.style.width = (@tileSize.width * 1.50) + 'px'
            markerImg.style.height = (@tileSize.height * 1.50) + 'px'

            @markersDiv.appendChild(markerImg)

        # Place labels
        for i in [0...@choosenFigures.length]

            # Create label
            markerLabel = document.createElement('p')
            markerLabel.textContent = @choosenFigures[i]
            markerLabel.style.textAlign = 'center'
            markerLabel.style.color = 'yellow'
            markerLabel.style.position = 'fixed'
            markerLabel.style.left = ((@positions[i].x * @tileSize.width) - (@tileSize.width * 0.5)) + 'px'
            markerLabel.style.top = ((@positions[i].y * @tileSize.height) - (@tileSize.height * 0.25)) + 'px'
            markerLabel.style.width = (@tileSize.width * 2.00) + 'px'
            markerLabel.style.height = (@tileSize.height * 1.50) + 'px'

            @markersDiv.appendChild(markerLabel)

        # Apply mask to positions
        maskSize =
            width: @tileSize.width * 8.0
            height: @tileSize.height * 8.0

        useMask = false
        for position in @positions
            if position.masked
                maskCircle = document.createElementNS("http://www.w3.org/2000/svg", "image")
                maskCircle.setAttributeNS(null, "href", "assets/images/figure_marker_mask.png")
                maskCircle.setAttributeNS(null, "x", ((position.x * @tileSize.width) + (@tileSize.width / 2.0) - (maskSize.width / 2.0)) + "px")
                maskCircle.setAttributeNS(null, "y", ((position.y * @tileSize.height) + (@tileSize.height / 2.0) - (maskSize.height / 2.0)) + "px")
                maskCircle.setAttributeNS(null, "width", maskSize.width + "px")
                maskCircle.setAttributeNS(null, "height", maskSize.height + "px")

                @maskElement.appendChild(maskCircle)

                useMask = true

        if not useMask
            maskCircle = document.createElementNS("http://www.w3.org/2000/svg", "rect")
            maskCircle.setAttributeNS(null, "x", "0px")
            maskCircle.setAttributeNS(null, "y", "0px")
            maskCircle.setAttributeNS(null, "width", window.innerWidth + "px")
            maskCircle.setAttributeNS(null, "height", window.innerHeight + "px")
            maskCircle.setAttributeNS(null, "style", "fill: white")

            @maskElement.appendChild(maskCircle)

    onKeydown: (event) ->
        if event.keyCode == 32  # Space
            @takeScreenshot()

    takeScreenshot: ->
        if not @readyForScreenshot
            return

        @readyForScreenshot = false

        # Take screenshot
        @markersDiv.style.opacity = '0'

        setTimeout(() =>
            @client.takeScreenshot(@client.boardAreaId_fullBoard, [@screenshotSize.width, @screenshotSize.height], "resources/tensorflow/images/image_" + @trainNumber + ".jpg", () =>
                @flashDiv.style.transition = "opacity 0s"
                @flashDiv.style.opacity = 1.0

                setTimeout(() =>
                    @flashDiv.style.transition = "opacity 2s"
                    @flashDiv.style.opacity = 0.0

                    setTimeout(() =>
                        @presentNewBackground()
                    , 2000)
                , 100)
            )
        , 500)

        # Create xml file
        screenshotTileSize =
            width: @screenshotSize.width / @tileCount.x
            height: @screenshotSize.height / @tileCount.y

        xmlText = ""
        xmlText += "<annotation>\n"
        xmlText += "    <folder>images</folder>\n"
        xmlText += "    <filename>image_" + @trainNumber + ".jpg</filename>\n"
        xmlText += "    <size>\n"
        xmlText += "        <width>" + @screenshotSize.width + "</width>\n"
        xmlText += "        <height>" + @screenshotSize.height + "</height>\n"
        xmlText += "        <depth>3</depth>\n"
        xmlText += "    </size>\n"
        xmlText += "    <segmented>0</segmented>\n"
        for i in [0...@choosenFigures.length]
            x1 = @positions[i].x * screenshotTileSize.width
            y1 = @positions[i].y * screenshotTileSize.height
            x2 = x1 + screenshotTileSize.width
            y2 = y1 + screenshotTileSize.height

            x1 = Math.max(0, x1 - (screenshotTileSize.width * 0.25))
            y1 = Math.max(0, y1 - (screenshotTileSize.height * 0.25))
            x2 = Math.min(@screenshotSize.width - 1, x2 + (screenshotTileSize.width * 0.25))
            y2 = Math.min(@screenshotSize.height - 1, y2 + (screenshotTileSize.height * 0.25))

            xmlText += "    <object>\n"
            xmlText += "        <name>" + @choosenFigures[i] + "</name>\n"
            xmlText += "        <pose>Unspecified</pose>\n"
            xmlText += "        <truncated>0</truncated>\n"
            xmlText += "        <occluded>0</occluded>\n"
            xmlText += "        <difficult>0</difficult>\n"
            xmlText += "        <bndbox>\n"
            xmlText += "            <xmin>" + x1 + "</xmin>\n"
            xmlText += "            <ymin>" + y1 + "</ymin>\n"
            xmlText += "            <xmax>" + x2 + "</xmax>\n"
            xmlText += "            <ymax>" + y2 + "</ymax>\n"
            xmlText += "        </bndbox>\n"
            xmlText += "    </object>\n"
        xmlText += "</annotation>\n"

        @client.writeTextToFile("resources/tensorflow/images/image_" + @trainNumber + ".xml", xmlText, () =>
            console.log("Wrote XML!")
        )

    writeLabelMap: ->
        labelMapText = ""
        for i in [0...@figures.length]
            labelMapText += "item {\n"
            labelMapText += "  id: " + (i + 1) + "\n"
            labelMapText += "  name: '" + @figures[i] + "'\n"
            labelMapText += "}\n"

        @client.writeTextToFile("resources/tensorflow/data/label_map.pbtxt", labelMapText, () =>
            console.log("Wrote label map!")
        )

    randomInRange: (min, max) ->
        return Math.floor(Math.random() * (max - min)) + min

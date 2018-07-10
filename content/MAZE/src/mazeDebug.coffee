class MazeDebug
    constructor: (@client, @canvasWidth, @canvasHeight, @tileMapWidth, @tileMapHeight) ->
        @enabled = false

        @setupCameraCanvas()
        @setupVisualizationCanvas()

        @resetTileMap(false)

        @setupClickListener()

    setupClickListener: ->
        capturedSelf = this
        document.addEventListener("click", (event) => capturedSelf.didClick(event.clientX, event.clientY))

    didClick: (x, y) ->
        if @enabled
            @toggleTile(x, y)
        else
            @enableDebug()

    enableDebug: ->
        @enabled = true
        @setDebugCameraImage("assets/images/calibration/board_calibration.png")
        document.body.appendChild(@visualizationCanvas)

    setupCameraCanvas: ->
        @cameraCanvas = document.createElement("CANVAS")
        @cameraCanvas.style = "position: absolute; left: 0; top: 0; width: 100%; height: 100%;"
        @cameraCanvas.width = @canvasWidth
        @cameraCanvas.height = @canvasHeight

        context = @cameraCanvas.getContext("2d")
        context.clearRect(0, 0, @cameraCanvas.width, @cameraCanvas.height)

    setupVisualizationCanvas: ->
        @visualizationCanvas = document.createElement("CANVAS")
        @visualizationCanvas.style = "position: absolute; left: 0; top: 0; width: 100%; height: 100%;"
        @visualizationCanvas.width = @canvasWidth
        @visualizationCanvas.height = @canvasHeight

        context = @visualizationCanvas.getContext("2d")
        context.clearRect(0, 0, @visualizationCanvas.width, @visualizationCanvas.height)

    resetTileMap: (updateCanvas = false) ->
        @tileMap = ((0 for x in [1..@tileMapWidth]) for y in [1..@tileMapHeight])
        if updateCanvas
            @updateCanvas()

    updateCameraCanvas: ->
        context = @cameraCanvas.getContext("2d")
        context.fillStyle = "white"
        context.fillRect(0, 0, @visualizationCanvas.width, @visualizationCanvas.height)

        context.fillStyle = "black"
        for y in [0..@tileMapHeight - 1]
            for x in [0..@tileMapWidth - 1]
                if @tileMap[y][x] != 0
                    context.fillRect(x * @canvasWidth / @tileMapWidth, y * @canvasHeight / @tileMapHeight, @canvasWidth / @tileMapWidth, @canvasHeight / @tileMapHeight)

        @client.setDebugCameraCanvas(@cameraCanvas)

    updateVisualizationCanvas: ->
        context = @visualizationCanvas.getContext("2d")
        context.clearRect(0, 0, @cameraCanvas.width, @cameraCanvas.height)

        context.fillStyle = "rgba(0, 0, 0, 0.7)"
        for y in [0..@tileMapHeight - 1]
            for x in [0..@tileMapWidth - 1]
                if @tileMap[y][x] != 0
                    context.fillRect(x * @canvasWidth / @tileMapWidth, y * @canvasHeight / @tileMapHeight, @canvasWidth / @tileMapWidth, @canvasHeight / @tileMapHeight)

    toggleTile: (screenX, screenY) ->
        x = Math.floor(screenX * @tileMapWidth / window.innerWidth)
        y = Math.floor(screenY * @tileMapHeight / window.innerHeight)
        @tileMap[y][x] = 1 - @tileMap[y][x]

        @updateCameraCanvas()
        @updateVisualizationCanvas()

    setDebugCameraImage: (filename, completionCallback) ->
        image = new Image()
        image.onload = () => @client.setDebugCameraImage(image, completionCallback)
        image.src = filename

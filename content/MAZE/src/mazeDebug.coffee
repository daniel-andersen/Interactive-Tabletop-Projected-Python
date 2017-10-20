class MazeDebug
    constructor: (@client, @canvasWidth, @canvasHeight, @tileMapWidth, @tileMapHeight) ->
        @setupCameraCanvas()
        @setupClickListener()

    setupClickListener: ->
        capturedSelf = this
        document.addEventListener("click", (event) => capturedSelf.toggleTile(event.clientX, event.clientY))

    setupCameraCanvas: ->
        @canvas = document.createElement("CANVAS")
        @canvas.width = @canvasWidth
        @canvas.height = @canvasHeight

        ctx = @canvas.getContext("2d")
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, @canvasWidth, @canvasHeight)

        @resetTileMap(false)

    resetTileMap: (updateCanvas = false) ->
        @tileMap = ((0 for x in [1..@tileMapWidth]) for y in [1..@tileMapHeight])
        if updateCanvas
            @updateCanvas()

    updateCanvas: ->
        ctx = @canvas.getContext("2d")
        for y in [0..@tileMapHeight - 1]
            for x in [0..@tileMapWidth - 1]
                ctx.fillStyle = if @tileMap[y][x] == 0 then "white" else "black"
                ctx.fillRect(x * @canvasWidth / @tileMapWidth, y * @canvasHeight / @tileMapHeight, @canvasWidth / @tileMapWidth, @canvasHeight / @tileMapHeight)

        @client.setDebugCameraCanvas(@canvas)

    toggleTile: (screenX, screenY) ->
        x = Math.floor(screenX * @tileMapWidth / window.innerWidth)
        y = Math.floor(screenY * @tileMapHeight / window.innerHeight)
        @tileMap[y][x] = 1 - @tileMap[y][x]

        @updateCanvas()

    setDebugCameraImage: (filename, completionCallback) ->
        image = new Image()
        image.onload = () => @client.setDebugCameraImage(image, completionCallback)
        image.src = filename

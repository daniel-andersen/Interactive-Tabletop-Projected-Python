GameState =
    INITIALIZING: 0
    INITIAL_PLACEMENT: 1
    PLAYING_GAME: 2



class MazeGame

    constructor: ->
        @detectingBricks = false

        @client = new Client()
        @mazeModel = new MazeModel()
        @mazeDebug = new MazeDebug(@client, 1280, 800, @mazeModel.width, @mazeModel.height)

    start: ->
        @setupUi()

        @client.connect(
          (() => @reset()),
          ((json) => )
        )

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset(undefined, (action, payload) =>
            @calibrateBoard()
        )

    calibrateBoard: ->
        @client.calibrateBoard((action, payload) =>
            @startNewGame()
        )

    startNewGame: ->

        # Clear current server state
        @client.clearState(() =>

            # Initialize board area
            @boardArea = 0
            @client.initializeTiledBoardArea(@mazeModel.width, @mazeModel.height, 0.0, 0.0, 1.0, 1.0, @boardArea, (action, payload) =>

                # Prepare game state
                @gameState = GameState.INITIALIZING

                # Prepare map
                setTimeout(() =>
                    @mazeDebug.resetTileMap()
                    @resetMaze()
                    @ready()
                , 1500)

                # Fade logo
                setTimeout(() =>
                    @titleImage.style.opacity = '1'
                , 1500)
            )
        )

    setupUi: ->

        # Misc constants
        @tileAlphaDark = 0.2

        # Get document elements
        @contentDiv = document.getElementById("content")
        @renderedCanvases = [document.getElementById("renderedCanvasBehind"), document.getElementById("renderedCanvasFront")]
        @tileCanvas = document.getElementById("tileCanvas")
        @titleImage = document.getElementById("title")
        @transientObjectsOverlay = document.getElementById("transientObjectsOverlay")

        # Setup canvases
        @currentRenderedCanvasIndex = 0

        for canvas in [@renderedCanvases[0], @renderedCanvases[1], @tileCanvas]
            canvas.width = window.innerWidth
            canvas.height = window.innerHeight
            canvas.style.width = window.innerWidth
            canvas.style.height = window.innerHeight

        # Load tiles
        @tileImages = []
        for i in [0..16]
            image = new Image()
            image.src = "assets/images/tiles/tile_" + i + ".png"
            @tileImages[i] = image

        # Load visibility mask
        @visibilityMask = new Image()
        @visibilityMask.src = "assets/images/tiles/visibility_mask.png"

        # Load background image
        @backgroundImage = new Image()
        @backgroundImage.src = "assets/images/background.png"

        # Load player footprints
        @playerFootprintLeft = new Image()
        @playerFootprintLeft.src = "assets/images/footprints/player_footprint_left.png"
        @playerFootprintRight = new Image()
        @playerFootprintRight.src = "assets/images/footprints/player_footprint_right.png"

        # Create treasure
        @treasureImage = document.createElement("img")
        @treasureImage.src = "assets/images/treasure.png"
        @treasureImage.style.opacity = "0"
        @treasureImage.style.transition = "opacity 1s linear"
        @treasureImage.style.position = "absolute"
        @treasureImage.style.width = (100.0 / @mazeModel.width) + "%"
        @treasureImage.style.height = (100.0 / @mazeModel.height) + "%"
        @transientObjectsOverlay.appendChild(@treasureImage)

    waitForStartPositions: ->
        for player in @mazeModel.players
            @requestPlayerInitialPosition(player)

    brickMovedToPosition: (player, position) ->
        switch @gameState
            when GameState.INITIAL_PLACEMENT
                if position.equals(player.position)
                    @playerPlacedInitialBrick(player, position)
                else
                    @playerMovedInitialBrick(player, position)
            when GameState.PLAYING_GAME
                if player.index == @currentPlayer.index
                    @playerMovedBrick(position)

    playerPlacedInitialBrick: (player, position) ->

        # Check if first player
        activatedPlayers = (aPlayer for aPlayer in @mazeModel.players when aPlayer.state != PlayerState.INITIAL_PLACEMENT)

        firstPlayer = activatedPlayers.length == 0

        # Activate player
        @preparePlayerTurn(player)
        if firstPlayer
            player.state = PlayerState.TURN
        else
            player.state = PlayerState.IDLE

        # Hide logo and show treasure if first player activated
        if firstPlayer

            # Fade logo away
            @titleImage.style.opacity = '0'

            # Show treasure
            p = @positionOnScreenInPercentage(@mazeModel.treasurePosition.x, @mazeModel.treasurePosition.y)
            @treasureImage.style.left = p.x + "%"
            @treasureImage.style.top = p.y + "%"

            setTimeout(() =>
                @treasureImage.style.opacity = "1"
            , 2000)

        # Update MAZE
        @updateMaze(1, () =>
            if firstPlayer
                @requestPlayerPosition(player)
        )

    playerMovedInitialBrick: (player, position) ->

        # Disable players with no brick placed
        for aPlayer in @mazeModel.players
            if aPlayer.state != PlayerState.IDLE
                aPlayer.state = PlayerState.DISABLED

        # Get starting playing game
        @gameState = GameState.PLAYING_GAME

        # Move player
        player.state = PlayerState.TURN
        @currentPlayer = player

        @playerMovedBrick(position)

    playerMovedBrick: (position) ->

        # Cancel all running requests
        @client.cancelRequests(() =>

            # Get distance moved
            moveDistance = @mazeModel.distanceBetweenPositions(@currentPlayer.position, position)

            # Animate movement
            positions = @mazeModel.shortestPathBetweenPositions(@currentPlayer.position, position)
            positions.shift()

            @movePlayer(positions, () =>

                # Check if player found treasure
                if @currentPlayer.position.equals(@mazeModel.treasurePosition)
                    @playerDidFindTreasure(positions[positions.length - 1])
                    return

                # Next player turn
                if @currentPlayer.movementCount <= 0
                    setTimeout(() =>
                        @nextPlayerTurn()
                    , 750)
                    return

                # Keep rolling!
                @requestPlayerPosition(@currentPlayer)
            )
        )

    movePlayer: (positions, completionCallback = undefined) ->
        if positions.length == 0
            if completionCallback?
                completionCallback()
            return

        positions = positions.slice()
        position = positions.shift()

        # Decrease movement count
        @currentPlayer.movementCount -= 1

        # Add footprint
        @currentPlayer.addFootprintAtPosition(position)

        # Move player
        @currentPlayer.position = position

        # Update maze
        @updateMaze(0.75, () =>
            setTimeout(() =>
                @movePlayer(positions, completionCallback)
            , 10)
        )

    playerDidFindTreasure: (fromPosition) ->

        @updateMaze(1, () =>

            # Animate treasure to former position
            setTimeout(() =>
                p = @positionOnScreenInPercentage(fromPosition.x, fromPosition.y)
            , 1000)

            # Disappear
            setTimeout(() =>

                # Disable players
                for player in @mazeModel.players
                    player.state = PlayerState.DISABLED

                # Fade treasure
                @treasureImage.style.opacity = "0"

                # Clear maze
                @clearMaze()
                @updateMaze(1, () =>
                    @startNewGame()
                )
            , 4000)
        )

    requestPlayerInitialPosition: (player) ->
        positions = ([position.x, position.y] for position in @mazeModel.positionsViewableFromPosition(player.position, player.viewDistance))
        @client.detectTiledBrick(@boardArea, positions, [player.position.x, player.position.y], true, (action, payload) =>
            position = new Position(payload["tile"][0], payload["tile"][1])
            @playerPlacedInitialBrick(player, position)
        )

    requestPlayerPosition: (player) ->

        # Get reachable positions
        playerPositions = @mazeModel.positionsViewableFromPosition(player.position, player.movementCount)

        # Remove other players position
        for otherPlayer in @mazeModel.players
            if otherPlayer.state != PlayerState.DISABLED
                playerPositions = (position for position in playerPositions when not position.equals(otherPlayer.position))

        # Request position
        positions = ([position.x, position.y] for position in playerPositions)
        positions.push([player.position.x, player.position.y])

        @client.detectTiledBrickMovement(@boardArea, positions, [player.position.x, player.position.y], undefined, (action, payload) =>
            position = new Position(payload["position"][0], payload["position"][1])
            @brickMovedToPosition(player, position)
        )

    ready: ->

        # Fade maze
        setTimeout(() =>
            @updateMaze(1)
        , 1500)

        # Wait for start positions
        setTimeout(() =>
            @waitForStartPositions()
        , 2500)

    resetMaze: ->

        # Create random maze and reset players
        @mazeModel.createRandomMaze(2)

        # Reset game state
        @gameState = GameState.INITIAL_PLACEMENT
        @currentPlayer = @mazeModel.players[0]

        # Draw maze
        @drawMaze()
        @updateMaze(1)

    nextPlayerTurn: ->

        # Find next player
        index = @currentPlayer.index

        while true
            index = (index + 1) % @mazeModel.players.length
            if @mazeModel.players[index].state != PlayerState.DISABLED
                @currentPlayer = @mazeModel.players[index]
                break

        # Idle all players
        for player in @mazeModel.players
            if player.state != PlayerState.DISABLED
                player.state = PlayerState.IDLE

        # Next player
        @currentPlayer.state = PlayerState.TURN

        # Prepare player
        @preparePlayerTurn(@currentPlayer)

        # Update maze
        @updateMaze(2, () =>

            # Start brick move reporter
            @requestPlayerPosition(@currentPlayer)
        )

    preparePlayerTurn: (player) ->
        player.state = PlayerState.TURN

        player.reachDistance = playerDefaultReachDistance
        player.viewDistance = 1000
        player.movementCount = player.reachDistance

    clearMaze: ->
        @drawMaze()

    updateMaze: (time = 1, completionCallback = undefined) ->

        # Swap rendered canvas
        @currentRenderedCanvasIndex = 1 - @currentRenderedCanvasIndex

        # Tilemap black as default
        tileAlphaMap = ((0.0 for x in [1..@mazeModel.width]) for y in [1..@mazeModel.height])

        for y in [0...@mazeModel.height]
            for x in [0...@mazeModel.width]
                tileAlphaMap[y][x] = 0.0

        # Check if any players are active
        if @mazeModel.players?

            # Update player tiles
            drawOrder = (i for i in [0...@mazeModel.players.length])
            drawOrder.splice(@currentPlayer.index, 1)
            drawOrder.push(@currentPlayer.index)

            for playerIndex in drawOrder
                player = @mazeModel.players[playerIndex]
                if player.state == PlayerState.DISABLED
                    continue

                for position in @mazeModel.positionsViewableFromPosition(player.position, player.viewDistance)
                    tileAlphaMap[position.y][position.x] = @tileAlphaDark

                for position in @mazeModel.positionsViewableFromPosition(player.position, player.movementCount)
                    if player.state == PlayerState.TURN or (@gameState == GameState.INITIAL_PLACEMENT and player.state == PlayerState.INITIAL_PLACEMENT)
                        tileAlphaMap[position.y][position.x] = 1.0
                    else
                        tileAlphaMap[position.y][position.x] = @tileAlphaDark

        # Draw tiles, footprints etc.
        @drawMaze()

        # Prepare rendered canvas
        canvas = @renderedCanvases[@currentRenderedCanvasIndex]

        context = canvas.getContext("2d")
        context.clearRect(0, 0, canvas.width, canvas.height)

        # Draw dark tiles mask
        context.globalCompositeOperation = "source-over"
        for y in [0...@mazeModel.height]
            for x in [0...@mazeModel.width]
                if tileAlphaMap[y][x] > 0.0
                    context.drawImage(@visibilityMask, (x - 1) * window.innerWidth / @mazeModel.width, (y - 1) * window.innerHeight / @mazeModel.height, 3 * window.innerWidth / @mazeModel.width, 3 * window.innerHeight / @mazeModel.height)

        # Darken tiles
        context.globalCompositeOperation = "source-in"
        context.fillStyle = "rgba(0, 0, 0, " + @tileAlphaDark + ")"
        context.fillRect(0, 0, canvas.width, canvas.height)

        # Draw bright tiles mask
        context.globalCompositeOperation = "source-over"
        for y in [0...@mazeModel.height]
            for x in [0...@mazeModel.width]
                if tileAlphaMap[y][x] == 1.0
                    context.drawImage(@visibilityMask, (x - 1) * window.innerWidth / @mazeModel.width, (y - 1) * window.innerHeight / @mazeModel.height, 3 * window.innerWidth / @mazeModel.width, 3 * window.innerHeight / @mazeModel.height)

        # Draw tile map on top of mask
        context.globalCompositeOperation = "source-in"
        context.drawImage(@tileCanvas, 0, 0, window.innerWidth, window.innerHeight)

        # Fade canvas
        @renderedCanvases[1].style.transition = "opacity " + time + "s linear"
        @renderedCanvases[1].style.opacity = if @currentRenderedCanvasIndex == 0 then 0.0 else 1.0

        # Completion callback
        if completionCallback?
            setTimeout(() =>
                completionCallback()
            , (time * 1000) + 10)

    drawMaze: ->

        # Prepare canvas
        context = @tileCanvas.getContext("2d")
        context.clearRect(0, 0, @tileCanvas.width, @tileCanvas.height)

        # Draw background
        context.drawImage(@backgroundImage, 0, 0, window.innerWidth, window.innerHeight)

        # Draw tiles
        for y in [0...@mazeModel.height]
            for x in [0...@mazeModel.width]
                tile = @mazeModel.tileAtCoordinate(x, y)
                context.drawImage(@tileImages[tile.imageIndex], x * window.innerWidth / @mazeModel.width, y * window.innerHeight / @mazeModel.height, window.innerWidth / @mazeModel.width, window.innerHeight / @mazeModel.height)

        # Draw player footprints
        for player in @mazeModel.players
            for i in [0...player.footprints.length]
                footprint = player.footprints[i]

                width = window.innerWidth / @mazeModel.width
                height = window.innerHeight / @mazeModel.height

                x = (footprint.position.x * window.innerWidth / @mazeModel.width) + (width / 2.0)
                y = (footprint.position.y * window.innerHeight / @mazeModel.height) + (height / 2.0)

                rotation = footprint.direction * Math.PI / 2.0

                context.globalAlpha = (i + 1) / player.footprints.length

                context.translate(x, y)
                context.rotate(rotation)
                context.drawImage(@playerFootprintLeft, -width / 2.0, -height / 2.0, width, height)
                context.drawImage(@playerFootprintRight, -width / 2.0, -height / 2.0, width, height)
                context.rotate(-rotation)
                context.translate(-x, -y)

        context.globalAlpha = 1.0

    positionOnScreenInPercentage: (x, y) ->
        return new Position(x * 100.0 / @mazeModel.width, y * 100.0 / @mazeModel.height)

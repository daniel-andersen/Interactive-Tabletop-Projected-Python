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
        @mazeDebug.setDebugCameraImage("assets/images/board_calibration.png", (action, payload) =>
            @client.calibrateBoard((action, payload) =>
                @startNewGame()
            )
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
        @tileAlphaDark = 0.3

        # Get document elements
        @contentDiv = document.getElementById("content")
        @tileMapDiv = document.getElementById("tileMap")
        @blackOverlayMapDiv = document.getElementById("blackOverlayMap")
        @titleImage = document.getElementById("title")
        @transientObjectsOverlay = document.getElementById("transientObjectsOverlay")

        # Load tiles
        @tileImages = []
        for i in [1..16]
          image = new Image()
          image.src = "assets/images/tiles/tile_" + i + ".png"
          @tileImages.push(image)

        # Create image grid
        @tileMap = ((document.createElement('img') for x in [1..@mazeModel.width]) for y in [1..@mazeModel.height])
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                tile = @tileMap[y][x]
                tile.src = @tileImages[0].src
                tile.style.position = "absolute"
                tile.style.left = (x * 100.0 / @mazeModel.width) + "%"
                tile.style.top = (y * 100.0 / @mazeModel.height) + "%"
                tile.style.width = (100.0 / @mazeModel.width) + "%"
                tile.style.height = (100.0 / @mazeModel.height) + "%"
                @tileMapDiv.appendChild(tile)

        # Create black overlay grid
        @blackOverlayMap = ((document.createElement('div') for x in [1..@mazeModel.width]) for y in [1..@mazeModel.height])
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                overlay = @blackOverlayMap[y][x]
                overlay.style.background = "#000000"
                overlay.style.opacity = "1"
                overlay.style.transition = "opacity 1s linear"
                overlay.style.position = "absolute"
                overlay.style.left = (x * 100.0 / @mazeModel.width) + "%"
                overlay.style.top = (y * 100.0 / @mazeModel.height) + "%"
                overlay.style.width = (100.0 / @mazeModel.width) + "%"
                overlay.style.height = (100.0 / @mazeModel.height) + "%"
                @blackOverlayMapDiv.appendChild(overlay)

        # Create tile alpha map
        @tileAlphaMap = ((0.0 for x in [1..@mazeModel.width]) for y in [1..@mazeModel.height])
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                @tileAlphaMap[y][x] = 0.0

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

        # Activate player
        player.state = PlayerState.IDLE
        player.reachDistance = playerDefaultReachDistance

        # Set player turn if first player
        firstPlayer = true
        for aPlayer in @mazeModel.players
            if aPlayer.state == PlayerState.TURN
                firstPlayer = false

        if firstPlayer
            player.state = PlayerState.TURN

        # Hide logo and show treasure
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
        @updateMaze(() =>
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

            # Move player
            oldPosition = @currentPlayer.position
            @currentPlayer.position = position

            # Check finished
            if @currentPlayer.position.equals(@mazeModel.treasurePosition)
                @playerDidFindTreasure(oldPosition)
            else
                @nextPlayerTurn()
        )

    playerDidFindTreasure: (fromPosition) ->

        @updateMaze(() =>

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
                @updateMaze(() =>
                    @startNewGame()
                )
            , 4000)
        )

    requestPlayerInitialPosition: (player) ->
        positions = ([position.x, position.y] for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2))
        @client.detectTiledBrick(@boardArea, positions, [player.position.x, player.position.y], true, (action, payload) =>
            position = new Position(payload["tile"][0], payload["tile"][1])
            @playerPlacedInitialBrick(player, position)
        )

    requestPlayerPosition: (player) ->

        # Get reachable positions
        playerPositions = @mazeModel.positionsReachableByPlayer(player)

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
            @updateMaze()
        , 1500)

        # Wait for start positions
        setTimeout(() =>
            @waitForStartPositions()
        , 2500)

    resetMaze: ->

        # Create random maze and reset players
        @mazeModel.createRandomMaze()

        # Reset game state
        @gameState = GameState.INITIAL_PLACEMENT
        @currentPlayer = @mazeModel.players[0]

        # Draw maze
        @drawMaze()
        @updateMaze()

    nextPlayerTurn: ->

        # Update maze
        @updateMaze(() =>

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

            # Update maze
            @updateMaze(() =>

                # Start brick move reporter
                @requestPlayerPosition(@currentPlayer)
            )
        )

    clearMaze: ->
        @drawMaze()

    updateMaze: (completionCallback = undefined) ->

        # Tilemap black as default
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                @tileAlphaMap[y][x] = 0.0

        # Check if any players are active
        if @mazeModel.players?

            # Update player tiles
            drawOrder = (i for i in [0..@mazeModel.players.length - 1])
            drawOrder.splice(@currentPlayer.index, 1)
            drawOrder.push(@currentPlayer.index)

            for playerIndex in drawOrder
                player = @mazeModel.players[playerIndex]
                if player.state == PlayerState.DISABLED
                    continue

                for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2)
                    @tileAlphaMap[position.y][position.x] = @tileAlphaDark

                for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance)
                    @tileAlphaMap[position.y][position.x] = if player.state == PlayerState.TURN then 1.0 else @tileAlphaDark

        # Update tile map
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                overlay = @blackOverlayMap[y][x]
                overlay.style.opacity = 1.0 - @tileAlphaMap[y][x]

        # Completion callback
        if completionCallback?
            setTimeout(() =>
                completionCallback()
            , 1750)

    drawMaze: ->
        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                entry = @mazeModel.entryAtCoordinate(x, y)
                tile = @tileMap[y][x]
                tile.src = @tileImages[entry.tileIndex].src

    positionOnScreenInPercentage: (x, y) ->
        return new Position(x * 100.0 / @mazeModel.width, y * 100.0 / @mazeModel.height)

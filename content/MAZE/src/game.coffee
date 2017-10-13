GameState =
    INITIALIZING: 0
    INITIAL_PLACEMENT: 1
    PLAYING_GAME: 2



class MazeGame

    constructor: ->
        @client = new Client()
        @mazeModel = new MazeModel()
        @mazeDebug = new MazeDebug(@client, 1280, 800, @mazeModel.width, @mazeModel.height)

    start: ->
        @setupUi()

        @client.connect(
          (() => @reset()),
          ((json) => @onMessage(json))
        )

    stop: ->
        @client.disconnect()

    reset: ->
        @client.reset()

    onMessage: (json) ->
        switch json["action"]
            when "reset" then @calibrateBoard()
            when "calibrateBoard" then @startNewGame()
            when "brickFoundAtPosition" then @brickFoundAtPosition(json["payload"])
            when "brickMovedToPosition" then @brickMovedToPosition(json["payload"])

    calibrateBoard: ->
        @mazeDebug.setDebugCameraImage("assets/images/board_calibration.png", (action, payload) =>
            @client.calibrateBoard()
        )

    startNewGame: ->

        # Prepare game state
        @gameState = GameState.INITIALIZING

        # Prepare map
        setTimeout(() =>
            @resetMaze()
            @ready()
        , 1500)

        # Fade logo
        setTimeout(() =>
            @titleImage.style.opacity = '1'
        , 1500)

    setupUi: ->

        # Misc constants
        @tileAlphaDark = 0.3

        # Get document elements
        @contentDiv = document.getElementById("content")
        @tileMapDiv = document.getElementById("tileMap")
        @blackOverlayMapDiv = document.getElementById("blackOverlayMap")
        @titleImage = document.getElementById("title")

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
                overlay.onclick = () => @tileClicked(x, y)
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
        @treasureImage.style.width = (100.0 / @mazeModel.width) + "%"
        @treasureImage.style.height = (100.0 / @mazeModel.height) + "%"


    waitForStartPositions: ->
        for player in @mazeModel.players
            @requestPlayerInitialPosition(player)

    brickFoundAtPosition: (payload) ->
        player = @mazeModel.players[payload["id"]]
        position = new Position(payload["position"][0], payload["position"][1])
        @playerPlacedInitialBrick(player, position)

    brickMovedToPosition: (payload) ->
        player = @mazeModel.players[payload["id"]]
        position = new Position(payload["position"][0], payload["position"][1])

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
        player.state = PlayerState.IDLE
        player.reachDistance = playerDefaultReachDistance
        @updateMaze()

        # Start brick move reporter
        setTimeout(() =>
            @requestPlayerPosition(player)
        , 1500)

    playerMovedInitialBrick: (player, position) ->

        # Disable players with no brick placed
        for aPlayer in @mazeModel.players
            if aPlayer.state != PlayerState.IDLE
                aPlayer.state = PlayerState.DISABLED

        # Get starting playing game
        @gameState = GameState.PLAYING_GAME

        # Fade logo away
        @titleImage.style.opacity = '0'

        # Show treasure
        p = @positionOnMap(@mazeModel.treasurePosition.x, @mazeModel.treasurePosition.y)
        @treasureImage.style.left = (p.x * 100.0 / @mazeModel.width) + "%"
        @treasureImage.style.top = (p.y * 100.0 / @mazeModel.height) + "%"

        setTimeout(() =>
            @treasureImage.style.opacity = "1"
        , 1000)

        # Move player
        player.state = PlayerState.TURN
        @currentPlayer = player

        @playerMovedBrick(position)

    playerMovedBrick: (position) ->

        # Reset reporters
        @client.resetReporters()

        # Move player
        oldPosition = @currentPlayer.position
        @currentPlayer.position = position
        @updateMaze()

        # Check finished
        if @currentPlayer.position.equals(@mazeModel.treasurePosition)
            @playerDidFindTreasure(oldPosition)
        else
            @nextPlayerTurn()

    playerDidFindTreasure: (fromPosition) ->

        # Animate treasure to former position
        setTimeout(() =>
            p = @positionOnMap(fromPosition.x, fromPosition.y)
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
            @updateMaze()
        , 4000)

        # Restart game
        setTimeout(() =>
            @startNewGame()
            @reset()
        , 7000)

    requestPlayerInitialPosition: (player) ->
        positions = ([position.x, position.y] for position in @mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2))
        @client.reportBackWhenBrickMovedToPosition(0, [player.position.x, player.position.y], positions, player.index)

    requestPlayerPosition: (player) ->

        # Get reachable positions
        playerPositions = @mazeModel.positionsReachableByPlayer(player)

        # Remove other players position
        for otherPlayer in @mazeModel.players
            if otherPlayer.state != PlayerState.DISABLED
                playerPositions = (position for position in playerPositions when not position.equals(otherPlayer.position))

        # Request position
        positions = ([position.x, position.y] for position in playerPositions)
        @client.reportBackWhenBrickMovedToAnyOfPositions(0, [player.position.x, player.position.y], positions, player.index)

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

        # Find next player
        index = @currentPlayer.index

        while true
            index = (index + 1) % @mazeModel.players.length
            if @mazeModel.players[index].state != PlayerState.DISABLED
                @currentPlayer = @mazeModel.players[index]
                break

        for player in @mazeModel.players
            if player.state != PlayerState.DISABLED
                player.state = PlayerState.IDLE
        @currentPlayer.state = PlayerState.TURN

        # Update maze
        @updateMaze()

        # Start brick move reporter
        setTimeout(() =>
            @requestPlayerPosition(@currentPlayer)
        , 2000)

    clearMaze: ->
        @drawMaze()

    updateMaze: ->

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


    drawMaze: ->

        for y in [0..@mazeModel.height - 1]
            for x in [0..@mazeModel.width - 1]
                entry = @mazeModel.entryAtCoordinate(x, y)
                tile = @tileMap[y][x]
                tile.src = @tileImages[entry.tileIndex].src

    tileClicked: (x, y) ->
        console.log(x + ", " + y)

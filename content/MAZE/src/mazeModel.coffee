Wall =
    UP: 1
    RIGHT: 2
    DOWN: 4
    LEFT: 8

Direction =
    UP: 0
    RIGHT: 1
    DOWN: 2
    LEFT: 3

directionMovements = [[0, -1], [1, 0], [0, 1], [-1, 0]]

class Tile
    constructor: (@position, @walls = [Wall.UP, Wall.RIGHT, Wall.DOWN, Wall.LEFT]) ->

    wallSum: -> @walls.reduce( (((t, s) -> t + s)), 0)


class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @width = 32
        @height = 20

    createRandomMaze: ->

        # Place players
        @placePlayers()

        # Create maze
        @resetMaze()
        @createMaze()
        @placeTreasure()

        console.log("Treasure position: " + @treasurePosition.x + ", " + @treasurePosition.y)

    resetMaze: ->

        # Reset maze
        @tileMap = ((new Tile(new Position(x, y)) for x in [0...@width]) for y in [0...@height])

    placePlayers: ->
        @players = (new Player(i) for i in [0..@numberOfPlayers - 1])

        @players[0].position = new Position(@width / 2, 0)
        @players[1].position = new Position(@width - 1, @height / 2)
        @players[2].position = new Position(@width / 2, @height - 1)
        @players[3].position = new Position(0, @height / 2)

    placeTreasure: ->

        # Calculate distance maps
        distanceMaps = []
        for player in @players
            distanceMaps.push(@distanceMapForPlayer(player))

        # Calculate treasure position
        @treasurePosition = null
        bestScore = null

        for y in [0...@height]
            for x in [0...@width]

                # Check valid position
                isValid = true
                for i in [0..@players.length - 1]
                    if distanceMaps[i][y][x] == -1
                        isValid = false
                if not isValid
                    continue

                # Calculate score
                maxDistance = null
                minDistance = null
                for i in [0..@players.length - 1]
                    distance = distanceMaps[i][y][x]
                    maxDistance = if maxDistance == null then distance else Math.max(maxDistance, distance)
                    minDistance = if minDistance == null then distance else Math.min(minDistance, distance)

                score = maxDistance * maxDistance
                if bestScore == null or score < bestScore
                    bestScore = score
                    @treasurePosition = new Position(x, y)

    createMaze: ->

        # Reset visited tile map
        visitedMap = ((false for x in [0...@width]) for y in [0...@height])

        # Reset list of tiles to visit
        tileList = []

        # Add random start tile
        tileList.push(@tileAtCoordinate(Util.randomInRange(0, @width), Util.randomInRange(0, @height)))

        # Build maze
        while tileList.length > 0

            # Choose tile from tile list
            index = @chooseTileListIndex(tileList)

            tile = tileList[index]

            # Mark tile as visited
            visitedMap[tile.position.y][tile.position.x] = true

            # Get unvisited neighbors
            unvisitedNeighborTiles = @unvisitedNeighborsOfTile(tile, visitedMap)

            # Remove, if there are no unvisited neighbors
            if unvisitedNeighborTiles.length == 0
                tileList.splice(index, 1)
                continue

            # Pick random unvisited neighbor
            neighborIndex = Util.randomInRange(0, unvisitedNeighborTiles.length)

            neighborTile = unvisitedNeighborTiles[neighborIndex]

            # Carve path between tiles
            @carvePathBetweenTiles(tile, neighborTile)

            # Add tile to unvisited tile list
            tileList.push(neighborTile)

    carvePathBetweenTiles: (tile1, tile2) ->
        if tile1.position.x == tile2.position.x - 1
            @removeWallFromTile(tile1, Wall.RIGHT)
            @removeWallFromTile(tile2, Wall.LEFT)

        if tile1.position.x == tile2.position.x + 1
            @removeWallFromTile(tile1, Wall.LEFT)
            @removeWallFromTile(tile2, Wall.RIGHT)

        if tile1.position.y == tile2.position.y - 1
            @removeWallFromTile(tile1, Wall.DOWN)
            @removeWallFromTile(tile2, Wall.UP)

        if tile1.position.y == tile2.position.y + 1
            @removeWallFromTile(tile1, Wall.UP)
            @removeWallFromTile(tile2, Wall.DOWN)

    removeWallFromTile: (tile, wall) ->
        wallIndex = tile.walls.indexOf(wall)
        if wallIndex > -1
            tile.walls.splice(wallIndex, 1)

    chooseTileListIndex: (tileList) ->
        return tileList.length - 1

    unvisitedNeighborsOfTile: (tile, visitedMap) ->
        return (adjacentTile for adjacentTile in @adjacentTiles(tile) when not visitedMap[adjacentTile.position.y][adjacentTile.position.x])

    adjacentTiles: (tile) ->
        tiles = []

        p = new Position(tile.position.x - 1, tile.position.y)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        p = new Position(tile.position.x + 1, tile.position.y)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        p = new Position(tile.position.x, tile.position.y - 1)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        p = new Position(tile.position.x, tile.position.y + 1)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        return tiles

    adjacentConnectedTiles: (tile) ->
        return (adjacentTile for adjacentTile in @adjacentTiles(tile) when @areTilesConnected(tile, adjacentTile))

    areTilesConnected: (tile1, tile2) ->

        # Horizontally adjacent
        if tile1.position.y == tile2.position.y
            if tile1.position.x == tile2.position.x - 1
                return tile1.walls.indexOf(Wall.RIGHT) == -1
            if tile1.position.x == tile2.position.x + 1
                return tile1.walls.indexOf(Wall.LEFT) == -1

        # Vertically adjacent
        if tile1.position.x == tile2.position.x
            if tile1.position.y == tile2.position.y - 1
                return tile1.walls.indexOf(Wall.DOWN) == -1
            if tile1.position.y == tile2.position.y + 1
                return tile1.walls.indexOf(Wall.UP) == -1

        return false

    isPositionValid: (position) ->
        return position.x >= 0 and position.y >= 0 and position.x < @width and position.y < @height

    distanceMapForPlayer: (player) ->
        distanceMap = ((-1 for _ in [0...@width]) for _ in [0...@height])
        distanceMap[player.position.y][player.position.x] = 0

        unvisitedTiles = []
        unvisitedTiles.push(@tileAtPosition(player.position))

        while unvisitedTiles.length > 0
            tile = unvisitedTiles.splice(0, 1)[0]
            currentDistance = distanceMap[tile.position.y][tile.position.x]

            for adjacentTile in @adjacentConnectedTiles(tile)
                if distanceMap[adjacentTile.position.y][adjacentTile.position.x] == -1
                    distanceMap[adjacentTile.position.y][adjacentTile.position.x] = currentDistance + 1
                    unvisitedTiles.push(adjacentTile)

        return distanceMap

    positionsReachableByPlayer: (player) -> (tile.position for tile in @tilesReachableByPlayer(player))

    positionsReachableFromPosition: (position, maxDistance) -> (tile.position for tile in @tilesReachableFromPosition(position, maxDistance))

    tilesReachableByPlayer: (player) -> @tilesReachableFromPosition(player.position, player.reachDistance)

    tilesReachableFromPosition: (position, maxDistance) ->

        # Clear distance map
        distanceMap = ((-1 for _ in [0...@width]) for _ in [0...@height])
        distanceMap[position.y][position.x] = 0

        # Reset tiles
        tiles = []
        tilesToVisit = [@tileAtPosition(position)]

        # Keep expanding until reach distance reached for all positions to visit
        while tilesToVisit.length > 0
            tile = tilesToVisit.splice(0, 1)[0]
            distance = distanceMap[tile.position.y][tile.position.x]

            if distance >= maxDistance
                continue

            # Add to reachable tiles
            tiles.push(tile)

            # Visit all adjacent positions that has not yet been visited
            for adjacentTile in @adjacentConnectedTiles(tile)
                if distanceMap[adjacentTile.position.y][adjacentTile.position.x] == -1
                    distanceMap[adjacentTile.position.y][adjacentTile.position.x] = distance + 1
                    tilesToVisit.push(adjacentTile)

        return tiles

    tileAtPosition: (position) -> @tileAtCoordinate(position.x, position.y)

    tileAtCoordinate: (x, y) -> @tileMap[y][x]

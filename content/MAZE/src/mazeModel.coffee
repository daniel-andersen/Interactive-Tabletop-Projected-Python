Wall =
    UP: 1
    RIGHT: 2
    DOWN: 4
    LEFT: 8


class Tile
    constructor: (@position, @walls = [Wall.UP, Wall.RIGHT, Wall.DOWN, Wall.LEFT]) ->
        @imageIndex = 0

    wallSum: -> @walls.reduce( (((t, s) -> t + s)), 0)

    hasWall: (wall) -> @walls.indexOf(wall) != -1

    isSolid: -> @hasWall(Wall.UP) and @hasWall(Wall.RIGHT) and @hasWall(Wall.DOWN) and @hasWall(Wall.LEFT)

    isPath: -> not @isSolid()


class MazeModel

    constructor: ->
        @numberOfPlayers = 4

        @width = 39
        @height = 25

    createRandomMaze: (granularity=1) ->

        # Create maze
        @resetMaze()
        @createMaze(granularity)
        @calculateTileImageIndices()

        # Place players
        @placePlayers(granularity)

        # Place treasure
        @placeTreasure()

        console.log("Treasure position: " + @treasurePosition.x + ", " + @treasurePosition.y)

    resetMaze: ->

        # Reset maze
        @tileMap = ((new Tile(new Position(x, y)) for x in [0...@width]) for y in [0...@height])

    placePlayers: (granularity=1)->
        @players = (new Player(i) for i in [0..@numberOfPlayers - 1])

        @players[0].position = new Position(Math.floor(@width / granularity / 2) * granularity, 0)
        @players[1].position = new Position(Math.floor((@width - 1) / granularity) * granularity, Math.floor(@height / granularity / 2) * granularity)
        @players[2].position = new Position(Math.floor(@width / granularity / 2) * granularity, Math.floor((@height - 1) / granularity) * granularity)
        @players[3].position = new Position(0, Math.floor(@height / granularity / 2) * granularity)

        @players[0].addFootprintAtPosition(@players[0].position, Direction.DOWN)
        @players[1].addFootprintAtPosition(@players[1].position, Direction.LEFT)
        @players[2].addFootprintAtPosition(@players[2].position, Direction.UP)
        @players[3].addFootprintAtPosition(@players[3].position, Direction.RIGHT)

    placeTreasure: ->

        # Calculate distance maps
        distanceMaps = []
        for player in @players
            distanceMaps.push(@distanceMapFromPosition(player.position))

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
                summedDistance = 0
                for i in [0..@players.length - 1]
                    distance = distanceMaps[i][y][x]
                    maxDistance = if maxDistance == null then distance else Math.max(maxDistance, distance)
                    minDistance = if minDistance == null then distance else Math.min(minDistance, distance)
                    summedDistance += distance * distance

                score = summedDistance * minDistance

                if bestScore == null or score > bestScore
                    bestScore = score
                    @treasurePosition = new Position(x, y)

    createMaze: (granularity=1) ->

        # Reset visited tile map
        visitedMap = ((false for x in [0...@width]) for y in [0...@height])

        # Reset list of tiles to visit
        tileList = []

        # Add random start tile
        tileList.push(@tileAtPosition(@randomPosition(granularity)))

        # Build maze
        while tileList.length > 0

            # Choose tile from tile list
            index = @chooseTileListIndex(tileList)

            tile = tileList[index]

            # Mark tile as visited
            visitedMap[tile.position.y][tile.position.x] = true

            # Get unvisited neighbors
            unvisitedNeighborTiles = @unvisitedNeighborsOfTile(tile, visitedMap, granularity)

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

            # Mark as visited
            visitedMap[neighborTile.position.y][neighborTile.position.x] = true

    calculateTileImageIndices: ->
        for y in [0...@height]
            for x in [0...@width]
                tile = @tileAtCoordinate(x, y)

                if tile.isPath()
                    tile.imageIndex = 0
                else
                    tile.imageIndex = 1

                    p = new Position(tile.position.x, tile.position.y - 1)
                    if @isPositionValid(p) and @tileAtPosition(p).isPath() then tile.imageIndex += Wall.UP

                    p = new Position(tile.position.x + 1, tile.position.y)
                    if @isPositionValid(p) and @tileAtPosition(p).isPath() then tile.imageIndex += Wall.RIGHT

                    p = new Position(tile.position.x, tile.position.y + 1)
                    if @isPositionValid(p) and @tileAtPosition(p).isPath() then tile.imageIndex += Wall.DOWN

                    p = new Position(tile.position.x - 1, tile.position.y)
                    if @isPositionValid(p) and @tileAtPosition(p).isPath() then tile.imageIndex += Wall.LEFT

    carvePathBetweenTiles: (tile1, tile2) ->
        if tile1.position.x < tile2.position.x
            @removeWallFromTile(@tileAtCoordinate(x, tile1.position.y), Wall.RIGHT) for x in [tile1.position.x...tile2.position.x]
            @removeWallFromTile(@tileAtCoordinate(x, tile1.position.y), Wall.LEFT) for x in [tile1.position.x + 1..tile2.position.x]

        if tile1.position.x > tile2.position.x
            @removeWallFromTile(@tileAtCoordinate(x, tile1.position.y), Wall.RIGHT) for x in [tile2.position.x...tile1.position.x]
            @removeWallFromTile(@tileAtCoordinate(x, tile1.position.y), Wall.LEFT) for x in [tile2.position.x + 1..tile1.position.x]

        if tile1.position.y < tile2.position.y
            @removeWallFromTile(@tileAtCoordinate(tile1.position.x, y), Wall.DOWN) for y in [tile1.position.y...tile2.position.y]
            @removeWallFromTile(@tileAtCoordinate(tile1.position.x, y), Wall.UP) for y in [tile1.position.y + 1..tile2.position.y]

        if tile1.position.y > tile2.position.y
            @removeWallFromTile(@tileAtCoordinate(tile1.position.x, y), Wall.DOWN) for y in [tile2.position.y...tile1.position.y]
            @removeWallFromTile(@tileAtCoordinate(tile1.position.x, y), Wall.UP) for y in [tile2.position.y + 1..tile1.position.y]

    removeWallFromTile: (tile, wall) ->
        wallIndex = tile.walls.indexOf(wall)
        if wallIndex > -1
            tile.walls.splice(wallIndex, 1)

    chooseTileListIndex: (tileList) ->
        if Util.randomInRange(0, 4) == 0
            return Util.randomInRange(0, tileList.length)
        else
            return tileList.length - 1

    unvisitedNeighborsOfTile: (tile, visitedMap, granularity=1) ->
        return (adjacentTile for adjacentTile in @adjacentTiles(tile, granularity) when not visitedMap[adjacentTile.position.y][adjacentTile.position.x])

    adjacentTiles: (tile, granularity=1) ->
        tiles = []

        p = new Position(tile.position.x - granularity, tile.position.y)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        p = new Position(tile.position.x + granularity, tile.position.y)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        p = new Position(tile.position.x, tile.position.y - granularity)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        p = new Position(tile.position.x, tile.position.y + granularity)
        if @isPositionValid(p) then tiles.push(@tileAtPosition(p))

        return tiles

    adjacentConnectedTiles: (tile, granularity=1) ->
        return (adjacentTile for adjacentTile in @adjacentTiles(tile, granularity) when @areTilesConnected(tile, adjacentTile, granularity))

    areTilesConnected: (tile1, tile2, granularity=1) ->

        # Horizontally adjacent
        if tile1.position.y == tile2.position.y
            if tile1.position.x == tile2.position.x - granularity
                return not tile1.hasWall(Wall.RIGHT)
            if tile1.position.x == tile2.position.x + granularity
                return not tile1.hasWall(Wall.LEFT)

        # Vertically adjacent
        if tile1.position.x == tile2.position.x
            if tile1.position.y == tile2.position.y - granularity
                return not tile1.hasWall(Wall.DOWN)
            if tile1.position.y == tile2.position.y + granularity
                return not tile1.hasWall(Wall.UP)

        return false

    isPositionValid: (position) ->
        return position.x >= 0 and position.y >= 0 and position.x < @width and position.y < @height

    shortestPathBetweenPositions: (fromPosition, toPosition, granularity=1) ->
        distanceMap = @distanceMapFromPosition(toPosition, granularity)
        positions = [fromPosition]

        while not fromPosition.equals(toPosition)
            newPosition = undefined

            for p in [fromPosition.left(), fromPosition.right(), fromPosition.up(), fromPosition.down()]
                if @isPositionValid(p) and distanceMap[p.y][p.x] == distanceMap[fromPosition.y][fromPosition.x] - 1
                    newPosition = p

            if not newPosition?
                break

            fromPosition = newPosition
            positions.push(fromPosition)

        return positions

    distanceMapFromPosition: (position, granularity=1) ->
        distanceMap = ((-1 for _ in [0...@width]) for _ in [0...@height])
        distanceMap[position.y][position.x] = 0

        unvisitedTiles = []
        unvisitedTiles.push(@tileAtPosition(position))

        while unvisitedTiles.length > 0
            tile = unvisitedTiles.splice(0, 1)[0]
            currentDistance = distanceMap[tile.position.y][tile.position.x]

            for adjacentTile in @adjacentConnectedTiles(tile, granularity)
                if distanceMap[adjacentTile.position.y][adjacentTile.position.x] == -1
                    distanceMap[adjacentTile.position.y][adjacentTile.position.x] = currentDistance + 1
                    unvisitedTiles.push(adjacentTile)

        return distanceMap

    distanceBetweenPositions: (fromPosition, toPosition, granularity=1) ->
        distanceMap = @distanceMapFromPosition(fromPosition, granularity)
        return distanceMap[toPosition.y][toPosition.x]

    positionsViewableFromPosition: (position, maxDistance=1000, granularity=1) ->
        viewablePositions = [position]

        # Leftwards
        p = new Position(position.x, position.y)
        while @isPositionValid(p) and not @tileAtPosition(p).hasWall(Wall.LEFT) and position.distance(p) < maxDistance
            p = p.left()
            viewablePositions.push(p)

        # Rightwards
        p = new Position(position.x, position.y)
        while @isPositionValid(p) and not @tileAtPosition(p).hasWall(Wall.RIGHT) and position.distance(p) < maxDistance
            p = p.right()
            viewablePositions.push(p)

        # Upwards
        p = new Position(position.x, position.y)
        while @isPositionValid(p) and not @tileAtPosition(p).hasWall(Wall.UP) and position.distance(p) < maxDistance
            p = p.up()
            viewablePositions.push(p)

        # Downwards
        p = new Position(position.x, position.y)
        while @isPositionValid(p) and not @tileAtPosition(p).hasWall(Wall.DOWN) and position.distance(p) < maxDistance
            p = p.down()
            viewablePositions.push(p)

        return viewablePositions

    positionsReachableFromPosition: (position, maxDistance, granularity=1) -> (tile.position for tile in @tilesReachableFromPosition(position, maxDistance, granularity))

    tilesReachableFromPosition: (position, maxDistance, granularity=1) ->

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
            for adjacentTile in @adjacentConnectedTiles(tile, granularity)
                if distanceMap[adjacentTile.position.y][adjacentTile.position.x] == -1
                    distanceMap[adjacentTile.position.y][adjacentTile.position.x] = distance + 1
                    tilesToVisit.push(adjacentTile)

        return tiles

    tileAtPosition: (position) -> @tileAtCoordinate(position.x, position.y)

    tileAtCoordinate: (x, y) -> @tileMap[y][x]

    randomPosition: (granularity) ->
        return new Position(
            Util.randomInRange(0, @width / granularity) * granularity,
            Util.randomInRange(0, @height / granularity) * granularity
        )

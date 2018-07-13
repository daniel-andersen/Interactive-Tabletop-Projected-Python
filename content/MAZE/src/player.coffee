PlayerState =
    DISABLED: 0
    INITIAL_PLACEMENT: 1
    IDLE: 2
    TURN: 3


playerDefaultReachDistance = 5
playerFootprintCount = 10


class Footprint
    constructor: (@position, @direction) ->


class Player
    constructor: (index) ->
        @state = PlayerState.INITIAL_PLACEMENT
        @position = new Position()
        @reachDistance = 0
        @viewDistance = 1
        @movementCount = @reachDistance
        @index = index
        @footprints = []

    addFootprintAtPosition: (position, direction = undefined) ->
        if not direction?
            direction = Direction.UP
            if @footprints.length > 0
                previousFootprint = @footprints[@footprints.length - 1]
                if position.x == previousFootprint.position.x - 1
                    direction = Direction.LEFT
                if position.x == previousFootprint.position.x + 1
                    direction = Direction.RIGHT
                if position.y == previousFootprint.position.y - 1
                    direction = Direction.UP
                if position.y == previousFootprint.position.y + 1
                    direction = Direction.DOWN

        @footprints.push(new Footprint(position, direction))
        @footprints.shift() while @footprints.length > playerFootprintCount

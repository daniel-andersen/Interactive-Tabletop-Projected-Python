Direction =
    UP: 0
    RIGHT: 1
    DOWN: 2
    LEFT: 3


class Util
    @randomInRange: (min, max) -> Math.floor(Math.random() * (max - min) + min)


class Position
    constructor: (@x = 0, @y = 0) ->

    equals: (position) -> @x == position.x and @y == position.y

    distance: (position) -> Math.sqrt((@x - position.x) * (@x - position.x) + (@y - position.y) * (@y - position.y))

    left: -> new Position(@x - 1, @y)
    right: -> new Position(@x + 1, @y)
    up: -> new Position(@x, @y - 1)
    down: -> new Position(@x, @y + 1)

class Util
    @randomInRange: (min, max) -> Math.floor(Math.random() * (max - min) + min)

    @setDebugCameraImage: (filename, client, completionCallback) ->
        image = new Image()
        image.onload = () => client.setDebugCameraImage(image, completionCallback)
        image.src = filename


class Position
    constructor: (@x = 0, @y = 0) ->

    equals: (position) -> @x == position.x and @y == position.y

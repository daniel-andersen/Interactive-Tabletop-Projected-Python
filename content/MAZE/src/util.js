var Position, Util;

Util = (function() {
  function Util() {}

  Util.randomInRange = function(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
  };

  Util.setDebugCameraImage = function(filename, client, completionCallback) {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return client.setDebugCameraImage(image, completionCallback);
      };
    })(this);
    return image.src = filename;
  };

  return Util;

})();

Position = (function() {
  function Position(x, y) {
    this.x = x != null ? x : 0;
    this.y = y != null ? y : 0;
  }

  Position.prototype.equals = function(position) {
    return this.x === position.x && this.y === position.y;
  };

  return Position;

})();

//# sourceMappingURL=util.js.map

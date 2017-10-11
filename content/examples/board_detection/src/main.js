var BoardDetectionExample;

BoardDetectionExample = (function() {
  function BoardDetectionExample() {
    this.client = new Client();
  }

  BoardDetectionExample.prototype.start = function() {
    return this.client.connect(((function(_this) {
      return function() {
        return _this.reset();
      };
    })(this)), ((function(_this) {
      return function(json) {
        return _this.onMessage(json);
      };
    })(this)));
  };

  BoardDetectionExample.prototype.stop = function() {
    return this.client.disconnect();
  };

  BoardDetectionExample.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.setDebugCameraImage("board_calibration.png", function(action, payload) {
          return _this.calibrateBoard();
        });
      };
    })(this));
  };

  BoardDetectionExample.prototype.onMessage = function(json) {};

  BoardDetectionExample.prototype.setDebugCameraImage = function(filename, completionCallback) {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setDebugCameraImage(image, completionCallback);
      };
    })(this);
    return image.src = "assets/images/" + filename;
  };

  BoardDetectionExample.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {
        return console.log('Calibrated board!');
      };
    })(this));
  };

  return BoardDetectionExample;

})();

//# sourceMappingURL=main.js.map

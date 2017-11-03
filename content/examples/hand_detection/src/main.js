var HandDetectionExample;

HandDetectionExample = (function() {
  function HandDetectionExample() {
    this.client = new Client();
  }

  HandDetectionExample.prototype.start = function() {
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

  HandDetectionExample.prototype.stop = function() {
    return this.client.disconnect();
  };

  HandDetectionExample.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.calibrateBoard();
      };
    })(this));
  };

  HandDetectionExample.prototype.onMessage = function(json) {};

  HandDetectionExample.prototype.setDebugCameraImage = function(filename, completionCallback) {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setDebugCameraImage(image, completionCallback);
      };
    })(this);
    return image.src = "assets/images/" + filename;
  };

  HandDetectionExample.prototype.calibrateBoard = function() {
    return this.setDebugCameraImage("calibration/board_calibration.png", (function(_this) {
      return function(action, payload) {
        return _this.client.calibrateBoard(function(action, payload) {
          return _this.calibrateHandDetection();
        });
      };
    })(this));
  };

  HandDetectionExample.prototype.calibrateHandDetection = function() {
    return this.setDebugCameraImage("hand_initial.png", (function(_this) {
      return function(action, payload) {
        return _this.client.calibrateHandDetection(function(action, payload) {
          return console.log("Hand detection initialized!");
        });
      };
    })(this));
  };

  return HandDetectionExample;

})();

//# sourceMappingURL=main.js.map

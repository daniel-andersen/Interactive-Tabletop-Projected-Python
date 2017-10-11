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
        return _this.setupTensorflowDetector();
      };
    })(this));
  };

  BoardDetectionExample.prototype.setupTensorflowDetector = function() {
    return this.client.setupTensorflowDetector(0, "brick", (function(_this) {
      return function(action, payload) {
        return _this.detectBricks();
      };
    })(this));
  };

  BoardDetectionExample.prototype.detectBricks = function() {
    return this.setDebugCameraImage("brick_detection.png", (function(_this) {
      return function(action, payload) {
        return _this.client.detectImages(_this.client.boardAreaId_fullBoard, 0, function(action, payload) {
          console.log("Bricks detected!");
          return console.log(payload);
        });
      };
    })(this));
  };

  return BoardDetectionExample;

})();

//# sourceMappingURL=main.js.map

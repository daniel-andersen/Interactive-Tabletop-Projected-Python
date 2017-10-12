var TensorflowBrickDetectionExample;

TensorflowBrickDetectionExample = (function() {
  function TensorflowBrickDetectionExample() {
    this.client = new Client();
  }

  TensorflowBrickDetectionExample.prototype.start = function() {
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

  TensorflowBrickDetectionExample.prototype.stop = function() {
    return this.client.disconnect();
  };

  TensorflowBrickDetectionExample.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.setDebugCameraImage("board_calibration.png", function(action, payload) {
          return _this.calibrateBoard();
        });
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.onMessage = function(json) {};

  TensorflowBrickDetectionExample.prototype.setDebugCameraImage = function(filename, completionCallback) {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setDebugCameraImage(image, completionCallback);
      };
    })(this);
    return image.src = "assets/images/" + filename;
  };

  TensorflowBrickDetectionExample.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {
        return _this.setupTensorflowDetector();
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.setupTensorflowDetector = function() {
    return this.client.setupTensorflowDetector(0, "brick", (function(_this) {
      return function(action, payload) {
        return _this.detectBricks();
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.detectBricks = function() {
    return this.setDebugCameraImage("brick_detection.png", (function(_this) {
      return function(action, payload) {
        return _this.client.detectImages(_this.client.boardAreaId_fullBoard, 0, function(action, payload) {
          console.log("Bricks detected!");
          return console.log(payload);
        });
      };
    })(this));
  };

  return TensorflowBrickDetectionExample;

})();

//# sourceMappingURL=main.js.map

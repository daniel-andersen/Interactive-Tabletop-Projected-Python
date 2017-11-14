var ImageDetectionExample;

ImageDetectionExample = (function() {
  function ImageDetectionExample() {
    this.client = new Client();
  }

  ImageDetectionExample.prototype.start = function() {
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

  ImageDetectionExample.prototype.stop = function() {
    return this.client.disconnect();
  };

  ImageDetectionExample.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.setDebugCameraImage("calibration/board_calibration.png", function(action, payload) {
          return _this.calibrateBoard();
        });
      };
    })(this));
  };

  ImageDetectionExample.prototype.onMessage = function(json) {};

  ImageDetectionExample.prototype.setDebugCameraImage = function(filename, completionCallback) {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setDebugCameraImage(image, completionCallback);
      };
    })(this);
    return image.src = "assets/images/" + filename;
  };

  ImageDetectionExample.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {
        return _this.setupImageDetector();
      };
    })(this));
  };

  ImageDetectionExample.prototype.setupImageDetector = function() {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setupImageDetector(0, image, void 0, function(action, payload) {
          return _this.detectImages();
        });
      };
    })(this);
    return image.src = "assets/images/image_source.png";
  };

  ImageDetectionExample.prototype.detectImages = function() {
    return this.setDebugCameraImage("image_detection.png", (function(_this) {
      return function(action, payload) {
        return _this.client.detectImages(_this.client.boardAreaId_fullBoard, 0, function(action, payload) {
          console.log("Images detected!");
          return console.log(payload);
        });
      };
    })(this));
  };

  return ImageDetectionExample;

})();

//# sourceMappingURL=main.js.map

var RaspberryPiInstructions;

RaspberryPiInstructions = (function() {
  function RaspberryPiInstructions() {
    this.client = new Client();
  }

  RaspberryPiInstructions.prototype.start = function() {
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

  RaspberryPiInstructions.prototype.stop = function() {
    return this.client.disconnect();
  };

  RaspberryPiInstructions.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.calibrateBoard();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.onMessage = function(json) {};

  RaspberryPiInstructions.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {
        return _this.calibrateHandDetection();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.calibrateHandDetection = function() {
    return this.client.calibrateHandDetection((function(_this) {
      return function(action, payload) {
        return _this.setupImageDetector();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.setupImageDetector = function() {
    var image;
    this.raspberryPiDetectorId = 0;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setupImageDetector(_this.raspberryPiDetectorId, image, void 0, function(action, payload) {
          return _this.start();
        });
      };
    })(this);
    return image.src = "assets/images/raspberry_pi_source.png";
  };

  RaspberryPiInstructions.prototype.start = function() {
    return console.log("Ready!");
  };

  return RaspberryPiInstructions;

})();

//# sourceMappingURL=main.js.map

var RaspberryPiInstructions,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

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
        return _this.setupImageDetectors();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.onMessage = function(json) {};

  RaspberryPiInstructions.prototype.setupImageDetectors = function() {
    var raspberry_pi_source_image;
    this.raspberry_pi_detector_id = 0;
    this.image_detectors = [];
    raspberry_pi_source_image = new Image();
    raspberry_pi_source_image.onload = (function(_this) {
      return function() {
        return _this.client.setupImageDetector(0, raspberry_pi_source_image, void 0, function(action, payload) {
          return _this.didSetupImageDetector(_this.raspberry_pi_detector_id);
        });
      };
    })(this);
    return raspberry_pi_source_image.src = "assets/images/raspberry_pi_source.png";
  };

  RaspberryPiInstructions.prototype.didSetupImageDetector = function(id) {
    var ref;
    this.image_detectors.push(id);
    if (ref = this.raspberry_pi_detector_id, indexOf.call(this.image_detectors, ref) < 0) {
      return;
    }
    return this.calibrateBoard();
  };

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
        return _this.ready();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.ready = function() {
    console.log("Ready!");
    return this.client.cancelRequests(function(action, payload) {
      return this.detectRaspberryPi();
    });
  };

  RaspberryPiInstructions.prototype.detectRaspberryPi = function() {
    return this.client.detectImages(this.client.boardAreaId_fullBoard, this.raspberry_pi_detector_id, true, (function(_this) {
      return function(action, payload) {
        console.log("Found Raspberry Pi!");
        return console.log(payload);
      };
    })(this));
  };

  return RaspberryPiInstructions;

})();

//# sourceMappingURL=main.js.map

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
    this.initialize();
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.setupImageDetectors();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.onMessage = function(json) {};

  RaspberryPiInstructions.prototype.initialize = function() {
    return this.instruction_place_raspberry_pi_on_table = document.getElementById('instruction_place_raspberry_pi_on_table');
  };

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
    this.raspberryPiDetectionHistory = [];
    return this.client.cancelRequests((function(_this) {
      return function(action, payload) {
        return _this.detectRaspberryPi();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.detectRaspberryPi = function() {
    return this.client.detectImages(this.client.boardAreaId_fullBoard, this.raspberry_pi_detector_id, true, (function(_this) {
      return function(action, payload) {
        return _this.updateRaspberryPiDetection(payload);
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.updateRaspberryPiDetection = function(payload) {
    var any_detected, detected, entry, i, len, ref;
    detected = indexOf.call(payload, "matches") >= 0;
    document.getElementById('detection_state').style.backgroundColor = detected ? 'green' : 'red';
    this.raspberryPiDetectionHistory.push({
      'timestamp': new Date().getMilliseconds(),
      'detected': detected
    });
    while (this.raspberryPiDetectionHistory.length > 0 && this.raspberryPiDetectionHistory[0]['timestamp'] < new Date().getMilliseconds() - 2) {
      this.raspberryPiDetectionHistory.pop();
    }
    any_detected = false;
    ref = this.raspberryPiDetectionHistory;
    for (i = 0, len = ref.length; i < len; i++) {
      entry = ref[i];
      if (entry['detected']) {
        any_detected = true;
      }
    }
    if (any_detected && this.instruction_place_raspberry_pi_on_table.style.opacity === 0) {
      this.showInstructions();
    }
    if (!any_detected && this.instruction_place_raspberry_pi_on_table.style.opacity === 1) {
      return this.showPlaceRaspberryPiOnTable();
    }
  };

  RaspberryPiInstructions.prototype.showPlaceRaspberryPiOnTable = function() {
    return this.client.detectNonobstructedArea(this.client.boardAreaId_fullBoard, [242.0 / 1280.0, 70.0 / 800], [0.5, 0.0], (function(_this) {
      return function(action, payload) {
        var match;
        if (indexOf.call(payload, "matches") >= 0) {
          match = payload['matches'][0];
          _this.instruction_place_raspberry_pi_on_table.style.left = match['left'] + 'px';
          _this.instruction_place_raspberry_pi_on_table.style.top = match['top'] + 'px';
          return _this.instruction_place_raspberry_pi_on_table.style.opacity = 1;
        } else {
          return _this.showPlaceRaspberryPiOnTable();
        }
      };
    })(this));
  };

  return RaspberryPiInstructions;

})();

//# sourceMappingURL=main.js.map

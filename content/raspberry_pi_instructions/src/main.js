var RaspberryPiInstructions;

RaspberryPiInstructions = (function() {
  var State;

  State = {
    Initializing: 0,
    Ready: 1,
    PlaceRaspberryPiOnTable: 2,
    Instructions: 3
  };

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
    this.state = State.Initializing;
    this.element_place_raspberry_pi_on_table = document.getElementById('instructions_place_raspberry_pi_on_table');
    this.element_gpio_pinout = document.getElementById('instructions_gpio_pinout');
    this.element_gpio_pinout_left = document.getElementById('instructions_gpio_pinout_left');
    this.element_gpio_pinout_right = document.getElementById('instructions_gpio_pinout_right');
    this.element_raspi_overlay = document.getElementById('instructions_raspi_overlay');
    this.element_palm_overlay_1 = document.getElementById('instructions_palm_overlay_1');
    this.element_palm_overlay_2 = document.getElementById('instructions_palm_overlay_2');
    this.all_elements = [this.element_place_raspberry_pi_on_table, this.element_gpio_pinout, this.element_gpio_pinout_left, this.element_gpio_pinout_right, this.element_raspi_overlay, this.element_palm_overlay_1, this.element_palm_overlay_2];
    this.current_place_raspberry_pi_on_table_position = void 0;
    this.current_gpio_pinout_position = void 0;
    this.current_gpio_pinout_left_position = void 0;
    this.current_gpio_pinout_right_position = void 0;
    this.element_padding = 0.05;
    this.raspberry_pi_position = void 0;
    this.raspberry_pi_position_current = void 0;
    this.raspberry_pi_size = void 0;
    this.raspberry_pi_angle = void 0;
    return this.raspberry_pi_angle_current = void 0;
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
    this.image_detectors.push(id);
    if (!(this.raspberry_pi_detector_id in this.image_detectors)) {
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
    this.state = State.Ready;
    this.raspberryPiDetectionHistory = [];
    return this.client.cancelRequests((function(_this) {
      return function(action, payload) {
        _this.detectRaspberryPi();
        return _this.detectGestures();
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.detectRaspberryPi = function() {
    return this.client.detectImages(this.client.boardAreaId_fullBoard, this.raspberry_pi_detector_id, true, (function(_this) {
      return function(action, payload) {
        _this.updateRaspberryPiDetection(payload);
        return false;
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.detectGestures = function() {
    return this.client.detectGestures(this.client.boardAreaId_fullBoard, void 0, true, (function(_this) {
      return function(action, payload) {
        _this.updateGesture(payload);
        return false;
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.updateRaspberryPiDetection = function(payload) {
    var angle, count, detected, detected_count, entry, i, j, len, len1, position, ref, ref1, size;
    detected = "matches" in payload;
    this.raspberryPiDetectionHistory.push({
      'timestamp': this.currentTimeSeconds(),
      'detected': detected,
      'payload': payload
    });
    while (this.raspberryPiDetectionHistory.length > 0 && this.raspberryPiDetectionHistory[0]['timestamp'] < this.currentTimeSeconds() - 1.0) {
      this.raspberryPiDetectionHistory.shift();
    }
    detected_count = 0;
    ref = this.raspberryPiDetectionHistory;
    for (i = 0, len = ref.length; i < len; i++) {
      entry = ref[i];
      if (entry['detected']) {
        detected_count += 1;
      }
    }
    position = [0.0, 0.0];
    size = [0.0, 0.0];
    angle = 0;
    count = 0;
    ref1 = this.raspberryPiDetectionHistory;
    for (j = 0, len1 = ref1.length; j < len1; j++) {
      entry = ref1[j];
      if (entry['detected']) {
        payload = entry['payload']['matches'][0];
        position = [position[0] + payload['x'], position[1] + payload['y']];
        size = [size[0] + payload['width'], size[1] + payload['height']];
        angle = payload['angle'];
        count += 1;
      }
    }
    if (count > 0) {
      this.raspberry_pi_position = [position[0] / count, position[1] / count];
      this.raspberry_pi_size = [size[0] / count, size[1] / count];
      this.raspberry_pi_angle = Math.round(angle);
      if (this.raspberry_pi_angle >= 180 - 5) {
        this.raspberry_pi_angle = 180;
      }
      if (this.raspberry_pi_angle <= -180 + 5) {
        this.raspberry_pi_angle = -180;
      }
    }
    if (detected_count >= this.raspberryPiDetectionHistory.length / 2 && this.state !== State.Instructions) {
      this.showState(State.Instructions);
    }
    if (detected_count === 0 && this.state !== State.PlaceRaspberryPiOnTable) {
      return this.showState(State.PlaceRaspberryPiOnTable);
    }
  };

  RaspberryPiInstructions.prototype.updateGesture = function(payload) {
    var hand, hands, height, ref, ref1, width;
    if (!('hands' in payload)) {
      this.element_palm_overlay_1.style.opacity = 0;
      this.element_palm_overlay_2.style.opacity = 0;
      return;
    }
    hands = payload['hands'];
    if (hands.length > 0 && hands[0]['gesture'] === 2) {
      hand = hands[0];
      ref = [45.0 / 1280.0, 44.0 / 800.0], width = ref[0], height = ref[1];
      this.element_palm_overlay_1.style.left = ((hand['palmCenter']['x'] - (width / 2.0)) * 100.0) + '%';
      this.element_palm_overlay_1.style.top = ((hand['palmCenter']['y'] - (height / 2.0)) * 100.0) + '%';
      this.element_palm_overlay_1.style.opacity = 1;
    } else {
      this.element_palm_overlay_1.style.opacity = 0;
    }
    if (hands.length > 1 && hands[1]['gesture'] === 2) {
      hand = hands[1];
      ref1 = [45.0 / 1280.0, 45.0 / 800.0], width = ref1[0], height = ref1[1];
      this.element_palm_overlay_2.style.left = ((hand['palmCenter']['x'] - (width / 2.0)) * 100.0) + '%';
      this.element_palm_overlay_2.style.top = ((hand['palmCenter']['y'] - (height / 2.0)) * 100.0) + '%';
      return this.element_palm_overlay_2.style.opacity = 1;
    } else {
      return this.element_palm_overlay_2.style.opacity = 0;
    }
  };

  RaspberryPiInstructions.prototype.showState = function(state, completionCallback) {
    if (completionCallback == null) {
      completionCallback = (function(_this) {
        return function() {};
      })(this);
    }
    if (state === this.state) {
      return;
    }
    this.state = state;
    return this.hideCurrentState((function(_this) {
      return function() {
        switch (_this.state) {
          case State.PlaceRaspberryPiOnTable:
            _this.showPlaceRaspberryPiOnTable();
            break;
          case State.Instructions:
            _this.showInstructions();
        }
        return setTimeout(function() {
          return completionCallback();
        }, 300);
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.showPlaceRaspberryPiOnTable = function() {
    var height, ref, width;
    ref = [242.0 / 1280.0, 70.0 / 800.0], width = ref[0], height = ref[1];
    return this.client.detectNonobstructedArea(this.client.boardAreaId_fullBoard, [width, height], [0.5, 0.0], this.current_place_raspberry_pi_on_table_position, [this.element_padding, this.element_padding], 0.25, false, (function(_this) {
      return function(action, payload) {
        var match;
        if (_this.state === State.PlaceRaspberryPiOnTable) {
          if ("matches" in payload) {
            match = payload['matches'][0];
            _this.current_place_raspberry_pi_on_table_position = match['center'];
            _this.element_place_raspberry_pi_on_table.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%';
            _this.element_place_raspberry_pi_on_table.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%';
            _this.element_place_raspberry_pi_on_table.style.opacity = 1;
          }
          return _this.showPlaceRaspberryPiOnTable();
        }
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.showInstructions = function() {
    this.updateInstructionGpioPinoutPosition();
    return this.updateRaspiOverlayPosition();
  };

  RaspberryPiInstructions.prototype.updateInstructionGpioPinoutPosition = function() {
    var height, ref, width;
    ref = [640.0 / 1280.0, 208.0 / 800.0], width = ref[0], height = ref[1];
    return this.client.detectNonobstructedArea(this.client.boardAreaId_fullBoard, [width, height], [0.5, 0.0], this.current_gpio_pinout_position, [this.element_padding, this.element_padding], 0.25, false, (function(_this) {
      return function(action, payload) {
        var match;
        if (_this.state === State.Instructions) {
          if ("matches" in payload) {
            match = payload['matches'][0];
            _this.current_gpio_pinout_position = match['center'];
            _this.element_gpio_pinout.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%';
            _this.element_gpio_pinout.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%';
            _this.element_gpio_pinout.style.opacity = 1;
            _this.element_gpio_pinout_left.style.opacity = 0;
            _this.element_gpio_pinout_right.style.opacity = 0;
            return setTimeout(function() {
              return _this.updateInstructionGpioPinoutPosition();
            }, 150);
          } else {
            _this.current_gpio_pinout_position = void 0;
            _this.element_gpio_pinout.style.opacity = 0;
            return setTimeout(function() {
              return _this.updateInstructionGpioPinoutLeftPosition();
            }, 150);
          }
        }
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.updateInstructionGpioPinoutLeftPosition = function() {
    var height, ref, width;
    ref = [232.0 / 1280.0, 150.0 / 800.0], width = ref[0], height = ref[1];
    return this.client.detectNonobstructedArea(this.client.boardAreaId_fullBoard, [width, height], [0.0, 0.0], this.current_gpio_pinout_left_position, [this.element_padding, this.element_padding], 0.25, false, (function(_this) {
      return function(action, payload) {
        var match;
        if (_this.state === State.Instructions) {
          if ("matches" in payload) {
            match = payload['matches'][0];
            _this.current_gpio_pinout_left_position = match['center'];
            _this.element_gpio_pinout_left.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%';
            _this.element_gpio_pinout_left.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%';
            _this.element_gpio_pinout_left.style.opacity = 1;
          } else {
            _this.current_gpio_pinout_left_position = void 0;
            _this.element_gpio_pinout_left.style.opacity = 0;
          }
        }
        return setTimeout(function() {
          return _this.updateInstructionGpioPinoutRightPosition();
        }, 150);
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.updateInstructionGpioPinoutRightPosition = function() {
    var height, ref, width;
    ref = [230.0 / 1280.0, 150.0 / 800.0], width = ref[0], height = ref[1];
    return this.client.detectNonobstructedArea(this.client.boardAreaId_fullBoard, [width, height], [1.0, 0.0], this.current_gpio_pinout_right_position, [this.element_padding, this.element_padding], 0.25, false, (function(_this) {
      return function(action, payload) {
        var match;
        if (_this.state === State.Instructions) {
          if ("matches" in payload) {
            match = payload['matches'][0];
            _this.current_gpio_pinout_right_position = match['center'];
            _this.element_gpio_pinout_right.style.left = ((match['center'][0] - (width / 2.0)) * 100.0) + '%';
            _this.element_gpio_pinout_right.style.top = ((match['center'][1] - (height / 2.0)) * 100.0) + '%';
            _this.element_gpio_pinout_right.style.opacity = 1;
          } else {
            _this.current_gpio_pinout_right_position = void 0;
            _this.element_gpio_pinout_right.style.opacity = 0;
          }
        }
        return setTimeout(function() {
          return _this.updateInstructionGpioPinoutPosition();
        }, 150);
      };
    })(this));
  };

  RaspberryPiInstructions.prototype.updateRaspiOverlayPosition = function() {
    var height, ref, width;
    if (this.state !== State.Instructions) {
      return;
    }
    if (this.raspberry_pi_position != null) {
      ref = [580.0 / 1280.0, 280.0 / 800.0], width = ref[0], height = ref[1];
      if (this.isNewPosition(this.raspberry_pi_position_current, this.raspberry_pi_position)) {
        this.raspberry_pi_position_current = this.raspberry_pi_position;
        this.element_raspi_overlay.style.left = ((this.raspberry_pi_position[0] - (width * 0.5)) * 100.0) + 'vw';
        this.element_raspi_overlay.style.top = ((this.raspberry_pi_position[1] - (height * 0.5)) * 100.0) + 'vh';
      }
      if (this.isNewAngle(this.raspberry_pi_angle_current, this.raspberry_pi_angle)) {
        this.raspberry_pi_angle_current = this.raspberry_pi_angle;
        this.element_raspi_overlay.style.transform = 'rotate(' + (this.raspberry_pi_angle + 180.0) + 'deg)';
      }
      this.element_raspi_overlay.style.opacity = 1;
    }
    return setTimeout((function(_this) {
      return function() {
        return _this.updateRaspiOverlayPosition();
      };
    })(this), 100);
  };

  RaspberryPiInstructions.prototype.hideCurrentState = function(completionCallback) {
    var element, i, len, ref;
    if (completionCallback == null) {
      completionCallback = (function(_this) {
        return function() {};
      })(this);
    }
    ref = this.all_elements;
    for (i = 0, len = ref.length; i < len; i++) {
      element = ref[i];
      element.style.opacity = 0;
    }
    this.current_place_raspberry_pi_on_table_position = void 0;
    this.current_gpio_pinout_position = void 0;
    this.current_gpio_pinout_left_position = void 0;
    this.current_gpio_pinout_right_position = void 0;
    this.raspberry_pi_position = void 0;
    this.raspberry_pi_position_current = void 0;
    return setTimeout((function(_this) {
      return function() {
        return completionCallback();
      };
    })(this), 300);
  };

  RaspberryPiInstructions.prototype.isNewPosition = function(currentPosition, newPosition) {
    if ((currentPosition == null) || (newPosition == null)) {
      return true;
    }
    return Math.abs(currentPosition[0] - newPosition[0]) > 10.0 / 1280.0 || Math.abs(currentPosition[1] - newPosition[1]) > 10.0 / 800.0;
  };

  RaspberryPiInstructions.prototype.isNewAngle = function(currentAngle, newAngle) {
    var angle_diff;
    if ((currentAngle == null) || (newAngle == null)) {
      return true;
    }
    angle_diff = Math.abs(currentAngle - newAngle);
    return angle_diff >= 5.0 && angle_diff <= 360.0 - 5.0;
  };

  RaspberryPiInstructions.prototype.currentTimeSeconds = function() {
    return new Date().getTime() / 1000.0;
  };

  return RaspberryPiInstructions;

})();

//# sourceMappingURL=main.js.map

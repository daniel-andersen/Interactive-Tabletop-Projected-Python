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
        _this.ready();
        return _this.calibrateBoard();
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.onMessage = function(json) {};

  TensorflowBrickDetectionExample.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {
        return _this.ready();
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.ready = function() {
    return window.addEventListener('keydown', ((function(_this) {
      return function(event) {
        return _this.onKeydown(event);
      };
    })(this)), false);
  };

  TensorflowBrickDetectionExample.prototype.onKeydown = function(event) {
    console.log('Received keydown event: ' + event.keyCode);
    if (event.keyCode === 32) {
      return this.takeScreenshot();
    }
  };

  TensorflowBrickDetectionExample.prototype.takeScreenshot = function() {
    return this.client.takeScreenshot(void 0, (function(_this) {
      return function() {
        var flashElement;
        flashElement = document.getElementById("flash");
        flashElement.style.transition = "opacity 0s";
        flashElement.style.opacity = 1.0;
        return setTimeout(function() {
          flashElement.style.transition = "opacity 2s";
          return flashElement.style.opacity = 0.0;
        }, 10);
      };
    })(this));
  };

  return TensorflowBrickDetectionExample;

})();

//# sourceMappingURL=main.js.map

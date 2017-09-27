var BoardDetectionExample;

BoardDetectionExample = (function() {
  function BoardDetectionExample() {
    this.initialize();
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

  BoardDetectionExample.prototype.initialize = function() {
    this.ready = void 0;
    this.cornersVisible = true;
    this.markerRelaxationTime = 1.0;
    this.markersHistory = [];
    this.headHistory = [];
    this.visibleMarkerPosition = void 0;
    this.visibleMarkerAngle = void 0;
    this.wholeBoardArea = [0.3, 0.3, 0.7, 0.7];
    return this.aspectRatio = screen.width / screen.height;
  };

  BoardDetectionExample.prototype.reset = function() {
    return this.client.reset([1600, 1200], (function(_this) {
      return function(action, payload) {
        _this.client.enableDebug();
        return _this.calibrateBoard();
      };
    })(this));
  };

  BoardDetectionExample.prototype.onMessage = function(json) {
    switch (json["action"]) {
      case "recognizeBoard":
        if (json["result"] === "BOARD_RECOGNIZED") {
          return this.boardRecognized();
        }
    }
  };

  BoardDetectionExample.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {};
    })(this));
  };

  return BoardDetectionExample;

})();

//# sourceMappingURL=main.js.map

var MazeDebug;

MazeDebug = (function() {
  function MazeDebug(client, canvasWidth, canvasHeight, tileMapWidth, tileMapHeight) {
    this.client = client;
    this.canvasWidth = canvasWidth;
    this.canvasHeight = canvasHeight;
    this.tileMapWidth = tileMapWidth;
    this.tileMapHeight = tileMapHeight;
    this.enabled = false;
    this.setupCameraCanvas();
    this.setupVisualizationCanvas();
    this.resetTileMap(false);
    this.setupClickListener();
  }

  MazeDebug.prototype.setupClickListener = function() {
    var capturedSelf;
    capturedSelf = this;
    return document.addEventListener("click", (function(_this) {
      return function(event) {
        return capturedSelf.didClick(event.clientX, event.clientY);
      };
    })(this));
  };

  MazeDebug.prototype.didClick = function(x, y) {
    if (this.enabled) {
      return this.toggleTile(x, y);
    } else {
      return this.enableDebug();
    }
  };

  MazeDebug.prototype.enableDebug = function() {
    this.enabled = true;
    this.setDebugCameraImage("assets/images/calibration/board_calibration.png");
    return document.body.appendChild(this.visualizationCanvas);
  };

  MazeDebug.prototype.setupCameraCanvas = function() {
    var context;
    this.cameraCanvas = document.createElement("CANVAS");
    this.cameraCanvas.style = "position: absolute; left: 0; top: 0; width: 100%; height: 100%;";
    this.cameraCanvas.width = this.canvasWidth;
    this.cameraCanvas.height = this.canvasHeight;
    context = this.cameraCanvas.getContext("2d");
    return context.clearRect(0, 0, this.cameraCanvas.width, this.cameraCanvas.height);
  };

  MazeDebug.prototype.setupVisualizationCanvas = function() {
    var context;
    this.visualizationCanvas = document.createElement("CANVAS");
    this.visualizationCanvas.style = "position: absolute; left: 0; top: 0; width: 100%; height: 100%;";
    this.visualizationCanvas.width = this.canvasWidth;
    this.visualizationCanvas.height = this.canvasHeight;
    context = this.visualizationCanvas.getContext("2d");
    return context.clearRect(0, 0, this.visualizationCanvas.width, this.visualizationCanvas.height);
  };

  MazeDebug.prototype.resetTileMap = function(updateCanvas) {
    var x, y;
    if (updateCanvas == null) {
      updateCanvas = false;
    }
    this.tileMap = (function() {
      var i, ref, results;
      results = [];
      for (y = i = 1, ref = this.tileMapHeight; 1 <= ref ? i <= ref : i >= ref; y = 1 <= ref ? ++i : --i) {
        results.push((function() {
          var j, ref1, results1;
          results1 = [];
          for (x = j = 1, ref1 = this.tileMapWidth; 1 <= ref1 ? j <= ref1 : j >= ref1; x = 1 <= ref1 ? ++j : --j) {
            results1.push(0);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    if (updateCanvas) {
      return this.updateCanvas();
    }
  };

  MazeDebug.prototype.updateCameraCanvas = function() {
    var context, i, j, ref, ref1, x, y;
    context = this.cameraCanvas.getContext("2d");
    context.fillStyle = "white";
    context.fillRect(0, 0, this.visualizationCanvas.width, this.visualizationCanvas.height);
    context.fillStyle = "black";
    for (y = i = 0, ref = this.tileMapHeight - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
      for (x = j = 0, ref1 = this.tileMapWidth - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
        if (this.tileMap[y][x] !== 0) {
          context.fillRect(x * this.canvasWidth / this.tileMapWidth, y * this.canvasHeight / this.tileMapHeight, this.canvasWidth / this.tileMapWidth, this.canvasHeight / this.tileMapHeight);
        }
      }
    }
    return this.client.setDebugCameraCanvas(this.cameraCanvas);
  };

  MazeDebug.prototype.updateVisualizationCanvas = function() {
    var context, i, ref, results, x, y;
    context = this.visualizationCanvas.getContext("2d");
    context.clearRect(0, 0, this.cameraCanvas.width, this.cameraCanvas.height);
    context.fillStyle = "rgba(0, 0, 0, 0.7)";
    results = [];
    for (y = i = 0, ref = this.tileMapHeight - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
      results.push((function() {
        var j, ref1, results1;
        results1 = [];
        for (x = j = 0, ref1 = this.tileMapWidth - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
          if (this.tileMap[y][x] !== 0) {
            results1.push(context.fillRect(x * this.canvasWidth / this.tileMapWidth, y * this.canvasHeight / this.tileMapHeight, this.canvasWidth / this.tileMapWidth, this.canvasHeight / this.tileMapHeight));
          } else {
            results1.push(void 0);
          }
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeDebug.prototype.toggleTile = function(screenX, screenY) {
    var x, y;
    x = Math.floor(screenX * this.tileMapWidth / window.innerWidth);
    y = Math.floor(screenY * this.tileMapHeight / window.innerHeight);
    this.tileMap[y][x] = 1 - this.tileMap[y][x];
    this.updateCameraCanvas();
    return this.updateVisualizationCanvas();
  };

  MazeDebug.prototype.setDebugCameraImage = function(filename, completionCallback) {
    var image;
    image = new Image();
    image.onload = (function(_this) {
      return function() {
        return _this.client.setDebugCameraImage(image, completionCallback);
      };
    })(this);
    return image.src = filename;
  };

  return MazeDebug;

})();

//# sourceMappingURL=mazeDebug.js.map

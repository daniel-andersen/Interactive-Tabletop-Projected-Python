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
    return this.setDebugCameraImage("assets/images/board_calibration.png");
  };

  MazeDebug.prototype.setupCameraCanvas = function() {
    var ctx;
    this.canvas = document.createElement("CANVAS");
    this.canvas.width = this.canvasWidth;
    this.canvas.height = this.canvasHeight;
    ctx = this.canvas.getContext("2d");
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, this.canvasWidth, this.canvasHeight);
    return this.resetTileMap(false);
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

  MazeDebug.prototype.updateCanvas = function() {
    var ctx, i, j, ref, ref1, x, y;
    ctx = this.canvas.getContext("2d");
    for (y = i = 0, ref = this.tileMapHeight - 1; 0 <= ref ? i <= ref : i >= ref; y = 0 <= ref ? ++i : --i) {
      for (x = j = 0, ref1 = this.tileMapWidth - 1; 0 <= ref1 ? j <= ref1 : j >= ref1; x = 0 <= ref1 ? ++j : --j) {
        ctx.fillStyle = this.tileMap[y][x] === 0 ? "white" : "black";
        ctx.fillRect(x * this.canvasWidth / this.tileMapWidth, y * this.canvasHeight / this.tileMapHeight, this.canvasWidth / this.tileMapWidth, this.canvasHeight / this.tileMapHeight);
      }
    }
    return this.client.setDebugCameraCanvas(this.canvas);
  };

  MazeDebug.prototype.toggleTile = function(screenX, screenY) {
    var x, y;
    x = Math.floor(screenX * this.tileMapWidth / window.innerWidth);
    y = Math.floor(screenY * this.tileMapHeight / window.innerHeight);
    this.tileMap[y][x] = 1 - this.tileMap[y][x];
    return this.updateCanvas();
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

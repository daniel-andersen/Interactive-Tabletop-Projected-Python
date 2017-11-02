var GameState, MazeGame;

GameState = {
  INITIALIZING: 0,
  INITIAL_PLACEMENT: 1,
  PLAYING_GAME: 2
};

MazeGame = (function() {
  function MazeGame() {
    this.detectingBricks = false;
    this.client = new Client();
    this.mazeModel = new MazeModel();
    this.mazeDebug = new MazeDebug(this.client, 1280, 800, this.mazeModel.width, this.mazeModel.height);
  }

  MazeGame.prototype.start = function() {
    this.setupUi();
    return this.client.connect(((function(_this) {
      return function() {
        return _this.reset();
      };
    })(this)), ((function(_this) {
      return function(json) {};
    })(this)));
  };

  MazeGame.prototype.stop = function() {
    return this.client.disconnect();
  };

  MazeGame.prototype.reset = function() {
    return this.client.reset(void 0, (function(_this) {
      return function(action, payload) {
        return _this.calibrateBoard();
      };
    })(this));
  };

  MazeGame.prototype.calibrateBoard = function() {
    return this.client.calibrateBoard((function(_this) {
      return function(action, payload) {
        return _this.startNewGame();
      };
    })(this));
  };

  MazeGame.prototype.startNewGame = function() {
    return this.client.clearState((function(_this) {
      return function() {
        _this.boardArea = 0;
        return _this.client.initializeTiledBoardArea(_this.mazeModel.width, _this.mazeModel.height, 0.0, 0.0, 1.0, 1.0, _this.boardArea, function(action, payload) {
          _this.gameState = GameState.INITIALIZING;
          setTimeout(function() {
            _this.mazeDebug.resetTileMap();
            _this.resetMaze();
            return _this.ready();
          }, 1500);
          return setTimeout(function() {
            return _this.titleImage.style.opacity = '1';
          }, 1500);
        });
      };
    })(this));
  };

  MazeGame.prototype.setupUi = function() {
    var i, image, j, k, l, m, n, o, overlay, q, ref, ref1, ref2, ref3, ref4, ref5, tile, x, y;
    this.tileAlphaDark = 0.3;
    this.contentDiv = document.getElementById("content");
    this.tileMapDiv = document.getElementById("tileMap");
    this.blackOverlayMapDiv = document.getElementById("blackOverlayMap");
    this.titleImage = document.getElementById("title");
    this.transientObjectsOverlay = document.getElementById("transientObjectsOverlay");
    this.tileImages = [];
    for (i = j = 1; j <= 16; i = ++j) {
      image = new Image();
      image.src = "assets/images/tiles/tile_" + i + ".png";
      this.tileImages.push(image);
    }
    this.tileMap = (function() {
      var k, ref, results;
      results = [];
      for (y = k = 1, ref = this.mazeModel.height; 1 <= ref ? k <= ref : k >= ref; y = 1 <= ref ? ++k : --k) {
        results.push((function() {
          var l, ref1, results1;
          results1 = [];
          for (x = l = 1, ref1 = this.mazeModel.width; 1 <= ref1 ? l <= ref1 : l >= ref1; x = 1 <= ref1 ? ++l : --l) {
            results1.push(document.createElement('img'));
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    for (y = k = 0, ref = this.mazeModel.height - 1; 0 <= ref ? k <= ref : k >= ref; y = 0 <= ref ? ++k : --k) {
      for (x = l = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? l <= ref1 : l >= ref1; x = 0 <= ref1 ? ++l : --l) {
        tile = this.tileMap[y][x];
        tile.src = this.tileImages[0].src;
        tile.style.position = "absolute";
        tile.style.left = (x * 100.0 / this.mazeModel.width) + "%";
        tile.style.top = (y * 100.0 / this.mazeModel.height) + "%";
        tile.style.width = (100.0 / this.mazeModel.width) + "%";
        tile.style.height = (100.0 / this.mazeModel.height) + "%";
        this.tileMapDiv.appendChild(tile);
      }
    }
    this.blackOverlayMap = (function() {
      var m, ref2, results;
      results = [];
      for (y = m = 1, ref2 = this.mazeModel.height; 1 <= ref2 ? m <= ref2 : m >= ref2; y = 1 <= ref2 ? ++m : --m) {
        results.push((function() {
          var n, ref3, results1;
          results1 = [];
          for (x = n = 1, ref3 = this.mazeModel.width; 1 <= ref3 ? n <= ref3 : n >= ref3; x = 1 <= ref3 ? ++n : --n) {
            results1.push(document.createElement('div'));
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    for (y = m = 0, ref2 = this.mazeModel.height - 1; 0 <= ref2 ? m <= ref2 : m >= ref2; y = 0 <= ref2 ? ++m : --m) {
      for (x = n = 0, ref3 = this.mazeModel.width - 1; 0 <= ref3 ? n <= ref3 : n >= ref3; x = 0 <= ref3 ? ++n : --n) {
        overlay = this.blackOverlayMap[y][x];
        overlay.style.background = "#000000";
        overlay.style.opacity = "1";
        overlay.style.transition = "opacity 1s linear";
        overlay.style.position = "absolute";
        overlay.style.left = (x * 100.0 / this.mazeModel.width) + "%";
        overlay.style.top = (y * 100.0 / this.mazeModel.height) + "%";
        overlay.style.width = (100.0 / this.mazeModel.width) + "%";
        overlay.style.height = (100.0 / this.mazeModel.height) + "%";
        this.blackOverlayMapDiv.appendChild(overlay);
      }
    }
    this.tileAlphaMap = (function() {
      var o, ref4, results;
      results = [];
      for (y = o = 1, ref4 = this.mazeModel.height; 1 <= ref4 ? o <= ref4 : o >= ref4; y = 1 <= ref4 ? ++o : --o) {
        results.push((function() {
          var q, ref5, results1;
          results1 = [];
          for (x = q = 1, ref5 = this.mazeModel.width; 1 <= ref5 ? q <= ref5 : q >= ref5; x = 1 <= ref5 ? ++q : --q) {
            results1.push(0.0);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    for (y = o = 0, ref4 = this.mazeModel.height - 1; 0 <= ref4 ? o <= ref4 : o >= ref4; y = 0 <= ref4 ? ++o : --o) {
      for (x = q = 0, ref5 = this.mazeModel.width - 1; 0 <= ref5 ? q <= ref5 : q >= ref5; x = 0 <= ref5 ? ++q : --q) {
        this.tileAlphaMap[y][x] = 0.0;
      }
    }
    this.treasureImage = document.createElement("img");
    this.treasureImage.src = "assets/images/treasure.png";
    this.treasureImage.style.opacity = "0";
    this.treasureImage.style.transition = "opacity 1s linear";
    this.treasureImage.style.position = "absolute";
    this.treasureImage.style.width = (100.0 / this.mazeModel.width) + "%";
    this.treasureImage.style.height = (100.0 / this.mazeModel.height) + "%";
    return this.transientObjectsOverlay.appendChild(this.treasureImage);
  };

  MazeGame.prototype.waitForStartPositions = function() {
    var j, len, player, ref, results;
    ref = this.mazeModel.players;
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      player = ref[j];
      results.push(this.requestPlayerInitialPosition(player));
    }
    return results;
  };

  MazeGame.prototype.brickMovedToPosition = function(player, position) {
    switch (this.gameState) {
      case GameState.INITIAL_PLACEMENT:
        if (position.equals(player.position)) {
          return this.playerPlacedInitialBrick(player, position);
        } else {
          return this.playerMovedInitialBrick(player, position);
        }
        break;
      case GameState.PLAYING_GAME:
        if (player.index === this.currentPlayer.index) {
          return this.playerMovedBrick(position);
        }
    }
  };

  MazeGame.prototype.playerPlacedInitialBrick = function(player, position) {
    var aPlayer, firstPlayer, j, len, p, ref;
    player.state = PlayerState.IDLE;
    player.reachDistance = playerDefaultReachDistance;
    firstPlayer = true;
    ref = this.mazeModel.players;
    for (j = 0, len = ref.length; j < len; j++) {
      aPlayer = ref[j];
      if (aPlayer.state === PlayerState.TURN) {
        firstPlayer = false;
      }
    }
    if (firstPlayer) {
      player.state = PlayerState.TURN;
    }
    if (firstPlayer) {
      this.titleImage.style.opacity = '0';
      p = this.positionOnScreenInPercentage(this.mazeModel.treasurePosition.x, this.mazeModel.treasurePosition.y);
      this.treasureImage.style.left = p.x + "%";
      this.treasureImage.style.top = p.y + "%";
      setTimeout((function(_this) {
        return function() {
          return _this.treasureImage.style.opacity = "1";
        };
      })(this), 2000);
    }
    return this.updateMaze((function(_this) {
      return function() {
        if (firstPlayer) {
          return _this.requestPlayerPosition(player);
        }
      };
    })(this));
  };

  MazeGame.prototype.playerMovedInitialBrick = function(player, position) {
    var aPlayer, j, len, ref;
    ref = this.mazeModel.players;
    for (j = 0, len = ref.length; j < len; j++) {
      aPlayer = ref[j];
      if (aPlayer.state !== PlayerState.IDLE) {
        aPlayer.state = PlayerState.DISABLED;
      }
    }
    this.gameState = GameState.PLAYING_GAME;
    player.state = PlayerState.TURN;
    this.currentPlayer = player;
    return this.playerMovedBrick(position);
  };

  MazeGame.prototype.playerMovedBrick = function(position) {
    return this.client.cancelRequests((function(_this) {
      return function() {
        var oldPosition;
        oldPosition = _this.currentPlayer.position;
        _this.currentPlayer.position = position;
        if (_this.currentPlayer.position.equals(_this.mazeModel.treasurePosition)) {
          return _this.playerDidFindTreasure(oldPosition);
        } else {
          return _this.nextPlayerTurn();
        }
      };
    })(this));
  };

  MazeGame.prototype.playerDidFindTreasure = function(fromPosition) {
    return this.updateMaze((function(_this) {
      return function() {
        setTimeout(function() {
          var p;
          return p = _this.positionOnScreenInPercentage(fromPosition.x, fromPosition.y);
        }, 1000);
        return setTimeout(function() {
          var j, len, player, ref;
          ref = _this.mazeModel.players;
          for (j = 0, len = ref.length; j < len; j++) {
            player = ref[j];
            player.state = PlayerState.DISABLED;
          }
          _this.treasureImage.style.opacity = "0";
          _this.clearMaze();
          return _this.updateMaze(function() {
            return _this.startNewGame();
          });
        }, 4000);
      };
    })(this));
  };

  MazeGame.prototype.requestPlayerInitialPosition = function(player) {
    var position, positions;
    positions = (function() {
      var j, len, ref, results;
      ref = this.mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2);
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        position = ref[j];
        results.push([position.x, position.y]);
      }
      return results;
    }).call(this);
    return this.client.detectTiledBrick(this.boardArea, positions, [player.position.x, player.position.y], true, (function(_this) {
      return function(action, payload) {
        position = new Position(payload["tile"][0], payload["tile"][1]);
        return _this.playerPlacedInitialBrick(player, position);
      };
    })(this));
  };

  MazeGame.prototype.requestPlayerPosition = function(player) {
    var j, len, otherPlayer, playerPositions, position, positions, ref;
    playerPositions = this.mazeModel.positionsReachableByPlayer(player);
    ref = this.mazeModel.players;
    for (j = 0, len = ref.length; j < len; j++) {
      otherPlayer = ref[j];
      if (otherPlayer.state !== PlayerState.DISABLED) {
        playerPositions = (function() {
          var k, len1, results;
          results = [];
          for (k = 0, len1 = playerPositions.length; k < len1; k++) {
            position = playerPositions[k];
            if (!position.equals(otherPlayer.position)) {
              results.push(position);
            }
          }
          return results;
        })();
      }
    }
    positions = (function() {
      var k, len1, results;
      results = [];
      for (k = 0, len1 = playerPositions.length; k < len1; k++) {
        position = playerPositions[k];
        results.push([position.x, position.y]);
      }
      return results;
    })();
    positions.push([player.position.x, player.position.y]);
    return this.client.detectTiledBrickMovement(this.boardArea, positions, [player.position.x, player.position.y], void 0, (function(_this) {
      return function(action, payload) {
        position = new Position(payload["position"][0], payload["position"][1]);
        return _this.brickMovedToPosition(player, position);
      };
    })(this));
  };

  MazeGame.prototype.ready = function() {
    setTimeout((function(_this) {
      return function() {
        return _this.updateMaze();
      };
    })(this), 1500);
    return setTimeout((function(_this) {
      return function() {
        return _this.waitForStartPositions();
      };
    })(this), 2500);
  };

  MazeGame.prototype.resetMaze = function() {
    this.mazeModel.createRandomMaze();
    this.gameState = GameState.INITIAL_PLACEMENT;
    this.currentPlayer = this.mazeModel.players[0];
    this.drawMaze();
    return this.updateMaze();
  };

  MazeGame.prototype.nextPlayerTurn = function() {
    return this.updateMaze((function(_this) {
      return function() {
        var index, j, len, player, ref;
        index = _this.currentPlayer.index;
        while (true) {
          index = (index + 1) % _this.mazeModel.players.length;
          if (_this.mazeModel.players[index].state !== PlayerState.DISABLED) {
            _this.currentPlayer = _this.mazeModel.players[index];
            break;
          }
        }
        ref = _this.mazeModel.players;
        for (j = 0, len = ref.length; j < len; j++) {
          player = ref[j];
          if (player.state !== PlayerState.DISABLED) {
            player.state = PlayerState.IDLE;
          }
        }
        _this.currentPlayer.state = PlayerState.TURN;
        return _this.updateMaze(function() {
          return _this.requestPlayerPosition(_this.currentPlayer);
        });
      };
    })(this));
  };

  MazeGame.prototype.clearMaze = function() {
    return this.drawMaze();
  };

  MazeGame.prototype.updateMaze = function(completionCallback) {
    var drawOrder, i, j, k, l, len, len1, len2, m, n, o, overlay, player, playerIndex, position, q, ref, ref1, ref2, ref3, ref4, ref5, x, y;
    if (completionCallback == null) {
      completionCallback = void 0;
    }
    for (y = j = 0, ref = this.mazeModel.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      for (x = k = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
        this.tileAlphaMap[y][x] = 0.0;
      }
    }
    if (this.mazeModel.players != null) {
      drawOrder = (function() {
        var l, ref2, results;
        results = [];
        for (i = l = 0, ref2 = this.mazeModel.players.length - 1; 0 <= ref2 ? l <= ref2 : l >= ref2; i = 0 <= ref2 ? ++l : --l) {
          results.push(i);
        }
        return results;
      }).call(this);
      drawOrder.splice(this.currentPlayer.index, 1);
      drawOrder.push(this.currentPlayer.index);
      for (l = 0, len = drawOrder.length; l < len; l++) {
        playerIndex = drawOrder[l];
        player = this.mazeModel.players[playerIndex];
        if (player.state === PlayerState.DISABLED) {
          continue;
        }
        ref2 = this.mazeModel.positionsReachableFromPosition(player.position, player.reachDistance + 2);
        for (m = 0, len1 = ref2.length; m < len1; m++) {
          position = ref2[m];
          this.tileAlphaMap[position.y][position.x] = this.tileAlphaDark;
        }
        ref3 = this.mazeModel.positionsReachableFromPosition(player.position, player.reachDistance);
        for (n = 0, len2 = ref3.length; n < len2; n++) {
          position = ref3[n];
          this.tileAlphaMap[position.y][position.x] = player.state === PlayerState.TURN ? 1.0 : this.tileAlphaDark;
        }
      }
    }
    for (y = o = 0, ref4 = this.mazeModel.height - 1; 0 <= ref4 ? o <= ref4 : o >= ref4; y = 0 <= ref4 ? ++o : --o) {
      for (x = q = 0, ref5 = this.mazeModel.width - 1; 0 <= ref5 ? q <= ref5 : q >= ref5; x = 0 <= ref5 ? ++q : --q) {
        overlay = this.blackOverlayMap[y][x];
        overlay.style.opacity = 1.0 - this.tileAlphaMap[y][x];
      }
    }
    if (completionCallback != null) {
      return setTimeout((function(_this) {
        return function() {
          return completionCallback();
        };
      })(this), 1750);
    }
  };

  MazeGame.prototype.drawMaze = function() {
    var entry, j, ref, results, tile, x, y;
    results = [];
    for (y = j = 0, ref = this.mazeModel.height - 1; 0 <= ref ? j <= ref : j >= ref; y = 0 <= ref ? ++j : --j) {
      results.push((function() {
        var k, ref1, results1;
        results1 = [];
        for (x = k = 0, ref1 = this.mazeModel.width - 1; 0 <= ref1 ? k <= ref1 : k >= ref1; x = 0 <= ref1 ? ++k : --k) {
          entry = this.mazeModel.entryAtCoordinate(x, y);
          tile = this.tileMap[y][x];
          results1.push(tile.src = this.tileImages[entry.tileIndex].src);
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeGame.prototype.positionOnScreenInPercentage = function(x, y) {
    return new Position(x * 100.0 / this.mazeModel.width, y * 100.0 / this.mazeModel.height);
  };

  return MazeGame;

})();

//# sourceMappingURL=game.js.map

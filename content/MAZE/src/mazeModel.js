var Direction, MazeModel, Tile, Wall, directionMovements;

Wall = {
  UP: 1,
  RIGHT: 2,
  DOWN: 4,
  LEFT: 8
};

Direction = {
  UP: 0,
  RIGHT: 1,
  DOWN: 2,
  LEFT: 3
};

directionMovements = [[0, -1], [1, 0], [0, 1], [-1, 0]];

Tile = (function() {
  function Tile(position1, walls) {
    this.position = position1;
    this.walls = walls != null ? walls : [Wall.UP, Wall.RIGHT, Wall.DOWN, Wall.LEFT];
  }

  Tile.prototype.wallSum = function() {
    return this.walls.reduce((function(t, s) {
      return t + s;
    }), 0);
  };

  return Tile;

})();

MazeModel = (function() {
  function MazeModel() {
    this.numberOfPlayers = 4;
    this.width = 32;
    this.height = 20;
  }

  MazeModel.prototype.createRandomMaze = function() {
    this.placePlayers();
    this.resetMaze();
    this.createMaze();
    this.placeTreasure();
    return console.log("Treasure position: " + this.treasurePosition.x + ", " + this.treasurePosition.y);
  };

  MazeModel.prototype.resetMaze = function() {
    var x, y;
    return this.tileMap = (function() {
      var j, ref, results;
      results = [];
      for (y = j = 0, ref = this.height; 0 <= ref ? j < ref : j > ref; y = 0 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (x = k = 0, ref1 = this.width; 0 <= ref1 ? k < ref1 : k > ref1; x = 0 <= ref1 ? ++k : --k) {
            results1.push(new Tile(new Position(x, y)));
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.placePlayers = function() {
    var i;
    this.players = (function() {
      var j, ref, results;
      results = [];
      for (i = j = 0, ref = this.numberOfPlayers - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
        results.push(new Player(i));
      }
      return results;
    }).call(this);
    this.players[0].position = new Position(this.width / 2, 0);
    this.players[1].position = new Position(this.width - 1, this.height / 2);
    this.players[2].position = new Position(this.width / 2, this.height - 1);
    return this.players[3].position = new Position(0, this.height / 2);
  };

  MazeModel.prototype.placeTreasure = function() {
    var bestScore, distance, distanceMaps, i, isValid, j, k, len, maxDistance, minDistance, player, ref, ref1, results, score, x, y;
    distanceMaps = [];
    ref = this.players;
    for (j = 0, len = ref.length; j < len; j++) {
      player = ref[j];
      distanceMaps.push(this.distanceMapForPlayer(player));
    }
    this.treasurePosition = null;
    bestScore = null;
    results = [];
    for (y = k = 0, ref1 = this.height; 0 <= ref1 ? k < ref1 : k > ref1; y = 0 <= ref1 ? ++k : --k) {
      results.push((function() {
        var l, m, n, ref2, ref3, ref4, results1;
        results1 = [];
        for (x = l = 0, ref2 = this.width; 0 <= ref2 ? l < ref2 : l > ref2; x = 0 <= ref2 ? ++l : --l) {
          isValid = true;
          for (i = m = 0, ref3 = this.players.length - 1; 0 <= ref3 ? m <= ref3 : m >= ref3; i = 0 <= ref3 ? ++m : --m) {
            if (distanceMaps[i][y][x] === -1) {
              isValid = false;
            }
          }
          if (!isValid) {
            continue;
          }
          maxDistance = null;
          minDistance = null;
          for (i = n = 0, ref4 = this.players.length - 1; 0 <= ref4 ? n <= ref4 : n >= ref4; i = 0 <= ref4 ? ++n : --n) {
            distance = distanceMaps[i][y][x];
            maxDistance = maxDistance === null ? distance : Math.max(maxDistance, distance);
            minDistance = minDistance === null ? distance : Math.min(minDistance, distance);
          }
          score = maxDistance * maxDistance;
          if (bestScore === null || score < bestScore) {
            bestScore = score;
            results1.push(this.treasurePosition = new Position(x, y));
          } else {
            results1.push(void 0);
          }
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeModel.prototype.createMaze = function() {
    var index, neighborIndex, neighborTile, results, tile, tileList, unvisitedNeighborTiles, visitedMap, x, y;
    visitedMap = (function() {
      var j, ref, results;
      results = [];
      for (y = j = 0, ref = this.height; 0 <= ref ? j < ref : j > ref; y = 0 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (x = k = 0, ref1 = this.width; 0 <= ref1 ? k < ref1 : k > ref1; x = 0 <= ref1 ? ++k : --k) {
            results1.push(false);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    tileList = [];
    tileList.push(this.tileAtCoordinate(Util.randomInRange(0, this.width), Util.randomInRange(0, this.height)));
    results = [];
    while (tileList.length > 0) {
      index = this.chooseTileListIndex(tileList);
      tile = tileList[index];
      visitedMap[tile.position.y][tile.position.x] = true;
      unvisitedNeighborTiles = this.unvisitedNeighborsOfTile(tile, visitedMap);
      if (unvisitedNeighborTiles.length === 0) {
        tileList.splice(index, 1);
        continue;
      }
      neighborIndex = Util.randomInRange(0, unvisitedNeighborTiles.length);
      neighborTile = unvisitedNeighborTiles[neighborIndex];
      this.carvePathBetweenTiles(tile, neighborTile);
      results.push(tileList.push(neighborTile));
    }
    return results;
  };

  MazeModel.prototype.carvePathBetweenTiles = function(tile1, tile2) {
    if (tile1.position.x === tile2.position.x - 1) {
      this.removeWallFromTile(tile1, Wall.RIGHT);
      this.removeWallFromTile(tile2, Wall.LEFT);
    }
    if (tile1.position.x === tile2.position.x + 1) {
      this.removeWallFromTile(tile1, Wall.LEFT);
      this.removeWallFromTile(tile2, Wall.RIGHT);
    }
    if (tile1.position.y === tile2.position.y - 1) {
      this.removeWallFromTile(tile1, Wall.DOWN);
      this.removeWallFromTile(tile2, Wall.UP);
    }
    if (tile1.position.y === tile2.position.y + 1) {
      this.removeWallFromTile(tile1, Wall.UP);
      return this.removeWallFromTile(tile2, Wall.DOWN);
    }
  };

  MazeModel.prototype.removeWallFromTile = function(tile, wall) {
    var wallIndex;
    wallIndex = tile.walls.indexOf(wall);
    if (wallIndex > -1) {
      return tile.walls.splice(wallIndex, 1);
    }
  };

  MazeModel.prototype.chooseTileListIndex = function(tileList) {
    return tileList.length - 1;
  };

  MazeModel.prototype.unvisitedNeighborsOfTile = function(tile, visitedMap) {
    var adjacentTile;
    return (function() {
      var j, len, ref, results;
      ref = this.adjacentTiles(tile);
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        adjacentTile = ref[j];
        if (!visitedMap[adjacentTile.position.y][adjacentTile.position.x]) {
          results.push(adjacentTile);
        }
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.adjacentTiles = function(tile) {
    var p, tiles;
    tiles = [];
    p = new Position(tile.position.x - 1, tile.position.y);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    p = new Position(tile.position.x + 1, tile.position.y);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    p = new Position(tile.position.x, tile.position.y - 1);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    p = new Position(tile.position.x, tile.position.y + 1);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    return tiles;
  };

  MazeModel.prototype.adjacentConnectedTiles = function(tile) {
    var adjacentTile;
    return (function() {
      var j, len, ref, results;
      ref = this.adjacentTiles(tile);
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        adjacentTile = ref[j];
        if (this.areTilesConnected(tile, adjacentTile)) {
          results.push(adjacentTile);
        }
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.areTilesConnected = function(tile1, tile2) {
    if (tile1.position.y === tile2.position.y) {
      if (tile1.position.x === tile2.position.x - 1) {
        return tile1.walls.indexOf(Wall.RIGHT) === -1;
      }
      if (tile1.position.x === tile2.position.x + 1) {
        return tile1.walls.indexOf(Wall.LEFT) === -1;
      }
    }
    if (tile1.position.x === tile2.position.x) {
      if (tile1.position.y === tile2.position.y - 1) {
        return tile1.walls.indexOf(Wall.DOWN) === -1;
      }
      if (tile1.position.y === tile2.position.y + 1) {
        return tile1.walls.indexOf(Wall.UP) === -1;
      }
    }
    return false;
  };

  MazeModel.prototype.isPositionValid = function(position) {
    return position.x >= 0 && position.y >= 0 && position.x < this.width && position.y < this.height;
  };

  MazeModel.prototype.distanceMapForPlayer = function(player) {
    var _, adjacentTile, currentDistance, distanceMap, j, len, ref, tile, unvisitedTiles;
    distanceMap = (function() {
      var j, ref, results;
      results = [];
      for (_ = j = 0, ref = this.height; 0 <= ref ? j < ref : j > ref; _ = 0 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (_ = k = 0, ref1 = this.width; 0 <= ref1 ? k < ref1 : k > ref1; _ = 0 <= ref1 ? ++k : --k) {
            results1.push(-1);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    distanceMap[player.position.y][player.position.x] = 0;
    unvisitedTiles = [];
    unvisitedTiles.push(this.tileAtPosition(player.position));
    while (unvisitedTiles.length > 0) {
      tile = unvisitedTiles.splice(0, 1)[0];
      currentDistance = distanceMap[tile.position.y][tile.position.x];
      ref = this.adjacentConnectedTiles(tile);
      for (j = 0, len = ref.length; j < len; j++) {
        adjacentTile = ref[j];
        if (distanceMap[adjacentTile.position.y][adjacentTile.position.x] === -1) {
          distanceMap[adjacentTile.position.y][adjacentTile.position.x] = currentDistance + 1;
          unvisitedTiles.push(adjacentTile);
        }
      }
    }
    return distanceMap;
  };

  MazeModel.prototype.positionsReachableByPlayer = function(player) {
    var j, len, ref, results, tile;
    ref = this.tilesReachableByPlayer(player);
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      tile = ref[j];
      results.push(tile.position);
    }
    return results;
  };

  MazeModel.prototype.positionsReachableFromPosition = function(position, maxDistance) {
    var j, len, ref, results, tile;
    ref = this.tilesReachableFromPosition(position, maxDistance);
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      tile = ref[j];
      results.push(tile.position);
    }
    return results;
  };

  MazeModel.prototype.tilesReachableByPlayer = function(player) {
    return this.tilesReachableFromPosition(player.position, player.reachDistance);
  };

  MazeModel.prototype.tilesReachableFromPosition = function(position, maxDistance) {
    var _, adjacentTile, distance, distanceMap, j, len, ref, tile, tiles, tilesToVisit;
    distanceMap = (function() {
      var j, ref, results;
      results = [];
      for (_ = j = 0, ref = this.height; 0 <= ref ? j < ref : j > ref; _ = 0 <= ref ? ++j : --j) {
        results.push((function() {
          var k, ref1, results1;
          results1 = [];
          for (_ = k = 0, ref1 = this.width; 0 <= ref1 ? k < ref1 : k > ref1; _ = 0 <= ref1 ? ++k : --k) {
            results1.push(-1);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    distanceMap[position.y][position.x] = 0;
    tiles = [];
    tilesToVisit = [this.tileAtPosition(position)];
    while (tilesToVisit.length > 0) {
      tile = tilesToVisit.splice(0, 1)[0];
      distance = distanceMap[tile.position.y][tile.position.x];
      if (distance >= maxDistance) {
        continue;
      }
      tiles.push(tile);
      ref = this.adjacentConnectedTiles(tile);
      for (j = 0, len = ref.length; j < len; j++) {
        adjacentTile = ref[j];
        if (distanceMap[adjacentTile.position.y][adjacentTile.position.x] === -1) {
          distanceMap[adjacentTile.position.y][adjacentTile.position.x] = distance + 1;
          tilesToVisit.push(adjacentTile);
        }
      }
    }
    return tiles;
  };

  MazeModel.prototype.tileAtPosition = function(position) {
    return this.tileAtCoordinate(position.x, position.y);
  };

  MazeModel.prototype.tileAtCoordinate = function(x, y) {
    return this.tileMap[y][x];
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map

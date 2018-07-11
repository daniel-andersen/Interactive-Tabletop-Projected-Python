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
    this.imageIndex = 0;
  }

  Tile.prototype.wallSum = function() {
    return this.walls.reduce((function(t, s) {
      return t + s;
    }), 0);
  };

  Tile.prototype.hasWall = function(wall) {
    return this.walls.indexOf(wall) !== -1;
  };

  Tile.prototype.isSolid = function() {
    return this.hasWall(Wall.UP) && this.hasWall(Wall.RIGHT) && this.hasWall(Wall.DOWN) && this.hasWall(Wall.LEFT);
  };

  Tile.prototype.isPath = function() {
    return !this.isSolid();
  };

  return Tile;

})();

MazeModel = (function() {
  function MazeModel() {
    this.numberOfPlayers = 4;
    this.width = 39;
    this.height = 25;
  }

  MazeModel.prototype.createRandomMaze = function(granularity) {
    if (granularity == null) {
      granularity = 1;
    }
    this.resetMaze();
    this.createMaze(granularity);
    this.calculateTileImageIndices();
    this.placePlayers(granularity);
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

  MazeModel.prototype.placePlayers = function(granularity) {
    var i;
    if (granularity == null) {
      granularity = 1;
    }
    this.players = (function() {
      var j, ref, results;
      results = [];
      for (i = j = 0, ref = this.numberOfPlayers - 1; 0 <= ref ? j <= ref : j >= ref; i = 0 <= ref ? ++j : --j) {
        results.push(new Player(i));
      }
      return results;
    }).call(this);
    this.players[0].position = new Position(Math.floor(this.width / granularity / 2) * granularity, 0);
    this.players[1].position = new Position(Math.floor((this.width - 1) / granularity) * granularity, Math.floor(this.height / granularity / 2) * granularity);
    this.players[2].position = new Position(Math.floor(this.width / granularity / 2) * granularity, Math.floor((this.height - 1) / granularity) * granularity);
    return this.players[3].position = new Position(0, Math.floor(this.height / granularity / 2) * granularity);
  };

  MazeModel.prototype.placeTreasure = function() {
    var bestScore, distance, distanceMaps, i, isValid, j, k, len, maxDistance, minDistance, player, ref, ref1, results, score, summedDistance, x, y;
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
          summedDistance = 0;
          for (i = n = 0, ref4 = this.players.length - 1; 0 <= ref4 ? n <= ref4 : n >= ref4; i = 0 <= ref4 ? ++n : --n) {
            distance = distanceMaps[i][y][x];
            maxDistance = maxDistance === null ? distance : Math.max(maxDistance, distance);
            minDistance = minDistance === null ? distance : Math.min(minDistance, distance);
            summedDistance += distance * distance;
          }
          score = summedDistance * minDistance;
          if (bestScore === null || score > bestScore) {
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

  MazeModel.prototype.createMaze = function(granularity) {
    var index, neighborIndex, neighborTile, results, tile, tileList, unvisitedNeighborTiles, visitedMap, x, y;
    if (granularity == null) {
      granularity = 1;
    }
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
    tileList.push(this.tileAtPosition(this.randomPosition(granularity)));
    results = [];
    while (tileList.length > 0) {
      index = this.chooseTileListIndex(tileList);
      tile = tileList[index];
      visitedMap[tile.position.y][tile.position.x] = true;
      unvisitedNeighborTiles = this.unvisitedNeighborsOfTile(tile, visitedMap, granularity);
      if (unvisitedNeighborTiles.length === 0) {
        tileList.splice(index, 1);
        continue;
      }
      neighborIndex = Util.randomInRange(0, unvisitedNeighborTiles.length);
      neighborTile = unvisitedNeighborTiles[neighborIndex];
      this.carvePathBetweenTiles(tile, neighborTile);
      tileList.push(neighborTile);
      results.push(visitedMap[neighborTile.position.y][neighborTile.position.x] = true);
    }
    return results;
  };

  MazeModel.prototype.calculateTileImageIndices = function() {
    var j, p, ref, results, tile, x, y;
    results = [];
    for (y = j = 0, ref = this.height; 0 <= ref ? j < ref : j > ref; y = 0 <= ref ? ++j : --j) {
      results.push((function() {
        var k, ref1, results1;
        results1 = [];
        for (x = k = 0, ref1 = this.width; 0 <= ref1 ? k < ref1 : k > ref1; x = 0 <= ref1 ? ++k : --k) {
          tile = this.tileAtCoordinate(x, y);
          if (tile.isPath()) {
            results1.push(tile.imageIndex = 0);
          } else {
            tile.imageIndex = 1;
            p = new Position(tile.position.x, tile.position.y - 1);
            if (this.isPositionValid(p) && this.tileAtPosition(p).isPath()) {
              tile.imageIndex += Wall.UP;
            }
            p = new Position(tile.position.x + 1, tile.position.y);
            if (this.isPositionValid(p) && this.tileAtPosition(p).isPath()) {
              tile.imageIndex += Wall.RIGHT;
            }
            p = new Position(tile.position.x, tile.position.y + 1);
            if (this.isPositionValid(p) && this.tileAtPosition(p).isPath()) {
              tile.imageIndex += Wall.DOWN;
            }
            p = new Position(tile.position.x - 1, tile.position.y);
            if (this.isPositionValid(p) && this.tileAtPosition(p).isPath()) {
              results1.push(tile.imageIndex += Wall.LEFT);
            } else {
              results1.push(void 0);
            }
          }
        }
        return results1;
      }).call(this));
    }
    return results;
  };

  MazeModel.prototype.carvePathBetweenTiles = function(tile1, tile2) {
    var j, k, l, m, n, o, q, r, ref, ref1, ref10, ref11, ref12, ref13, ref14, ref15, ref2, ref3, ref4, ref5, ref6, ref7, ref8, ref9, results, x, y;
    if (tile1.position.x < tile2.position.x) {
      for (x = j = ref = tile1.position.x, ref1 = tile2.position.x; ref <= ref1 ? j < ref1 : j > ref1; x = ref <= ref1 ? ++j : --j) {
        this.removeWallFromTile(this.tileAtCoordinate(x, tile1.position.y), Wall.RIGHT);
      }
      for (x = k = ref2 = tile1.position.x + 1, ref3 = tile2.position.x; ref2 <= ref3 ? k <= ref3 : k >= ref3; x = ref2 <= ref3 ? ++k : --k) {
        this.removeWallFromTile(this.tileAtCoordinate(x, tile1.position.y), Wall.LEFT);
      }
    }
    if (tile1.position.x > tile2.position.x) {
      for (x = l = ref4 = tile2.position.x, ref5 = tile1.position.x; ref4 <= ref5 ? l < ref5 : l > ref5; x = ref4 <= ref5 ? ++l : --l) {
        this.removeWallFromTile(this.tileAtCoordinate(x, tile1.position.y), Wall.RIGHT);
      }
      for (x = m = ref6 = tile2.position.x + 1, ref7 = tile1.position.x; ref6 <= ref7 ? m <= ref7 : m >= ref7; x = ref6 <= ref7 ? ++m : --m) {
        this.removeWallFromTile(this.tileAtCoordinate(x, tile1.position.y), Wall.LEFT);
      }
    }
    if (tile1.position.y < tile2.position.y) {
      for (y = n = ref8 = tile1.position.y, ref9 = tile2.position.y; ref8 <= ref9 ? n < ref9 : n > ref9; y = ref8 <= ref9 ? ++n : --n) {
        this.removeWallFromTile(this.tileAtCoordinate(tile1.position.x, y), Wall.DOWN);
      }
      for (y = o = ref10 = tile1.position.y + 1, ref11 = tile2.position.y; ref10 <= ref11 ? o <= ref11 : o >= ref11; y = ref10 <= ref11 ? ++o : --o) {
        this.removeWallFromTile(this.tileAtCoordinate(tile1.position.x, y), Wall.UP);
      }
    }
    if (tile1.position.y > tile2.position.y) {
      for (y = q = ref12 = tile2.position.y, ref13 = tile1.position.y; ref12 <= ref13 ? q < ref13 : q > ref13; y = ref12 <= ref13 ? ++q : --q) {
        this.removeWallFromTile(this.tileAtCoordinate(tile1.position.x, y), Wall.DOWN);
      }
      results = [];
      for (y = r = ref14 = tile2.position.y + 1, ref15 = tile1.position.y; ref14 <= ref15 ? r <= ref15 : r >= ref15; y = ref14 <= ref15 ? ++r : --r) {
        results.push(this.removeWallFromTile(this.tileAtCoordinate(tile1.position.x, y), Wall.UP));
      }
      return results;
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
    if (Util.randomInRange(0, 4) === 0) {
      return Util.randomInRange(0, tileList.length);
    } else {
      return tileList.length - 1;
    }
  };

  MazeModel.prototype.unvisitedNeighborsOfTile = function(tile, visitedMap, granularity) {
    var adjacentTile;
    if (granularity == null) {
      granularity = 1;
    }
    return (function() {
      var j, len, ref, results;
      ref = this.adjacentTiles(tile, granularity);
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

  MazeModel.prototype.adjacentTiles = function(tile, granularity) {
    var p, tiles;
    if (granularity == null) {
      granularity = 1;
    }
    tiles = [];
    p = new Position(tile.position.x - granularity, tile.position.y);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    p = new Position(tile.position.x + granularity, tile.position.y);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    p = new Position(tile.position.x, tile.position.y - granularity);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    p = new Position(tile.position.x, tile.position.y + granularity);
    if (this.isPositionValid(p)) {
      tiles.push(this.tileAtPosition(p));
    }
    return tiles;
  };

  MazeModel.prototype.adjacentConnectedTiles = function(tile, granularity) {
    var adjacentTile;
    if (granularity == null) {
      granularity = 1;
    }
    return (function() {
      var j, len, ref, results;
      ref = this.adjacentTiles(tile, granularity);
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        adjacentTile = ref[j];
        if (this.areTilesConnected(tile, adjacentTile, granularity)) {
          results.push(adjacentTile);
        }
      }
      return results;
    }).call(this);
  };

  MazeModel.prototype.areTilesConnected = function(tile1, tile2, granularity) {
    if (granularity == null) {
      granularity = 1;
    }
    if (tile1.position.y === tile2.position.y) {
      if (tile1.position.x === tile2.position.x - granularity) {
        return !tile1.hasWall(Wall.RIGHT);
      }
      if (tile1.position.x === tile2.position.x + granularity) {
        return !tile1.hasWall(Wall.LEFT);
      }
    }
    if (tile1.position.x === tile2.position.x) {
      if (tile1.position.y === tile2.position.y - granularity) {
        return !tile1.hasWall(Wall.DOWN);
      }
      if (tile1.position.y === tile2.position.y + granularity) {
        return !tile1.hasWall(Wall.UP);
      }
    }
    return false;
  };

  MazeModel.prototype.isPositionValid = function(position) {
    return position.x >= 0 && position.y >= 0 && position.x < this.width && position.y < this.height;
  };

  MazeModel.prototype.distanceMapForPlayer = function(player, granularity) {
    var _, adjacentTile, currentDistance, distanceMap, j, len, ref, tile, unvisitedTiles;
    if (granularity == null) {
      granularity = 1;
    }
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
      ref = this.adjacentConnectedTiles(tile, granularity);
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

  MazeModel.prototype.positionsReachableByPlayer = function(player, granularity) {
    var j, len, ref, results, tile;
    if (granularity == null) {
      granularity = 1;
    }
    ref = this.tilesReachableByPlayer(player, granularity);
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      tile = ref[j];
      results.push(tile.position);
    }
    return results;
  };

  MazeModel.prototype.positionsReachableFromPosition = function(position, maxDistance, granularity) {
    var j, len, ref, results, tile;
    if (granularity == null) {
      granularity = 1;
    }
    ref = this.tilesReachableFromPosition(position, maxDistance, granularity);
    results = [];
    for (j = 0, len = ref.length; j < len; j++) {
      tile = ref[j];
      results.push(tile.position);
    }
    return results;
  };

  MazeModel.prototype.tilesReachableByPlayer = function(player, granularity) {
    if (granularity == null) {
      granularity = 1;
    }
    return this.tilesReachableFromPosition(player.position, player.reachDistance, granularity);
  };

  MazeModel.prototype.tilesReachableFromPosition = function(position, maxDistance, granularity) {
    var _, adjacentTile, distance, distanceMap, j, len, ref, tile, tiles, tilesToVisit;
    if (granularity == null) {
      granularity = 1;
    }
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
      ref = this.adjacentConnectedTiles(tile, granularity);
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

  MazeModel.prototype.randomPosition = function(granularity) {
    return new Position(Util.randomInRange(0, this.width / granularity) * granularity, Util.randomInRange(0, this.height / granularity) * granularity);
  };

  return MazeModel;

})();

//# sourceMappingURL=mazeModel.js.map

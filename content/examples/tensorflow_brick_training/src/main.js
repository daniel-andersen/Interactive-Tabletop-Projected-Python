var TensorflowBrickDetectionExample;

TensorflowBrickDetectionExample = (function() {
  function TensorflowBrickDetectionExample() {
    this.client = new Client();
    this.figures = ["Black", "Red", "Blue", "Green"];
    this.backgroundCount = 2;
    this.tileCount = {
      x: 32,
      y: 20
    };
    this.tileSize = {
      width: window.innerWidth / this.tileCount.x,
      height: window.innerHeight / this.tileCount.y
    };
    this.aspectRatio = 640 / window.innerWidth;
    this.screenshotSize = {
      width: 640,
      height: this.aspectRatio * window.innerHeight
    };
    this.tiles = [
      {
        "filename": "tiles1.png",
        "tilemap": ["      ", " ***  ", " **** ", " ***  ", "      "]
      }, {
        "filename": "tiles2.png",
        "tilemap": ["         ", "   ****  ", " ******* ", "   ****  ", "   ****  ", "     *   ", "         "]
      }, {
        "filename": "tiles3.png",
        "tilemap": ["     ", " *** ", " *** ", " *** ", " *   ", "     "]
      }, {
        "filename": "tiles4.png",
        "tilemap": ["      ", " **** ", "  *** ", "  *** ", "      "]
      }, {
        "filename": "tiles5.png",
        "tilemap": ["       ", "    *  ", "   *** ", " ***** ", "   *** ", "       "]
      }, {
        "filename": "tiles6.png",
        "tilemap": ["        ", " ****   ", " ****** ", " ****   ", " ****   ", "  *     ", "  *     ", "        "]
      }, {
        "filename": "tiles7.png",
        "tilemap": ["     ", "  *  ", "  *  ", " *** ", " *** ", " *** ", "     "]
      }, {
        "filename": "tiles8.png",
        "tilemap": ["      ", " **** ", " **   ", " **   ", " **   ", " *    ", " *    ", "      "]
      }, {
        "filename": "tiles9.png",
        "tilemap": ["      ", " **** ", " **** ", " **** ", " **** ", "  *   ", "      "]
      }, {
        "filename": "tiles10.png",
        "tilemap": ["     ", " *** ", " *** ", " *** ", "     "]
      }, {
        "filename": "tiles11.png",
        "tilemap": ["   ", " * ", " * ", " * ", " * ", "   "]
      }, {
        "filename": "tiles12.png",
        "tilemap": ["     ", " *** ", " *   ", " *   ", "     "]
      }
    ];
    this.backgroundDiv = document.getElementById("background");
    this.markersDiv = document.getElementById("markers");
    this.tilesDiv = document.getElementById("tiles");
    this.flashDiv = document.getElementById("flash");
    this.maskElement = document.getElementById("mask");
    this.trainNumber = 0;
    this.readyForScreenshot = false;
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
        return _this.client.setDebugCameraImageFilename("assets/images/calibration/board_calibration.png", function(action, payload) {
          return _this.calibrateBoard();
        });
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
    window.addEventListener('keydown', ((function(_this) {
      return function(event) {
        return _this.onKeydown(event);
      };
    })(this)), false);
    this.writeLabelMap();
    return this.presentNewBackground();
  };

  TensorflowBrickDetectionExample.prototype.presentNewBackground = function() {
    if (this.markersDiv.firstChild != null) {
      this.backgroundDiv.style.opacity = '0';
      setTimeout((function(_this) {
        return function() {
          while (_this.markersDiv.firstChild != null) {
            _this.markersDiv.removeChild(_this.markersDiv.firstChild);
          }
          while (_this.tilesDiv.firstChild != null) {
            _this.tilesDiv.removeChild(_this.tilesDiv.firstChild);
          }
          while (_this.maskElement.firstChild != null) {
            _this.maskElement.removeChild(_this.maskElement.firstChild);
          }
          return _this.presentNewBackground();
        };
      })(this), 1000);
      return;
    }
    if (Math.random() <= 0.75) {
      this.presentRandomTiles();
    } else {
      this.presentRandomBackground();
    }
    this.pickRandomPositions();
    setTimeout((function(_this) {
      return function() {
        _this.markersDiv.style.opacity = '1';
        _this.backgroundDiv.style.opacity = '1';
        return setTimeout(function() {
          return _this.readyForScreenshot = true;
        }, 1000);
      };
    })(this), 100);
    return this.trainNumber += 1;
  };

  TensorflowBrickDetectionExample.prototype.presentRandomTiles = function() {
    var i, j, k, l, m, n, o, p, positionValid, ref, ref1, ref2, ref3, ref4, results, tile, tileCount, tileImg, tileNumber, tilePosition, tilemap;
    this.tilePositions = [];
    tilemap = (function() {
      var l, ref, results;
      results = [];
      for (i = l = 0, ref = this.tileCount.y; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {
        results.push((function() {
          var m, ref1, results1;
          results1 = [];
          for (j = m = 0, ref1 = this.tileCount.x; 0 <= ref1 ? m < ref1 : m > ref1; j = 0 <= ref1 ? ++m : --m) {
            results1.push(false);
          }
          return results1;
        }).call(this));
      }
      return results;
    }).call(this);
    results = [];
    for (k = l = 0, ref = this.randomInRange(3, 6); 0 <= ref ? l < ref : l > ref; k = 0 <= ref ? ++l : --l) {
      tileNumber = this.randomInRange(0, this.tiles.length);
      tile = this.tiles[tileNumber];
      tileCount = {
        x: tile["tilemap"][0].length,
        y: tile["tilemap"].length
      };
      positionValid = false;
      while (!positionValid) {
        tilePosition = {
          x: this.randomInRange(0, this.tileCount.x - tileCount.x),
          y: this.randomInRange(0, this.tileCount.y - tileCount.y)
        };
        positionValid = true;
        for (i = m = 0, ref1 = tileCount.y; 0 <= ref1 ? m < ref1 : m > ref1; i = 0 <= ref1 ? ++m : --m) {
          for (j = n = 0, ref2 = tileCount.x; 0 <= ref2 ? n < ref2 : n > ref2; j = 0 <= ref2 ? ++n : --n) {
            if (tilemap[i + tilePosition.y][j + tilePosition.x]) {
              positionValid = false;
            }
          }
        }
      }
      for (i = o = 0, ref3 = tileCount.y; 0 <= ref3 ? o < ref3 : o > ref3; i = 0 <= ref3 ? ++o : --o) {
        for (j = p = 0, ref4 = tileCount.x; 0 <= ref4 ? p < ref4 : p > ref4; j = 0 <= ref4 ? ++p : --p) {
          tilemap[i + tilePosition.y][j + tilePosition.x] = true;
          if (tile["tilemap"][i][j] === "*") {
            this.tilePositions.push({
              "x": j + tilePosition.x,
              "y": i + tilePosition.y,
              "masked": false
            });
          }
        }
      }
      tileImg = document.createElement('img');
      tileImg.src = 'assets/images/' + tile["filename"];
      tileImg.style.position = 'fixed';
      tileImg.style.left = (tilePosition.x * this.tileSize.width) + 'px';
      tileImg.style.top = (tilePosition.y * this.tileSize.height) + 'px';
      tileImg.style.width = (tileCount.x * this.tileSize.width) + 'px';
      tileImg.style.height = (tileCount.y * this.tileSize.height) + 'px';
      results.push(this.tilesDiv.appendChild(tileImg));
    }
    return results;
  };

  TensorflowBrickDetectionExample.prototype.presentRandomBackground = function() {
    var i, j, l, m, number, ref, ref1, tileImg, useMask;
    useMask = this.randomInRange(0, 3) > 0;
    this.tilePositions = [];
    for (i = l = 0, ref = this.tileCount.y; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {
      for (j = m = 0, ref1 = this.tileCount.x; 0 <= ref1 ? m < ref1 : m > ref1; j = 0 <= ref1 ? ++m : --m) {
        this.tilePositions.push({
          "x": j,
          "y": i,
          "masked": useMask
        });
      }
    }
    number = this.randomInRange(0, this.backgroundCount);
    tileImg = document.createElement('img');
    tileImg.src = 'assets/images/background' + (number + 1) + '.png';
    tileImg.style.position = 'fixed';
    tileImg.style.left = '0%';
    tileImg.style.top = '%0';
    tileImg.style.width = '100%';
    tileImg.style.height = '100%';
    return this.tilesDiv.appendChild(tileImg);
  };

  TensorflowBrickDetectionExample.prototype.pickRandomPositions = function() {
    var availableFigures, count, figure, figureIndex, i, l, len, len1, len2, m, markerImg, markerLabel, maskCircle, maskSize, n, o, p, position, positionIndex, ref, ref1, ref2, ref3, ref4, useMask;
    this.choosenFigures = [];
    availableFigures = (function() {
      var l, len, ref, results;
      ref = this.figures;
      results = [];
      for (l = 0, len = ref.length; l < len; l++) {
        figure = ref[l];
        results.push(figure);
      }
      return results;
    }).call(this);
    count = this.randomInRange(1, this.figures.length + 1);
    for (i = l = 0, ref = count; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {
      figureIndex = this.randomInRange(0, availableFigures.length);
      this.choosenFigures.push(availableFigures[figureIndex]);
      availableFigures.splice(figureIndex, 1);
    }
    this.positions = [];
    ref1 = this.choosenFigures;
    for (m = 0, len = ref1.length; m < len; m++) {
      figure = ref1[m];
      positionIndex = this.randomInRange(0, this.tilePositions.length);
      position = this.tilePositions[positionIndex];
      this.tilePositions.splice(positionIndex, 1);
      this.positions.push(position);
      console.log("Place figure '" + figure + "' at (" + position.x + ", " + position.y + ")");
    }
    ref2 = this.positions;
    for (n = 0, len1 = ref2.length; n < len1; n++) {
      position = ref2[n];
      markerImg = document.createElement('img');
      markerImg.src = 'assets/images/figure_marker.png';
      markerImg.style.position = 'fixed';
      markerImg.style.left = ((position.x * this.tileSize.width) - (this.tileSize.width * 0.25)) + 'px';
      markerImg.style.top = ((position.y * this.tileSize.height) - (this.tileSize.height * 0.25)) + 'px';
      markerImg.style.width = (this.tileSize.width * 1.50) + 'px';
      markerImg.style.height = (this.tileSize.height * 1.50) + 'px';
      this.markersDiv.appendChild(markerImg);
    }
    for (i = o = 0, ref3 = this.choosenFigures.length; 0 <= ref3 ? o < ref3 : o > ref3; i = 0 <= ref3 ? ++o : --o) {
      markerLabel = document.createElement('p');
      markerLabel.textContent = this.choosenFigures[i];
      markerLabel.style.textAlign = 'center';
      markerLabel.style.color = 'yellow';
      markerLabel.style.position = 'fixed';
      markerLabel.style.left = ((this.positions[i].x * this.tileSize.width) - (this.tileSize.width * 0.5)) + 'px';
      markerLabel.style.top = ((this.positions[i].y * this.tileSize.height) - (this.tileSize.height * 0.25)) + 'px';
      markerLabel.style.width = (this.tileSize.width * 2.00) + 'px';
      markerLabel.style.height = (this.tileSize.height * 1.50) + 'px';
      this.markersDiv.appendChild(markerLabel);
    }
    maskSize = {
      width: this.tileSize.width * 8.0,
      height: this.tileSize.height * 8.0
    };
    useMask = false;
    ref4 = this.positions;
    for (p = 0, len2 = ref4.length; p < len2; p++) {
      position = ref4[p];
      if (position.masked) {
        maskCircle = document.createElementNS("http://www.w3.org/2000/svg", "image");
        maskCircle.setAttributeNS(null, "href", "assets/images/figure_marker_mask.png");
        maskCircle.setAttributeNS(null, "x", ((position.x * this.tileSize.width) + (this.tileSize.width / 2.0) - (maskSize.width / 2.0)) + "px");
        maskCircle.setAttributeNS(null, "y", ((position.y * this.tileSize.height) + (this.tileSize.height / 2.0) - (maskSize.height / 2.0)) + "px");
        maskCircle.setAttributeNS(null, "width", maskSize.width + "px");
        maskCircle.setAttributeNS(null, "height", maskSize.height + "px");
        this.maskElement.appendChild(maskCircle);
        useMask = true;
      }
    }
    if (!useMask) {
      maskCircle = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      maskCircle.setAttributeNS(null, "x", "0px");
      maskCircle.setAttributeNS(null, "y", "0px");
      maskCircle.setAttributeNS(null, "width", window.innerWidth + "px");
      maskCircle.setAttributeNS(null, "height", window.innerHeight + "px");
      maskCircle.setAttributeNS(null, "style", "fill: white");
      return this.maskElement.appendChild(maskCircle);
    }
  };

  TensorflowBrickDetectionExample.prototype.onKeydown = function(event) {
    if (event.keyCode === 32) {
      return this.takeScreenshot();
    }
  };

  TensorflowBrickDetectionExample.prototype.takeScreenshot = function() {
    var i, l, ref, screenshotTileSize, x1, x2, xmlText, y1, y2;
    if (!this.readyForScreenshot) {
      return;
    }
    this.readyForScreenshot = false;
    this.markersDiv.style.opacity = '0';
    setTimeout((function(_this) {
      return function() {
        return _this.client.takeScreenshot(_this.client.boardAreaId_fullBoard, [_this.screenshotSize.width, _this.screenshotSize.height], "resources/tensorflow/images/image_" + _this.trainNumber + ".jpg", function() {
          _this.flashDiv.style.transition = "opacity 0s";
          _this.flashDiv.style.opacity = 1.0;
          return setTimeout(function() {
            _this.flashDiv.style.transition = "opacity 2s";
            _this.flashDiv.style.opacity = 0.0;
            return setTimeout(function() {
              return _this.presentNewBackground();
            }, 2000);
          }, 100);
        });
      };
    })(this), 500);
    screenshotTileSize = {
      width: this.screenshotSize.width / this.tileCount.x,
      height: this.screenshotSize.height / this.tileCount.y
    };
    xmlText = "";
    xmlText += "<annotation>\n";
    xmlText += "    <folder>images</folder>\n";
    xmlText += "    <filename>image_" + this.trainNumber + ".jpg</filename>\n";
    xmlText += "    <size>\n";
    xmlText += "        <width>" + this.screenshotSize.width + "</width>\n";
    xmlText += "        <height>" + this.screenshotSize.height + "</height>\n";
    xmlText += "        <depth>3</depth>\n";
    xmlText += "    </size>\n";
    xmlText += "    <segmented>0</segmented>\n";
    for (i = l = 0, ref = this.choosenFigures.length; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {
      x1 = this.positions[i].x * screenshotTileSize.width;
      y1 = this.positions[i].y * screenshotTileSize.height;
      x2 = x1 + screenshotTileSize.width;
      y2 = y1 + screenshotTileSize.height;
      x1 = Math.max(0, x1 - (screenshotTileSize.width * 0.5));
      y1 = Math.max(0, y1 - (screenshotTileSize.height * 0.5));
      x2 = Math.min(this.screenshotSize.width - 1, x2 + (screenshotTileSize.width * 0.5));
      y2 = Math.min(this.screenshotSize.height - 1, y2 + (screenshotTileSize.height * 0.5));
      xmlText += "    <object>\n";
      xmlText += "        <name>" + this.choosenFigures[i] + "</name>\n";
      xmlText += "        <pose>Unspecified</pose>\n";
      xmlText += "        <truncated>0</truncated>\n";
      xmlText += "        <occluded>0</occluded>\n";
      xmlText += "        <difficult>0</difficult>\n";
      xmlText += "        <bndbox>\n";
      xmlText += "            <xmin>" + x1 + "</xmin>\n";
      xmlText += "            <ymin>" + y1 + "</ymin>\n";
      xmlText += "            <xmax>" + x2 + "</xmax>\n";
      xmlText += "            <ymax>" + y2 + "</ymax>\n";
      xmlText += "        </bndbox>\n";
      xmlText += "    </object>\n";
    }
    xmlText += "</annotation>\n";
    return this.client.writeTextToFile("resources/tensorflow/images/image_" + this.trainNumber + ".xml", xmlText, (function(_this) {
      return function() {
        return console.log("Wrote XML!");
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.writeLabelMap = function() {
    var i, l, labelMapText, ref;
    labelMapText = "";
    for (i = l = 0, ref = this.figures.length; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {
      labelMapText += "item {\n";
      labelMapText += "  id: " + (i + 1) + "\n";
      labelMapText += "  name: '" + this.figures[i] + "'\n";
      labelMapText += "}\n";
    }
    return this.client.writeTextToFile("resources/tensorflow/data/label_map.pbtxt", labelMapText, (function(_this) {
      return function() {
        return console.log("Wrote label map!");
      };
    })(this));
  };

  TensorflowBrickDetectionExample.prototype.randomInRange = function(min, max) {
    return Math.floor(Math.random() * (max - min)) + min;
  };

  return TensorflowBrickDetectionExample;

})();

//# sourceMappingURL=main.js.map

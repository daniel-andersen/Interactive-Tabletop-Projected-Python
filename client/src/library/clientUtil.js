var ClientUtil;

ClientUtil = (function() {
  function ClientUtil() {}

  ClientUtil.uuid = function() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r, v;
      r = Math.random() * 16 | 0;
      v = c === 'x' ? r : r & 0x3 | 0x8;
      return v.toString(16);
    });
  };

  ClientUtil.randomRequestId = function() {
    return Math.floor(Math.random() * 1000000);
  };

  ClientUtil.convertImageToDataURL = function(image, callback) {
    var canvas, ctx, dataURL;
    canvas = document.createElement("CANVAS");
    canvas.width = image.width;
    canvas.height = image.height;
    ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0);
    dataURL = canvas.toDataURL("image/png");
    dataURL = dataURL.replace(/^.*;base64,/, "");
    callback(dataURL);
    return canvas = null;
  };

  ClientUtil.convertImagesToDataURLs = function(images, callback) {
    var canvas, ctx, dataURL, dataURLs, i, image, len;
    dataURLs = [];
    for (i = 0, len = images.length; i < len; i++) {
      image = images[i];
      canvas = document.createElement("CANVAS");
      canvas.width = image.width;
      canvas.height = image.height;
      ctx = canvas.getContext("2d");
      ctx.drawImage(image, 0, 0);
      dataURL = canvas.toDataURL("image/png");
      dataURL = dataURL.replace(/^.*;base64,/, "");
      dataURLs.push(dataURL);
      canvas = null;
    }
    return callback(dataURLs);
  };

  ClientUtil.readFileBase64 = function(filename, callback) {
    var xhr;
    xhr = new XMLHttpRequest();
    xhr.open("GET", filename, true);
    xhr.responseType = "blob";
    xhr.onload = function(e) {
      var blob, fileReader;
      if (this.status === 200) {
        blob = new Blob([this.response], {
          type: "text/xml"
        });
        fileReader = new FileReader();
        fileReader.onload = (function(_this) {
          return function(e) {
            var contents;
            contents = e.target.result;
            contents = contents.replace(/^.*;base64,/, "");
            return callback(contents);
          };
        })(this);
        fileReader.onerror = (function(_this) {
          return function(e) {
            return console.log("Error loading file: " + e);
          };
        })(this);
        return fileReader.readAsDataURL(blob);
      }
    };
    return xhr.send();
  };

  return ClientUtil;

})();

//# sourceMappingURL=clientUtil.js.map

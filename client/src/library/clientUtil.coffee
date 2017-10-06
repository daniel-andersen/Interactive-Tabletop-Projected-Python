class ClientUtil
    @uuid: ->
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace /[xy]/g, (c) ->
            r = Math.random() * 16 | 0
            v = if c == 'x' then r else r & 0x3 | 0x8
            return v.toString(16)

    @randomRequestId: -> Math.floor(Math.random() * 1000000)

    @convertImageToDataURL: (image, callback) ->
        canvas = document.createElement("CANVAS")
        canvas.width = image.width
        canvas.height = image.height

        ctx = canvas.getContext("2d")
        ctx.drawImage(image, 0, 0)

        dataURL = canvas.toDataURL("image/png")
        dataURL = dataURL.replace(/^.*;base64,/, "")

        callback(dataURL)

        canvas = null

    @readFileBase64: (filename, callback) ->
        xhr = new XMLHttpRequest()
        xhr.open("GET", filename, true)
        xhr.responseType = "blob"

        xhr.onload = (e) ->
            if this.status == 200
                blob = new Blob([this.response], {type: "text/xml"})

                fileReader = new FileReader()
                fileReader.onload = (e) =>
                    contents = e.target.result
                    contents = contents.replace(/^.*;base64,/, "")
                    callback(contents)
                fileReader.onerror = (e) =>
                    console.log("Error loading file: " + e)

                fileReader.readAsDataURL(blob)

        xhr.send();

Building
--------

Build and serve using:

`$ gulp`

This will compile all submodules listed in _gulpfile.js_, copy everything into the _build_ directory and finally
serve it from http://localhost:9002.

To list available modules, run:

`$ gulp modules`

Alternatively, to build and serve a specific module only, fx. MAZE, run:

`$ gulp MAZE`

Content
-------

To include new content, simply add a new entry to the _modules_ array in _gulpfile.js_ following the MAZE example.

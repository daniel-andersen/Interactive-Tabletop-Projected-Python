module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    jshint: {
      files: ['Gruntfile.js', 'src/**/*.js']
    },
    pkg: grunt.file.readJSON('package.json'),
    coffee: {
      coffee_to_js: {
        options: {
          bare: true,
          sourceMap: true
        },
        expand: true,
        flatten: false,
        cwd: "src",
        src: ["**/*.coffee"],
        dest: 'src',
        ext: ".js"
      }
    },
    serve: {
      options: {
        port: 9002,
        serve: {
		  path: "target"
		}
      }
	},
    subgrunt: {
      example_board_detection: {
        projects: {
          "../content/examples/board_detection": "default"
        }
      }
    },
    clean: ["target"],
    copy: {
      library: {
        expand: true,
        cwd: "src",
        src: "**",
        dest: "target/"
      },
      example_board_detection: {
        files: [
          {expand: true, cwd: "../content/examples/board_detection/assets", src: "**", dest: "target/content/examples/board_detection/assets"},
          {expand: true, cwd: "../content/examples/board_detection/src", src: "**", dest: "target/content/examples/board_detection/src"},
          {expand: true, cwd: "../content/examples/board_detection/lib", src: "**", dest: "target/content/examples/board_detection/lib"},
          {expand: true, cwd: "../content/examples/board_detection/", src: "*.html", dest: "target/content/examples/board_detection/"}
        ]
      }
    }
  });

  // Load plugins
  grunt.loadNpmTasks("grunt-contrib-clean");
  grunt.loadNpmTasks("grunt-contrib-copy");
  grunt.loadNpmTasks("grunt-contrib-coffee");
  grunt.loadNpmTasks("grunt-subgrunt");
  grunt.loadNpmTasks("grunt-serve");

  // Tasks
  grunt.registerTask("default", ["clean", "coffee", "subgrunt", "copy"]);
  grunt.registerTask("run", ["default", "serve"]);
};
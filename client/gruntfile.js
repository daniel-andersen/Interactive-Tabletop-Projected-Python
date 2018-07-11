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
      /*example_board_detection: {
        projects: {
          "../content/examples/board_detection": "default"
        }
      },
      example_hand_detection: {
        projects: {
          "../content/examples/hand_detection": "default"
        }
      },
      example_image_detection: {
        projects: {
          "../content/examples/image_detection": "default"
        }
      },
      example_tensorflow_brick_detection: {
        projects: {
          "../content/examples/tensorflow_brick_detection": "default"
        }
      },*/
      example_tensorflow_brick_training: {
        projects: {
          "../content/examples/tensorflow_brick_training": "default"
        }
      }
      /*raspberry_pi_instructions: {
        projects: {
          "../content/raspberry_pi_instructions": "default"
        }
      },
      MAZE: {
        projects: {
          "../content/MAZE": "default"
        }
      }*/
    },
    clean: ["target"],
    copy: {
      library: {
        expand: true,
        cwd: "src",
        src: "**",
        dest: "target/"
      },
      /*example_board_detection: {
        files: [
          {expand: true, cwd: "../content/examples/board_detection/assets", src: "**", dest: "target/content/examples/board_detection/assets"},
          {expand: true, cwd: "../content/examples/board_detection/src", src: "**", dest: "target/content/examples/board_detection/src"},
          {expand: true, cwd: "../content/examples/board_detection/lib", src: "**", dest: "target/content/examples/board_detection/lib"},
          {expand: true, cwd: "../content/examples/board_detection/", src: "*.html", dest: "target/content/examples/board_detection/"}
        ]
      },
      example_hand_detection: {
        files: [
          {expand: true, cwd: "../content/examples/hand_detection/assets", src: "**", dest: "target/content/examples/hand_detection/assets"},
          {expand: true, cwd: "../content/examples/hand_detection/src", src: "**", dest: "target/content/examples/hand_detection/src"},
          {expand: true, cwd: "../content/examples/hand_detection/lib", src: "**", dest: "target/content/examples/hand_detection/lib"},
          {expand: true, cwd: "../content/examples/hand_detection/", src: "*.html", dest: "target/content/examples/hand_detection/"}
        ]
      },
      example_image_detection: {
        files: [
          {expand: true, cwd: "../content/examples/image_detection/assets", src: "**", dest: "target/content/examples/image_detection/assets"},
          {expand: true, cwd: "../content/examples/image_detection/src", src: "**", dest: "target/content/examples/image_detection/src"},
          {expand: true, cwd: "../content/examples/image_detection/lib", src: "**", dest: "target/content/examples/image_detection/lib"},
          {expand: true, cwd: "../content/examples/image_detection/", src: "*.html", dest: "target/content/examples/image_detection/"}
        ]
      },
      example_tensorflow_brick_detection: {
        files: [
          {expand: true, cwd: "../content/examples/tensorflow_brick_detection/assets", src: "**", dest: "target/content/examples/tensorflow_brick_detection/assets"},
          {expand: true, cwd: "../content/examples/tensorflow_brick_detection/src", src: "**", dest: "target/content/examples/tensorflow_brick_detection/src"},
          {expand: true, cwd: "../content/examples/tensorflow_brick_detection/lib", src: "**", dest: "target/content/examples/tensorflow_brick_detection/lib"},
          {expand: true, cwd: "../content/examples/tensorflow_brick_detection/", src: "*.html", dest: "target/content/examples/tensorflow_brick_detection/"}
        ]
      },*/
      example_tensorflow_brick_training: {
        files: [
          {expand: true, cwd: "../content/examples/tensorflow_brick_training/assets", src: "**", dest: "target/content/examples/tensorflow_brick_training/assets"},
          {expand: true, cwd: "../content/examples/tensorflow_brick_training/src", src: "**", dest: "target/content/examples/tensorflow_brick_training/src"},
          {expand: true, cwd: "../content/examples/tensorflow_brick_training/lib", src: "**", dest: "target/content/examples/tensorflow_brick_training/lib"},
          {expand: true, cwd: "../content/examples/tensorflow_brick_training/", src: "*.html", dest: "target/content/examples/tensorflow_brick_training/"}
        ]
      }
      /*raspberry_pi_instructions: {
        files: [
          {expand: true, cwd: "../content/raspberry_pi_instructions/assets", src: "**", dest: "target/content/raspberry_pi_instructions/assets"},
          {expand: true, cwd: "../content/raspberry_pi_instructions/src", src: "**", dest: "target/content/raspberry_pi_instructions/src"},
          {expand: true, cwd: "../content/raspberry_pi_instructions/lib", src: "**", dest: "target/content/raspberry_pi_instructions/lib"},
          {expand: true, cwd: "../content/raspberry_pi_instructions/", src: "*.html", dest: "target/content/raspberry_pi_instructions/"}
        ]
      },
      MAZE: {
        files: [
          {expand: true, cwd: "../content/MAZE/assets", src: "**", dest: "target/content/MAZE/assets"},
          {expand: true, cwd: "../content/MAZE/src", src: "**", dest: "target/content/MAZE/src"},
          {expand: true, cwd: "../content/MAZE/lib", src: "**", dest: "target/content/MAZE/lib"},
          {expand: true, cwd: "../content/MAZE/", src: "*.html", dest: "target/content/MAZE/"}
        ]
      }*/
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

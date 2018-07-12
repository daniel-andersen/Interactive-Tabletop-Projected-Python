var gulp = require('gulp');
var connect = require('gulp-connect');
var coffee = require('gulp-coffee');
var del = require('del');

const modules = [
    {'name': 'library', 'inputPath': '../client', 'outputPath': 'build/library'},
    {'name': 'MAZE', 'inputPath': 'MAZE', 'outputPath': 'build/MAZE'},
    {'name': 'raspberry_pi_instructions', 'inputPath': 'raspberry_pi_instructions', 'outputPath': 'build/raspberry_pi_instructions'},
    {'name': 'board_detection', 'inputPath': 'examples/board_detection', 'outputPath': 'build/examples/board_detection'},
    {'name': 'hand_detection', 'inputPath': 'examples/hand_detection', 'outputPath': 'build/examples/hand_detection'},
    {'name': 'image_detection', 'inputPath': 'examples/image_detection', 'outputPath': 'build/examples/image_detection'},
    {'name': 'tensorflow_brick_detection', 'inputPath': 'examples/tensorflow_brick_detection', 'outputPath': 'build/examples/tensorflow_brick_detection'},
    {'name': 'tensorflow_brick_training', 'inputPath': 'examples/tensorflow_brick_training', 'outputPath': 'build/examples/tensorflow_brick_training'},
];

gulp.task('clean', () => {
    return del(['build']);
});

gulp.task('connect', done => {
    connect.server({
        port: 9002,
        livereload: true,
        root: ['.', 'build']
    });
    done();
});

function addTask(task, src, dest) {
    gulp.task(task, done => {
        gulp.src(src)
            .pipe(gulp.dest(dest))
            .pipe(connect.reload());
        done();
    });
}

function addModule(module, inputPath, outputPath) {
    addTask(module + '_css', inputPath + '/css/**/*.css', outputPath + '/css');
    addTask(module + '_assets', inputPath + '/assets/**/*', outputPath + '/assets');
    addTask(module + '_html', inputPath + '/html/**/*.html', outputPath);
    gulp.task(module + '_coffee', done => {
        gulp.src(inputPath + '/src/**/*.coffee')
            .pipe(coffee({bare: true}))
            .pipe(gulp.dest(outputPath + '/scripts'))
            .pipe(connect.reload());
        done();
    });
    gulp.task(module + '_watch', done => {
        gulp.watch(inputPath + '/css/**/*.css', gulp.series(module + '_css'));
        gulp.watch(inputPath + '/assets/**/*', gulp.series(module + '_assets'));
        gulp.watch(inputPath + '/html/**/*.html', gulp.series(module + '_html'));
        gulp.watch(inputPath + '/src/**/*.coffee', gulp.series(module + '_coffee'));
        done();
    });
    gulp.task(module + '_build', gulp.series(
        module + '_css',
        module + '_assets',
        module + '_html',
        module + '_coffee'
    ));
    gulp.task(module, gulp.series(
        module + '_build',
        gulp.parallel(
            'connect',
            module + '_watch'
        )
    ));
}

modules.forEach(moduleDict => {
    addModule(moduleDict.name, moduleDict.inputPath, moduleDict.outputPath);
});

gulp.task('modules', (done) => {
    modules.forEach(moduleDict => console.log("Module: " + moduleDict.name));
    done();
});

gulp.task('default', gulp.series(
    'clean',
    modules.map(moduleDict => moduleDict.name + '_build'),
    gulp.parallel(
        'connect',
        modules.map(moduleDict => moduleDict.name + '_watch')
    )
));

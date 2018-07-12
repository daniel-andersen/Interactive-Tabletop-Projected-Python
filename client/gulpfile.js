var gulp = require('gulp');
var coffee = require('gulp-coffee');
var del = require('del');

gulp.task('clean', () => {
    return del(['build']);
});

gulp.task('assets', done => {
    gulp.src('assets/**/*')
        .pipe(gulp.dest('build/assets'));
    done();
});

gulp.task('coffee', done => {
    gulp.src('src/**/*.coffee')
        .pipe(coffee({bare: true}))
        .pipe(gulp.dest('build'));
    done();
});

gulp.task('default',
    gulp.series(
        'clean',
        gulp.parallel(
            'assets',
            'coffee'
        )
    )
);

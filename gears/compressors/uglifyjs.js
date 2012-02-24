var uglify = require('uglify-js'),
    source = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function(chunk) {
  source += chunk;
});

process.stdin.on('end', function() {
  process.stdout.write(uglify(source));
});

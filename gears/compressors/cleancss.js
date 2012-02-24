var cleancss = require('clean-css'),
    source = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function(chunk) {
  source += chunk;
});

process.stdin.on('end', function() {
  process.stdout.write(cleancss.process(source));
});

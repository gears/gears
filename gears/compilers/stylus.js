var stylus = require('stylus'),
    source = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function (chunk) {
  source += chunk;
});

process.stdin.on('end', function () {
  var style = stylus(source, {filename: process.argv[2]});
  style.render(function (err, css) {
    if (err) {
      throw err;
    }
    process.stdout.write(css);
  })
});

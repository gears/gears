var less   = require('less'),
    source = '';

process.stdin.resume()
process.stdin.setEncoding('utf8');

process.stdin.on('data', function (chunk) {
  source += chunk;
});

process.stdin.on('end', function () {
  var parser = new less.Parser();
  parser.parse(source, function (err, tree) {
    if (err) {
      less.writeError(err);
      process.exit(1);
    }
    process.stdout.write(tree.toCSS());
  });
});

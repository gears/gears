var coffee = require('coffee-script'),
    source = '';

process.stdin.resume()
process.stdin.setEncoding('utf8');

process.stdin.on('data', function (chunk) {
  source += chunk;
});

process.stdin.on('end', function () {
  process.stdout.write(coffee.compile(source));
});

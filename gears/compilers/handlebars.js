var handlebars = require('handlebars'),
    template   = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function (chunk) {
  template += chunk;
});

process.stdin.on('end', function () {
  process.stdout.write(handlebars.precompile(template));
});

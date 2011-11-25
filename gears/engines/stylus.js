#!/usr/bin/env node

var stylus = require('stylus'),
    source = '';

process.stdin.resume();
process.stdin.setEncoding('utf8');

process.stdin.on('data', function (chunk) {
  source += chunk;
});

process.stdin.on('end', function () {
  var style = stylus(source);
  style.render(function (err, css) {
    if (err) {
      process.exit(1);
    }
    process.stdout.write(css);
  })
});

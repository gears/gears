(function () {
  console.log('external lib');
}).call(this);

(function () {
  var App = this.App = {
    Models: {},
    Views:  {}
  };
}).call(this);

console.log('simple_lib.js');

console.log('useful_lib.js');

(function () {
  console.log('application models');
}).call(this);

(function () {
  console.log('application views');
}).call(this);

console.log('utils/a.js');

console.log('utils/b/a.js');

console.log('utils/b/b.js');

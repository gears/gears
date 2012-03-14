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

console.log('usefull_lib');

(function () {
  console.log('application models');
}).call(this);

(function () {
  console.log('application views');
}).call(this);

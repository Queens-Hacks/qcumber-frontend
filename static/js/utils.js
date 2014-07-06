var indexOf = function(arr, x) {
  var l = arr.length;
  for (var i=0; i < l; i++) {
    if (arr[i] === x) return i;
  }

  return -1;
};

var forEach = function(arr, cb) {
  var l = arr.length;
  for (var i=0; i < l; i++) {
    cb(arr[i], i);
  }
};

var map = function(arr, cb) {
  var l = arr.length;
  var narr = Array(l);
  for (var i=0; i < l; i++) {
    narr[i] = cb(arr[i], i);
  }
  return narr;
};

var mapIf = function(arr, cb) {
  var l = arr.length;
  var narr = [];
  for (var i=0; i < l; i++) {
    var v = cb(arr[i], i);
    if (v) narr.push(v);
  }

  return narr;
};

var sum = function(arr) {
  var l = arr.length;
  var s = 0;
  for (var i=0; i < l; i++)
    s += arr[i];
  return s;
};

var all = function(arr, cb) {
  var l = arr.length;
  for (var i=0; i < l; i++)
    if (!cb(arr[i], i)) return false;
  return true;
};

var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F'
};

var escapeHTML = function(s) {
  return String(s).replace(/[&<>"'\/]/g, function(s) {
    return entityMap[s];
  });
}



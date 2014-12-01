/* List functions */
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

/* HTML helper functions */

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
};

var slugify = function(s) {
  return String(s).toLowerCase().replace(/ /g, '-');
};

/*
 Utility function for creating dom elements.
 Used as N(dom_element_type, attributes, children)
 */
var N = function(elt_ty, attrs, chldrn) {
  attrs = attrs || {};
  chldrn = chldrn || [];

  var elt = document.createElement(elt_ty);

  // Add each of the attributes to the element
  for (var attr in attrs) {
    if (Object.prototype.hasOwnProperty.call(attrs, attr)) {
      if (! attrs[attr]) continue;

      elt.setAttribute(attr, attrs[attr]);
    }
  }

  // Append each of the children
  forEach(chldrn, function(child) {
    if (typeof child === 'string') {
      // Automatically create text nodes
      child = document.createTextNode(child);
    }
    
    elt.appendChild(child);
  });
  
  return elt;
};

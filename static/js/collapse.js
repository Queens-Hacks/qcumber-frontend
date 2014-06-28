(function() {
  var indexOf = function(arr, x) {
    var l = arr.length;
    for (var i=0; i < l; i++) {
      if (arr[i] === x) return i;
    }

    return -1;
  }

  var forEach = function(arr, cb) {
    var l = arr.length;
    for (var i=0; i < l; i++) {
      cb(arr[i], i);
    }
  }

  var map = function(arr, cb) {
    var l = arr.length;
    var narr = Array(l);
    for (var i=0; i < l; i++) {
      narr[i] = cb(arr[i], i);
    }
    return narr;
  }

  function toggle(tgt) {
    var tgtSel = tgt.getAttribute('data-collapse-trigger');
    var targets = document.querySelectorAll(tgtSel);

    forEach(targets, function(target) {
      if (indexOf(target.classList, 'collapsed') !== -1) {
        target.className = target.className.replace(' collapsed', '');
      } else {
        target.className += ' collapsed';
      }
    });
  }

  function handle() {
    // This function handles 
    var collapsers = document.querySelectorAll('[data-collapse-trigger]');
    forEach(collapsers, function(trigger) {
      // Change the HTML content if collapse is avaliable
      if (trigger.hasAttribute('data-collapse-html'))
        trigger.innerHTML = trigger.getAttribute('data-collapse-html');

      // Clicking on the trigger will cause the area to become hidden
      trigger.addEventListener('click', function(e) {
        toggle(e.currentTarget);
      });

      if (trigger.getAttribute('data-collapse-default'))
        toggle(trigger);

      trigger.className += ' toggler';
    });
  }

  handle();
})();

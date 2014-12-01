(function() {
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

  function registerCollapsers(parent) {
    // This function handles 
    var collapsers = parent.querySelectorAll('[data-collapse-trigger]');
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

  registerCollapsers(document);

  window.registerCollapsers = registerCollapsers;
})();

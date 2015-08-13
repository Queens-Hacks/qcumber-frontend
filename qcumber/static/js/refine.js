(function() {
  var refineIds = {
    'subject': 'String',
    'course': 'String',
    'units': 'Number',
    'seasons': {
      'fall': 'Fall',
      'winter': 'Winter',
      'summer': 'Summer',
      'unoffered': 'Unoffered'
    },
    'careers': {
      'undergraduate': 'Undergraduate',
      'graduate': 'Graduate',
      'distance': 'Distance Studies',
      'nonCredit': 'Non-Credit'
    }
  };

  var injected = true;

  // The inject function reads in the elements in the refine pane, and then
  // modifies the query such that it contains those restraints. It is possible
  // to create queries in the query pane which will cause the refine pane to
  // act incorrectly, but I can't easily fix that.
  function inject() {
    // Prevent inject from being called multiple times without ininjecting
    if (injected) return;
    injected = true;

    // Build up the query string
    var query = '';

    Object.keys(refineIds).forEach(function(rId){
      var vType = refineIds[rId];
      var val;
      // plain text input
      if (['String', 'Number'].indexOf(vType) !== -1){
        val = document.getElementById('refine-'+rId).value.trim();
      }
      // array of checkboxes
      else if (typeof vType === 'object'){
        val = [];
        Object.keys(vType).forEach(function(subKey){
          if (document.getElementById('refine-'+subKey).checked){
            val.push(vType[subKey]);
          }
        });
        // if none checked, or all checked (the default), don't add to query string
        if (val.length === 0 || val.length === Object.keys(vType).length)
          val = undefined;
      }
      else { console.error('Check your ids object definition'); }
      // if set, add to query string
      if (val){
        if (query)
          query += '; ';
        query += rId + ': ' + val.toString();
      }
    });

    // Write out the query segment to the query string
    document.getElementById('query').value = query || '';
  }

  // Read in the query string
  // Extract the values, and put them into the fields.
  function uninject() {
    if (!injected) return;
    injected = false;

    // Get the current query
    var query = parseQueryString(document.getElementById('query').value);

    // Fill the values in the form
    Object.keys(refineIds).forEach(function(rId){
      var vType = refineIds[rId];
      // plain text input
      if (['String', 'Number'].indexOf(vType) !== -1){
        document.getElementById('refine-'+rId).value = query[rId] || '';
      }
      // array of checkboxes
      else if (typeof vType === 'object'){
        if (!query[rId])
          var deflt = true;
        Object.keys(vType).forEach(function(subKey){
          document.getElementById('refine-'+subKey).checked =
            (deflt !== undefined) ? deflt : query[rId].indexOf(vType[subKey]) !== -1;
        });
      }
    });

    document.getElementById('query').value = '';
  }

  function parseQueryString(q){
    var query = {};
    if (q.indexOf(':') === -1){
      // assume that its a search of the form '{subject abbrev} {course number}'
      q = q.split(' ');
      query['subject'] = (q.length > 0) ? q[0] : '';
      query['course'] = (q.length > 1) ? q[1] : '';
    }
    else {
      // advanced query string should have key:value pairs separated by semicolons
      query = q.split(';')
        .map(function(val){
          var pair = val.split(':');
          if (pair[1] && pair[1].indexOf(',') !== -1){
            pair[1] = pair[1].split(',').map(function(s){return s.trim();});
          }
          return pair;
        })
        .reduce(function(main, currentPair){
          if(currentPair[0]){
            main[currentPair[0].trim()] = currentPair[1];
          }
          return main;
        }, {});
    }
    return query;
  }
  // We inject/uninject when someone toggles the refine pane, and when the search form is submitted.
  var refineBtn = document.querySelector('button[class=refine-button]');
  refineBtn.addEventListener('click', function() {
    if (injected) uninject(); else inject();
  });
  var searchForm = document.getElementById('search-form');
  searchForm.addEventListener('submit', function() {
    // update the query to use expanded syntax
    uninject();
    inject();
  });
})();


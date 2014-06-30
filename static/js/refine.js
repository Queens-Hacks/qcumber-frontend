(function() {
  var seasonsQuerySegments = {
    fall: 'seasons: Fall',
    winter: 'seasons: Winter',
    summer: 'seasons: Summer',
    unoffered: '_missing_: seasons'
  };

  var careersQuerySegments = {
    undergraduate: 'career: Undergraduate',
    graduate: 'career: Graduate',
    distance: 'career: Distance\\ Studies',
    nonCredit: 'career: Non-Credit'
  };

  function escapeQuerySegment(s) {
    return s.replace(' ', '\\ ');
  }

  function unescapeQuerySegment(s) {
    return s.replace('\\ ', ' ');
  }

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

    var subject = document.getElementById('refine-subject').value.trim();
    if (subject)
      query += ' subject: '+escapeQuerySegment(subject);

    var course = document.getElementById('refine-course').value.trim();
    if (course)
      query += ' number: '+escapeQuerySegment(course);

    var units = document.getElementById('refine-units').value.trim();
    if (units)
      query += ' units: '+escapeQuerySegment(units);

    var seasons = {
      fall: document.getElementById('refine-fall').checked,
      winter: document.getElementById('refine-winter').checked,
      summer: document.getElementById('refine-summer').checked,
      unoffered: document.getElementById('refine-unoffered').checked
    };

    // If they check none of them.. Ignore them. They are silly.
    var seasonQueries = mapIf(['fall', 'winter', 'summer', 'unoffered'], function(season) {
      if (seasons[season]) return seasonsQuerySegments[season];
    });

    if (seasonQueries.length == 1)
      query += ' ' + seasonQueries[0];
    else if (seasonQueries.length < 4)
      query += ' (' + seasonQueries.join(' OR ') + ')';

    var careers = {
      undergraduate: document.getElementById('refine-undergraduate').checked,
      graduate: document.getElementById('refine-graduate').checked,
      distance: document.getElementById('refine-distance').checked,
      nonCredit: document.getElementById('refine-nonCredit').checked
    };

    var careerQueries = mapIf(['undergraduate', 'graduate', 'distance', 'nonCredit'], function(career) {
      if (careers[career]) return careersQuerySegments[career];
    });


    if (careerQueries.length == 1)
      query += ' ' + careerQueries[0];
    else if (careerQueries.length < 4)
      query += ' (' + careerQueries.join(' OR ') + ')';

    // Write out the query segment to the query string
    var queryElement = document.getElementById('query');
    if (queryElement.value.length > 0)
      queryElement.value += query;
    else if (query.length > 0)
      queryElement.value += query.substring(1); // Strip the leading space
  }

  // Yup. I'm using a regexp to parse a context-free language. I'm a bad person.
  // This regexp is extremely fragile, and will easily break. Unfortunate, but
  // I can't think of a much better solution without writing a complex parser,
  // maintaining hidden state, or 
  var uninjectRe = RegExp('(?:(?: |^)subject: ?((?:[^ ]|\\\\ )*))?' +
                          '(?:(?: |^)number: ?((?:[^ ]|\\\\ )*))?' +
                          '(?:(?: |^)units: ?((?:[^ ]|\\\\ )*))?' +
                          '(?:(?: |^)\\(?' +
                                 '(?:seasons: ?(Fall)(?: OR )?)?' +
                                 '(?:seasons: ?(Winter)(?: OR )?)?' +
                                 '(?:seasons: ?(Summer)(?: OR )?)?' +
                                 '(?:(_missing_): ?seasons(?: OR )?)?' +
                          '\\)?)?'+
                          '(?:(?: |^)\\(?' +
                                 '(?:career: ?(Undergraduate)(?: OR )?)?' +
                                 '(?:career: ?(Graduate)(?: OR )?)?' +
                                 '(?:career: ?(Distance\\\\ Studies)(?: OR )?)?' +
                                 '(?:career: ?(Non-Credit))?' +
                          '\\)?)?$');

  // Read in the query string, using the above RegExp to try and find relevant fields.
  // Extract the values, and put them into the fields.
  function uninject() {
    if (!injected) return;
    injected = false;

    // Get the current query
    var queryElement = document.getElementById('query');
    var q = queryElement.value;
    var m = q.match(uninjectRe);

    if (!m) return;

    var r = q.substring(0, m.index);
    queryElement.value = r;

    // Fill the values in the form
    document.getElementById('refine-subject').value = unescapeQuerySegment(m[1] || '');
    document.getElementById('refine-course').value = unescapeQuerySegment(m[2] || '');
    document.getElementById('refine-units').value = unescapeQuerySegment(m[3] || '');

    if (m[4] || m[5] || m[6] || m[7]) {
      document.getElementById('refine-fall').checked = !!m[4];
      document.getElementById('refine-winter').checked = !!m[5];
      document.getElementById('refine-summer').checked = !!m[6];
      document.getElementById('refine-unoffered').checked = !!m[7];
    } else {
      (document.getElementById('refine-fall').checked = 
        document.getElementById('refine-winter').checked = 
        document.getElementById('refine-summer').checked = 
        document.getElementById('refine-unoffered').checked = true);
    }

    if (m[8] || m[9] || m[10] || m[11]) {
      document.getElementById('refine-undergraduate').checked = !!m[8];
      document.getElementById('refine-graduate').checked = !!m[9];
      document.getElementById('refine-distance').checked = !!m[10];
      document.getElementById('refine-nonCredit').checked = !!m[11];
    } else {
      (document.getElementById('refine-undergraduate').checked = 
        document.getElementById('refine-graduate').checked = 
        document.getElementById('refine-distance').checked = 
        document.getElementById('refine-nonCredit').checked = true);
    }
  }

  // We inject/uninject when someone toggles the refine pane, and when the search form is submitted.
  var refineBtn = document.querySelector('button[class=refine-button]');
  refineBtn.addEventListener('click', function() {
    if (injected) uninject(); else inject();
  });
  var searchForm = document.getElementById('search-form');
  searchForm.addEventListener('submit', function() { inject(); });
})();


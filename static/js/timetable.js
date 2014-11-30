(function() {
  var day_height = 60;
  var start_time = 7 * 60;

  /*********************
   * Conflict Handling *
   *********************/
  function start(item) {
    return item.startHr * 60 + item.startMin;
  }

  function end(item) {
    return item.endHr * 60 + item.endMin;
  }

  function conflicting(a, b) {
    var start_a = start(a)
      , start_b = start(b)
      , end_a   = end(a)
      , end_b   = end(b);

    return ((start_a > start_b && start_a < end_b) ||
            (end_a > start_b && end_a < end_b) ||
            (start_a <= start_b && end_a >= end_b));
  }

  /**********************************
   * Populating the schedule proper *
   * This runs once on each day     *
   **********************************/
  function renderSchedule(elem, schedule) {
    // Sort by start times
    // schedule.sort(function(a, b) { return start(a) - start(b); });

    var maxColumn = 0; // The highest column which is required
    var processed = []; // The items which have already had their column caclulated

    // Determine which column the particular timetable entry should be placed in
    // This is done by finding the smallest column number which isn't conflicting
    // with an already processed item
    forEach(schedule, function(entry, i) {
      entry.width = 1;

      // Determine the set of columns which have conflicts with this entry
      var badColumns = [];
      forEach(processed, function(item) {
        if (conflicting(entry, item))
          badColumns.push(item.column);
      });

      // Calculate the smallest column not in this list
      var column = 0;
      while (indexOf(badColumns, column) !== -1) column++;

      // Record the new column, and save the entry as being processed
      entry.column = column;
      if (column > maxColumn) maxColumn = column;

      processed[i] = entry;
    });

    // Every day in the HTML is 100% wide. We will split that into widths
    // for each of the individual columns
    var colWidth = 100 / (maxColumn + 1);

    // Expand every entry as much as possible, so that entries aren't all
    // pushed up against the left. This is done by incrementing the
    // width property as much as possible
    forEach(processed, function(entry) {
      for (var i = entry.column + 1; i <= maxColumn; i++) {
        if (all(processed, // Check if there are any items conflicting with this column
            function(item) { return item.column != i || !conflicting(entry, item); })) {
          entry.width++; // Expand!
        } else {
          break;
        }
      }

      // Create the element and add it to the day in question.
      var element = document.createElement('div');
      element.className = 'section';
      if (entry.code) {
        // Render the code for the item to the screen
        var course_code_el = document.createElement('h3');

        if (entry.link) {
          var course_code_link = document.createElement('a');
          course_code_link.setAttribute('href', entry.link);
          course_code_link.textContent = entry.code;
          course_code_el.appendChild(course_code_link);
        } else {
          course_code_el.textContent = entry.code;
        }

        element.appendChild(course_code_el);
      }

      if (entry.room) {
        // Render the code for the item to the screen
        var room_el = document.createElement('p');

        room_el.textContent = entry.room;

        element.appendChild(room_el);
      }

      // Positioning the element
      element.style.top = ((start(entry) - start_time) * day_height / 60) + 'px';
      element.style.height = ((end(entry) - start(entry)) * day_height / 60) + 'px';
      element.style.left = (entry.column * colWidth) + '%';
      element.style.width = (entry.width * colWidth) + '%';

      elem.appendChild(element);
    });
  }

  var unloaded = 0;
  var seasons = {};
  function getDays(season) {
    if (!seasons[season]) {
      seasons[season] = [
        [], // Sunday
        [], // Monday
        [], // Tuesday
        [], // Wednesday
        [], // Thursday
        [], // Friday
        []  // Saturday
      ];
    }

    return seasons[season];
  }

  // Load each of the sections stored in localStorage by making XHR requests
  // to the /timetable/section endpoint
  var sections = JSON.parse(localStorage.getItem('timetable-sections') || '[]');
  forEach(sections, function(section) {
    unloaded++;

    var xhr = new XMLHttpRequest();
    xhr.addEventListener('load', function() {
      unloaded--;
      var data = JSON.parse(this.responseText);
      forEach(data.classes, function(aClass) {
        try {
          // The Z is added to ensure that the browser parses the date signiture correctly
          // The RFC states that Z ensures a UTC offset of 00:00, which means that we can
          // use getUTCHours and getUTCMinutes and not have values offset from those appearing
          // in the input string. This is good, because we don't actually care about timezones.
          // SEE https://www.ietf.org/rfc/rfc3339.txt
          var startTime = new Date(aClass.start_time + 'Z');
          var endTime = new Date(aClass.end_time + 'Z');

          var section_data = {
            room: aClass.location,
            code: data.subject + ' ' + data.course,
            link: '/catalog/' + data.subject + '/' + data.course,
            startHr: startTime.getUTCHours(),
            startMin: startTime.getUTCMinutes(),
            endHr: endTime.getUTCHours(),
            endMin: endTime.getUTCMinutes()
          };

          getDays(data.season + ' ' + data.year)[aClass.day_of_week].push(section_data);
        } catch (e) { }
      });

      if (unloaded <= 0)
        renderAllSchedules();
    });

    xhr.open('get', '/timetable/section/' + encodeURIComponent(section), true);
    xhr.send();
  });


  function createSeason(season) {
    var day_sections = [];

    /*****************************
     * Creating the DOM elements *
     *****************************/

    var wrapper = document.createElement('div');
    wrapper.className = 'timetable-wrapper';
    wrapper.setAttribute('id', slugify(season));

    // Times column
    var times = document.createElement('div');
    times.className='times';

    // Times has an empty heading
    var times_heading = document.createElement('h2');
    times_heading.className = 'day-label';
    times_heading.innerHTML = '&nbsp;';
    times.appendChild(times_heading);

    // Create each of the time slots.
    for (var i = 0; i < 15; i++) { // @TODO: This should not have magic numbers...
      var time = document.createElement('div');
      time.className = 'time';
      time.textContent = ((i + 6) % 12) + 1;

      times.appendChild(time);
    }

    // Add the times column
    wrapper.appendChild(times);

    // Add each of the day columns
    for (var i = 0; i < 5; i++) {
      var day = document.createElement('div');
      day.className = 'day';

      // Heading
      var day_heading = document.createElement('h2');
      day_heading.className = 'day-label';
      switch (i) {
        case 0: day_heading.textContent = 'Monday'; break;
        case 1: day_heading.textContent = 'Tuesday'; break;
        case 2: day_heading.textContent = 'Wednesday'; break;
        case 3: day_heading.textContent = 'Thursday'; break;
        case 4: day_heading.textContent = 'Friday'; break;
      }
      day.appendChild(day_heading);

      // Body area for sections
      var sections = document.createElement('div');
      sections.className = 'day-sections';
      day_sections.push(sections);
      day.appendChild(sections);

      wrapper.appendChild(day);
    }

    /**************************************
     * Season label & collapse components *
     **************************************/

    var season_wrapper = document.createElement('div');
    season_wrapper.style.clear = 'both';

    // Heading for the season
    var header = document.createElement('h2');
    header.className = 'timetable-heading';

    var header_link = document.createElement('a');
    header_link.setAttribute('href', '#');
    header_link.setAttribute('data-collapse-trigger', '#' + slugify(season));

    if (outdated(season)) // Outdated seasons should be collapsed by default
      header_link.setAttribute('data-collapse-default', 'true');

    header_link.textContent = season;
    header.appendChild(header_link);

    // Add the header & main body into the season_wrapper
    season_wrapper.appendChild(header);
    season_wrapper.appendChild(wrapper);

    // And add the season_wrapper to the DOM
    var contents = document.querySelector('.contents');
    contents.appendChild(season_wrapper);

    // Return the list of divs which the sections should be inserted into
    return day_sections;
  }

  function seasonToInt(season) {
    var parts = season.split(' ');
    var n = parseInt(parts[1]) * 3;

    if (parts[0] === 'Winter')
      n += 0;
    else if (parts[0] === 'Summer')
      n += 1;
    else
      n += 2;

    return n;
  }

  function outdated(season) {
    var now = new Date();
    return seasonToInt(season) < now.getFullYear() * 3 + (now.getMonth() % 4);
  }


  function renderAllSchedules() {
    // Sort the seasons in time ascending order
    var keys = Object.keys(seasons).sort(function(aStr, bStr) {
      return seasonToInt(aStr) - seasonToInt(bStr);
    });

    // Render each of the seasons to the DOM
    forEach(keys, function(season) {
      var days = seasons[season];

      // Create the area in the DOM to place the season
      var day_sections = createSeason(season);

      // Render the sections into each of the day columns
      for (var i = 0; i < day_sections.length; i++) {
        renderSchedule(day_sections[i], days[i+1]);
      }
    });

    // Ensure that the collapser callbacks are correctly hooked up
    registerCollapsers(document.querySelector('.contents'));
  }

})();

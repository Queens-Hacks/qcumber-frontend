(function() {
  var day_height = 60;
  var start_time = 7 * 60;

  function start(item) {
    return item.startHr * 60 + item.startMin;
  }

  function end(item) {
    return item.endHr * 60 + item.endMin;
  }

  function countConflicts(i, schedule) {
    var c = 0;
    var l = schedule.length;
    for (var i = 0; i < l; i++) {
      var s = schedule[i];
      if ((start(i) > start(s) && start(i) < end(s)) ||
          (end(i) > start(s) && end(i) < end(s)) ||
          (start(i) <= start(s) && end(i) >= end(s))) {
        c++;
      }
    }

    return c;
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

  function renderSchedule(elem, schedule) {
    // Sort by start times
    // schedule.sort(function(a, b) { return start(a) - start(b); });

    var maxColumn = 0; // The highest column which is required
    var processed = []; // The items which have already had their column caclulated

    forEach(schedule, function(entry, i) {
      entry.width = 1;

      // The entry will be put in the lowest column which is 
      // not conflicting with another entry.
      var badColumns = [];
      forEach(processed, function(item) {
        if (conflicting(entry, item))
          badColumns.push(item.column);
      });

      var column = 0;
      while (indexOf(badColumns, column) !== -1) column++;

      // Record the new column, and save the entry as being processed
      entry.column = column;
      if (column > maxColumn) maxColumn = column;

      processed[i] = entry;
    });

    var colWidth = 100 / (maxColumn + 1);

    forEach(processed, function(entry) {
      // Attempt to expand the width of the item to the right
      for (var i = entry.column + 1; i <= maxColumn; i++) {
        if (all(processed,
            function(item) { return item.column != i || !conflicting(entry, item); })) {
          entry.width++; // Expand!
        } else {
          break;
        }
      }

      // Create the element and add it to the day in question.
      var element = document.createElement('div');
      element.className = 'section';
      if (entry.code)
        element.innerHTML += '<h3>' + escapeHTML(entry.code) + '</h3>';

      if (entry.room)
        element.innerHTML += '<p>' + escapeHTML(entry.room) + '</p>';

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

  var sections = JSON.parse(localStorage.getItem('timetable-sections') || '[]');
  forEach(sections, function(section) {
    unloaded++;

    var xhr = new XMLHttpRequest();
    xhr.addEventListener('load', function() {
      unloaded--;
      var data = JSON.parse(this.responseText);
      forEach(data.classes, function(aClass) {
        try {
          var startTime = new Date(aClass.start_time);
          var endTime = new Date(aClass.end_time);

          console.log(startTime);
          console.log(endTime);

          getDays(data.season + ' ' + data.year)[aClass.day_of_week].push({
            room: aClass.location,
            code: data.subject + ' ' + data.course,
            startHr: startTime.getUTCHours(),
            startMin: startTime.getUTCMinutes(),
            endHr: endTime.getUTCHours(),
            endMin: endTime.getUTCMinutes()
          });
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

    var wrapper = document.createElement('div');
    wrapper.className = 'timetable-wrapper';
    wrapper.setAttribute('id', slugify(season));

    var times = document.createElement('div');
    times.className='times';

    var day_label = document.createElement('h2');
    day_label.className = 'day-label';
    day_label.innerHTML = '&nbsp;';
    times.appendChild(day_label);

    for (var i = 0; i < 15; i++) {
      var time = document.createElement('div');
      time.className = 'time';
      time.textContent = ((i + 6) % 12) + 1;

      times.appendChild(time);
    }

    wrapper.appendChild(times);

    for (var i = 0; i < 5; i++) {
      var day = document.createElement('div');
      day.className = 'day';

      var label = document.createElement('h2');
      label.className = 'day-label';
      switch (i) {
        case 0: label.textContent = 'Monday'; break;
        case 1: label.textContent = 'Tuesday'; break;
        case 2: label.textContent = 'Wednesday'; break;
        case 3: label.textContent = 'Thursday'; break;
        case 4: label.textContent = 'Friday'; break;
      }
      day.appendChild(label);

      var sections = document.createElement('div');
      sections.className = 'day-sections';
      day_sections.push(sections);
      day.appendChild(sections);

      wrapper.appendChild(day);
    }

    // Add the item
    var something = document.createElement('div');
    something.style.clear = 'both';

    var header = document.createElement('h2');
    header.className = 'timetable-heading';

    var header_link = document.createElement('a');
    header_link.setAttribute('href', '#');
    header_link.setAttribute('data-collapse-trigger', '#' + slugify(season));

    if (outdated(season))
      header_link.setAttribute('data-collapse-default', 'true');

    header_link.textContent = season;
    header.appendChild(header_link);
    
    console.log(header);

    something.appendChild(header);
    something.appendChild(wrapper);

    var contents = document.querySelector('.contents');
    contents.appendChild(something);

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
    console.log(now.getFullYear() * 3 + (now.getMonth() % 4));
    console.log(season, seasonToInt(season));
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
      var day_sections = createSeason(season);

      for (var i = 0; i < day_sections.length; i++) {
        renderSchedule(day_sections[i], days[i+1]);
      }
    });

    // Ensure that the collapser callbacks are correctly hooked up
    registerCollapsers(document.querySelector('.contents'));
  }

})();

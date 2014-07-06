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

  /* var schedule = [
    {
      room: 'DUNNING AUD',
      code: "CISC 121",
      startHr: 8,
      startMin: 30,
      endHr: 9,
      endMin: 30
    },
    {
      room: 'DUNNING AUD',
      code: "CISC 226",
      startHr: 9,
      startMin: 30,
      endHr: 10,
      endMin: 30
    },
    {
      room: 'DUNNING AUD',
      code: "CISC 345",
      startHr: 13,
      startMin: 30,
      endHr: 15,
      endMin: 00
    },
    {
      room: 'DUNNING AUD',
      startHr: 11,
      startMin: 30,
      endHr: 14,
      endMin: 30
    }
  ];

  renderSchedule(document.getElementById('day-1'), schedule);
  renderSchedule(document.getElementById('day-2'), schedule); */
  var unloaded = 0;
  var days = [
    [], // Sunday
    [], // Monday
    [], // Tuesday
    [], // Wednesday
    [], // Thursday
    [], // Friday
    []  // Saturday
  ];

  var sections = JSON.parse(localStorage.getItem('timetable-sections') || '[]');
  forEach(sections, function(section) {
    unloaded++;

    var xhr = new XMLHttpRequest();
    xhr.addEventListener('load', function() {
      unloaded--;
      var data = JSON.parse(this.responseText);
      forEach(data.classes, function(aClass) {
        var startTime = new Date(aClass.start_time);
        var endTime = new Date(aClass.end_time);

        console.log(startTime);
        console.log(endTime);

        days[aClass.day_of_week].push({
          room: aClass.location,
          code: data.subject + ' ' + data.course,
          startHr: startTime.getUTCHours(),
          startMin: startTime.getUTCMinutes(),
          endHr: endTime.getUTCHours(),
          endMin: endTime.getUTCMinutes()
        });
      });

      console.log('unloaded: ' + unloaded);
      console.log(days);

      if (unloaded <= 0)
        renderAllSchedules();
    });
    xhr.open('get', '/timetable/section/' + encodeURIComponent(section), true);
    xhr.send();
  });


  function renderAllSchedules() {
    for (var i=1; i < 6; i++) { // Skip SATURADY and SUNDAY
      renderSchedule(document.getElementById('day-' + i), days[i]);
    }
  }
  console.log(sections);


})();

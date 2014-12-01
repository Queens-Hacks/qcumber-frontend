(function() {
  var sections = JSON.parse(localStorage.getItem('timetable-sections') || "[]");

  var sectionElements = document.querySelectorAll('.section');

  forEach(sectionElements, function(section) {
    var header = section.querySelector('header');
    var id = section.getAttribute('data-id');

    // Create the link item
    var linky = document.createElement('a');

    if (indexOf(sections, id) !== -1)
      linky.innerHTML = 'Remove from Timetable';
    else
      linky.innerHTML = 'Add to Timetable';

    linky.className = 'timetable-add';
    linky.href = '#';

    linky.addEventListener('click', function(e) {

      var i;
      if ((i = indexOf(sections, id)) !== -1) {
        console.log(i);
        sections.splice(i, 1);
        console.log(sections);
        localStorage.setItem('timetable-sections', JSON.stringify(sections));

        linky.innerHTML = 'Add to Timetable';
      } else {
        sections.push(id);
        localStorage.setItem('timetable-sections', JSON.stringify(sections));

        linky.innerHTML = 'Remove from Timetable';
      }

      e.preventDefault();
    });

    header.appendChild(linky);
  });
})();

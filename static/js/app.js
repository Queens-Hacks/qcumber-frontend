(function() {
  $('body').djax('.updatable', []);

  $(window).on('djaxLoad', function(e, data) {
    // TODO: Consider possibility of not parsing entire target page for class
    var $data = $('<div>'+data.response+'</div>');
    var newCls = $data.find('#page-wrapper').attr('class');
    $('#page-wrapper').attr('class', newCls);

    $(window).trigger('pageReady');
  });

  $(window).on('pageReady', function(e) {
    // Try to re-render any facebook stuff
    if (FB)
      FB.XFBML.parse();
  });

  var searchPrompts = [
    "Courses in: MATH",
    "More about: ANAT 100",
    "Courses about: Statistics",
    "Courses about: Relativity",
    "Courses about: Germany",
    "More about: CISC 124",
    "Courses in: ARTF",
    "Courses about: Biotechnology",
    "Courses about: Neuroscience"
  ];
  var generateSearchPrompt = function() {
    if ($('#page-wrapper').hasClass('home')) {
      var idx = Math.floor(Math.random() * searchPrompts.length);
      $('#home-search-box').attr('placeholder', searchPrompts[idx]);
    }
  }
  var searchPromptInterval = null;
  $(window).on('pageReady', function(e) {
    if ($('#page-wrapper').hasClass('home')) {
      // Select the search box
      $('#home-search-box').focus().select();

      // Generate random prompts
      generateSearchPrompt();
      searchPromptInterval = setInterval(generateSearchPrompt, 4000);
    } else {
      // Clear the random prompt generator
      clearInterval(searchPromptInterval);
    }
  });

  $(window).load(function() {
    $(window).trigger('pageReady');
  });
})();


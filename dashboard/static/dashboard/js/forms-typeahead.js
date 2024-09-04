/**
 * Typeahead (jquery)
 */

'use strict';

$(function () {
  // String Matcher function
  var substringMatcher = function (strs) {
    return function findMatches(q, cb) {
      var matches, substrRegex;
      matches = [];
      substrRegex = new RegExp(q, 'i');
      $.each(strs, function (i, str) {
        if (substrRegex.test(str)) {
          matches.push(str);
        }
      });

      cb(matches);
    };
  };
  fetch('../../static/dashboard/json/education.json')
        .then(response => response.json())
        .then(data => {
            // Check if data is a plain array
            if (Array.isArray(data)) {

      if (isRtl) {
        $('.typeahead').attr('dir', 'rtl');
      }

      // Basic
      // --------------------------------------------------------------------
      $('.typeahead').typeahead(
        {
          hint: !isRtl,
          highlight: true,
          minLength: 1
        },
        {
          name: 'states',
          source: substringMatcher(data)
        }
      );
      } else {
                console.error('Education data is not an array:', data);
            }
        })
        .catch(error => console.error('Error fetching education:', error));


});

// Function to show suggestions when a field is clicked
  function showSuggestions(fieldId) {
    // Hide all suggestion messages
    var suggestions = document.querySelectorAll(".form-text.text-muted");
    suggestions.forEach(function(suggestion) {
      suggestion.style.display = "none";
    });

    // Get the suggestion message element for the clicked field
    var suggestion = document.getElementById(fieldId + "_suggestion");

    // Show the suggestion message for the clicked field
    suggestion.style.display = "block";
  }

  // Function to hide suggestion when focus is lost
  function hideSuggestions(fieldId) {
    // Get the suggestion message element for the field
    var suggestion = document.getElementById(fieldId + "_suggestion");

    // Hide the suggestion message
    suggestion.style.display = "none";
  }


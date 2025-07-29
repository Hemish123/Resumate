// Function to show suggestions when a field is clicked
function showSuggestions(fieldId) {
  // Hide all suggestion messages
  var suggestions = document.querySelectorAll(".form-text.text-muted");
  suggestions.forEach(function (suggestion) {
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

document.addEventListener("DOMContentLoaded", () => {
  const toggles = document.querySelectorAll(".toggle-password");

  toggles.forEach((icon) => {
    icon.addEventListener("click", () => {
      const inputId = icon.getAttribute("data-target");
      const input = document.getElementById(inputId);

      if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
      } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
      }
    });
  });
});

// Get all buttons with the class 'btn-link' and attach event listeners
document.querySelectorAll('.btn-link').forEach(function(button) {
    button.addEventListener('click', function() {
        // Get the URL from the button's data-url attribute
        var link = this.getAttribute('data-url');

        // Get the icon inside the button
        var icon = this.querySelector(".ti-copy");

        // Create a temporary textarea element to hold the URL
        var tempInput = document.createElement("textarea");
        tempInput.value = link;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);

        // Change the icon class to indicate success
        icon.classList.remove("ti-copy");
        icon.classList.add("ti-copy-check-filled");

        // Revert the icon back to the original after 3 seconds
        setTimeout(function() {
            icon.classList.remove("ti-copy-check-filled");
            icon.classList.add("ti-copy");
        }, 3000); // Revert after 3 seconds
    });
});

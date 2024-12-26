// your.js

document.addEventListener('DOMContentLoaded', function() {

    // Toastr options
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": false,
        "positionClass": "toast-top-center",
        "preventDuplicates": true,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    // Select all message divs

    const messageDivs = document.querySelectorAll('.messages');

    // Iterate over each message div and display it using Toastr
    messageDivs.forEach(div => {
        const messageText = div.getAttribute('data-message');
        const messageTags = div.getAttribute('data-tags');

        if (messageTags === 'error') {
            toastr.error(messageText);
        } else if (messageTags === 'success') {
            toastr.success(messageText);
            toastr.options.showDuration = 3000;
        } else if (messageTags === 'info') {
            toastr.info(messageText);
        } else if (messageTags === 'warning') {
            toastr.warning(messageText);
        }

        // Optionally, remove the message div from the DOM after displaying it as a toast
        div.remove();
    });
});

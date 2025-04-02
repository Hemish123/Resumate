$(document).ready(function() {
function searchResumes() {
        var query = $('#search-input').val();

        $.ajax({
            url: "/candidate/resume-search/",
            type: "GET",
            data: { 'q': query },
            success: function(data) {
                var results = data.results;
                var counts = data.counts;
                var tableBody = $('table tbody');
                var countDiv = $('#count');
                tableBody.empty();  // Clear the existing rows

                if (results.length > 0) {
                    results.forEach(function(result) {
                        var row = '<tr data-id="' + result.id + '">' +
                                    '<td><input type="checkbox" class="row-checkbox" /></td>' +
                                    '<td><a href="' + result.resume_url + '">' + result.filename + '</a></td>' +
                                    '<td>' + result.content + '</td>' +
                                    '<td>' + result.updated + '</td>' +
                                  '</tr>';
                        tableBody.append(row);
                    });
                    countDiv.html('<div id="count" class="m-2 mt-4"><p>' + counts + '</p></div>');

                } else {
                    tableBody.append('<tr><td colspan="4">No results found</td></tr>');
                    countDiv.html('<div id="count">' + counts + '</div>');
                }
            },
            error: function(xhr, status, error) {
                console.log('Error:', error);
            }
        });
    }
    $('#search-button').on('click', function() {
       searchResumes();
    });
        // Search on Enter key press inside the search input
    $('#search-input').on('keypress', function(event) {
        if (event.which === 13) {  // 13 is the Enter key
            event.preventDefault();  // Prevent form submission (if inside a form)
            searchResumes();
        }
    });

    const selectAll = document.getElementById("select-all");
        const checkboxes = document.querySelectorAll(".row-checkbox");
        const bulkAction = document.getElementById("shareJobOpeningForm");

    // Select all checkboxes
    $(document).on('change', '#select-all', function () {
        const isChecked = $(this).is(':checked');
        $('.row-checkbox').prop('checked', isChecked); // Update all row checkboxes
        toggleBulkActionButton();
    });

    // Toggle bulk action button based on row checkboxes
    $(document).on('change', '.row-checkbox', function () {
        toggleBulkActionButton();
    });

        function toggleBulkActionButton() {
            const anyChecked = Array.from(checkboxes).some((checkbox) => checkbox.checked);
            bulkAction.disabled = !anyChecked;
        }


        $('#shareJobOpeningForm').on('submit', function(e) {
        e.preventDefault();  // Prevent default form submission
        checkboxes.forEach((checkbox) => {
    console.log('Checkbox checked:', checkbox.checked, 'Row ID:', checkbox.closest('tr').dataset.id);
});
                    const selectedIds = $('.row-checkbox:checked').map(function () {
                        return $(this).closest('tr').data('id');
                    }).get(); // Use `.get()` to retrieve an array of IDs

            console.log('d', selectedIds);
            if (selectedIds.length) {
               var selectedJobOpening = $('#jobOpening').val(); // Get the selected job opening ID
                // Perform your desired action (e.g., send data to server)
                $.ajax({
                  url: $(this).attr('action'),  // Replace with your delete endpoint
                  method: 'POST',
                  data: {
                    'ids[]': selectedIds,
                    'job_opening_id': selectedJobOpening,  // Include job opening ID

                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // Add CSRF token
                  },
                  success: function(response) {
                    // On success, remove rows from DataTable
                    $('.row-checkbox').prop('checked', false); // Uncheck individual checkboxes
                    $('#select-all').prop('checked', false);
                    $('#shareOpening').modal('hide');
                  },
                  error: function(xhr, status, error) {
                    console.error('Error sending mail:', status, error);
                    // Optionally, show an error message to the user
                  }
                });
            }
        });
});

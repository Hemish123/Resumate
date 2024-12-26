$(document).ready(function() {
    $('#search-button').on('click', function() {
        var query = $('#search-input').val();

        $.ajax({
            url: "/candidate/resume-search/",
            type: "GET",
            data: { 'q': query },
            success: function(data) {
                var results = data.results;
                var tableBody = $('table tbody');
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
                } else {
                    tableBody.append('<tr><td colspan="3">No results found</td></tr>');
                }
            },
            error: function(xhr, status, error) {
                console.log('Error:', error);
            }
        });
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

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

        // Select/Deselect all checkboxes
        selectAll.addEventListener("change", function () {
            checkboxes.forEach((checkbox) => {
                checkbox.checked = selectAll.checked;
            });
            toggleBulkActionButton();
        });

        // Toggle bulk action button based on selected rows
        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", toggleBulkActionButton);
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
            const selectedIds = Array.from(checkboxes)
                .filter((checkbox) => checkbox.checked)
                .map((checkbox) => checkbox.closest("tr").dataset.id);
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
                    dt_basic.rows('.selected').nodes().to$().find('input[type="checkbox"]').prop('checked', false);
                    dt_basic.rows().nodes().to$().removeClass('selected');
                    $('.dt-checkboxes-select-all input').prop('checked', false);
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

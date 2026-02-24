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
        // const checkboxes = document.querySelectorAll(".row-checkbox");
        function getCheckboxes() {
            return document.querySelectorAll(".row-checkbox");
        }
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

        // function toggleBulkActionButton() {
        //     const anyChecked = Array.from(checkboxes).some((checkbox) => checkbox.checked);
        //     bulkAction.disabled = !anyChecked;
        // }
        function toggleBulkActionButton() {
            const anyChecked = Array.from(getCheckboxes())
                .some((checkbox) => checkbox.checked);
            bulkAction.disabled = !anyChecked;
        }


        $('#shareJobOpeningForm').on('submit', function(e) {
        e.preventDefault();  // Prevent default form submission
        // checkboxes.forEach((checkbox) => {
         getCheckboxes().forEach((checkbox) => {
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
                    "ids": JSON.stringify(selectedIds),
                    'job_opening_id': selectedJobOpening,  // Include job opening ID

                    csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // Add CSRF token
                  },
                  success: function(response) {
                    // On success, remove rows from DataTable
                    $('.row-checkbox').prop('checked', false); // Uncheck individual checkboxes
                    $('#select-all').prop('checked', false);
                    $('#shareOpening').modal('hide');
                  },
                  error: function(xhr){
                    console.log("Error:", xhr.responseText);
                }
                });
            }
        });

/* ================= FILTER ================= */

const tableBody = document.getElementById("resume-body");
const countDiv = document.getElementById("count");

function fetchFilteredData() {

    let params = new URLSearchParams({

        name: $('#filter-name').val(),
        filename: $('#filter-filename').val(),
        designation: $('#filter-designation').val(),
        experience: $('#filter-experience').val(),
        education: $('#filter-education').val(),
        skill: $('#filter-skill').val(),
        industry: $('#filter-industry').val(),
        location: $('#filter-location').val(),

    });

    fetch(`/candidate/resume-filter/?${params.toString()}`)
        .then(response => response.json())
        .then(data => {

            tableBody.innerHTML = "";

            if (data.results.length > 0) {

                data.results.forEach(item => {
                    tableBody.innerHTML += `
                        <tr data-id="${item.id}">
                            <td><input type="checkbox" class="row-checkbox" /></td>
                            <td>
                                <a href="${item.resume_url}" target="_blank">
                                    ${item.filename}
                                </a>
                            </td>
                            <td>${item.content}</td>
                            <td>${item.updated}</td>
                        </tr>
                    `;
                });

            } else {

                tableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center">
                            No results found
                        </td>
                    </tr>
                `;
            }

            if (countDiv) {
                countDiv.innerHTML = `<p>${data.counts}</p>`;
            }

        })
        .catch(error => {
            console.error("Filter error:", error);
        });
}


/* Trigger on typing */
$('#filter-name, #filter-filename, #filter-designation, #filter-experience, #filter-education, #filter-skill, #filter-industry,#filter-location')
    .on('keyup change', function () {
        fetchFilteredData();
    });


});


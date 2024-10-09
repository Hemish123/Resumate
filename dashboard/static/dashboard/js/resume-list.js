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
                        var row = '<tr>' +
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
});

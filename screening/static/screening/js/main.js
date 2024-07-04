
document.addEventListener('DOMContentLoaded', function(){
    // delete button
    function deleteResumes(){
        var deleteButton = document.querySelectorAll('.delete-button');
         deleteButton.forEach(function(button, index) {

                button.addEventListener('click', function() {
                    if (confirm("Are you sure you want to delete this item?")) {
                          button.closest('.deleteForm').submit();
                    }
                });
            });
    }



    // for dropdown selection
    function dropdownSelection() {
        console.log(categoryChoices);

        // Get the initial value of the field
        var field = $('#id_field').val();

        // Change event handler for the field
        $('#id_field').change(function() {
            const field = $(this).val();
            console.log(field);

            // Get the category choices for the selected field
            const category = categoryChoices[field];
            const $fieldDropdown = $('#id_field');
            const $categoryDropdown = $('#id_category');

            // Clear the category dropdown and populate with new options
            $categoryDropdown.empty();
            $categoryDropdown.append($('<option>', { value: '', text: 'Please Select Category', selected: true }));

            $.each(category, function(index, category) {
                console.log(category);
                $categoryDropdown.append($('<option>', { value: category[0], text: category[1] }));
            });
        });

        // Trigger change event to populate category dropdown initially
        $('#id_field').trigger('change');
    }


    // input for upload
    function uploadResumes(){
        const fileInput = document.getElementById('fileInput');
        const fileNameDisplay = document.getElementById('fileName');

        fileInput.addEventListener('change', function() {
            fileNameDisplay.textContent = 'Selected Files: ';
            files = fileInput.files;
            for (var i = 0; i < files.length; i++) {
                // Access individual file using files[i]
                fileNameDisplay.textContent += files[i].name;
                if (i<(files.length-1)) {
                    fileNameDisplay.textContent += ' , ' ;
                }
            }
        });
    }

    deleteResumes();
    dropdownSelection();
    uploadResumes();

});


//for goback button logic
function goBack() {
    window.history.back();
}
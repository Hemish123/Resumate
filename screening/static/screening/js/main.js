
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

        if (fileInput && fileName) {
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
    }

    function checkLength() {
        const element = document.getElementById('id_notice_period');
        if (element) {
        element.addEventListener('input', function() {
                if (element.value.length > 2) {
                    element.value = element.value.slice(0, 2);
                }
            });
        }
    }

//    // Automatically remove messages after 2 seconds
//    setTimeout(function() {
//        var messagesElement = document.querySelector('.messages');
//        if (messagesElement) {
//            messagesElement.remove();
//        }
//    }, 2000); // 2000 milliseconds = 2 seconds

    checkLength();
    deleteResumes();
    dropdownSelection();
    uploadResumes();


});


//for goback button logic
function goBack() {
    window.history.back();
}
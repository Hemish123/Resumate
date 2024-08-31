
const fileInput = document.getElementById("fileInput");

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}


// for resume upload in application
if (fileInput){
fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('upload_resume', file);

        // Send the file to the server via Fetch API
        fetch('', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),  // CSRF token for security
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('success!');
                // Populate form fields with parsed data
//                document.querySelector('input[name="name"]').value = data.parsed_data.name;
//                document.querySelector('input[name="email"]').value = data.parsed_data.email;
//                document.querySelector('input[name="skills"]').value = data.parsed_data.skills;
//                document.querySelector('input[name="experience"]').value = data.parsed_data.experience;
            } else {
                alert('Error parsing resume. Please try again.');
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
}
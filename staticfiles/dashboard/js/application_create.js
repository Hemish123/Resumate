
const fileInput = document.getElementById("fileInput");
const form_field = document.getElementById("parse_data");
if (form_field){
    form_field.style.display = "none";
}

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

        document.querySelector('.preloader-container').style.display = 'flex';

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
            document.querySelector('.preloader-container').style.display = 'none';
            form_field.style.display = "block";
//                alert('success!');
                // Populate form fields with parsed data
                document.querySelector('input[name="name"]').value = data.parsed_data.name;
                document.querySelector('input[name="email"]').value = data.parsed_data.email;
                document.querySelector('input[name="contact"]').value = data.parsed_data.contact;
                document.querySelector('input[name="education"]').value = data.parsed_data.education;
                document.querySelector('input[name="location"]').value = data.parsed_data.location;

                document.querySelector('input[name="current_designation"]').value = data.parsed_data.designation;
//                document.querySelector('input[name="skills"]').value = data.parsed_data.skills;
                if (data.parsed_data.total_experience) {
                    document.querySelector('input[name="experience"]').value = data.parsed_data.total_experience;
                }
                else {
                    document.querySelector('input[name="experience"]').value = 0;
                }
            } else {
                document.querySelector('.preloader-container').style.display = 'none';
                alert('Error parsing resume. Please try again.');
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
}
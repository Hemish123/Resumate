
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
// ✅ NEW FUNCTION: Display error alert
function showErrorAlert(errorMessage, errorType = 'error') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-danger alert-dismissible fade show mt-2`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <strong>❌ ${errorType === 'storage' ? 'Storage Error:' : errorType === 'parse' ? 'Parse Error:' : 'Upload Error:'}</strong>
        <div class="mt-1">${errorMessage}</div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Get file input's parent div
    const fileInputDiv = document.querySelector('[name="upload_resume"]').parentElement;
    
    // Remove any existing error alert
    const existingAlert = fileInputDiv.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // Add new error alert
    fileInputDiv.appendChild(alertDiv);
}
 
// ✅ NEW FUNCTION: Clear error alerts
function clearErrorAlert() {
    const fileInputDiv = document.querySelector('[name="upload_resume"]').parentElement;
    const existingAlert = fileInputDiv.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    fileInput.classList.remove('is-invalid');
}

// for resume upload in application
if (fileInput){
fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        clearErrorAlert();
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
                // ✅ MODIFY THIS SECTION: Handle all response types
                document.querySelector('.preloader-container').style.display = 'none';
                
                // ✅ NEW: Check for storage error
                if (data.storage_exceeded || data.is_storage_error) {
                    fileInput.classList.add('is-invalid');
                    const errorMsg = data.error_message || (data.errors && data.errors.upload_resume ? data.errors.upload_resume[0] : 'Storage limit exceeded! Your storage limit is 1 GB. If you need more storage, please contact info@jmsadvisory.in.');
                    showErrorAlert(errorMsg, 'storage');
                    fileInput.value = '';
                    return;
                }
                
                // ✅ NEW: Check for parse error
                if (!data.success) {
                    fileInput.classList.add('is-invalid');
                    const errorMsg = data.error_message || 'Error parsing resume. Please try again.';
                    showErrorAlert(errorMsg, 'parse');
                    fileInput.value = '';
                    return;
                }
                
                // ✅ Success case (keep existing code)
                if (data.success) {
                    form_field.style.display = "block";
                    // Populate form fields with parsed data
                    document.querySelector('input[name="name"]').value = data.parsed_data.name;
                    document.querySelector('input[name="email"]').value = data.parsed_data.email;
                    document.querySelector('input[name="contact"]').value = data.parsed_data.contact;
                    document.querySelector('input[name="education"]').value = data.parsed_data.education;
                    document.querySelector('input[name="location"]').value = data.parsed_data.location;
                    document.querySelector('input[name="current_designation"]').value = data.parsed_data.designation;
                    
                    if (data.parsed_data.total_experience) {
                        document.querySelector('input[name="experience"]').value = data.parsed_data.total_experience;
                    } else {
                        document.querySelector('input[name="experience"]').value = 0;
                    }
                }
            })
            .catch(error => {
                // ✅ MODIFY THIS SECTION: Show error alert instead of console
                document.querySelector('.preloader-container').style.display = 'none';
                console.error('Error:', error);
                fileInput.classList.add('is-invalid');
                showErrorAlert('Network error. Please try again.', 'error');
            });
        }
    });
}

document.querySelector('form').addEventListener('submit', function () {
        const preloader = document.querySelector('.preloader-container');
        const innerDiv = preloader.querySelector('div');
        innerDiv.innerText = "Loading";

        document.querySelector('.preloader-container').style.display = 'flex';
});



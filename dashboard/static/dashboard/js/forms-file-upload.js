/**
 * File Upload
 */

// my created dropzone

const fileInput = document.getElementById("fileInput");
const dropzone = document.getElementById("dropzone");
const selectedFilenameSpan = document.getElementById("selected-filename");
let selectedFile = null; // Store the selected file

// Event listeners for file selection
fileInput.addEventListener("change", handleFile);
dropzone.addEventListener("drop", handleDrop);
dropzone.addEventListener("click", function () {
  fileInput.click(); // Simulate click on file input when dropzone is clicked
});

// Drag and drop behavior
document.addEventListener("dragover", function (event) {
  event.preventDefault();
  dropzone.classList.add("dragover"); // Add visual feedback on drag
});

document.addEventListener("dragleave", function (event) {
  event.preventDefault();
  dropzone.classList.remove("dragover"); // Remove visual feedback on drag leave
});


function handleFile(event) {
  selectedFile = event.target.files[0]; // Get the first selected file
  if (selectedFile) {
    selectedFilenameSpan.textContent = selectedFile.name;
  } else {
    selectedFilenameSpan.textContent = "No file selected";
  }
}

function handleDrop(event) {
  event.preventDefault();
  selectedFile = event.dataTransfer.files[0]; // Get the first dropped file
  if (selectedFile) {
    selectedFilenameSpan.textContent = selectedFile.name;
    updateFileInput();
  } else {
    selectedFilenameSpan.textContent = "No file selected";
  }
}

function updateFileInput() {
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(selectedFile);
  document.getElementById("fileInput").files = dataTransfer.files;
}

function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

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

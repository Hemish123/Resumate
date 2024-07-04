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
  } else {
    selectedFilenameSpan.textContent = "No file selected";
  }
}
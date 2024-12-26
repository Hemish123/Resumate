let allSelectedFiles = [];

document.getElementById("fileInput").addEventListener("change", function (event) {
  handleFiles(event.target.files);
  updateFileInput();
});

document.getElementById("dropArea").addEventListener("drop", function (event) {
  event.preventDefault();
  handleFiles(event.dataTransfer.files);
  updateFileInput();
});

document.addEventListener("dragover", function (event) {
  event.preventDefault();
});

function handleFiles(files) {
  const fileList = document.getElementById("fileList");
  fileList.innerHTML = ""; // Clear previous file list

  // Check if newly selected files already exist in the list
  for (const file of files) {
    if (!allSelectedFiles.some((f) => f.name === file.name && f.size === file.size)) {
      // If the file doesn't exist, add it to the list
      allSelectedFiles.push(file);
    }
  }

  if (allSelectedFiles.length === 0) {
    fileList.innerHTML = '<p class="d-flex justify-content-center">No file chosen</p>';
    return;
  }

  // Create a table element
  const table = document.createElement("table");
  table.className = "table table-striped";

  // Create table header
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  const headerCell = document.createElement("th");
  headerCell.textContent = "Selected Files";
  headerRow.appendChild(headerCell);
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Create table body
  const tbody = document.createElement("tbody");

  // List all selected files
  for (const file of allSelectedFiles) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.textContent = file.name;
    row.appendChild(cell);
    tbody.appendChild(row);
  }

  table.appendChild(tbody);
  const tableContainer = document.createElement("div");
  tableContainer.className = "table-container";
  tableContainer.appendChild(table);
  fileList.appendChild(tableContainer);
}

function updateFileInput() {
  const dataTransfer = new DataTransfer();
  allSelectedFiles.forEach((file) => dataTransfer.items.add(file));
  document.getElementById("fileInput").files = dataTransfer.files;
}

function uploadFile() {
  const formData = new FormData();
  allSelectedFiles.forEach((file) => formData.append("upload_resume", file));
  formData.append("csrfmiddlewaretoken", document.querySelector("[name=csrfmiddlewaretoken]").value);

  fetch(document.getElementById("uploadForm").action, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text()) // Get response as text
    .then((data) => {
      window.location.href = '{% url "parsing-resumes" %}';
      allSelectedFiles = [];
      handleFiles(allSelectedFiles);
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

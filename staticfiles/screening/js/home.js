// document.addEventListener("DOMContentLoaded", function() {
//     // Get references to field and category dropdowns
//     var fieldDropdown = document.getElementById("id_field");
//     var categoryDropdown = document.getElementById("id_category");
//     var allResumeScreeningBtn = document.getElementById("allResumeScreeningBtn");
//     var categoryError = document.getElementById("categoryError");
//     var fieldError = document.getElementById("fieldError");

//     // Event listener for field dropdown change
//     fieldDropdown.addEventListener("change", function() {
//         var selectedField = fieldDropdown.value;
//         if (selectedField) {
//             // Show category dropdown
//             document.getElementById("categoryDropdown").style.display = "block";

//             // Get categories based on selected field
//             var categories = getCategoryOptions(selectedField);

//             // Clear previous options
//             categoryDropdown.innerHTML = '<option value="" selected disabled>Choose a Category</option>';

//             // Populate category dropdown with new options
//             categories.forEach(function(category) {
//                 var option = document.createElement('option');
//                 option.value = category;
//                 option.text = category;
//                 categoryDropdown.appendChild(option);
//             });

//             // Hide error message if field is changed
//             fieldError.style.display = "none";
//         } else {
//             // Hide category dropdown if no field selected
//             categoryDropdown.style.display = "none";
//             // Clear category dropdown
//             categoryDropdown.innerHTML = '';
//         }
//     });

//     // Event listener for category dropdown change
//     categoryDropdown.addEventListener("change", function() {
//         if (categoryDropdown.value) {
//             // Hide error message if category is selected
//             categoryError.style.display = "none";
//         }
//     });

//     // Event listener for "All Resume Screening" button
//     allResumeScreeningBtn.addEventListener("click", function(event) {
//         var selectedField = fieldDropdown.value;
//         var selectedCategory = categoryDropdown.value;
//         if (!selectedField || selectedField === "") {
//             event.preventDefault();
//             // Show error message for field
//             fieldError.style.display = "block";
//         } else if (!selectedCategory || selectedCategory === "") {
//             event.preventDefault();
//             // Show error message for category
//             categoryError.style.display = "block";
//         } 
//     });

//     // Function to get categories based on selected field
//     function getCategoryOptions(field) {
//         // Define categories for IT and Non-IT fields
//         var itCategories = ['Python Developer', 'Java Developer', 'DevOps Engineer', 'Database', 'Data Science', 'Web Designing', 'SAP Developer', 'Automation Testing', 'Network Security Engineer', 'DotNet Developer', 'Blockchain', 'Hadoop', 'ETL Developer'];
//         var nonItCategories = ['HR', 'Advocate', 'Arts', 'Mechanical Engineer', 'Sales', 'Health and fitness', 'Civil Engineer', 'Business Analyst', 'Electrical Engineering', 'Operations Manager', 'PMO', 'Testing'];

//         // Return categories based on the selected field
//         if (field === 'IT') {
//             return itCategories;
//         } else if (field === 'Non-IT') {
//             return nonItCategories;
//         } else {
//             return [];
//         }
//     }
// });

// Ensure both dropdowns are initially empty
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("id_field").value = "";
    document.getElementById("id_category").value = "";
});
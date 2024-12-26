// this function is show for confirmation message
function confirmDelete(formId) {
    if (confirm("Are you sure you want to delete this file?")) {
        document.getElementById("deleteForm" + formId).submit();
    } else {
        // Do nothing
    }
}


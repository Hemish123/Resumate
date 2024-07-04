const radioInputs = document.querySelectorAll('input[name="content_type"]');
const fileUploadDiv = document.getElementById('file_upload');
const textInputDiv = document.getElementById('text_input');
const defaultDiv = document.getElementById('default_area');

textInputDiv.style.display = 'none';
fileUploadDiv.style.display = 'none';

radioInputs.forEach(radioInput => {
  radioInput.addEventListener('change', function() {
    defaultDiv.style.display = 'none';
    if (this.value === 'file') {
      fileUploadDiv.style.display = 'block';
      textInputDiv.style.display = 'none';
    } else {
      fileUploadDiv.style.display = 'none';
      textInputDiv.style.display = 'block';
    }
  });
});
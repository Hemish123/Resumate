
// select option for job description
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

// select option for hiring
const hiringFor = document.querySelectorAll('input[name="hiring_for"]');
const clientSelected = document.getElementById('client_selected');
const idClientInput = clientSelected.querySelector('#id_client'); // Use querySelector to find the input element


let selectedValue = '';  // Initialize a variable to hold the selected value

// Loop through each 'hiring_for' radio button to find the checked one
hiringFor.forEach((input) => {
    if (input.checked) {  // If the radio button is checked
        selectedValue = input.value;  // Get the value of the checked radio button
    }
});
if (selectedValue == "client") {
    clientSelected.style.display = 'block';
    idClientInput.setAttribute('required', '');

}
else {
    clientSelected.style.display = 'none';
    idClientInput.removeAttribute('required');
}


hiringFor.forEach(radioInput => {
  radioInput.addEventListener('change', function() {
    if (this.value === 'client') {
      clientSelected.style.display = 'block';
      idClientInput.setAttribute('required', '');
    } else {
      clientSelected.style.display = 'none';
      idClientInput.removeAttribute('required');
    }
  });
});



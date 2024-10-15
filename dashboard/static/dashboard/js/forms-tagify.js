document.addEventListener('DOMContentLoaded', function () {
    fetch('../../../static/dashboard/json/skills.json')
        .then(response => response.json())
        .then(data => {
            // Check if data is a plain array
            if (Array.isArray(data)) {
                // Create the Tagify instance
                const requiredSkillsEl = document.querySelector('#id_requiredskills');
                const requiredSkillsTagify = new Tagify(requiredSkillsEl, {
                    whitelist: data, // Ensure Tagify receives correct format
                    maxTags: 10,
                    dropdown: {
                        maxItems: Infinity,  // Display all items in the dropdown
                        classname: '',       // Additional classes to add to the dropdown
                        enabled: 0,          // Shows the dropdown immediately on focus
                        closeOnSelect: false // Keep the dropdown open after selecting a tag
                    }
                });

                // Ensure the form data is submitted in a format Django can process
                requiredSkillsTagify.on('change', function(e) {
                    const selectedSkills = requiredSkillsTagify.value.map(tag => tag.value).join(', ');
                    requiredSkillsEl.value = selectedSkills;
                    console.log('r', requiredSkillsEl.value);
                });
            } else {
                console.error('Skills data is not an array:', data);
            }
        })
        .catch(error => console.error('Error fetching skills:', error));
});

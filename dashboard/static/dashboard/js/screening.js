'use strict';

const approveBtn = document.querySelectorAll(".approve-btn"),
approveAll = document.querySelector(".approve-all-btn"),
rejectBtn = document.querySelectorAll(".reject-btn");

function getCookie(name) {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) return parts.pop().split(';').shift();
        }


if (approveAll){
        approveAll.addEventListener('click', async(e) => {
            const jobOpeningId = approveAll.getAttribute('data-job_opening_id');
            const response = await fetch(`/screening/screening/${jobOpeningId}/`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({'action': 'approveall'})  // Convert the data to JSON format
                  });

                  const data = await response.json();  // Process the JSON response from the server
                  if (data.status === 'success') {
                  // Remove approve button and replace with "Approved!"
                    const buttonCell = approveAll.parentElement;
                    buttonCell.innerHTML = '<span class="text-success fw-bold">All Approved!</span>';
                  } else {
                    console.log('Failed to approve candidate', data.message);
                  }

        });
}

if (approveBtn){
    approveBtn.forEach(function(btn) {
        btn.addEventListener('click', async(e) => {
            const candidateRow = btn.closest('tr');
            const candidateId = candidateRow.getAttribute('data-id');
            const jobOpeningId = candidateRow.getAttribute('data-job_opening_id');
            const response = await fetch(`/screening/screening/${jobOpeningId}/`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({'candidateId': candidateId, 'action': 'approve'})  // Convert the data to JSON format
                  });

                  const data = await response.json();  // Process the JSON response from the server
                  if (data.status === 'success') {
                      const tooltipInstance = bootstrap.Tooltip.getInstance(btn);
                        if (tooltipInstance) {
                            tooltipInstance.dispose();
                        }
                  // Remove approve button and replace with "Approved!"
                    const buttonCell = btn.parentElement;
                    buttonCell.innerHTML = '<span class="text-success fw-bold">Approved!</span>';
                  } else {
                    console.log('Failed to approve candidate', data.message);
                  }

        });
    });
}

if (rejectBtn) {
    rejectBtn.forEach(function(btn) {
        btn.addEventListener('click', async(e) => {
            e.preventDefault();
            const candidateRow = btn.closest('tr');
            const candidateId = candidateRow.getAttribute('data-id');
            const jobOpeningId = candidateRow.getAttribute('data-job_opening_id');
            const response = await fetch(`/screening/screening/${jobOpeningId}/`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({'candidateId': candidateId, 'action': 'reject'})  // Convert the data to JSON format
                  });

                  const data = await response.json();  // Process the JSON response from the server
                  if (data.status === 'success') {
                    const tooltipInstance = bootstrap.Tooltip.getInstance(btn);
                    if (tooltipInstance) {
                        tooltipInstance.dispose();
                    }
                  // Remove approve button and replace with "Approved!"
                    const buttonCell = btn.parentElement;
                    buttonCell.innerHTML = '<span class="text-danger fw-bold">Rejected!</span>';

                  } else {
                    console.log('Failed to reject candidate', data.message);
                  }

        });
    });
}
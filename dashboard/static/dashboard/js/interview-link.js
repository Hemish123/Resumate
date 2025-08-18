let isSending = false; // flag to prevent duplicate sends

document.addEventListener("DOMContentLoaded", function () {
    const sendBtn = document.getElementById("sendInterviewLink");

    sendBtn.addEventListener("click", function (event) {
        event.preventDefault(); // prevent form from submitting if inside a form

        if (isSending) return; // stop if already sending
        isSending = true;

        sendBtn.disabled = true;
        sendBtn.textContent = "Sending...";

        fetch("/api/send-interview-link/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                candidate_id: selectedCandidateId,
                job_opening_id: selectedJobId,
                additional_notes: notes
            }),
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
        })
        .catch(err => console.error(err))
        .finally(() => {
            isSending = false;
            sendBtn.disabled = false;
            sendBtn.textContent = "Send Interview Link";
        });
    }, { once: true }); // once:true ensures listener is added only once
});

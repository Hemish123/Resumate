    const socket = new WebSocket('wss://' + window.location.host + '/ws/notification/');
    let notificationDot = document.getElementById('notification-dot');
    let notificationCount = document.getElementById("notification-count");
        // Extract the current count from the notification count element
    let currentCountText = notificationCount.innerHTML.trim();
    let currentCount = parseInt(currentCountText.split(' ')[0]);
    if (currentCount === 0){
        notificationDot.style.display = 'none';
    }

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const message = data.message;
        const time = data.time;
        const notificationDropdown = document.getElementById("notification-dropdown");
        const newNotification = document.createElement("li");
        newNotification.className = "list-group-item list-group-item-action dropdown-notifications-item waves-effect";
        newNotification.innerHTML = `<div class="d-flex notification" data-timestamp="${time}">
                                        <div class="flex-grow-1">
                                          <h6 class="small mb-1">${message}</h6>
                                          <small class="text-muted">Just Now</small>
                                        </div>
                                        <div class="flex-shrink-0 dropdown-notifications-actions">
                                          <a href="javascript:void(0)" class="dropdown-notifications-read"
                                            ><span class="badge badge-dot"></span
                                          ></a>
                                          <a href="javascript:void(0)" class="dropdown-notifications-archive"
                                            ><span class="ti ti-x"></span
                                          ></a>
                                        </div>
                                    </div>`;
        notificationDropdown.prepend(newNotification);
        notificationDot.style.display = "inline-block";
        if (!isNaN(currentCount)){
            currentCount += 1;
            notificationCount.innerHTML = `${currentCount} new`;
        }
        else{
            notificationCount.innerHTML = "1 new";

        }
        initializeNotificationHandlers();

    };

    socket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly');
    };

   // Function to update "time ago" for each notification
function updateTimeAgo() {
    const notifications = document.querySelectorAll('.notification');

    notifications.forEach(notification => {
        const timestamp = new Date(notification.getAttribute('data-timestamp'));
        const now = new Date();
        const secondsElapsed = Math.floor((now - timestamp) / 1000);

        let timeAgo;
        if (secondsElapsed < 60) {
            timeAgo = "Just Now";
        } else if (secondsElapsed < 3600) {
            timeAgo = `${Math.floor(secondsElapsed / 60)} minutes ago`;
        } else if (secondsElapsed < 86400) {
            timeAgo = `${Math.floor(secondsElapsed / 3600)} hours ago`;
        } else {
            timeAgo = `${Math.floor(secondsElapsed / 86400)} days ago`;
        }

        notification.querySelector('small.text-muted').textContent = timeAgo; // Update display
    });
}

// Set up interval to update time every minute
setInterval(updateTimeAgo, 60000);
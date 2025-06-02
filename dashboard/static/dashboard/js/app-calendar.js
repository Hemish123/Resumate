/**
 * App Calendar
 */

/**
 * ! If both start and end dates are same Full calendar will nullify the end date value.
 * ! Full calendar will end the event on a day before at 12:00:00AM thus, event won't extend to the end date.
 * ! We are getting events from a separate file named app-calendar-events.js. You can add or remove events from there.
 *
 **/

'use strict';

let direction = 'ltr';

if (isRtl) {
  direction = 'rtl';
}

document.addEventListener('DOMContentLoaded', function () {
  (function () {
    const calendarEl = document.getElementById('calendar'),
      appCalendarSidebar = document.querySelector('.app-calendar-sidebar'),
      addEventSidebar = document.getElementById('addEventSidebar'),
      appOverlay = document.querySelector('.app-overlay'),
      calendarsColor = {
        facetoface: 'primary',
        telephonic: 'success',
        virtual: 'info'
      },
      offcanvasTitle = document.querySelector('.offcanvas-title'),
      btnToggleSidebar = document.querySelector('.btn-toggle-sidebar'),
      btnSubmit = document.querySelector('#addEventBtn'),
      btnDeleteEvent = document.querySelector('.btn-delete-event'),
      btnCancel = document.querySelector('.btn-cancel'),
      eventTitle = document.querySelector('#eventTitle'),
      eventStartDate = document.querySelector('#eventStartDate'),
      eventStartTime = document.querySelector('#eventStartTime'),
      eventEndTime = document.querySelector('#eventEndTime'),
      eventUrl = document.querySelector('#eventURL'),
      interviewer = document.querySelector('#interviewer'),
      eventLabel = $('#eventLabel'), // ! Using jquery vars due to select2 jQuery dependency
      eventGuests = $('#eventGuests'), // ! Using jquery vars due to select2 jQuery dependency
      designation = $('#designation'),
      eventLocation = document.querySelector('#eventLocation'),
      eventDescription = document.querySelector('#eventDescription'),

//      allDaySwitch = document.querySelector('.allDay-switch'),
      selectAll = document.querySelector('.select-all'),
      filterInput = [].slice.call(document.querySelectorAll('.input-filter'));
//      inlineCalendar = document.querySelector('.inline-calendar');




    if (interviewer){
        new Tagify(interviewer, {
            pattern: /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/, // Email validation pattern
            delimiters: ", ",  // Allows adding emails with a comma or space
            enforceWhitelist: false,  // Allow users to enter emails freely
            maxTags: Infinity,  // Allow as many emails as necessary
            dropdown: {
                enabled: 1, // Show suggestions after one character input
                maxItems: 5
            }
        });
    }

    function updateEventBadgeColors(){
        document.querySelectorAll('[id^="upcoming_event_"]').forEach(badge => {
        badge.classList.add({facetoface: 'bg-label-primary', telephonic: 'bg-label-success', virtual: 'bg-label-info'}[badge.dataset.interview_type] || 'bg-label-primary');
    });
    }
    updateEventBadgeColors();


    let events = JSON.parse(calendarEl.dataset.events);

    let eventToUpdate,
      currentEvents = events, // Assign app-calendar-events.js file events (assume events from API) to currentEvents (browser store/object) to manage and update calender events
      isFormValid = false,
      inlineCalInstance;

    // Init event Offcanvas
    const bsAddEventSidebar = new bootstrap.Offcanvas(addEventSidebar);

    //! TODO: Update Event label and guest code to JS once select removes jQuery dependency
    // Event Label (select2)
    if (eventLabel.length) {
      function renderBadges(option) {
        if (!option.id) {
          return option.text;
        }
        var $badge =
          "<span class='badge badge-dot bg-" + $(option.element).data('label') + " me-2'> " + '</span>' + option.text;

        return $badge;
      }
      eventLabel.wrap('<div class="position-relative"></div>').select2({
        placeholder: 'Select value',
        dropdownParent: eventLabel.parent(),
        templateResult: renderBadges,
        templateSelection: renderBadges,
        minimumResultsForSearch: -1,
        escapeMarkup: function (es) {
          return es;
        }
      });
    }

    // Event Guests (select2)
//    if (eventGuests.length) {
//      eventGuests.wrap('<div class="position-relative"></div>').select2({
//        placeholder: 'Select value',
//        dropdownParent: eventGuests.parent(),
//        closeOnSelect: false,
//        escapeMarkup: function (es) {
//          return es;
//        }
//      });
//    }

    // Event start (flatpicker)
    if (eventStartDate) {
      var date = eventStartDate.flatpickr({
        enableTime: false,
        altFormat: 'Y-m-d',
        minDate: "today",
        onReady: function (selectedDates, dateStr, instance) {
          if (instance.isMobile) {
            instance.mobileInput.setAttribute('step', null);
          }
        }
      });
    }

    // Event end (flatpicker)
    if (eventStartTime) {
      var start = eventStartTime.flatpickr({
        enableTime: true,
        noCalendar: true,
        altFormat: 'H:i:S',
        onReady: function (selectedDates, dateStr, instance) {
          if (instance.isMobile) {
            instance.mobileInput.setAttribute('step', null);
          }
        },
        onChange: function(selectedDates, dateStr, instance) {
            if (eventEndTime) {
                // Update the minimum time for the end time picker based on start time
                end.set('minTime', dateStr);
            }
        }
      });
    }
    if (eventEndTime) {
      var end = eventEndTime.flatpickr({
        enableTime: true,
        noCalendar: true,
        altFormat: 'H:i:S',
        onReady: function (selectedDates, dateStr, instance) {
          if (instance.isMobile) {
            instance.mobileInput.setAttribute('step', null);
          }
        }
      });
    }

    // Inline sidebar calendar (flatpicker)
//    if (inlineCalendar) {
//      inlineCalInstance = inlineCalendar.flatpickr({
//        monthSelectorType: 'static',
//        inline: true
//      });
//    }

    // Event click function
    function eventClick(info) {
      eventToUpdate = info.event;
      if (eventToUpdate.url) {
        info.jsEvent.preventDefault();
        window.open(eventToUpdate.url, '_blank');
      }
      bsAddEventSidebar.show();
      // For update event set offcanvas title text: Update Event
      if (offcanvasTitle) {
        offcanvasTitle.innerHTML = 'Update Interview';
      }
      btnSubmit.innerHTML = 'Update';
      btnSubmit.classList.add('btn-update-event');
      btnSubmit.classList.remove('btn-add-event');
      btnDeleteEvent.classList.remove('d-none');

      eventTitle.value = eventToUpdate.title;

      start.setDate(eventToUpdate.extendedProps.start_time, true, 'H:i:S');
      date.setDate(eventToUpdate.extendedProps.date, true, 'Y-m-d');
      end.setDate(eventToUpdate.extendedProps.end_time, true, 'H:i:S');
//      eventToUpdate.allDay === true ? (allDaySwitch.checked = true) : (allDaySwitch.checked = false);

      eventLabel.val(eventToUpdate._def.extendedProps.interview_type).trigger('change');
      eventToUpdate._def.extendedProps.location !== undefined
        ? (eventLocation.value = eventToUpdate._def.extendedProps.location)
        : null;
      eventToUpdate._def.extendedProps.candidate_id !== undefined
        ? eventGuests.val(eventToUpdate._def.extendedProps.candidate_id).trigger('change')
        : null;
      eventToUpdate._def.extendedProps.jobopening_id !== undefined
        ? designation.val(eventToUpdate._def.extendedProps.jobopening_id).trigger('change')
        : null;
      eventToUpdate._def.extendedProps.description !== undefined
        ? (eventDescription.value = eventToUpdate._def.extendedProps.description)
        : null;
      eventToUpdate._def.extendedProps.interviewer !== undefined
        ? (interviewer.value = eventToUpdate._def.extendedProps.interviewer)
        : null;
      eventToUpdate._def.extendedProps.interview_url !== undefined
        ? (eventUrl.value = eventToUpdate._def.extendedProps.interview_url)
        : null;

      // // Call removeEvent function
//       btnDeleteEvent.addEventListener('click', async(e) => {
//       console.log('del');
//       const response = await fetch(`/calendar/`, {
//        method: 'DELETE',
//        headers: {
//          'Content-Type': 'application/json',
//          'X-CSRFToken': getCookie('csrftoken')
//        },
//        body: JSON.stringify({'id': eventToUpdate.id})  // Convert the data to JSON format
//          });
//
//          const data = await response.json();  // Process the JSON response from the server
//          if (data.status === 'success') {
//            console.log('Event deleted successfully');
//          } else {
//            console.log('Failed to delete event', data.message);
//          }
//         removeEvent(parseInt(eventToUpdate.id));
//          eventToUpdate.remove();
//         bsAddEventSidebar.hide();
//       });
    }

    // Modify sidebar toggler
    function modifyToggler() {
      const fcSidebarToggleButton = document.querySelector('.fc-sidebarToggle-button');
      fcSidebarToggleButton.classList.remove('fc-button-primary');
      fcSidebarToggleButton.classList.add('d-lg-none', 'd-inline-block', 'ps-0');
      while (fcSidebarToggleButton.firstChild) {
        fcSidebarToggleButton.firstChild.remove();
      }
      fcSidebarToggleButton.setAttribute('data-bs-toggle', 'sidebar');
      fcSidebarToggleButton.setAttribute('data-overlay', '');
      fcSidebarToggleButton.setAttribute('data-target', '#app-calendar-sidebar');
      fcSidebarToggleButton.insertAdjacentHTML('beforeend', '<i class="ti ti-menu-2 ti-lg text-heading"></i>');
    }

    // Filter events by calender
    function selectedCalendars() {
      let selected = [],
        filterInputChecked = [].slice.call(document.querySelectorAll('.input-filter:checked'));

      filterInputChecked.forEach(item => {
        selected.push(item.getAttribute('data-value'));
      });

      return selected;
    }

    // --------------------------------------------------------------------------------------------------
    // AXIOS: fetchEvents
    // * This will be called by fullCalendar to fetch events. Also this can be used to refetch events.
    // --------------------------------------------------------------------------------------------------
    function fetchEvents(info, successCallback) {
      // Fetch Events from API endpoint reference
      /* $.ajax(
        {
          url: '../../../app-assets/data/app-calendar-events.js',
          type: 'GET',
          success: function (result) {
            // Get requested calendars as Array
            var calendars = selectedCalendars();

            return [result.events.filter(event => calendars.includes(event.extendedProps.calendar))];
          },
          error: function (error) {
            console.log(error);
          }
        }
      ); */

      let calendars = selectedCalendars();
      // We are reading event object from app-calendar-events.js file directly by including that file above app-calendar file.
      // You should make an API call, look into above commented API call for reference
      let selectedEvents = currentEvents.filter(function (event) {
        // console.log(event.extendedProps.calendar.toLowerCase());
        return calendars.includes(event.extendedProps.interview_type.toLowerCase());
      });
      // if (selectedEvents.length > 0) {
      successCallback(selectedEvents);
      // }
    }

    // Init FullCalendar
    // ------------------------------------------------
    let calendar = new Calendar(calendarEl, {
      initialView: 'dayGridMonth',
      validRange: {
        start: new Date()  // Disables past dates
      },
      events: fetchEvents,
      plugins: [dayGridPlugin, interactionPlugin, listPlugin, timegridPlugin],
      editable: true,
      dragScroll: true,
      dayMaxEvents: 2,
      eventResizableFromStart: true,
      customButtons: {
        sidebarToggle: {
          text: 'Sidebar'
        }
      },
      headerToolbar: {
        start: 'sidebarToggle, prev,next, title',
        end: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
      },
      direction: direction,
      initialDate: new Date(),
      navLinks: true, // can click day/week names to navigate views
      eventClassNames: function ({ event: calendarEvent }) {
        const colorName = calendarsColor[calendarEvent._def.extendedProps.interview_type];
        // Background Color
        return ['fc-event-' + colorName];
      },
      dateClick: function (info) {
        let date = moment(info.date).format('YYYY-MM-DD');
        resetValues();
        bsAddEventSidebar.show();

        // For new event set offcanvas title text: Add Event
        if (offcanvasTitle) {
          offcanvasTitle.innerHTML = 'Add Interview';
        }
        btnSubmit.innerHTML = 'Add';
        btnSubmit.classList.remove('btn-update-event');
        btnSubmit.classList.add('btn-add-event');
        btnDeleteEvent.classList.add('d-none');
        eventStartDate.value = date;
      },
      eventClick: function (info) {
        eventClick(info);
      },
      datesSet: function () {
        modifyToggler();
      },
      viewDidMount: function () {
        modifyToggler();
      }
    });

    // Render calendar
    calendar.render();
    // Modify sidebar toggler
    modifyToggler();




    const eventForm = document.getElementById('eventForm');
    const fv = FormValidation.formValidation(eventForm, {
      fields: {
        title: {
          validators: {
            notEmpty: {
              message: 'Please enter event title '
            }
          }
        },
        interview_type: {
          validators: {
            notEmpty: {
              message: 'Please select type of interview '
            }
          }
        },
        date: {
          validators: {
            notEmpty: {
              message: 'Please enter start date '
            }
          }
        },
        starttime: {
          validators: {
            notEmpty: {
              message: 'Please enter start time '
            }
          }
        },
        endtime: {
          validators: {
            notEmpty: {
              message: 'Please enter end time '
            }
          }
        },

        interviewer: {
          validators: {
            notEmpty: {
              message: 'Please enter interviewer email '
            }
          }
        },
        candidate: {
          validators: {
            notEmpty: {
              message: 'Please select candidate '
            }
          }
        },
        designation: {
          validators: {
            notEmpty: {
              message: 'Please select designation '
            }
          }
        },
        location: {
          validators: {
            notEmpty: {
              message: 'Please enter location URL '
            }
          }
        },
        interview_url: {
          validators: {
            notEmpty: {
              message: 'Please provide an interview URL '
            }
          }
        }
      },
      plugins: {
        trigger: new FormValidation.plugins.Trigger(),
        bootstrap5: new FormValidation.plugins.Bootstrap5({
          // Use this for enabling/changing valid/invalid class
          eleValidClass: '',
          rowSelector: function (field, ele) {
            // field is the field name & ele is the field element
            return '.mb-5';
          }
        }),
        submitButton: new FormValidation.plugins.SubmitButton(),
        // Submit the form when all fields are valid
        // defaultSubmit: new FormValidation.plugins.DefaultSubmit(),
        autoFocus: new FormValidation.plugins.AutoFocus()
      }
    })
      .on('core.form.valid', function () {
        // Jump to the next step when all fields in the current step are valid
        isFormValid = true;
      })
      .on('core.form.invalid', function () {
        // if fields are invalid
        isFormValid = false;
      });

    // Select the interview type dropdown and the fields
    const interviewTypeField = document.getElementById("eventLabel");
    const interviewURLField = document.getElementById("eventURL").closest(".mb-5");
    const locationField = document.getElementById("eventLocation").closest(".mb-5");

    // Helper function to check if a field is already registered
    const isFieldRegistered = (fieldName) => {
      return fv.getFields().hasOwnProperty(fieldName);
    };

    // Function to toggle fields based on interview type
    const toggleFields = () => {
        const selectedType = interviewTypeField.value;

        // Reset the validators for location and interview_url
      // Remove fields safely
      if (isFieldRegistered("location")) {
        fv.removeField("location");
      }
      if (isFieldRegistered("interview_url")) {
        fv.removeField("interview_url");
      }

      // Add validation based on the selected interview type

        if (selectedType === "facetoface") {
            // Show Location, hide Interview URL
            locationField.style.display = "block";
            interviewURLField.style.display = "none";
            fv.addField('location', {
              validators: {
                notEmpty: {
                  message: 'Please enter location '
                }
              }
            });
            if (isFieldRegistered("interview_url")) {
                fv.removeField("interview_url");
              }
        } else if (selectedType === "virtual") {
            // Show Interview URL, hide Location
            interviewURLField.style.display = "block";
            locationField.style.display = "none";
            fv.addField('interview_url', {
              validators: {
                notEmpty: {
                  message: 'Please provide an interview URL '
                }
              }
            });
            if (isFieldRegistered("location")) {
                fv.removeField("location");
              }
        } else if (selectedType === "telephonic") {
            // Hide both fields
            interviewURLField.style.display = "block";
            locationField.style.display = "none";
            if (isFieldRegistered("location")) {
                fv.removeField("location");
              }
              if (isFieldRegistered("interview_url")) {
                fv.removeField("interview_url");
              }
        }
    };

    // Initialize fields on page load
    toggleFields();

    // Add event listener for changes
    $('#eventLabel').on("change", toggleFields);
    // Sidebar Toggle Btn
    if (btnToggleSidebar) {
      btnToggleSidebar.addEventListener('click', e => {
        btnCancel.classList.remove('d-none');
      });
    }

    function getCookie(name) {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) return parts.pop().split(';').shift();
        }
    // Add Event
    // ------------------------------------------------
    function addEvent(eventData) {
      // ? Add new event data to current events object and refetch it to display on calender
      // ? You can write below code to AJAX call success response

      currentEvents.push(eventData);
      calendar.refetchEvents();

      // ? To add event directly to calender (won't update currentEvents object)
      // calendar.addEvent(eventData);
    }

    // Update Event
    // ------------------------------------------------
    function updateEvent(eventData) {
      // ? Update existing event data to current events object and refetch it to display on calender
      // ? You can write below code to AJAX call success response
      eventData.id = parseInt(eventData.id);
      currentEvents[currentEvents.findIndex(el => el.id === eventData.id)] = eventData; // Update event by id
      calendar.refetchEvents();

      // ? To update event directly to calender (won't update currentEvents object)
      // let propsToUpdate = ['id', 'title', 'url'];
      // let extendedPropsToUpdate = ['calendar', 'guests', 'location', 'description'];

      // updateEventInCalendar(eventData, propsToUpdate, extendedPropsToUpdate);
    }

    // Remove Event
    // ------------------------------------------------

    function removeEvent(eventId) {
      // ? Delete existing event data to current events object and refetch it to display on calender
      // ? You can write below code to AJAX call success response
      currentEvents = currentEvents.filter(function (event) {
        return event.id != eventId;
      });
      calendar.refetchEvents();

      // ? To delete event directly to calender (won't update currentEvents object)
      // removeEventInCalendar(eventId);
    }

    // (Update Event In Calendar (UI Only)
    // ------------------------------------------------
    const updateEventInCalendar = (updatedEventData, propsToUpdate, extendedPropsToUpdate) => {
      const existingEvent = calendar.getEventById(updatedEventData.id);

      // --- Set event properties except date related ----- //
      // ? Docs: https://fullcalendar.io/docs/Event-setProp
      // dateRelatedProps => ['start', 'end', 'allDay']
      // eslint-disable-next-line no-plusplus
      for (var index = 0; index < propsToUpdate.length; index++) {
        var propName = propsToUpdate[index];
        existingEvent.setProp(propName, updatedEventData[propName]);
      }

      // --- Set date related props ----- //
      // ? Docs: https://fullcalendar.io/docs/Event-setDates
      existingEvent.setDates(updatedEventData.start, updatedEventData.end, {
        allDay: updatedEventData.allDay
      });

      // --- Set event's extendedProps ----- //
      // ? Docs: https://fullcalendar.io/docs/Event-setExtendedProp
      // eslint-disable-next-line no-plusplus
//      for (var index = 0; index < extendedPropsToUpdate.length; index++) {
//        var propName = extendedPropsToUpdate[index];
//        existingEvent.setExtendedProp(propName, updatedEventData.extendedProps[propName]);
//      }
    };

    // Remove Event In Calendar (UI Only)
    // ------------------------------------------------
    function removeEventInCalendar(eventId) {
      calendar.getEventById(eventId).remove();
    }

    // Add new event
    // ------------------------------------------------
    btnSubmit.addEventListener('click', async(e) => {
      if (btnSubmit.classList.contains('btn-add-event')) {
      console.log('d', isFormValid);
        if (isFormValid) {
          let newEvent = {
            title: eventTitle.value,
            date: eventStartDate.value,
            start_time: eventStartTime.value,
            end_time: eventEndTime.value,
            interview_url: eventUrl.value,
            interviewer: interviewer.value,
            display: 'block',
            location: eventLocation.value,
            candidate: eventGuests.val(),
            designation: designation.val(),
            interview_type: eventLabel.val(),
            description: eventDescription.value

          };
//          if (allDaySwitch.checked) {
//            newEvent.allDay = true;
//          }
        const response = await fetch(`/calendar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(newEvent)  // Convert the data to JSON format
          });

          const data = await response.json();  // Process the JSON response from the server
          if (data.status === 'success') {
            console.log('Event created successfully');
          } else {
            console.log('Failed to create event', data.message);
          }
          addEvent(data.event_data);
          addEventToUpcoming(data.event_data);
          bsAddEventSidebar.hide();
        }
      } else {
        // Update event
        // ------------------------------------------------
        if (isFormValid) {
          let eventData = {
            id: eventToUpdate.id,
            title: eventTitle.value,
            date: eventStartDate.value,
            start_time: eventStartTime.value,
            end_time: eventEndTime.value,
            interview_url: eventUrl.value,
            interviewer: interviewer.value,
            display: 'block',
            location: eventLocation.value,
            candidate: eventGuests.val(),
            designation: designation.val(),
            interview_type: eventLabel.val(),
            description: eventDescription.value

//            allDay: allDaySwitch.checked ? true : false
          };
        const response = await fetch(`/calendar/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(eventData)  // Convert the data to JSON format
          });

          const data = await response.json();  // Process the JSON response from the server
          if (data.status === 'success') {
            console.log('Event updated successfully');
          } else {
            console.log('Failed to update event:', data.message);
          }
          updateEvent(data.event_data);
          bsAddEventSidebar.hide();
        }
      }
    });

    // Call removeEvent function
    btnDeleteEvent.addEventListener('click', async(e) => {
    const response = await fetch(`/calendar/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({'id': eventToUpdate.id})  // Convert the data to JSON format
          });

          const data = await response.json();  // Process the JSON response from the server
          if (data.status === 'success') {
            console.log('Event deleted successfully');
          } else {
            console.log('Failed to delete event', data.message);
          }
      removeEvent(parseInt(eventToUpdate.id));
      removeEventUpcoming(eventToUpdate);
       eventToUpdate.remove();
      bsAddEventSidebar.hide();
    });

    // Function to add event dynamically to upcoming interviews
function addEventToUpcoming(event) {
    const year = new Date(event.extendedProps.date).getFullYear();
    const month = new Intl.DateTimeFormat('en', { month: 'long' }).format(new Date(event.extendedProps.date));  // Get full month name

    // Check if year section exists, if not, create it
    let yearElement = document.querySelector(`h6[data-year='${year}']`);
    if (!yearElement) {
        // Create year section if it doesn't exist
        const yearContainer = document.createElement('h6');
        yearContainer.setAttribute('data-year', year);
        yearContainer.textContent = year;
        document.querySelector('.upcoming-events-container').appendChild(yearContainer);
        yearElement = yearContainer;
    }

    // Check if month section exists under the year, if not, create it
    let monthElement = document.querySelector(`h6[data-month='${month}']`);
    if (!monthElement || monthElement.textContent !== month) {
        const monthContainer = document.createElement('h6');
        monthContainer.classList.add('mb-0', 'mt-2');
        monthContainer.textContent = month;
        yearElement.parentNode.insertBefore(monthContainer, yearElement.nextSibling);
        monthElement = monthContainer;
    }
    // Create event element and append it to the month section
    const eventContainer = document.createElement('div');
    const time = event.extendedProps.start_time;
    let h;
    const convertedTime = `${((h = parseInt(time.split(':')[0])) % 12 || 12)}:${time.split(':')[1]} ${h >= 12 ? 'PM' : 'AM'}`;
    eventContainer.innerHTML = `
        <div> ${event.extendedProps.date.split('-')[event.extendedProps.date.split('-').length - 1]}, ${convertedTime} </div>
        <div class="badge text-start mb-1" id="upcoming_event_${event.id}" data-interview_type="${event.extendedProps.interview_type}">
            ${event.extendedProps.candidate} for ${event.extendedProps.designation}
        </div>
    `;

    monthElement.insertAdjacentElement('afterend', eventContainer);
    const badge = document.querySelector(`#upcoming_event_${event.id}`);

    updateEventBadgeColors();
}

function removeEventUpcoming(event) {
    const eventElement = document.querySelector(`#upcoming_event_${event.id}`);

    let eventDiv1 = eventElement.previousElementSibling;

        // Remove the specific event elements (divs) for the event
            if (eventDiv1 && eventDiv1.tagName.toLowerCase() === 'div') {
            eventDiv1.remove();  // Remove the first div (e.g., event date)
        }

        if (eventElement && eventElement.tagName.toLowerCase() === 'div') {
            eventElement.remove();  // Remove the second div (e.g., event details)
        }

}

    // Reset event form inputs values
    // ------------------------------------------------
    function resetValues() {
      eventEndTime.value = '';
      eventUrl.value = '';
      eventStartDate.value = '';
      eventStartTime.value = '';
      eventTitle.value = '';
      eventLocation.value = '';
//      allDaySwitch.checked = false;
      eventGuests.val('').trigger('change');
      designation.val('').trigger('change');
      eventDescription.value = '';
    }

    // When modal hides reset input values
    addEventSidebar.addEventListener('hidden.bs.offcanvas', function () {
      resetValues();
    });

    // Hide left sidebar if the right sidebar is open
    btnToggleSidebar.addEventListener('click', e => {
      if (offcanvasTitle) {
        offcanvasTitle.innerHTML = 'Add Interview';
      }
      btnSubmit.innerHTML = 'Add';
      btnSubmit.classList.remove('btn-update-event');
      btnSubmit.classList.add('btn-add-event');
      btnDeleteEvent.classList.add('d-none');
      appCalendarSidebar.classList.remove('show');
      appOverlay.classList.remove('show');
    });

    // Calender filter functionality
    // ------------------------------------------------
    if (selectAll) {
      selectAll.addEventListener('click', e => {
        if (e.currentTarget.checked) {
          document.querySelectorAll('.input-filter').forEach(c => (c.checked = 1));
        } else {
          document.querySelectorAll('.input-filter').forEach(c => (c.checked = 0));
        }
        calendar.refetchEvents();
      });
    }

    if (filterInput) {
      filterInput.forEach(item => {
        item.addEventListener('click', () => {
          document.querySelectorAll('.input-filter:checked').length < document.querySelectorAll('.input-filter').length
            ? (selectAll.checked = false)
            : (selectAll.checked = true);
          calendar.refetchEvents();
        });
      });
    }

    // Jump to date on sidebar(inline) calendar change
//    inlineCalInstance.config.onChange.push(function (date) {
//      calendar.changeView(calendar.view.type, moment(date[0]).format('YYYY-MM-DD'));
//      modifyToggler();
//      appCalendarSidebar.classList.remove('show');
//      appOverlay.classList.remove('show');
//    });
  })();
});

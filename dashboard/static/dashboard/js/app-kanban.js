/**
 * App Kanban
 */

'use strict';

(async function () {
  let boards;
  const kanbanSidebar = document.querySelector('.kanban-update-item-sidebar'),
    kanbanWrapper = document.querySelector('.kanban-wrapper'),
    commentEditor = document.querySelector('.comment-editor'),
    kanbanAddNewBoard = document.querySelector('.kanban-add-new-board'),
    kanbanAddNewInput = [].slice.call(document.querySelectorAll('.kanban-add-board-input')),
    kanbanAddBoardBtn = document.querySelector('.kanban-add-board-btn'),
    datePicker = document.querySelector('#due-date'),
    select2 = $('.select2'), // ! Using jquery vars due to select2 jQuery dependency
    assetsPath = document.querySelector('html').getAttribute('data-assets-path');

  // Init kanban Offcanvas
  const kanbanOffcanvas = new bootstrap.Offcanvas(kanbanSidebar);

    const data = document.currentScript.dataset;
  const jobOpeningId = data.jobopeningid;
  // Get kanban data

  const kanbanResponse = await fetch(`/stage-api/${jobOpeningId}/`);
  if (!kanbanResponse.ok) {
    console.error('error', kanbanResponse);
  }
  const stages = await kanbanResponse.json();

boards = stages.map(stage => ({
    id: String(stage.id),
    title: stage.name,
    item: stage.candidates.map(candidateStage => ({
      id: String(candidateStage.id),
      title: candidateStage.candidate.name,
      contact: candidateStage.candidate.contact,
      email: candidateStage.candidate.email,
      feedback:candidateStage.candidate.feedback
    }))
  }));

    const fetchCandidates = async () => {
    const cresponse = await fetch('/candidate-api/');
    if (!cresponse.ok) {
      console.error('error', cresponse);
      return [];
    }
    const data = await cresponse.json();
    if (data.detail) {
      // No candidates found, show a message to the user
      const noCandidatesMessage = document.createElement('p');
      noCandidatesMessage.textContent = data.detail;
      document.body.appendChild(noCandidatesMessage);
      return [];
    }
    return data;
  };

  const candidates = await fetchCandidates();
  let candidateSelect;
  if (candidates.length > 0) {
    candidateSelect = document.createElement('select');
    candidateSelect.id = 'candidateSelect';
    candidateSelect.className = 'form-control add-new-item selectpicker w-100';
    candidateSelect.setAttribute('data-show-subtext', 'true');
    candidateSelect.setAttribute('data-placeholder', 'Select');
    candidateSelect.setAttribute('data-style', 'btn-default');
    candidateSelect.setAttribute('autofocus', '');
    candidateSelect.setAttribute('required', '');
      candidates.forEach(candidate => {
      const option = document.createElement('option');
      option.value = candidate.id;
      option.setAttribute('data-subtext', candidate.email);
      option.text = `${candidate.name}`;
      candidateSelect.appendChild(option);

    });
  }

  // datepicker init
//  if (datePicker) {
//    datePicker.flatpickr({
//      monthSelectorType: 'static',
//      altInput: true,
//      altFormat: 'j F, Y',
//      dateFormat: 'Y-m-d'
//    });
//  }

  //! TODO: Update Event label and guest code to JS once select removes jQuery dependency
  // select2
//  if (select2.length) {
//    function renderLabels(option) {
//      if (!option.id) {
//        return option.text;
//      }
//      var $badge = "<div class='badge " + $(option.element).data('color') + "'> " + option.text + '</div>';
//      return $badge;
//    }
//
//    select2.each(function () {
//      var $this = $(this);
//      $this.wrap("<div class='position-relative'></div>").select2({
//        placeholder: 'Select Label',
//        dropdownParent: $this.parent(),
//        templateResult: renderLabels,
//        templateSelection: renderLabels,
//        escapeMarkup: function (es) {
//          return es;
//        }
//      });
//    });
//  }

  // Comment editor
 if (commentEditor) {
   new Quill(commentEditor, {
     modules: {
       toolbar: '.comment-toolbar'
     },
     placeholder: 'Write a Comment... ',
     theme: 'snow'
   });
 }

  // Render board dropdown
  function renderBoardDropdown() {
    return (
      "<div class='dropdown'>" +
      "<i class='dropdown-toggle ti ti-dots-vertical cursor-pointer' id='board-dropdown' data-bs-toggle='dropdown' aria-haspopup='true' aria-expanded='false'></i>" +
      "<div class='dropdown-menu dropdown-menu-end' aria-labelledby='board-dropdown'>" +
      "<a class='dropdown-item delete-board' href='javascript:void(0)'> <i class='ti ti-trash ti-xs' me-1></i> <span class='align-middle'>Delete</span></a>" +
      "<a class='dropdown-item' href='javascript:void(0)'><i class='ti ti-edit ti-xs' me-1></i> <span class='align-middle'>Rename</span></a>" +
      "<a class='dropdown-item' href='javascript:void(0)'><i class='ti ti-archive ti-xs' me-1></i> <span class='align-middle'>Archive</span></a>" +
      '</div>' +
      '</div>'
    );
  }
  // Render item dropdown
  function renderDropdown() {
    return (
      "<div class='dropdown kanban-tasks-item-dropdown'>" +
      "<i class='dropdown-toggle ti ti-dots-vertical' id='kanban-tasks-item-dropdown' data-bs-toggle='dropdown' aria-haspopup='true' aria-expanded='false'></i>" +
      "<div class='dropdown-menu dropdown-menu-end' aria-labelledby='kanban-tasks-item-dropdown'>" +
      "<a class='dropdown-item' href='javascript:void(0)'>Copy task link</a>" +
      "<a class='dropdown-item' href='javascript:void(0)'>Duplicate task</a>" +
      "<a class='dropdown-item delete-task' href='javascript:void(0)'>Delete</a>" +
      '</div>' +
      '</div>'
    );
  }
  // Render header
  function renderHeader(email) {
    return (
      "<div class='d-flex justify-content-between flex-wrap align-items-start mb-2'>" +
      "<div class='item-badges'> " +
      "<span class='d-flex align-items-start'>" + email +
      '</span>' +
      '</div>' +
      renderDropdown() +
      '</div>'
    );
  }

    function getCookie(name) {
          const value = `; ${document.cookie}`;
          const parts = value.split(`; ${name}=`);
          if (parts.length === 2) return parts.pop().split(';').shift();
        }

  // Render footer
  function renderFooter(comments) {
    return (
      "<div class='d-flex justify-content-between align-items-center flex-wrap mt-2'>" +
      "<div class='d-flex'><span class='d-flex align-items-center ms-2'><i class='ti ti-message-2 me-1'></i>" +
      '<span> ' +
      comments +
      ' </span>' +
      '</span></div>' +
      '</div>'
    );
  }
  // Init kanban
  const kanban = new jKanban({
    element: '.kanban-wrapper',
    gutter: '12px',
    widthBoard: '250px',
    dragItems: true,
    boards: boards,
    dragBoards: true,
    addItemButton: true,
    buttonContent: '+ Add Item',
    itemAddOptions: {
      enabled: true, // add a button to board for easy item creation
      content: '+ Add New Item', // text or html content of the board button
      class: 'kanban-title-button btn', // default class of the button
      footer: false // position the button on footer
    },
    click: function (el) {
      let element = el;
      let title = element.getAttribute('data-eid')
          ? element.querySelector('.kanban-text').textContent
          : element.textContent,
        contact = element.getAttribute('data-contact'),
        email = element.getAttribute('data-email'),
        feedback = element.getAttribute('data-feedback');
        console.log('f', feedback);
//        dateObj = new Date(),
//        year = dateObj.getFullYear(),
//        dateToUse = date
//          ? date + ', ' + year
//          : dateObj.getDate() + ' ' + dateObj.toLocaleString('en', { month: 'long' }) + ', ' + year,
//        label = element.getAttribute('data-badge-text'),
//        avatars = element.getAttribute('data-assigned');

      // Show kanban offcanvas
      kanbanOffcanvas.show();

      // To get data on sidebar
      kanbanSidebar.querySelector('#title').value = title;
      kanbanSidebar.querySelector('#contact').value = contact;
      kanbanSidebar.querySelector('#email').value = email;
      kanbanSidebar.querySelector('#feedback').value = feedback;

      // ! Using jQuery method to get sidebar due to select2 dependency
      $('.kanban-update-item-sidebar').find(select2).val(label).trigger('change');

      // Remove & Update assigned
//      kanbanSidebar.querySelector('.assigned').innerHTML = '';
//      kanbanSidebar
//        .querySelector('.assigned')
//        .insertAdjacentHTML(
//          'afterbegin',
//          renderAvatar(avatars, false, 'xs', '1', el.getAttribute('data-members')) +
//            "<div class='avatar avatar-xs ms-1'>" +
//            "<span class='avatar-initial rounded-circle bg-label-secondary'><i class='ti ti-plus ti-xs text-heading'></i></span>" +
//            '</div>'
//        );




//    // Add event listener to board headers
    document.querySelectorAll('.kanban-board-header').forEach(header => {
      header.addEventListener('click', function () {
        const stageId = this.parentNode.getAttribute('data-id');
        document.getElementById('stage_id').value = stageId;
      });
    });

    },

    // update item order on drag and drop

    dropEl: ItemDrop,


    // update board order on drag and drop

    dropBoard: BoardDrop,



    buttonClick: function (el, boardId) {
      const addNew = document.createElement('form');
      addNew.className = 'new-item-form card-body';
      addNew.setAttribute('method', 'POST'); // Set method to POST
      addNew.setAttribute('enctype', 'multipart/form-data'); // Set enctype
      addNew.innerHTML =
        '<div class="mb-4">' +
        '<label class="form-label" for="candidateSelect">Select Candidate</label>' +
        `${candidateSelect.outerHTML}` +
        '</div>' +
        '<div class="mb-4">' +
        '<button type="submit" class="btn btn-primary btn-sm me-4 waves-effect waves-light">Add</button>' +
        '<button type="button" class="btn btn-label-secondary btn-sm cancel-add-item waves-effect waves-light">Cancel</button>' +
        '</div>';
      kanban.addForm(boardId, addNew);
      $('.selectpicker').selectpicker();

      addNew.addEventListener('submit', async (event) => {
      event.preventDefault();
      const candidateId = document.getElementById('candidateSelect').value;
      const id = el.closest('.kanban-board').getAttribute('data-id');


      const response = await fetch(`/stage-api/${jobOpeningId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 'candidateid' : candidateId, 'id' : id })
      });

      if (response.ok) {
        const stage = await response.json();
        const newCandidate = stage.candidates[stage.candidates.length - 1];
//
//        // Add the new candidate to the kanban board
        kanban.addElement(id, {
          id: newCandidate.id,
          title: `${renderHeader(newCandidate.candidate.email)}
                    <span class='kanban-text'>
                    ${newCandidate.candidate.name}

                  </span>`
        });
      } else {
        console.error('Error adding candidate:', response);
      }

//        const currentBoard = [].slice.call(
//          document.querySelectorAll(`.kanban-board[data-id=${boardId}] .kanban-item`)
//        );
//        kanban.addElement(id, {
//          title: "<span class='kanban-text'>" + e.target[0].value + '</span>',
//          id: boardId + '-' + currentBoard.length + 1
//        });
//        }
        // add dropdown in new boards


        const kanbanText = [].slice.call(

          document.querySelectorAll('.kanban-board[data-id="' + boardId + '"] .kanban-text')
        );

        kanbanText.forEach(function (e) {
          e.insertAdjacentHTML('beforebegin', renderDropdown());
        });

      // add drag and drop functionality for new items
        el.addEventListener('drop', ItemDrop);

        // prevent sidebar to open onclick dropdown buttons of new tasks
        const newTaskDropdown = [].slice.call(document.querySelectorAll('.kanban-item .kanban-tasks-item-dropdown'));
        if (newTaskDropdown) {
          newTaskDropdown.forEach(function (e) {
            e.addEventListener('click', function (el) {
              el.stopPropagation();
            });
          });
        }

        // delete tasks for new boards
        const deleteTask = [].slice.call(
          document.querySelectorAll('.kanban-board[data-id="' + boardId + '"] .delete-task')
        );
        deleteTask.forEach(function (e) {
          e.addEventListener('click', async function () {
            const id = this.closest('.kanban-item').getAttribute('data-eid');
            const stageid = this.closest('.kanban-board').getAttribute('data-id');
            const response = await fetch(`/stage-api/${jobOpeningId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'candidate_id': id, 'candidate_stage_id': stageid })
            });
            kanban.removeElement(id);
          });
        });
        addNew.remove();
      });

      // Remove form on clicking cancel button
      addNew.querySelector('.cancel-add-item').addEventListener('click', function (e) {
        addNew.remove();
      });
    }
  });

// Apply background color to boards
function applyBoardColors() {
        const boards = document.querySelectorAll('.kanban-board');
        const lastBoard = boards[boards.length - 1]; // The last board
        lastBoard.style.backgroundColor = '#d6ffe1';
        // Set background color for all child elements of the last board
        Array.from(lastBoard.children).forEach(child => {
          child.style.backgroundColor = '#d6ffe1';
        });
        const secondLastBoard = boards[boards.length - 2]; // The last board
        secondLastBoard.style.backgroundColor = '#fcc0bb';
        // Set background color for all child elements of the last board
        Array.from(secondLastBoard.children).forEach(child => {
          child.style.backgroundColor = '#fcc0bb';
        });
//    boards.forEach(board => {
//        const boardElement = document.querySelector(`.kanban-board:last-child`);
//        if (boardElement) {
//            boardElement.style.backgroundColor = '#b1fcc5';
//        }
//    });
}
applyBoardColors();

// drop update order item
  async function ItemDrop(el, target, source, sibling) {
  const stageId = target.parentElement.getAttribute('data-id');
  const candidateId = el.dataset.eid;

  // Create the order array
  const item_order = Array.from(target.children).map((item, index) => ({
    id: item.dataset.eid,
    order: index + 1
  }));

  try {
    // Send the order array to the backend
    const response = await fetch(`/stage-api/${jobOpeningId}/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is included for security
      },
      body: JSON.stringify({'order': item_order, 'stage_id': stageId})
    });

    if (!response.ok) {
      console.error('Error updating order:', response);
    } else {
      console.log('Order updated successfully');
      // Update the UI with the new order
//          renderOrderedItems(target, order);
    }
  } catch (error) {
    console.error('Error updating order:', error);
  }
}

// drop update order board
    async function BoardDrop(el, target, source, sibling) {
    // Create the order array for boards (stages)
    const board_order = Array.from(document.querySelectorAll('.kanban-board')).map((board, index) => ({
        id: board.dataset.id,
        order: index + 1
    }));

    try {
        // Send the board order array to the backend
        const response = await fetch(`/stage-api/${jobOpeningId}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 'order': board_order })
        });

        if (!response.ok) {
            console.error('Error updating board order:', response);
        } else {
            console.log('Board order updated successfully');
        }
    } catch (error) {
        console.error('Error updating board order:', error);
    }
  }


  // Kanban Wrapper scrollbar
  if (kanbanWrapper) {
    new PerfectScrollbar(kanbanWrapper);
  }

  const kanbanContainer = document.querySelector('.kanban-container'),
    kanbanTitleBoard = [].slice.call(document.querySelectorAll('.kanban-title-board')),
    kanbanItem = [].slice.call(document.querySelectorAll('.kanban-item'));

  // Render custom items
  if (kanbanItem) {
    kanbanItem.forEach(function (el) {
      const element = "<span class='kanban-text'>" + el.textContent + '</span>';
      let img = '';
      if (el.getAttribute('data-image') !== null) {
        img =
          "<img class='img-fluid rounded mb-2' src='" +
          assetsPath +
          'img/elements/' +
          el.getAttribute('data-image') +
          "'>";
      }
      el.textContent = '';
      if (el.getAttribute('data-email') !== undefined) {
        el.insertAdjacentHTML(
          'afterbegin',
          renderHeader(el.getAttribute('data-email')) + img + element
        );
      }
      if (
        el.getAttribute('data-feedback') !== 'undefined'
      ) {
        el.insertAdjacentHTML(
          'beforeend',
          renderFooter(
            el.getAttribute('data-feedback')

          )
        );
      }
      else {
      el.insertAdjacentHTML(
          'beforeend',
          renderFooter(0)
        );
      }
    });
  }

  // To initialize tooltips for rendered items
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // prevent sidebar to open onclick dropdown buttons of tasks
  const tasksItemDropdown = [].slice.call(document.querySelectorAll('.kanban-tasks-item-dropdown'));
  if (tasksItemDropdown) {
    tasksItemDropdown.forEach(function (e) {
      e.addEventListener('click', function (el) {
        el.stopPropagation();
      });
    });
  }

  // Toggle add new input and actions add-new-btn
  if (kanbanAddBoardBtn) {
    kanbanAddBoardBtn.addEventListener('click', () => {
      kanbanAddNewInput.forEach(el => {
        el.value = '';
        el.classList.toggle('d-none');
      });
    });
  }

  // Render add new inline with boards
  if (kanbanContainer) {
    kanbanContainer.appendChild(kanbanAddNewBoard);
  }

  // Makes kanban title editable for rendered boards
  if (kanbanTitleBoard) {
    kanbanTitleBoard.forEach(function (elem) {
      elem.addEventListener('mouseenter', function () {
        this.contentEditable = 'true';
      });

      // Appends delete icon with title
      elem.insertAdjacentHTML('afterend', renderBoardDropdown());
    });
  }

  // To delete Board for rendered boards
  const deleteBoards = [].slice.call(document.querySelectorAll('.delete-board'));
  if (deleteBoards) {
    deleteBoards.forEach(function (elem) {
      elem.addEventListener('click', async function () {
        const id = this.closest('.kanban-board').getAttribute('data-id');
        const response = await fetch(`/stage-api/${jobOpeningId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'stage_id': id })
            });

            if (response.ok) {
                kanban.removeBoard(id);
            } else {
                console.error('Error deleting board');
            }
      });
    });
  }

  // Delete task for rendered boards
  const deleteTask = [].slice.call(document.querySelectorAll('.delete-task'));
  if (deleteTask) {
    deleteTask.forEach(function (e) {
      e.addEventListener('click', async function () {
        const id = this.closest('.kanban-item').getAttribute('data-eid');
        const stageid = this.closest('.kanban-board').getAttribute('data-id');
        const response = await fetch(`/stage-api/${jobOpeningId}/`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 'candidate_id': id, 'candidate_stage_id': stageid })
            });
        kanban.removeElement(id);

      });
    });
  }

  // Cancel btn add new input
  const cancelAddNew = document.querySelector('.kanban-add-board-cancel-btn');
  if (cancelAddNew) {
    cancelAddNew.addEventListener('click', function () {
      kanbanAddNewInput.forEach(el => {
        el.classList.toggle('d-none');
      });
    });
  }

  // Add new board

  // Function to generate a new board ID
    function generateNewBoardId() {
        const allBoards = document.querySelectorAll('.kanban-board');
        let maxId = 0;

        allBoards.forEach(board => {
            const id = parseInt(board.getAttribute('data-id'), 10);
            if (!isNaN(id) && id > maxId) {
                maxId = id;
            }
        });

        return maxId + 1;
    }

  if (kanbanAddNewBoard) {
    kanbanAddNewBoard.addEventListener('submit', async function (e) {
      e.preventDefault();
      const thisEle = this,
        value = thisEle.querySelector('.form-control').value,
        id = String(generateNewBoardId());
        const boards = document.querySelectorAll('.kanban-board');
        const lastBoard = boards[boards.length - 1]; // The last board

      kanban.addBoards([
        {
          id: id,
          title: value
        }
      ]);
      const response = await fetch(`/stage-api/${jobOpeningId}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 'id' : id, 'title' : value })
      });

      // Adds delete board option to new board, delete new boards & updates data-order
      const kanbanBoardLastChild = document.querySelector(`.kanban-board[data-id="${id}"]`);
      if (kanbanBoardLastChild && lastBoard) {
        lastBoard.parentNode.insertBefore(kanbanBoardLastChild, lastBoard);
      }
      if (kanbanBoardLastChild) {
        const header = kanbanBoardLastChild.querySelector('.kanban-title-board');
        header.insertAdjacentHTML('afterend', renderBoardDropdown());

        // To make newly added boards title editable
        kanbanBoardLastChild.querySelector('.kanban-title-board').addEventListener('mouseenter', function () {
          this.contentEditable = 'true';
        });
      }

      // add drag and drop functionality for new boards
      kanbanBoardLastChild.addEventListener('drop', BoardDrop);

      // Add delete event to delete newly added boards
      const deleteNewBoards = kanbanBoardLastChild.querySelector('.delete-board');
      if (deleteNewBoards) {
        deleteNewBoards.addEventListener('click', async function () {
          const id = this.closest('.kanban-board').getAttribute('data-id');
            const response = await fetch(`/stage-api/${jobOpeningId}/`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({ 'stage_id': id })
                });

                if (response.ok) {
                    kanban.removeBoard(id);
                } else {
                    console.error('Error deleting board');
                }
            });
      }

      // Remove current append new add new form
      if (kanbanAddNewInput) {
        kanbanAddNewInput.forEach(el => {
          el.classList.add('d-none');
        });
      }

      // To place inline add new btn after clicking add btn
      if (kanbanContainer) {
        kanbanContainer.appendChild(kanbanAddNewBoard);
      }
    });
  }

  // Clear comment editor on close
  kanbanSidebar.addEventListener('hidden.bs.offcanvas', function () {
    kanbanSidebar.querySelector('.ql-editor').firstElementChild.innerHTML = '';
  });

  // Re-init tooltip when offcanvas opens(Bootstrap bug)
  if (kanbanSidebar) {
    kanbanSidebar.addEventListener('shown.bs.offcanvas', function () {
      const tooltipTriggerList = [].slice.call(kanbanSidebar.querySelectorAll('[data-bs-toggle="tooltip"]'));
      tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
      });
    });
  }
})();

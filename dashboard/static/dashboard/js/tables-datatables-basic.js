/**
 * DataTables Basic
 */

'use strict';

let fv, offCanvasEl;

// datatable (jquery)
$(function () {
    let startTime = performance.now();

    var dt_basic_table = $('.datatables-basic'),

    dt_basic;
    var actions = $('#actioncheck');
    const urlParams = new URLSearchParams(window.location.search);
    const statusParam = urlParams.get("status");

    // If status param exists
    if (statusParam) {
        const statusesFromUrl = statusParam.split(',');

        // Loop through each checkbox and check if its data-value matches
        $('#filter-status .form-check-input').each(function () {
            const checkboxValue = $(this).data('value');
            if (statusesFromUrl.includes(checkboxValue)) {
                $(this).prop('checked', true);
            }
        });
    }


  // DataTable with buttons
  // --------------------------------------------------------------------
var selectedRows = '';
  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
        processing: true,
        serverSide: true,    // Load data page-by-page
        ajax: {
        url: "/candidate/candidate-list-api/"+ window.location.search, // Update with your API endpoint
        data: function(d) {
            d.experience = $('#experience-input').val().trim(); // Send experience filter
            d.status = $('.form-check-input:checked').map(function() { // Send status filter
                return $(this).data('value');
            }).get().join(',');
        }
        },  // API to fetch data
      columns: [
        { data: null, defaultContent: '' },
        { data: 'id' },
        { data: 'name'
//        render: function (data, type, row) {
//          return `<div class="d-flex justify-content-start align-items-center user-name">
//          <div class="d-flex flex-column">
//          <a href="/candidate/candidate-details/${row.id}">${data}</a></div>
//          </div>`;
//        }
        },
        { data: 'designation' },
        { data: 'contact' },
        { data: 'email' },
        { data: 'location' },
        { data: 'experience' },
        { data: 'status' },
        { data: 'updated' }
      ],
      columnDefs: [
//        {
//          // For Responsive
//          className: 'control',
//          orderable: false,
//          searchable: false,
//          responsivePriority: 2,
//          targets: 0,
//          render: function (data, type, full, meta) {
//            return '';
//          }
//        },
        {
          // For Checkboxes
          targets: 0,
          orderable: false,
          searchable: false,
          responsivePriority: 3,
          checkboxes: true,
          render: function () {
            return '<input type="checkbox" class="dt-checkboxes form-check-input">';
          },
          checkboxes: {
            selectAllRender: '<input type="checkbox" class="form-check-input">'
          }
        },
        {
          // For id
          targets: 1,
          orderable: false,
          searchable: false,
          visible : false,
        },
        {
          targets: 3,
          orderable: false,
        },
        {
          targets: 4,
          orderable: false,
        },
        {
          targets: 5,
          orderable: false,
        },


        {
          // Avatar image/badge, Name and post
          targets: 2,
          responsivePriority: 4,
          render: function (data, type, full, meta) {
              var rowElement = dt_basic_table.find('tbody tr').eq(meta.row); // Get the row element by index
              var isNew = rowElement.attr('data-new'); // Get the data-new attribute
            var $user_img = full['avatar'],
              $name = full['name'],
              $id = full['id'],

              $post = full['post'];
            if ($user_img) {
//               For Avatar image
              var $output =
                '<img src="' + assetsPath + 'img/avatars/' + $user_img + '" alt="Avatar" class="rounded-circle">';
            } else {
              // For Avatar badge
              var stateNum = Math.floor(Math.random() * 6);
              var states = ['success', 'danger', 'warning', 'info', 'primary', 'secondary'];
              var $state = states[stateNum];
              var start = $name.indexOf('>') + 1;
              var end = $name.lastIndexOf('<'),
                $initials = $name.slice(start, end).split(' ').slice(0,2).map(function(part) {
                  return part.charAt(0);
                }).join('').toUpperCase(),
//                 $link = $name.slice(0,start);
              $output = '<span class="avatar-initial rounded-circle bg-label-' + $state + '">' + $initials + '</span>';
            }
            // Creates full output for row
            var $row_output =
                `<a href="/candidate/candidate-details/` +
                $id +
                `">` +
              `<div class="d-flex justify-content-start align-items-center user-name">` +
              '<div class="avatar-wrapper">' +
              '<div class="avatar me-2">' +
              $output +
              '</div>' +
              '</div>' +
              '<div class="d-flex flex-column">' +
              '<span class="emp_name text-truncate">' +
              $name +
              '</span></div>';

              if (isNew === 'True') {
              $row_output +=
                `<span class="ms-1 badge bg-label-success small">New</span>`;
            }

            $row_output += '</div></a>';
            return $row_output;
          }
        },
        {
          responsivePriority: 1,
          targets: 4
        },
        {
          // status
          targets: 8,
          orderable: false,
          render: function (data, type, full, meta) {
            var $status_number = full['status'];
            var stages = $status_number.toLowerCase().split(' ');
            var $status = {
              'other': { title: 'In Stage', class: 'bg-label-primary' },
              'initial': { title: 'Initial', class: ' bg-label-custom' },
              'hired': { title: 'Hired', class: ' bg-label-success' },
              'rejected': { title: 'Rejected', class: ' bg-label-danger' },
              'applied': { title: 'Applied', class: ' bg-label-info' },
              '': { title: 'Inactive', class: ' bg-label-secondary' }
            };

            var statusHTML= '';
            if (stages.includes('hired')){
                statusHTML = ('<span class="badge ' + $status['hired'].class + '">' + $status['hired'].title + '</span>');
            }
            else if (stages.includes('initial')){
              statusHTML = ('<span class="badge ' + $status['initial'].class + '">' + $status['initial'].title + '</span>');
            }
            else if (stages.includes('rejected')){
              statusHTML = ('<span class="badge ' + $status['rejected'].class + '">' + $status['rejected'].title + '</span>');
            }
            else if (stages.includes('applied')){
              statusHTML = ('<span class="badge ' + $status['applied'].class + '">' + $status['applied'].title + '</span>');
            }
            else {
            stages.forEach(function(stage){
            if (stage in $status) {
              statusHTML = ('<span class="badge ' + $status[stage].class + '">' + $status[stage].title + '</span>');
            } else {
            statusHTML = (
              '<span class="badge ' + $status['other'].class + '">' + $status['other'].title + '</span>'
            );
            }
            });
            }
            return statusHTML;

          }
        }
      ],

      order: [[9, 'desc']],
      dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-6 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end mt-n6 mt-md-0"f>><"table-responsive"r t><"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      displayLength: 10,
      lengthMenu: [7, 10, 25, 50, 75, 100],
      deferRender: true,  // Render only visible rows first
      language: {
        processing:
        `<div class="loading-spinner">
                  <div class="sk-chase sk-primary">
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                  </div>
                </div>`
        ,
        paginate: {
          next: '<i class="ti ti-chevron-right ti-sm"></i>',
          previous: '<i class="ti ti-chevron-left ti-sm"></i>'
        }
      },
      buttons: [
        {
            text: '<i class="ti ti-user-plus  ti-xs me-sm-1"></i><span class="d-none d-sm-inline-block">Import</span>',
            className: 'btn btn-primary me-4 waves-effect waves-light border-none',
            action: function (e, dt, node, config) {
              // Define the action you want to perform when the button is clicked
              // For example, redirect to an "Add Candidate" form page
              window.location.href = "/candidate/add-candidate-form/";
            }
          },
//        {
//          extend: 'collection',
//          className: 'btn btn-label-primary dropdown-toggle me-4 waves-effect waves-light border-none',
//          text: '<i class="ti ti-file-export ti-xs me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
//          buttons: [
//            {
//              extend: 'print',
//              text: '<i class="ti ti-printer me-1" ></i>Print',
//              className: 'dropdown-item',
//              exportOptions: {
//                columns: [3, 4, 5, 6, 7],
//                // prevent avatar to be display
//                format: {
//                  body: function (inner, coldex, rowdex) {
//                    if (inner.length <= 0) return inner;
//                    var el = $.parseHTML(inner);
//                    var result = '';
//                    $.each(el, function (index, item) {
//                      if (item.classList !== undefined && item.classList.contains('user-name')) {
//                        result = result + item.lastChild.firstChild.textContent;
//                      } else if (item.innerText === undefined) {
//                        result = result + item.textContent;
//                      } else result = result + item.innerText;
//                    });
//                    return result;
//                  }
//                }
//              },
//              customize: function (win) {
//                //customize print view for dark
//                $(win.document.body)
//                  .css('color', config.colors.headingColor)
//                  .css('border-color', config.colors.borderColor)
//                  .css('background-color', config.colors.bodyBg);
//                $(win.document.body)
//                  .find('table')
//                  .addClass('compact')
//                  .css('color', 'inherit')
//                  .css('border-color', 'inherit')
//                  .css('background-color', 'inherit');
//              }
//            },
//            {
//              extend: 'csv',
//              text: '<i class="ti ti-file-text me-1" ></i>Csv',
//              className: 'dropdown-item',
//              exportOptions: {
//                columns: [3, 4, 5, 6, 7],
//                // prevent avatar to be display
//                format: {
//                  body: function (inner, coldex, rowdex) {
//                    if (inner.length <= 0) return inner;
//                    var el = $.parseHTML(inner);
//                    var result = '';
//                    $.each(el, function (index, item) {
//                      if (item.classList !== undefined && item.classList.contains('user-name')) {
//                        result = result + item.lastChild.firstChild.textContent;
//                      } else if (item.innerText === undefined) {
//                        result = result + item.textContent;
//                      } else result = result + item.innerText;
//                    });
//                    return result;
//                  }
//                }
//              }
//            },
//            {
//              extend: 'excel',
//              text: '<i class="ti ti-file-spreadsheet me-1"></i>Excel',
//              className: 'dropdown-item',
//              exportOptions: {
//                columns: [3, 4, 5, 6, 7],
//                // prevent avatar to be display
//                format: {
//                  body: function (inner, coldex, rowdex) {
//                    if (inner.length <= 0) return inner;
//                    var el = $.parseHTML(inner);
//                    var result = '';
//                    $.each(el, function (index, item) {
//                      if (item.classList !== undefined && item.classList.contains('user-name')) {
//                        result = result + item.lastChild.firstChild.textContent;
//                      } else if (item.innerText === undefined) {
//                        result = result + item.textContent;
//                      } else result = result + item.innerText;
//                    });
//                    return result;
//                  }
//                }
//              }
//            },
//            {
//              extend: 'pdf',
//              text: '<i class="ti ti-file-description me-1"></i>Pdf',
//              className: 'dropdown-item',
//              exportOptions: {
//                columns: [3, 4, 5, 6, 7],
//                // prevent avatar to be display
//                format: {
//                  body: function (inner, coldex, rowdex) {
//                    if (inner.length <= 0) return inner;
//                    var el = $.parseHTML(inner);
//                    var result = '';
//                    $.each(el, function (index, item) {
//                      if (item.classList !== undefined && item.classList.contains('user-name')) {
//                        result = result + item.lastChild.firstChild.textContent;
//                      } else if (item.innerText === undefined) {
//                        result = result + item.textContent;
//                      } else result = result + item.innerText;
//                    });
//                    return result;
//                  }
//                }
//              }
//            },
//            {
//              extend: 'copy',
//              text: '<i class="ti ti-copy me-1" ></i>Copy',
//              className: 'dropdown-item',
//              exportOptions: {
//                columns: [3, 4, 5, 6, 7],
//                // prevent avatar to be display
//                format: {
//                  body: function (inner, coldex, rowdex) {
//                    if (inner.length <= 0) return inner;
//                    var el = $.parseHTML(inner);
//                    var result = '';
//                    $.each(el, function (index, item) {
//                      if (item.classList !== undefined && item.classList.contains('user-name')) {
//                        result = result + item.lastChild.firstChild.textContent;
//                      } else if (item.innerText === undefined) {
//                        result = result + item.textContent;
//                      } else result = result + item.innerText;
//                    });
//                    return result;
//                  }
//                }
//              }
//            }
//          ]
//        }
      ],

      initComplete: function (settings, json) {
      var header = $('.card-header');
        $('.card-header').after('<hr class="my-0">');
        actions.prop('disabled', true);
    }

    });

    // Clean up any extra content injected by DataTables
    dt_basic.on('processing.dt', function (e, settings, processing) {
      const $proc = $('.dataTables_processing');
      $proc.children().not('.loading-spinner').remove(); // Keep only your custom spinner
        const $tbody = $(this).find('tbody');
    console.log('proce', processing);
      if (processing) {
        // Insert loading row if not exists
        if ($tbody.find('.loading-row').length === 0) {
          const loadingRow = `
            <tr class="loading-row">
              <td colspan="6" style="text-align:center;">
                <div class="loading-spinner">
                  <div class="sk-chase sk-primary">
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                    <div class="sk-chase-dot"></div>
                  </div>
                </div>
              </td>
            </tr>`;
          $tbody.html(loadingRow);
        }
      } else {
        // Remove loading row after data loads
        $tbody.find('.loading-row').remove();
      }
    });
    if (statusParam) {
    console.log("d", statusParam);
            dt_basic.ajax.reload();
        }

    let endTime = performance.now();
    console.log(`Execution time: ${(endTime - startTime).toFixed(2)} ms`);
    // Select the title element from the DOM
    var titleElement = $('#datatable-title').detach();

    // Insert the title into the target div
    $('div.head-label').html(titleElement);

      // Trigger table reload on filter change
  $('#experience-input, .form-check-input').on('input', function () {
    dt_basic.ajax.reload();
  });
  $('#filter-status').on('change', '.form-check-input', function () {
    dt_basic.ajax.reload();
  });

  // Get status param from URL
//    const urlParams = new URLSearchParams(window.location.search);
//    const statusParam = urlParams.get("status");
//
//    // If status param exists
//    if (statusParam) {
//        const statusesFromUrl = statusParam.split(',');
//
//        // Loop through each checkbox and check if its data-value matches
//         $('#filter-status .form-check-input').each(function () {
//            const checkboxValue = $(this).data('value');
//            if (statusesFromUrl.includes(checkboxValue)) {
//                $(this).prop('checked', true);
//            }
//        });
//    }


        // Event handler for individual checkboxes
    $('.datatables-basic tbody').on('change', '.dt-checkboxes', function () {
      var row = $(this).closest('tr');
      var rowData = dt_basic.row(row).data();
      if (this.checked) {
        row.addClass('selected');

      } else {
        row.removeClass('selected');

      }
      updateSelectedRows();
      getSelectedIds();

    });

        // Handle "Select All" checkbox
    $('.dt-checkboxes-select-all input').on('change', function () {
      var checked = $(this).prop('checked');
      // select only filtered rows
      dt_basic.rows({ search: 'applied' }).nodes().to$().find('input[type="checkbox"]').prop('checked', checked);

      if (checked) {
        dt_basic.rows({ search: 'applied' }).nodes().to$().addClass('selected');
      }
      else {
        dt_basic.rows({ search: 'applied' }).nodes().to$().removeClass('selected');
      }
      updateSelectedRows();
      getSelectedIds();
    });
    

    function updateSelectedRows() {
      // Get all selected rows
      selectedRows = dt_basic.rows('.selected').data().toArray();

      // Perform actions with the selected rows, e.g., updating the button state
      if (selectedRows.length > 0) {
        actions.prop('disabled', false);  // Enable button
      } else {
        actions.prop('disabled', true);  // Disable button
      }
    }
        // Append filter inputs to the filter container
    'use strict';

$(function () {

  // Handle Experience Comparator Dropdown
  $('#experience-comparator').on('click', '.dropdown-item', function () {
    var comparator = $(this).data('comparator');
    var comparatorText = $(this).text(); // Get the text of the selected item
    $('#experience-input').val(comparator + ' '); // Set the comparator in the input field
    $('#experience-input').data('comparator', comparator); // Store comparator in data attribute
//    filterCandidatesByExperience(); // Apply filter immediately after selection
  });

   // Set default comparator if none is selected
   if (!$('#experience-input').data('comparator')) {
    $('#experience-input').data('comparator', '=');
    $('#experience-input').val(' '); // Default to "="
  }


  // Append filter inputs to the filter container
  var filterHTML = $('#filter-container');
  var filterline = $('#DataTables_Table_0_filter').parents('.row').first();
  filterline.after(filterHTML).after('<hr class="my-0">');
  filterHTML.show();

});



// Function to get selected IDs
function getSelectedIds() {
    var selectedIds = [];
    updateSelectedRows();
    selectedIds.push(selectedRows.map(row => row.id));  // Add the ID to the array
    console.log('ids: ', selectedIds);
    return selectedIds;
}

  // Delete Record

  const delbtn = $('#delete_btn');

  $('#deleteForm').on('submit', function(e) {
    e.preventDefault();  // Prevent default form submission
   var idsToDelete = getSelectedIds();
    if (idsToDelete.length > 0) {
    // Send AJAX request to delete rows
    $.ajax({
      url: $(this).attr('action'),  // Replace with your delete endpoint
      method: 'POST',
      data: {
        'ids[]': idsToDelete,
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // Add CSRF token
      },
      success: function(response) {
        // On success, remove rows from DataTable
        dt_basic.rows('.selected').remove().draw(false);
        $('.dt-checkboxes-select-all input').prop('checked', false);
        $('#basicModal').modal('hide');
      },
      error: function(xhr, status, error) {
        console.error('Error deleting rows:', status, error);
        // Optionally, show an error message to the user
      }
    });
  }

  });

  $('#shareJobOpeningForm').on('submit', function(e) {
    e.preventDefault();  // Prevent default form submission
   var idsToShare = getSelectedIds();
   var selectedJobOpening = $('#jobOpening').val(); // Get the selected job opening ID
    $('#shareOpening').modal('hide');
    if (idsToShare.length > 0) {
    // Send AJAX request to delete rows
    $.ajax({
      url: $(this).attr('action'),  // Replace with your delete endpoint
      method: 'POST',
      data: {
        'ids[]': idsToShare,
        'job_opening_id': selectedJobOpening,  // Include job opening ID

        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // Add CSRF token
      },
      success: function(response) {
        // On success, remove rows from DataTable
        dt_basic.rows('.selected').nodes().to$().find('input[type="checkbox"]').prop('checked', false);
        dt_basic.rows().nodes().to$().removeClass('selected');
        $('.dt-checkboxes-select-all input').prop('checked', false);
//        $('#shareOpening').modal('hide');
      },
      error: function(xhr, status, error) {
        console.error('Error sending mail:', status, error);
//        $('#shareOpening').modal('hide');

          // Show Django style message dynamically
//        let message = "Email id may not be correct! Please check all email id and try again.";
//        let tags = "danger"; // For error messages, use 'danger' | For success, use 'success'
//
//        // Append message using the same structure
//        $('#messages').html(`
//          <div class="messages alert alert-danger" data-tags="${tags}" data-message="${message}">
//            ${message}
//          </div>
//        `);
        // Automatically hide message after 3 seconds
//        setTimeout(function () {
//          $('.messages').fadeOut('slow');
//        }, 6000);
        // Optionally, show an error message to the user
      }
    });
  }

  });

}



const scrollContainer = document.querySelector(".table-responsive");
let scrollInterval;

scrollContainer.addEventListener("mousemove", (e) => {
  const bounds = scrollContainer.getBoundingClientRect();
  const mouseX = e.clientX - bounds.left;
  const scrollThreshold = 50; // px from edge

  clearInterval(scrollInterval); // stop previous scroll

  if (mouseX > bounds.width - scrollThreshold) {
    // Near right edge
    scrollInterval = setInterval(() => {
      scrollContainer.scrollLeft += 5;
    }, 20);
  } else if (mouseX < scrollThreshold) {
    // Near left edge
    scrollInterval = setInterval(() => {
      scrollContainer.scrollLeft -= 5;
    }, 20);
  }
});



scrollContainer.addEventListener("mouseleave", () => {
  clearInterval(scrollInterval); // stop scrolling when mouse leaves
});
});


/**
 * DataTables Basic
 */

'use strict';

let fv, offCanvasEl;

// datatable (jquery)
$(function () {
  var dt_basic_table = $('.datatables-basic'),
    dt_basic;
    var actions = $('#actioncheck');


  // DataTable with buttons
  // --------------------------------------------------------------------

  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
      columns: [
        { data: '' },
        { data: 'id' },
        { data: 'name' },
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
          // For Checkboxes
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
            var $user_img = full['avatar'],
              $name = full['name'];

//              $post = full['post'];
            if ($user_img) {
              // For Avatar image
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
                }).join('').toUpperCase();
                var $link = $name.slice(0,start);
              $output = '<span class="avatar-initial rounded-circle bg-label-' + $state + '">' + $initials + '</span>';
            }
            // Creates full output for row
            var $row_output =
                `${$link}` +
              `<div class="d-flex justify-content-start align-items-center user-name">` +
              '<div class="avatar-wrapper">' +
              '<div class="avatar me-2">' +
              $output +
              '</div>' +
              '</div>' +
              '<div class="d-flex flex-column">' +
              '<span class="emp_name text-truncate">' +
              $name.slice(start, end) +
              '</span>' +
              '</div>' +
              '</div></a>';
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
      order: [[2, 'desc']],
      dom: '<"card-header flex-column flex-md-row"<"head-label text-center"><"dt-action-buttons text-end pt-6 pt-md-0"B>><"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end mt-n6 mt-md-0"f>><"table-responsive"t><"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      displayLength: 9,
      lengthMenu: [7, 10, 25, 50, 75, 100],
      language: {
        paginate: {
          next: '<i class="ti ti-chevron-right ti-sm"></i>',
          previous: '<i class="ti ti-chevron-left ti-sm"></i>'
        }
      },
      buttons: [
        {
          extend: 'collection',
          className: 'btn btn-label-primary dropdown-toggle me-4 waves-effect waves-light border-none',
          text: '<i class="ti ti-file-export ti-xs me-sm-1"></i> <span class="d-none d-sm-inline-block">Export</span>',
          buttons: [
            {
              extend: 'print',
              text: '<i class="ti ti-printer me-1" ></i>Print',
              className: 'dropdown-item',
              exportOptions: {
                columns: [3, 4, 5, 6, 7],
                // prevent avatar to be display
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('user-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              },
              customize: function (win) {
                //customize print view for dark
                $(win.document.body)
                  .css('color', config.colors.headingColor)
                  .css('border-color', config.colors.borderColor)
                  .css('background-color', config.colors.bodyBg);
                $(win.document.body)
                  .find('table')
                  .addClass('compact')
                  .css('color', 'inherit')
                  .css('border-color', 'inherit')
                  .css('background-color', 'inherit');
              }
            },
            {
              extend: 'csv',
              text: '<i class="ti ti-file-text me-1" ></i>Csv',
              className: 'dropdown-item',
              exportOptions: {
                columns: [3, 4, 5, 6, 7],
                // prevent avatar to be display
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('user-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            },
            {
              extend: 'excel',
              text: '<i class="ti ti-file-spreadsheet me-1"></i>Excel',
              className: 'dropdown-item',
              exportOptions: {
                columns: [3, 4, 5, 6, 7],
                // prevent avatar to be display
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('user-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            },
            {
              extend: 'pdf',
              text: '<i class="ti ti-file-description me-1"></i>Pdf',
              className: 'dropdown-item',
              exportOptions: {
                columns: [3, 4, 5, 6, 7],
                // prevent avatar to be display
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('user-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            },
            {
              extend: 'copy',
              text: '<i class="ti ti-copy me-1" ></i>Copy',
              className: 'dropdown-item',
              exportOptions: {
                columns: [3, 4, 5, 6, 7],
                // prevent avatar to be display
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('user-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            }
          ]
        }
      ],
//      responsive: {
//        details: {
//          display: $.fn.dataTable.Responsive.display.modal({
//            header: function (row) {
//              var data = row.data();
//              return 'Details of ' + data['name'];
//            }
//          }),
//          type: 'column',
//          renderer: function (api, rowIdx, columns) {
//            var data = $.map(columns, function (col, i) {
//              return col.title !== '' // ? Do not show row in modal popup if title is blank (for check box)
//                ? '<tr data-dt-row="' +
//                    col.rowIndex +
//                    '" data-dt-column="' +
//                    col.columnIndex +
//                    '">' +
//                    '<td>' +
//                    col.title +
//                    ':' +
//                    '</td> ' +
//                    '<td>' +
//                    col.data +
//                    '</td>' +
//                    '</tr>'
//                : '';
//            }).join('');
//
//            return data ? $('<table class="table"/><tbody />').append(data) : false;
//          }
//        }
//      },
      initComplete: function (settings, json) {
      var header = $('.card-header');
        $('.card-header').after('<hr class="my-0">');
        actions.prop('disabled', true);
    }
    });
    // Select the title element from the DOM
    var titleElement = $('#datatable-title').detach();

    // Insert the title into the target div
    $('div.head-label').html(titleElement);


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
    });

        // Handle "Select All" checkbox
    $('.dt-checkboxes-select-all input').on('change', function () {
      var checked = $(this).prop('checked');
      dt_basic.rows().nodes().to$().find('input[type="checkbox"]').prop('checked', checked);
      if (checked) {
        dt_basic.rows().nodes().to$().addClass('selected');
      }
      else {
        dt_basic.rows().nodes().to$().removeClass('selected');
      }
      updateSelectedRows();
    });
    

var selectedRows = '';
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
    filterCandidatesByExperience(); // Apply filter immediately after selection
  });

   // Set default comparator if none is selected
   if (!$('#experience-input').data('comparator')) {
    $('#experience-input').data('comparator', '=');
    $('#experience-input').val(' '); // Default to "="
  }

  // Handle Experience filter input
  $('#experience-input').on('input', function () {
    filterCandidatesByExperience(); // Apply filter when input changes
  });

  // Append filter inputs to the filter container
  var filterHTML = $('#filter-container');
  var filterline = $('#DataTables_Table_0_filter').parents('.row').first();
  filterline.after(filterHTML).after('<hr class="my-0">');
  filterHTML.show();

  // Handle Status filter
  $('#filter-status').on('change', '.form-check-input', function () {
    var filterPattern = applyFilters();
    dt_basic.column(8).search(filterPattern, true, false).draw();
});

  // Function to filter candidates based on experience
  function filterCandidatesByExperience() {
    var comparator = $('#experience-input').data('comparator') || '';
    var experienceValue = $('#experience-input').val().replace(comparator, '').trim();

    if (comparator && experienceValue !== '') {
      dt_basic.draw(); // Trigger the DataTable to redraw
    } else {
      dt_basic.search('').draw(); // Clear search if no comparator or value
    }
  }

  // DataTables custom search function for experience
  $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
    var comparator = $('#experience-input').data('comparator') || '=';
    var experienceValue = $('#experience-input').val().replace(comparator, '').trim();
    var experience = parseFloat(data[7]) || 0; // Assuming experience is in the 7th column (index 6)

    if (comparator && experienceValue !== '') {
      experienceValue = parseFloat(experienceValue);
      switch (comparator) {
        case '<':
          return experience < experienceValue;
        case '>':
          return experience > experienceValue;
        case '=':
          return experience == experienceValue;
        default:
          return true;
      }
    }
    return true;
  });

  // Collect selected checkboxes' values for status filter
  function applyFilters() {
    let selectedValues = [];
    $('.form-check-input:checked').each(function () {
      selectedValues.push($(this).data('value'));
    });
    var filterPattern = selectedValues.length > 0 ? selectedValues.join('|') : '';

    // Convert array to a regex pattern for DataTables search
    return filterPattern;
  }
});



// Function to get selected IDs
function getSelectedIds() {
    var selectedIds = [];
    selectedIds.push(selectedRows.map(row => row.id));  // Add the ID to the array

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

}
});


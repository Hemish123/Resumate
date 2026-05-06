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
        setTimeout(function () {
            const dtButtons = document.querySelector('.dt-buttons');
            const rightToolbar = document.getElementById('datatable-toolbar-right');

            if (dtButtons && rightToolbar) {
              rightToolbar.appendChild(dtButtons);
            }
          }, 500);
    }


  // DataTable with buttons
  // --------------------------------------------------------------------
var selectedRows = '';
var selectAllMode = false;
  if (dt_basic_table.length) {
    dt_basic = dt_basic_table.DataTable({
        processing: true,
        serverSide: true,    // Load data page-by-page
        ajax: {
        url: "/candidate/candidate-list-api/"+ window.location.search, // Update with your API endpoint
        data: function(d) {
            // d.experience = $('#experience-input').val().trim(); // Send experience filter
            d.min_exp = $('#min-exp').val().trim();
            d.max_exp = $('#max-exp').val().trim();
            d.status = $('.form-check-input:checked').map(function() { // Send status filter
                return $(this).data('value');
            }).get().join(',');
            d.location = $('#filter-location').val().trim();
            d.designation = $('#filter-designation').val().trim();
            d.name = $('#filter-name').val();
            d.contact = $('#filter-contact').val();
            d.email = $('#filter-email').val();
            d.updated = $('#filter-updated').val();
            d.preferred_location = $('#filter-preferred-location').val();
            d.current_ctc = $('#filter-current-ctc').val();
            d.expected_ctc = $('#filter-expected-ctc').val();
            d.notice_period = $('#filter-notice').val();
            d.share_from = $('#filter-share-from').val();
            d.share_to = $('#filter-share-to').val();
            d.dob = $('#filter-dob').val();
            d.college = $('#filter-college').val();
            d.client = $('#filter-client').val();
            d.organization = $('#filter-organization').val();


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
        { data: 'preferred_location' },
        { data: 'experience' },
        
        { data: 'current_ctc' },
        { data: 'expected_ctc' },
        { data: 'notice_period' },
        { data: 'share_date' },
        { data: 'status' },
        { data: 'updated' },
        { data: 'dob' },
        { data: 'college' },
        { data: 'client' },
        { data: 'current_organization' },
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
          targets:13,
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

      order: [[14, 'desc']],
dom:
  '<"row"<"col-md-6"><"col-md-6">>' +
  '<"row"<"col-md-6"l><"col-md-6"f>>' +
  '<"dt-buttons-wrapper"B>' +
  '<"table-responsive"rt>' +
  '<"row"<"col-md-6"i><"col-md-6"p>>',

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
          // {
          //   text: '<i class="ti ti-download ti-xs me-sm-1"></i><span class="d-none d-sm-inline-block">Export CSV</span>',
          //   className: 'btn btn-primary me-4 waves-effect waves-light border-none',
          //   action: function () {
          //     const ids = getSelectedIds();

          //     if (ids.length === 0) {
          //       alert("Please select at least one candidate");
          //       return;
          //     }

          //     // redirect with ids
          //     window.location.href = `/candidate/export-selected-csv/?ids=${ids.join(',')}`;
          //   }
          // }

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

      initComplete: function () {

  // Add separator line after card header (optional)
  $('.card-header').after('<hr class="my-0">');

  // Disable Action button initially
  $('#actioncheck').prop('disabled', true);

  // Move Import button next to Action
  const dtButtons = document.querySelector('.dt-buttons');
  const rightToolbar = document.getElementById('datatable-toolbar-right');

  if (dtButtons && rightToolbar) {
    rightToolbar.appendChild(dtButtons);
  }
}


    });
      /* ADD THIS CODE HERE */
      dt_basic.on("draw", function () {
        $('.dt-checkboxes-select-all input')
            .off("change")
            .on("change", function () {
                let checked = $(this).prop("checked");
                selectAllMode = checked;

                dt_basic.rows({ search: 'applied' }).every(function () {
                    var node = this.node();
                    $(node).find(".dt-checkboxes").prop("checked", checked);
                });

                // ENABLE / DISABLE ACTION BUTTON
                actions.prop("disabled", !checked);
            });
             $(".dt-checkboxes").off("change").on("change", function () {
              if (!$(this).prop("checked")) {
                  selectAllMode = false; // ADD THIS
              }
              updateSelectedRows();
          });
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
/* =========================
   FILTER TRIGGERS (MAIN)
========================= */

// Text inputs
$('#filter-name, #filter-contact, #filter-email, #filter-designation, #filter-location')
.on('keyup', function () {
    dt_basic.ajax.reload();
});

// Date filter
$('#filter-updated').on('change', function () {
    dt_basic.ajax.reload();
});

      // Trigger table reload on filter change
  // $('#experience-input, .form-check-input').on('input', function () {
  //   dt_basic.ajax.reload();
  // });
  $('#min-exp, #max-exp,.form-check-input').on('input', function () {
    dt_basic.ajax.reload();
  });

  $('#filter-status').on('change', '.form-check-input', function () {
    dt_basic.ajax.reload();
  });
   $('#filter-preferred-location, #filter-share-date, #filter-current-ctc, #filter-expected-ctc, #filter-notice').on('input change', function () {
    dt_basic.ajax.reload();
  });

  $('#filter-share-from, #filter-share-to').on('change', function () {
    dt_basic.ajax.reload();
  });

  $('#filter-dob, #filter-college, #filter-client, #filter-organization')
  .on('keyup change', function () {
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
    let anyChecked = false;

    dt_basic.rows().every(function () {
        var node = this.node();
        var checkbox = $(node).find(".dt-checkboxes");

        if (checkbox.prop("checked")) {
            anyChecked = true;
        }
    });

    actions.prop("disabled", !anyChecked);
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
    dt_basic.rows().every(function () {
        var node = this.node();
        var checkbox = $(node).find(".dt-checkboxes");

        if (checkbox.prop("checked")) {
            selectedIds.push(this.data().id);
        }
    });

    console.log("Selected IDs:", selectedIds);
    return selectedIds;
}

  
          // Delete Record

  const delbtn = $('#delete_btn');
$('#deleteForm').on('submit', function (e) {
    e.preventDefault();

    const ids = getSelectedIds(); // [1,2,3]

    if (ids.length === 0) {
        alert("Please select at least one candidate");
        return;
    }

    $.ajax({
        url: $(this).attr('action'),
        type: 'POST',
        data: {
            ids: ids.join(','),   // 🔥 "1,2,3"
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (response) {
            if (response.status === 'success') {
                dt_basic.rows('.selected').remove().draw(false);
                $('#basicModal').modal('hide');
            } else {
                alert(response.message);
            }
        }
    });
});


  // $('#deleteForm').on('submit', function(e) {
  //   e.preventDefault();  // Prevent default form submission
  //  var idsToDelete = getSelectedIds();
  //   if (idsToDelete.length > 0) {
  //   // Send AJAX request to delete rows
  //   $.ajax({
  //     url: $(this).attr('action'),  // Replace with your delete endpoint
  //     method: 'POST',
  //     data: {
  //       'ids[]': idsToDelete,
  //       csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()  // Add CSRF token
  //     },
  //     success: function(response) {
  //       // On success, remove rows from DataTable
  //       dt_basic.rows('.selected').remove().draw(false);
  //       $('.dt-checkboxes-select-all input').prop('checked', false);
  //       $('#basicModal').modal('hide');
  //     },
  //     error: function(xhr, status, error) {
  //       console.error('Error deleting rows:', status, error);
  //       // Optionally, show an error message to the user
  //     }
  //   });
  // }

  // });

//   $('#shareJobOpeningForm').on('submit', function(e) {
//     e.preventDefault();

//     const ids = getSelectedIds();
//     const job_opening_id = $("#jobOpening").val();

//     if (ids.length === 0) {
//         alert("Please select at least one candidate.");
//         return;
//     }

//     $.ajax({
//         url: $(this).attr("action"),
//         method: "POST",
//         data: {
//             "ids": JSON.stringify(ids),   // VERY IMPORTANT
//             "job_opening_id": job_opening_id,
//             csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
//         },
//         success: function (response) {
//             $('#shareOpening').modal('hide');
//             $('.dt-checkboxes-select-all input').prop('checked', false);
//             dt_basic.ajax.reload();
//         },
//         error: function (xhr) {
//             console.error("Error:", xhr.responseText);
//         }
//     });
// });

$('#shareJobOpeningForm').on('submit', function (e) {
    e.preventDefault();

    const ids = getSelectedIds();
    const job_opening_id = $('#jobOpening').val();

    if (ids.length === 0) {
        alert("Please select at least one candidate.");
        return;
    }
     // 🔥 START LOADER (Correct IDs)
    $('#sendEmailBtn').prop('disabled', true);
    $('#btnText').text('Sending...');
    $('#btnLoader').removeClass('d-none');

    $.ajax({
        url: $(this).attr("action"),
        method: "POST",
        data: {
            "ids": JSON.stringify(ids),   // 🔥 EXACT match
            "job_opening_id": job_opening_id,
            csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (response) {
            // 🔥 STOP LOADER
            $('#sendEmailBtn').prop('disabled', false);
            $('#btnText').text('Send Email');
            $('#btnLoader').addClass('d-none');

            if (response.status === "success") {

                alert("Job opening shared successfully!");

                $('#shareOpening').modal('hide');
                dt_basic.ajax.reload(null, false);
            } else {
                alert(response.message);
            }
        },
        error: function (xhr) {
             // 🔥 STOP LOADER ON ERROR
            $('#sendEmailBtn').prop('disabled', false);
            $('#btnText').text('Send Email');
            $('#btnLoader').addClass('d-none');

            alert("Something went wrong!");
            console.error("Error:", xhr.responseText);
        }
    });
});


// ==========================
// EXPORT CSV FROM ACTION
// ==========================
// $('#exportCsvAction').on('click', function () {
//     const ids = getSelectedIds();

//     if (ids.length === 0) {
//         alert("Please select at least one candidate");
//         return;
//     }

//     window.location.href = `/candidate/export-selected-csv/?ids=${ids.join(',')}`;
// });

// }
// ==========================
// EXPORT CSV FROM ACTION
// ==========================
$('#exportCsvAction').on('click', function () {
    const params = new URLSearchParams(window.location.search);

    params.set('name',               $('#filter-name').val());
    params.set('designation',        $('#filter-designation').val());
    params.set('contact',            $('#filter-contact').val());
    params.set('email',              $('#filter-email').val());
    params.set('location',           $('#filter-location').val());
    params.set('preferred_location', $('#filter-preferred-location').val());
    params.set('min_exp',            $('#min-exp').val());
    params.set('max_exp',            $('#max-exp').val());
    params.set('dob',                $('#filter-dob').val());
    params.set('college',            $('#filter-college').val());
    params.set('client',             $('#filter-client').val());
    params.set('organization',       $('#filter-organization').val());
    params.set('current_ctc',        $('#filter-current-ctc').val());
    params.set('expected_ctc',       $('#filter-expected-ctc').val());
    params.set('notice_period',      $('#filter-notice').val());
    params.set('updated',            $('#filter-updated').val());
    params.set('search_value',       dt_basic.search());

    const sfrom = $('#filter-share-from').length ? $('#filter-share-from').val() : '';
    const sto   = $('#filter-share-to').length   ? $('#filter-share-to').val()   : '';
    params.set('share_from', sfrom || '');
    params.set('share_to',   sto   || '');

    const status = $('.form-check-input:checked').map(function () {
        return $(this).data('value');
    }).get().join(',');
    params.set('status', status);

    const selectedIds = getSelectedIds();
    if (!selectAllMode && selectedIds.length > 0) {
        // ✅ Specific rows selected → export only those
        params.set('ids', selectedIds.join(','));
    }
    // ✅ No selection / select-all → export ALL filtered (no ids param)

    window.location.href = `/candidate/export-selected-csv/?${params.toString()}`;
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
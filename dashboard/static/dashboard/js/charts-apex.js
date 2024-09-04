/**
 * Charts Apex
 */

'use strict';

(function () {
  let cardColor, headingColor, labelColor, borderColor, legendColor;

  if (isDarkStyle) {
    cardColor = config.colors_dark.cardColor;
    headingColor = config.colors_dark.headingColor;
    labelColor = config.colors_dark.textMuted;
    legendColor = config.colors_dark.bodyColor;
    borderColor = config.colors_dark.borderColor;
  } else {
    cardColor = config.colors.cardColor;
    headingColor = config.colors.headingColor;
    labelColor = config.colors.textMuted;
    legendColor = config.colors.bodyColor;
    borderColor = config.colors.borderColor;
  }

  // Color constant
  const chartColors = {
    column: {
      series1: '#826af9',
      series2: '#d2b0ff',
      bg: '#f8d3ff'
    },
    donut: {
      series1: '#fee802',
      series2: '#F1F0F2',
      series3: '#826bf8',
      series4: '#3fd0bd'
    },
    area: {
      series1: '#29dac7',
      series2: '#60f2ca',
      series3: '#a5f8cd'
    },
    bar: {
      bg: '#1D9FF2'
    }
  };

  // Heat chart data generator
  function generateDataHeat(count, yrange) {
    let i = 0;
    let series = [];
    while (i < count) {
      let x = 'w' + (i + 1).toString();
      let y = Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min;

      series.push({
        x: x,
        y: y
      });
      i++;
    }
    return series;
  }


  // Horizontal Bar Chart
  // --------------------------------------------------------------------

  function getRandomColor() {
    // Define a range for each color channel to avoid extremes
    const min = 64; // minimum value for R, G, and B to avoid very dark colors
    const max = 192; // maximum value for R, G, and B to avoid very light colors

    const r = Math.floor(Math.random() * (max - min + 1)) + min;
    const g = Math.floor(Math.random() * (max - min + 1)) + min;
    const b = Math.floor(Math.random() * (max - min + 1)) + min;

    return `rgb(${r}, ${g}, ${b})`;
  }
  // Get data from database
  const horizontalBarChartEl = document.querySelector('#horizontalBarChart'),
  data =  JSON.parse(horizontalBarChartEl.getAttribute('data-response')),
  skills_level = data.skills_level,
  transformedSkillsLevel = Object.fromEntries(
    Object.entries(skills_level).map(([key, value]) => [key, parseInt(value, 10)])),
  skills = Object.keys(transformedSkillsLevel),
  skills_value = Object.values(transformedSkillsLevel),
  categories = Array.from({ length: skills.length }, (_, i) => i + 1).reverse(),

  barcolors = Array.from({ length: skills.length }, () => getRandomColor()),
  horizontalBarChartConfig = {
      chart: {
        height: 500,
        type: 'bar',
        toolbar: {
          show: false
        }
      },
      plotOptions: {
        bar: {
          horizontal: true,
          barHeight: '50%',
          distributed: true,
          startingShape: 'rounded',
          borderRadius: 8
        }
      },
      grid: {
        strokeDashArray: 10,
        borderColor: borderColor,
        xaxis: {
          lines: {
            show: true
          }
        },
        yaxis: {
          lines: {
            show: false
          }
        },
        padding: {
          top: -20,
          bottom: -12
        }
      },
       colors: barcolors,
      fill: {
        opacity: [1, 1, 1, 1, 1, 1, 1]
      },
      dataLabels: {
        enabled: true,
        style: {
          colors: ['#fff'],
          fontWeight: 400,
          fontSize: '13px',
          fontFamily: 'Public Sans'
        },
        formatter: function (val, opts) {
          return skills[opts.dataPointIndex];
        },
        offsetX: 0,
        dropShadow: {
          enabled: false
        }
        },
      labels: skills,
      series: [
        {
          name: 'Level',
          data: skills_value
        }
      ],
      xaxis: {
        categories: categories,
        axisBorder: {
          show: false
        },
        axisTicks: {
          show: false
        },
        labels: {
          style: {
            colors: labelColor,
            fontSize: '13px'
          }
        }
      },
      yaxis: {
        max: 5,
        labels: {
          style: {
            colors: labelColor,
            fontSize: '13px'
          }
        }
      },
      tooltip: {
        enabled: true,
        style: {
          fontSize: '12px'
        },
        onDatasetHover: {
          highlightDataSeries: false
        },
        custom: function ({ series, seriesIndex, dataPointIndex, w }) {
          return '<div class="px-3 py-2">' + '<span>Level : ' + series[seriesIndex][dataPointIndex] + '</span>' + '</div>';
        }
      },
      legend: {
        show: false
      }
    };

  if (typeof horizontalBarChartEl !== undefined && horizontalBarChartEl !== null) {
    const horizontalBarChart = new ApexCharts(horizontalBarChartEl, horizontalBarChartConfig);
    horizontalBarChart.render();
  }


  // JobMatching Radial Bar Chart
  // --------------------------------------------------------------------
  const jobMatchingChartEl = document.querySelector('#jobMatching'),


    jobMatchingChartConfig = {
      chart: {
        height: 100,
        sparkline: {
          enabled: true
        },
        parentHeightOffset: 0,
        type: 'radialBar'
      },
      colors: [config.colors.warning],
      series: [data.job_matching.match],
      plotOptions: {
        radialBar: {
          offsetY: 0,
          startAngle: -90,
          endAngle: 90,
          hollow: {
            size: '70%'
          },
          track: {
            strokeWidth: '45%',
            background: borderColor
          },
          dataLabels: {
            name: {
              show: false
            },
            value: {
              fontSize: '36px',
              color: headingColor,
              fontWeight: 500,
              offsetY: -5
            }
          }
        }
      },
      grid: {
        show: false,
        padding: {
          bottom: 5
        }
      },
      stroke: {
        lineCap: 'round'
      },
      labels: ['Progress'],
      responsive: [
        {
          breakpoint: 1442,
          options: {
            chart: {
              height: 300
            },
            plotOptions: {
              radialBar: {
                hollow: {
                  size: '65%'
                },
                dataLabels: {
                  value: {
                    fontSize: '36px',
                    offsetY: -1
                  }
                }
              }
            }
          }
        },
        {
          breakpoint: 1200,
          options: {
            chart: {
              height: 228
            },
            plotOptions: {
              radialBar: {
                hollow: {
                  size: '75%'
                },
                track: {
                  strokeWidth: '50%'
                },
                dataLabels: {
                  value: {
                    fontSize: '26px'
                  }
                }
              }
            }
          }
        },
        {
          breakpoint: 890,
          options: {
            chart: {
              height: 180
            },
            plotOptions: {
              radialBar: {
                hollow: {
                  size: '70%'
                }
              }
            }
          }
        },
        {
          breakpoint: 426,
          options: {
            chart: {
              height: 142
            },
            plotOptions: {
              radialBar: {
                hollow: {
                  size: '70%'
                },
                dataLabels: {
                  value: {
                    fontSize: '22px'
                  }
                }
              }
            }
          }
        },
        {
          breakpoint: 376,
          options: {
            chart: {
              height: 105
            },
            plotOptions: {
              radialBar: {
                hollow: {
                  size: '60%'
                },
                dataLabels: {
                  value: {
                    fontSize: '18px'
                  }
                }
              }
            }
          }
        }
      ]
    };
  if (typeof jobMatchingChartEl !== undefined && jobMatchingChartEl !== null) {
    const expensesRadialChart = new ApexCharts(jobMatchingChartEl, jobMatchingChartConfig);
    expensesRadialChart.render();
  }

})();


const visitedTabs = {
    'job-matching': false,
    'skill-analysis': false,
    'personality': false,
    'questions': false
};
const tabs = ['job-matching', 'skill-analysis', 'personality', 'questions'];
const activeTab = document.querySelector('.nav-tabs .active');
const activeTabId = activeTab.getAttribute('data-bs-target');
visitedTabs[activeTabId.substring(1)] = true;


// Event listener to track tab changes
document.querySelectorAll('.nav-tabs .nav-link').forEach(tab => {

    tab.addEventListener('shown.bs.tab', function (event) {

        const tabId = event.target.getAttribute('data-bs-target').substring(1); // Remove leading '#'
        visitedTabs[tabId] = true;

    });
});


var exportbtn = document.getElementById("exportbtn");
const filename = exportbtn.getAttribute('data-name') + '.pdf';

 if (exportbtn) {
 exportbtn.addEventListener("click", async function() {
 const allVisited = Object.values(visitedTabs).every(Boolean);
     if (!allVisited) {
        alert('Please review all tabs before exporting.');
        return;
    }

    const activeTab = document.querySelector('.nav-tabs .active');
    const activeTabId = activeTab.getAttribute('data-bs-target');

    activeTab.classList.remove('active');


//            const chartContainer = document.getElementById("jobMatching");
//
//            // Capture chart as image
//            const chartCanvas = await html2canvas(chartContainer, { scale: 2 });
//            const chartImgData = chartCanvas.toDataURL('image/png');
//
//            // Replace chart with image
//            chartContainer.innerHTML = `<img src="${chartImgData}" style="width: 100%;"/>`;

            // Create an HTML element for exporting

                        // Convert HTML content to PDF

               // Initialize the pdf variable
            const imageurl = exportbtn.getAttribute('data-imageurl');
            const designation = exportbtn.getAttribute('data-des');
            const name = exportbtn.getAttribute('data-name');
            let pdfContent = `<img src="${imageurl}" alt="Descriptive text" width="100" height="auto">`
                              + `<div class="text-center"><h4 class="mb-1">${name}</h4><h5>${designation}</h5></div>`          ;

            for (let i = 0; i < tabs.length; i++) {
                const TabId = document.querySelector(`[data-bs-target="#${tabs[i]}"]`);

                const tabElement = document.getElementById(tabs[i]);

                TabId.classList.add('active');
                const tabContentClone = tabElement.cloneNode(true);

                // Select the specific <div> element you want to remove
                const unwantedDiv = tabContentClone.querySelector('.unwanted-div-class'); // Use the correct class or ID
                if (unwantedDiv) {
                    unwantedDiv.remove();
                    pdfContent += '<div class="mt-5"></div>' + tabContentClone.innerHTML + '<div class="html2pdf__page-break"></div>'; // Store each tab's content in the array

                }
                else if (i==(tabs.length-1)){
                    pdfContent += '<div class="mt-5"></div>' + tabElement.innerHTML; // Store each tab's content in the array
                }
                else{
                   pdfContent += '<div class="mt-5"></div>' + tabElement.innerHTML + '<div class="html2pdf__page-break"></div>'; // Store each tab's content in the array

                }

                console.log('Downloading..', tabs[i]);


                console.log('Saved:', `exported_report_${tabs[i]}.pdf`);

                TabId.classList.remove('active');
            }
            const opt = {
                margin: [20, 50, 50, 50],
                filename: filename, // Save with one filename for the entire PDF
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'pt', format: 'a4', orientation: 'portrait' }
            };

            await html2pdf().from(pdfContent).set(opt).save();

    document.querySelector(`[data-bs-target="${activeTabId}"]`).classList.add('active');
    console.log('All PDFs saved.');
    });
 }

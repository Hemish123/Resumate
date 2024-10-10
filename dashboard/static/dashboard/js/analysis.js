        const skillschart = document.getElementById('skillsMatchChart'),
        data =  JSON.parse(skillschart.getAttribute('data-response')),
        ctx = skillschart.getContext('2d');
        const matchPercentage = data.skills_matching.match; // Fetching the match percentage from your backend

        const skillsMatchChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Match', 'No Match'],
                datasets: [{
                    data: [matchPercentage, 100 - matchPercentage], // Match percentage and remaining percentage
                    backgroundColor: ['#4CAF50', '#e0e0e0'], // Colors for the matching section and no match section
                    borderColor: ['#4CAF50', '#e0e0e0'], // Border colors
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                cutout: '70%', // Makes it a doughnut shape with a hole in the center
                plugins: {
                    legend: {
                        display: false // Hide legend
                    },
                    tooltip: {
                        enabled: false // Disable tooltip if not needed
                    }
                }
            },
            plugins: [{
                // Custom plugin to add text inside the doughnut chart
                beforeDraw: function(chart) {
                    var width = chart.width,
                        height = chart.height,
                        ctx = chart.ctx;

                    ctx.restore();
                    var fontSize = (height / 100).toFixed(2); // Dynamic font size
                    ctx.font = fontSize + "em sans-serif"; // Set font
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = "#000"; // Text color

                    var text = matchPercentage + '%',
                        textX = Math.round((width - ctx.measureText(text).width) / 2),
                        textY = height / 2;

                    ctx.fillText(text, textX, textY); // Render text
                    ctx.save();
                }
            }]
        });


var exportbtn = document.getElementById("exportbtn");
const filename = exportbtn.getAttribute('data-name') + '.pdf';

 if (exportbtn) {
 exportbtn.addEventListener("click", async function() {

 const chartContainer = document.getElementById("skillsMatchChart");

// Capture chart as image
const chartCanvas = await html2canvas(chartContainer, { scale: 2 });
const chartImgData = chartCanvas.toDataURL('image/png');

// Replace chart with image
chartContainer.innerHTML = `<img src="${chartImgData}" style="width: 100%;"/>`;

            // Create an HTML element for exporting

                        // Convert HTML content to PDF

               // Initialize the pdf variable
            const imageurl = exportbtn.getAttribute('data-imageurl');
            const designation = exportbtn.getAttribute('data-des');
            const name = exportbtn.getAttribute('data-name');
            let pdfContent = `<img src="${imageurl}" alt="Descriptive text" width="100" height="auto">`
                              + `<div class="text-center"><h4 class="mb-1">${name}</h4><h5>${designation}</h5></div>`          ;


                const tabElement = document.getElementById('export-section');


                    const tabContentClone = tabElement.cloneNode(true);



                    pdfContent += '<div class="mt-5"></div>' + tabContentClone.innerHTML + '<div class="html2pdf__page-break"></div>'; // Store each tab's content in the array

                console.log('Downloading..', tabElement);

            const opt = {
                margin: [20, 50, 50, 50],
                filename: filename, // Save with one filename for the entire PDF
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'pt', format: 'a4', orientation: 'landscape' }
            };

            await html2pdf().from(pdfContent).set(opt).save();

    });
 }
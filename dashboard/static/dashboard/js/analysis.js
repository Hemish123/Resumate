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



            // Create an HTML element for exporting

                        // Convert HTML content to PDF

               // Initialize the pdf variable
            const imageurl = exportbtn.getAttribute('data-imageurl');
            const designation = exportbtn.getAttribute('data-des');
            const name = exportbtn.getAttribute('data-name');
            let pdfContent = `<div class="d-flex justify-content-between"><img src="${imageurl}" alt="Descriptive text" width="75" height="auto">`
                              + `<a href="https://www.jmsadvisory.in" class="ms-2 text-primary" target="_blank" style="text-decoration: none;">www.jmsadvisory.in</a></div>`

                              + `<div class="text-center mt-0"><h4 class="fw-bold text-primary my-0">${name}</h4><h6>${designation}</h6></div>`          ;


                const tabElement = document.getElementById('export-section');
                const chartContainer = document.getElementById("skillsMatchChart");

                    // Capture chart as image
                    const chartCanvas = await html2canvas(chartContainer, { scale: 2 });
                    const chartImgData = chartCanvas.toDataURL('image/png');


                    const tabContentClone = tabElement.cloneNode(true);
                    tabContentClone.style.margin = '0';           // Remove excessive margin
                    tabContentClone.style.padding = '0';

                    const clonedChartContainer = tabContentClone.querySelector("#skillsMatchChart"); // Chart in the cloned element

                    if (clonedChartContainer){
                        clonedChartContainer.parentNode.innerHTML = `<img src="${chartImgData}" style="width: 100%;"/>`;

                    }

                        // Step 2: Reduce unnecessary spacing (CSS adjustments)
                    const allText = tabContentClone.querySelectorAll('*');
                    allText.forEach((el) => {

                        if (el.tagName === 'H3'){
                            el.remove();
                        }
                        else if (el.tagName === 'H5') {
                            el.style.fontSize = '16px';
                            el.style.margin = '0';           // Remove excessive margin
                            el.style.padding = '0';          // Remove excessive padding
                        }
                        else if (el.className == 'badge bg-primary me-1 mt-1') {
                            el.style.fontSize = '14px';   // Reduce font size slightly
                            el.style.margin = '0';           // Remove excessive margin
                            el.style.padding = '5px';          // Remove excessive padding
                        }
                        else{
                            el.style.fontSize = '14px';   // Reduce font size slightly
                            el.style.margin = '0';           // Remove excessive margin
                            el.style.padding = '0';          // Remove excessive padding

                        }


                    });

                    const colDivs = tabContentClone.querySelectorAll("#newpage .col-md-3");
                        const hr = document.createElement("hr");

                        if (colDivs){
                            colDivs.forEach(div => {
                                div.classList.replace("col-md-3", "col-md-5");
                                div.style.margin = '5px';
                                div.style.padding = '5px';
                            });
                        }

                    // Reduce image sizes (Candidate image)
                    const candidateImg = tabContentClone.querySelector("img");
                    if (candidateImg) {
                        candidateImg.style.maxWidth = '150px';  // Limit image width
                        candidateImg.style.height = 'auto';     // Maintain aspect ratio
                    }
                    // Replace chart with image

                    const newPageElement = tabContentClone.querySelector('#newpage');

                    if (newPageElement) {
                        // Create the page break div
                        const pageBreakDiv = document.createElement('div');
                        pageBreakDiv.classList.add('html2pdf__page-break');

                        // Insert the page break before the specified element
                        newPageElement.parentNode.insertBefore(pageBreakDiv, newPageElement);
                    }

                    pdfContent += tabContentClone.innerHTML; // Store each tab's content in the array

                console.log('Downloading..', tabContentClone);

            const opt = {
                margin: [20, 20, 20, 20],
                filename: filename, // Save with one filename for the entire PDF
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'pt', format: 'a4', orientation: 'portrait' }
            };

            await html2pdf().from(pdfContent).set(opt).save();

    });
 }
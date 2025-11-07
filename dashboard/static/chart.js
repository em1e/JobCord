document.addEventListener("DOMContentLoaded", function () {
    // Job Status Pie Chart
    const statusCtx = document.getElementById("statusChart").getContext("2d");
    const statusChart = new Chart(statusCtx, {
        type: "pie",
        data: {
            labels: Object.keys(statusCounts),
            datasets: [{
                label: "Job Statuses",
                data: Object.values(statusCounts),
                backgroundColor: [
                    "rgba(54, 162, 235, 0.7)",   // Applied
                    "rgba(255, 99, 132, 0.7)",   // Denied
                    "rgba(75, 192, 192, 0.7)",   // Accepted
                    "rgba(255, 206, 86, 0.7)"    // Interview
                ],
                borderColor: [
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 99, 132, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(255, 206, 86, 1)"
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                },
                title: {
                    display: true,
                    text: "Job Application Statuses"
                }
            }
        }
    });

    // Jobs per Source Bar Chart
    const sourceCtx = document.getElementById("sourceChart").getContext("2d");
    const sourceChart = new Chart(sourceCtx, {
        type: "bar",
        data: {
            labels: Object.keys(sourceCounts),
            datasets: [{
                label: "Jobs Scraped",
                data: Object.values(sourceCounts),
                backgroundColor: "rgba(153, 102, 255, 0.7)",
                borderColor: "rgba(153, 102, 255, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: "Number of Jobs Scraped per Source"
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
});
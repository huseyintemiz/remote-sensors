// Chart.js visualization for sensor data

// Store chart instances
const charts = {};
const chartRanges = {}; // Store selected time range per machine

// Chart configuration
const chartConfig = {
    cpu: {
        borderColor: 'rgb(102, 126, 234)',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        label: 'CPU Temperature (°C)'
    },
    gpu: {
        borderColor: 'rgb(240, 147, 251)',
        backgroundColor: 'rgba(240, 147, 251, 0.1)',
        label: 'GPU Temperature (°C)'
    }
};

/**
 * Initialize a chart for a specific machine
 */
async function initializeChart(hostname) {
    const canvasId = `chart-${hostname}`;
    const ctx = document.getElementById(canvasId);

    if (!ctx) {
        console.error(`Canvas not found for ${hostname}`);
        return;
    }

    // Set default time range (10 minutes)
    chartRanges[hostname] = 10;

    // Fetch historical data
    const historyData = await fetchHistory(hostname, 60);

    if (!historyData || !historyData.readings) {
        console.error(`No data available for ${hostname}`);
        return;
    }

    // Prepare chart data
    const chartData = prepareChartData(historyData.readings);

    // Create chart
    charts[hostname] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: chartConfig.cpu.label,
                    data: chartData.cpuData,
                    borderColor: chartConfig.cpu.borderColor,
                    backgroundColor: chartConfig.cpu.backgroundColor,
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: true
                },
                {
                    label: chartConfig.gpu.label,
                    data: chartData.gpuData,
                    borderColor: chartConfig.gpu.borderColor,
                    backgroundColor: chartConfig.gpu.backgroundColor,
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(1) + '°C';
                            } else {
                                label += 'N/A';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        maxTicksLimit: 8,
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Temperature (°C)'
                    },
                    beginAtZero: false,
                    suggestedMin: 20,
                    suggestedMax: 100
                }
            }
        }
    });
}

/**
 * Prepare chart data from historical readings
 */
function prepareChartData(readings) {
    const labels = [];
    const cpuData = [];
    const gpuData = [];

    readings.forEach(reading => {
        // Format timestamp as HH:MM:SS
        const date = new Date(reading.timestamp * 1000);
        const timeStr = date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });

        labels.push(timeStr);
        cpuData.push(reading.cpu_temp);
        gpuData.push(reading.gpu_temp);
    });

    return { labels, cpuData, gpuData };
}

/**
 * Fetch historical data for a machine
 */
async function fetchHistory(hostname, limit = 60) {
    try {
        const response = await fetch(`/api/history/${hostname}?limit=${limit}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching history:', error);
        return null;
    }
}

/**
 * Fetch current data for all machines
 */
async function fetchCurrentData() {
    try {
        const response = await fetch('/api/current');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching current data:', error);
        return null;
    }
}

/**
 * Update all charts with latest data
 */
async function updateAllCharts() {
    for (const hostname in charts) {
        await updateChart(hostname);
    }
}

/**
 * Update a specific chart with latest data
 */
async function updateChart(hostname) {
    const chart = charts[hostname];
    if (!chart) return;

    const range = chartRanges[hostname] || 10;
    const limit = Math.ceil(range * 60 / 60); // Convert minutes to data points (assuming 60s interval)

    const historyData = await fetchHistory(hostname, limit);

    if (!historyData || !historyData.readings) {
        return;
    }

    const chartData = prepareChartData(historyData.readings);

    chart.data.labels = chartData.labels;
    chart.data.datasets[0].data = chartData.cpuData;
    chart.data.datasets[1].data = chartData.gpuData;
    chart.update('none'); // Update without animation for smoother refresh
}

/**
 * Update chart time range
 */
async function updateChartRange(hostname, minutes) {
    chartRanges[hostname] = minutes;

    // Update button states
    const container = document.querySelector(`#chart-${hostname}`).closest('.chart-container');
    const buttons = container.querySelectorAll('.time-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update chart
    await updateChart(hostname);
}

console.log('Charts module loaded and ready');

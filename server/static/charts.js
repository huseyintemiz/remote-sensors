// Placeholder for future chart functionality
// This file can be extended to add time-series graphs using libraries like Chart.js or Plotly.js

console.log('Charts module loaded - ready for future enhancements');

// Example: Fetch historical data for a machine
async function fetchHistory(hostname) {
    try {
        const response = await fetch(`/api/history/${hostname}`);
        const data = await response.json();
        console.log(`History for ${hostname}:`, data);
        return data;
    } catch (error) {
        console.error('Error fetching history:', error);
        return null;
    }
}

// Example: Fetch current data for all machines
async function fetchCurrentData() {
    try {
        const response = await fetch('/api/current');
        const data = await response.json();
        console.log('Current data:', data);
        return data;
    } catch (error) {
        console.error('Error fetching current data:', error);
        return null;
    }
}

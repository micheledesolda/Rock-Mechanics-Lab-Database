// scripts.js

function fillExperimentId() {
    const fileInput = document.getElementById('experimentFile');
    const experimentIdInput = document.getElementById('experimentId');
    if (fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        const baseName = fileName.replace('.tdms', '');
        experimentIdInput.value = baseName;
    }
}

async function fetchMeasurements() {
    const experimentId = document.getElementById('experimentId').value;
    const response = await fetch(`/experiments/${experimentId}/measurements`);
    const channelNames = await response.json();
    displayChannelNames(channelNames);
}

function displayChannelNames(channelNames) {
    const measurementsDiv = document.getElementById('measurements');
    measurementsDiv.innerHTML = '<h3>ADC Channel Names:</h3>';
    const list = document.createElement('ul');
    channelNames.forEach(name => {
        const listItem = document.createElement('li');
        
        const span = document.createElement('span');
        span.textContent = name;

        // Create the "Process measurement" button
        const processButton = document.createElement('button');
        processButton.textContent = 'Process measurement';
        processButton.onclick = () => processMeasurement(name);

        // Append the span and button to the list item
        listItem.appendChild(span);
        listItem.appendChild(processButton);
        list.appendChild(listItem);
    });
    measurementsDiv.appendChild(list);
}

async function processMeasurement(channelName) {
    const experimentId = document.getElementById('experimentId').value;
    alert(`Processing measurement for channel: ${channelName} in experiment: ${experimentId}`);
    // Additional logic to process the measurement can be added here
}

async function fetchExperiments() {
    console.log('Fetching experiments...');
    const response = await fetch('/experiments/all_ids');
    if (!response.ok) {
        console.error('Failed to fetch experiments', response.status);
        return;
    }
    const experimentIds = await response.json();
    console.log('Fetched experiment IDs:', experimentIds);
    displayExperimentIds(experimentIds);
}

function displayExperimentIds(experimentIds) {
    const dropdown = document.getElementById('experimentDropdown');
    dropdown.innerHTML = ''; // Clear existing content
    experimentIds.forEach(id => {
        const a = document.createElement('a');
        a.textContent = id;
        a.href = "#";
        a.onclick = () => selectExperiment(id);
        dropdown.appendChild(a);
    });
    console.log('Dropdown updated with experiment IDs.');
}

function selectExperiment(experimentId) {
    console.log('Selected experiment ID:', experimentId);
    document.getElementById('experimentId').value = experimentId;
    hideExperimentDropdown();
}

function showExperimentDropdown() {
    console.log('Showing experiment dropdown...');
    fetchExperiments();
    document.getElementById('experimentDropdown').classList.add('show');
}

function hideExperimentDropdown() {
    console.log('Hiding experiment dropdown...');
    document.getElementById('experimentDropdown').classList.remove('show');
}

async function uploadExperiment() {
    const fileInput = document.getElementById('experimentFile');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/experiments/create_experiment_from_file', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    alert(`Experiment created with ID: ${result.experiment_id}`);
}

async function saveMeasurements() {
    const experimentId = document.getElementById('experimentId').value;
    const measurements = []; // Collect measurements data
    const response = await fetch(`/experiments/${experimentId}/save_measurements`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(measurements)
    });
    const result = await response.json();
    alert(`Measurements saved at: ${result.file_location}`);
}

// Hide the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('button')) {
        hideExperimentDropdown();
    }
}

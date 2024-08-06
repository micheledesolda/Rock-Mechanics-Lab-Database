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
    const machineId = 'YourMachineID';  // Replace with the actual machine ID or logic to get it
    const layerThicknessMeasuredMm = 6;  // Replace with actual value or logic to get it
    const layerThicknessMeasuredPoint = 0;  // Replace with actual value or logic to get it

    const data = {
        experiment_id: experimentId,
        machine_id: machineId,
        layer_thickness_measured_mm: layerThicknessMeasuredMm,
        layer_thickness_measured_point: layerThicknessMeasuredPoint
    };

    try {
        const response = await fetch('/experiments/reduce_experiment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            console.error('Failed to process measurement', response.status);
            const errorText = await response.text();
            console.error('Error details:', errorText);
            return;
        }

        const result = await response.json();
        console.log('Processed measurement result:', result);

        // Display the processed results
        displayProcessedResults(result);

    } catch (error) {
        console.error('Error processing measurement:', error);
    }
}

function displayProcessedResults(result) {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `
        <h3>Processed Results:</h3>
        <p>Shear Stress (MPa): ${result.shear_stress_MPa}</p>
        <p>Normal Stress (MPa): ${result.normal_stress_MPa}</p>
        <p>Load Point Displacement (mm): ${result.load_point_displacement_mm}</p>
        <p>Layer Thickness (mm): ${result.layer_thickness_mm}</p>
    `;
}


async function fetchExperiments() {
    console.log('Fetching experiments...');
    try {
        const response = await fetch('/experiments/experiments/all_ids');
        if (!response.ok) {
            console.error('Failed to fetch experiments', response.status);
            const errorText = await response.text();
            console.error('Error details:', errorText);
            return;
        }
        const experimentIds = await response.json();
        console.log('Fetched experiment IDs:', experimentIds);
        displayExperimentIds(experimentIds);
    } catch (error) {
        console.error('Error fetching experiments:', error);
    }
}

function displayExperimentIds(experimentIds) {
    const dropdown = document.getElementById('experimentDropdown');
    dropdown.innerHTML = ''; // Clear existing content
    if (experimentIds.length === 0) {
        const noExperimentsMessage = document.createElement('p');
        noExperimentsMessage.textContent = 'No experiments found';
        dropdown.appendChild(noExperimentsMessage);
    } else {
        experimentIds.forEach(id => {
            const listItem = document.createElement('a');
            listItem.textContent = id;
            listItem.href = "#";
            listItem.onclick = () => selectExperiment(id);
            dropdown.appendChild(listItem);
        });
    }
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

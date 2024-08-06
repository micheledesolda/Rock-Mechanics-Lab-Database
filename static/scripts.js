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
    // Add input fields for machine_id, layer_thickness_measured_mm, and layer_thickness_measured_point
    const inputFieldsDiv = document.getElementById('inputFields');
    inputFieldsDiv.innerHTML = `
        <input type="text" id="machineId" placeholder="Enter Machine ID">
        <input type="number" id="layerThicknessMeasuredMm" placeholder="Enter Layer Thickness Measured (mm)">
        <input type="number" id="layerThicknessMeasuredPoint" placeholder="Enter Layer Thickness Measured Point">
    `;
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

        // Create a container for the button to align them
        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('measurement-buttons');
        buttonContainer.appendChild(processButton);

        // Append the span and button container to the list item
        listItem.appendChild(span);
        listItem.appendChild(buttonContainer);
        list.appendChild(listItem);
    });
    measurementsDiv.appendChild(list);
}

async function processMeasurement(channelName) {
    const experimentId = document.getElementById('experimentId').value;
    const machineId = document.getElementById('machineId').value;
    const layerThicknessMeasuredMm = document.getElementById('layerThicknessMeasuredMm').value || 6;
    const layerThicknessMeasuredPoint = document.getElementById('layerThicknessMeasuredPoint').value || 0;

    const data = {
        experiment_id: experimentId,
        machine_id: machineId,
        layer_thickness_measured_mm: layerThicknessMeasuredMm,
        layer_thickness_measured_point: layerThicknessMeasuredPoint
    };

    let endpoint = '';
    let yAxisLabel = '';
    if (channelName === 'Vertical Load') {
        endpoint = `/experiments/${experimentId}/process_vertical_load`;
        yAxisLabel = 'Shear Stress (MPa)';
    } else if (channelName === 'Horizontal Load') {
        endpoint = `/experiments/${experimentId}/process_horizontal_load`;
        yAxisLabel = 'Normal Stress (MPa)';
    } else if (channelName === 'Vertical Displacement') {
        endpoint = `/experiments/${experimentId}/process_vertical_displacement`;
        yAxisLabel = 'Load Point Displacement (mm)';
    } else if (channelName === 'Horizontal Displacement') {
        endpoint = `/experiments/${experimentId}/process_horizontal_displacement`;
        yAxisLabel = 'Layer Thickness (mm)';
    }

    if (endpoint) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        console.log(result);
        updatePlot(channelName, result, yAxisLabel);
        alert(`Processed ${channelName} for experiment: ${experimentId}`);
    } else {
        alert('No processing method defined for this channel.');
    }
}

function updatePlot(channelName, data, yAxisLabel) {
    const plotDiv = document.getElementById('plot');
    const trace = {
        x: [...Array(data.length).keys()],
        y: data,
        mode: 'lines',
        name: channelName
    };

    const layout = {
        title: 'Measurement Data',
        xaxis: { title: 'Record Number' },
        yaxis: { title: yAxisLabel },
    };

    Plotly.newPlot(plotDiv, [trace], layout);
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
    const list = document.createElement('ul');
    experimentIds.forEach(id => {
        const listItem = document.createElement('a');
        listItem.textContent = id;
        listItem.href = "#";
        listItem.onclick = () => selectExperiment(id);
        dropdown.appendChild(listItem);
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

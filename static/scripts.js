// scripts.js

let plotData = {};

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

        const processButton = document.createElement('button');
        processButton.textContent = 'Process measurement';
        processButton.onclick = () => processMeasurement(name);

        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('measurement-buttons');
        buttonContainer.appendChild(processButton);

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
    let plotKey = '';

    if (channelName === 'Vertical Load') {
        endpoint = `/experiments/${experimentId}/process_vertical_load`;
        plotKey = 'shear_stress_MPa';
    } else if (channelName === 'Horizontal Load') {
        endpoint = `/experiments/${experimentId}/process_horizontal_load`;
        plotKey = 'normal_stress_MPa';
    } else if (channelName === 'Vertical Displacement') {
        endpoint = `/experiments/${experimentId}/process_vertical_displacement`;
        plotKey = 'load_point_displacement_mm';
    } else if (channelName === 'Horizontal Displacement') {
        endpoint = `/experiments/${experimentId}/process_horizontal_displacement`;
        plotKey = 'layer_thickness_mm';
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
        plotData[plotKey] = result[plotKey];
        updatePlot();
        alert(`Processed ${channelName} for experiment: ${experimentId}`);
    } else {
        alert('No processing method defined for this channel.');
    }
}

function updatePlot() {
    const plotDiv = document.getElementById('plot');
    const traces = [];

    if (plotData.shear_stress_MPa) {
        traces.push({
            x: [...Array(plotData.shear_stress_MPa.length).keys()],
            y: plotData.shear_stress_MPa,
            mode: 'lines',
            name: 'Shear Stress (MPa)',
            yaxis: 'y1'
        });
    }

    if (plotData.normal_stress_MPa) {
        traces.push({
            x: [...Array(plotData.normal_stress_MPa.length).keys()],
            y: plotData.normal_stress_MPa,
            mode: 'lines',
            name: 'Normal Stress (MPa)',
            yaxis: 'y1'
        });
    }

    if (plotData.load_point_displacement_mm) {
        traces.push({
            x: [...Array(plotData.load_point_displacement_mm.length).keys()],
            y: plotData.load_point_displacement_mm,
            mode: 'lines',
            name: 'Load Point Displacement (mm)',
            yaxis: 'y2'
        });
    }

    if (plotData.layer_thickness_mm) {
        traces.push({
            x: [...Array(plotData.layer_thickness_mm.length).keys()],
            y: plotData.layer_thickness_mm,
            mode: 'lines',
            name: 'Layer Thickness (mm)',
            yaxis: 'y2'
        });
    }

    const layout = {
        title: 'Measurement Data',
        xaxis: { title: 'Record Number' },
        yaxis: { title: 'Stress (MPa)', side: 'left' },
        yaxis2: {
            title: 'Displacement (mm)',
            overlaying: 'y',
            side: 'right'
        },
        showlegend: true,
        legend: { x: 1, xanchor: 'right', y: 1 }
    };

    Plotly.react(plotDiv, traces, layout);
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

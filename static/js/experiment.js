document.addEventListener('DOMContentLoaded', function() {
    fetchOptions();

    document.getElementById('experimentForm').addEventListener('submit', async function(event) {
        event.preventDefault();

        const experimentData = {
            experiment_id: document.getElementById('experiment_id').value,
            experiment_type: document.getElementById('experiment_type').value,
            gouges: Array.from(document.getElementById('gouges').selectedOptions).map(option => ({ gouge_id: option.value })),
            core_sample_id: document.getElementById('core_sample_id').value,
            blocks: Array.from(document.getElementById('blocks').selectedOptions).map(option => ({ block_id: option.value }))
        };

        try {
            const response = await fetch('/experiments/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(experimentData)
            });

            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }

            const result = await response.json();
            document.getElementById('message').innerText = result.message || 'Experiment created successfully';
        } catch (error) {
            document.getElementById('message').innerText = 'Experiment creation failed: ' + error.message;
        }
    });
});

async function fetchOptions() {
    try {
        const response = await fetch('/experiments/options');
        const options = await response.json();

        populateSelect('gouges', options.gouges);
        populateSelect('core_sample_id', options.core_sample_ids);
        populateSelect('blocks', options.blocks);
    } catch (error) {
        console.error('Error fetching options:', error);
    }
}

function populateSelect(elementId, options) {
    const select = document.getElementById(elementId);
    select.innerHTML = ''; // Clear existing options
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option.id;
        opt.textContent = option.name;
        select.appendChild(opt);
    });
}

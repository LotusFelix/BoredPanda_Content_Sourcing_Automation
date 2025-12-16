// Frontend JavaScript for Index Page

const API_BASE = window.location.origin;

document.getElementById('startBtn').addEventListener('click', async () => {
    // Get selected categories
    const categories = Array.from(document.querySelectorAll('input[name="category"]:checked'))
        .map(cb => cb.value);

    // Get selected sources
    const sources = Array.from(document.querySelectorAll('input[name="source"]:checked'))
        .map(cb => cb.value);

    // Get days
    const days = parseInt(document.getElementById('days').value);

    // Validate
    if (categories.length === 0) {
        alert('Please select at least one category');
        return;
    }

    if (sources.length === 0) {
        alert('Please select at least one source');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('startBtn').disabled = true;
    document.getElementById('statusText').textContent = 'Initializing scraping job...';

    try {
        // Start scraping job
        const response = await fetch(`${API_BASE}/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                categories,
                sources,
                days_back: days
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }

        const data = await response.json();
        const jobId = data.job_id;

        document.getElementById('statusText').textContent = 'Scraping in progress... Polling for results...';

        // Poll for results
        pollResults(jobId);

    } catch (error) {
        alert(`Error: ${error.message}`);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('startBtn').disabled = false;
    }
});

async function pollResults(jobId) {
    const maxAttempts = 60; // 2 minutes max
    let attempts = 0;

    const interval = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${API_BASE}/results/${jobId}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                // Store results and redirect
                sessionStorage.setItem('jobId', jobId);
                sessionStorage.setItem('results', JSON.stringify(data.top_stories));
                window.location.href = '/dashboard';
            } else if (data.status === 'failed') {
                clearInterval(interval);
                alert('Scraping job failed. Please try again.');
                document.getElementById('loading').style.display = 'none';
                document.getElementById('startBtn').disabled = false;
            } else {
                document.getElementById('statusText').textContent =
                    `Scraping in progress... (${attempts}/${maxAttempts})`;
            }

            if (attempts >= maxAttempts) {
                clearInterval(interval);
                alert('Timeout: Job is taking longer than expected. Please check back later.');
                document.getElementById('loading').style.display = 'none';
                document.getElementById('startBtn').disabled = false;
            }

        } catch (error) {
            console.error('Polling error:', error);
        }

    }, 2000); // Poll every 2 seconds
}

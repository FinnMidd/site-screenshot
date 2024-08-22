// static/script.js
document.addEventListener('DOMContentLoaded', (event) => {
    const captureForm = document.getElementById('captureForm');
    const compareButton = document.getElementById('compareButton');
    const resultsDiv = document.getElementById('results');

    captureForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = document.getElementById('urlInput').value;
        
        resultsDiv.innerHTML = 'Capturing screenshots...';
        
        try {
            const response = await fetch('/capture', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}`
            });
            
            const data = await response.json();
            resultsDiv.innerHTML = data.message;
        } catch (error) {
            resultsDiv.innerHTML = 'Error capturing screenshots';
        }
    });

    compareButton.addEventListener('click', async () => {
        resultsDiv.innerHTML = 'Comparing screenshots...';
        
        try {
            const response = await fetch('/compare', {
                method: 'POST'
            });
            
            const data = await response.json();
            if (data.non_matching_files.length > 0) {
                resultsDiv.innerHTML = 'The following files do not match:<br>' + data.non_matching_files.join('<br>');
            } else {
                resultsDiv.innerHTML = 'All screenshots match!';
            }
        } catch (error) {
            resultsDiv.innerHTML = 'Error comparing screenshots';
        }
    });
});
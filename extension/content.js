// Create the island element
const island = document.createElement('div');
island.id = 'upd-island';
island.innerHTML = `
    <div class="upd-icon" id="upd-icon">?</div>
    <div class="upd-text" id="upd-text">Scanning...</div>
`;
document.body.appendChild(island);

let hideTimeout;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "showVerdict") {
        showVerdict(request.verdict, request.confidence);
    }
});

function showVerdict(verdict, confidence) {
    const icon = document.getElementById('upd-icon');
    const text = document.getElementById('upd-text');

    // Reset classes
    island.className = 'visible';
    icon.className = 'upd-icon';

    // Set content based on verdict
    if (verdict === 'benign') {
        island.classList.add('benign');
        icon.classList.add('benign');
        icon.textContent = '✓';
        text.textContent = 'Safe';

        // Auto-hide benign results after 3 seconds
        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
            island.classList.remove('visible');
        }, 3000);

    } else if (verdict === 'suspicious') {
        island.classList.add('suspicious');
        icon.classList.add('suspicious');
        icon.textContent = '!';
        text.textContent = `Suspicious (${Math.round(confidence * 100)}%)`;

        // Keep suspicious results visible longer
        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
            island.classList.remove('visible');
        }, 8000);

    } else if (verdict === 'malicious') {
        island.classList.add('malicious');
        icon.classList.add('malicious');
        icon.textContent = '✕';
        text.textContent = `Malicious Site! (${Math.round(confidence * 100)}%)`;

        // Keep malicious results visible until clicked
        clearTimeout(hideTimeout);
    }
}

// Allow clicking to dismiss
island.addEventListener('click', () => {
    island.classList.remove('visible');
});

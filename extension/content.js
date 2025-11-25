// Create the island element
const island = document.createElement('div');
island.id = 'upd-island';
island.innerHTML = `
    <div id="upd-header">
        <div id="upd-icon" class="upd-icon"></div>
        <span id="upd-text">Scanning...</span>
    </div>
    <div id="upd-details">
        <div class="upd-detail-row">
            <span class="upd-label">Location</span>
            <span id="upd-location">Unknown</span>
        </div>
        <div class="upd-detail-row">
            <span class="upd-label">Domain Age</span>
            <span id="upd-age">Unknown</span>
        </div>
        <div class="upd-detail-row">
            <span class="upd-label">Security</span>
            <span id="upd-security">Unknown</span>
        </div>
    </div>
`;
document.body.appendChild(island);

// Hover events
island.addEventListener('mouseenter', () => {
    island.classList.add('expanded');
});

island.addEventListener('mouseleave', () => {
    island.classList.remove('expanded');
});

let hideTimeout;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "showVerdict") {
        showVerdict(message.verdict, message.confidence, message.additional_info);
    }
});

function showVerdict(verdict, confidence, additionalInfo) {
    const island = document.getElementById('upd-island');
    const icon = document.getElementById('upd-icon');
    const text = document.getElementById('upd-text');

    // Update details
    if (additionalInfo) {
        document.getElementById('upd-location').textContent = additionalInfo.server_location || 'Unknown';

        const age = additionalInfo.domain_age_days;
        document.getElementById('upd-age').textContent = age ? `${age} days` : 'Unknown';

        const https = additionalInfo.is_https ? 'HTTPS' : 'HTTP';
        const dns = additionalInfo.dns_valid ? 'DNS Valid' : 'DNS Unknown';
        document.getElementById('upd-security').textContent = `${https} • ${dns}`;
    }

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

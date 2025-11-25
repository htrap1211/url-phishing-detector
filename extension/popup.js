const API_BASE = 'http://localhost:8000/api/v1';

// Get current tab URL
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0] && tabs[0].url) {
        const url = tabs[0].url;
        if (url.startsWith('http')) {
            document.getElementById('currentUrlSection').style.display = 'block';
            document.getElementById('currentUrl').textContent = url;
            document.getElementById('checkCurrentBtn').onclick = () => checkURL(url);
        }
    }
});

// Manual URL check
document.getElementById('checkBtn').addEventListener('click', () => {
    const url = document.getElementById('urlInput').value.trim();
    if (url) {
        checkURL(url);
    }
});

// Enter key support
document.getElementById('urlInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const url = document.getElementById('urlInput').value.trim();
        if (url) {
            checkURL(url);
        }
    }
});

async function checkURL(url) {
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    document.getElementById('error').style.display = 'none';

    try {
        // Submit URL
        const submitResponse = await fetch(`${API_BASE}/url/check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });

        if (!submitResponse.ok) {
            throw new Error('Failed to submit URL');
        }

        const submitData = await submitResponse.json();
        const checkId = submitData.check_id;

        // Get result
        const resultResponse = await fetch(`${API_BASE}/url/${checkId}`);

        if (!resultResponse.ok) {
            throw new Error('Failed to get result');
        }

        const result = await resultResponse.json();

        // Display result
        displayResult(result);

        // Save to storage
        saveToHistory(result);

    } catch (error) {
        showError(error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function displayResult(result) {
    const resultDiv = document.getElementById('result');
    const verdict = result.verdict.toLowerCase();

    const icon = verdict === 'benign' ? '✓' : verdict === 'malicious' ? '✗' : '⚠';
    const confidence = (result.confidence * 100).toFixed(1);

    let featuresHTML = '';
    if (result.top_features && result.top_features.length > 0) {
        featuresHTML = '<div class="features"><strong>Top Features:</strong>';
        result.top_features.slice(0, 3).forEach(f => {
            featuresHTML += `<div class="feature-item">• ${f.name}: ${f.value.toFixed(2)}</div>`;
        });
        featuresHTML += '</div>';
    }

    let detailsHTML = '';
    if (result.additional_info) {
        const info = result.additional_info;
        const location = info.server_location || 'Unknown';
        const age = info.domain_age_days ? `${info.domain_age_days} days` : 'Unknown';
        const https = info.is_https ? 'HTTPS' : 'HTTP';
        const dns = info.dns_valid ? 'Valid' : 'Unknown';

        detailsHTML = `
        <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3); font-size: 0.9rem;">
            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                <span style="opacity: 0.8;">Location:</span>
                <strong>${location}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                <span style="opacity: 0.8;">Domain Age:</span>
                <strong>${age}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                <span style="opacity: 0.8;">Security:</span>
                <strong>${https} • DNS ${dns}</strong>
            </div>
        </div>`;
    }

    resultDiv.className = `result ${verdict}`;
    resultDiv.innerHTML = `
    <div class="verdict">
      <span>${icon}</span>
      <span>${verdict.toUpperCase()}</span>
    </div>
    <div class="confidence">Confidence: ${confidence}%</div>
    <div style="font-size: 0.85rem;">Model: ${result.model_version}</div>
    ${detailsHTML}
    ${featuresHTML}
  `;
    resultDiv.style.display = 'block';
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.className = 'error';
    errorDiv.textContent = `Error: ${message}. Make sure the backend is running at ${API_BASE}`;
    errorDiv.style.display = 'block';
}

function saveToHistory(result) {
    chrome.storage.local.get(['history'], (data) => {
        const history = data.history || [];
        history.unshift({
            url: result.url,
            verdict: result.verdict,
            confidence: result.confidence,
            timestamp: new Date().toISOString()
        });

        // Keep only last 50
        if (history.length > 50) {
            history.pop();
        }

        chrome.storage.local.set({ history });
    });
}

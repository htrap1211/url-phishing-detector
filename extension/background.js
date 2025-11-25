const API_BASE = 'https://url-phishing-detector-muwd.onrender.com/api/v1';

// Create context menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'checkURL',
        title: 'Check URL for Phishing',
        contexts: ['link', 'page']
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'checkURL') {
        const url = info.linkUrl || info.pageUrl;
        if (url) {
            checkURLInBackground(url, tab.id);
        }
    }
});

async function checkURLInBackground(url, tabId) {
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

        // Show notification
        const verdict = result.verdict.toLowerCase();
        const icon = verdict === 'benign' ? '✓' : verdict === 'malicious' ? '✗' : '⚠';
        const confidence = (result.confidence * 100).toFixed(0);

        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: `${icon} ${verdict.toUpperCase()}`,
            message: `Confidence: ${confidence}%\n${url.substring(0, 100)}`,
            priority: verdict === 'malicious' ? 2 : 1
        });

    } catch (error) {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Check Failed',
            message: 'Could not check URL. Make sure backend is running.'
        });
    }
}

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'checkURL') {
        checkURLInBackground(request.url, sender.tab?.id).then(() => {
            sendResponse({ success: true });
        }).catch((error) => {
            sendResponse({ success: false, error: error.message });
        });
        return true; // Keep channel open for async response
    }
});

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && (tab.url.startsWith('http') || tab.url.startsWith('https'))) {
        scanTab(tabId, tab.url);
    }
});

async function scanTab(tabId, url) {
    try {
        // Submit URL
        const submitResponse = await fetch(`${API_BASE}/url/check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        if (!submitResponse.ok) return;

        const submitData = await submitResponse.json();
        const checkId = submitData.check_id;

        // Get result
        const resultResponse = await fetch(`${API_BASE}/url/${checkId}`);
        if (!resultResponse.ok) return;

        const result = await resultResponse.json();

        // Send verdict to content script
        chrome.tabs.sendMessage(tabId, {
            action: "showVerdict",
            verdict: result.verdict.toLowerCase(),
            confidence: result.confidence
        }).catch(() => {
            // Content script might not be ready or injected yet
        });

    } catch (error) {
        console.error("Scan failed:", error);
    }
}

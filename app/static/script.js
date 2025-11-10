// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Hide error message when switching tabs
        hideError();
    });
});

// Summarize form handler
document.getElementById('summarize-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Check authentication
    if (!window.currentUser || !window.currentUser()) {
        showError('Please login to use this feature');
        // Open auth modal
        const authBtn = document.getElementById('auth-btn');
        if (authBtn) authBtn.click();
        return;
    }
    
    const url = document.getElementById('video-url').value.trim();
    const submitBtn = document.getElementById('summarize-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const resultBox = document.getElementById('summary-result');
    const resultText = document.getElementById('summary-text');
    
    // Validate URL
    if (!isValidYouTubeUrl(url)) {
        showError('Please enter a valid YouTube URL');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    resultBox.style.display = 'none';
    hideError();
    
    try {
        const pureState = document.getElementById('pure-state-summarize').checked;
        const response = await fetch('/url/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ 
                name: url,
                pure_state: { state: pureState }
            })
        });
        
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            if (contentType.includes('application/json')) {
                const errJson = await response.json().catch(() => ({}));
                const detail = errJson && errJson.detail;
                const message = Array.isArray(detail)
                    ? detail.map(d => (d && d.msg) ? d.msg : JSON.stringify(d)).join('; ')
                    : (typeof detail === 'string' ? detail : 'Failed to generate summary');
                throw new Error(message);
            }
            const errText = await response.text().catch(() => 'Failed to generate summary');
            throw new Error(errText || 'Failed to generate summary');
        }

        const text = await response.text();

        // Show result
        resultText.textContent = text;
        resultBox.style.display = 'block';
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        showError(error.message);
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Translate form handler
document.getElementById('translate-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Check authentication
    if (!window.currentUser || !window.currentUser()) {
        showError('Please login to use this feature');
        // Open auth modal
        const authBtn = document.getElementById('auth-btn');
        if (authBtn) authBtn.click();
        return;
    }
    
    const url = document.getElementById('translate-url').value.trim();
    const language = document.getElementById('language').value;
    const submitBtn = document.getElementById('translate-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const resultBox = document.getElementById('translate-result');
    const resultText = document.getElementById('translate-text');
    
    // Validate inputs
    if (!isValidYouTubeUrl(url)) {
        showError('Please enter a valid YouTube URL');
        return;
    }
    
    if (!language) {
        showError('Please select a target language');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    resultBox.style.display = 'none';
    hideError();
    
    try {
        const pureState = document.getElementById('pure-state-translate').checked;
        const response = await fetch('/url/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ 
                name: url,
                language: language,
                pure_state: { state: pureState }
            })
        });
        
        const contentType = response.headers.get('content-type') || '';
        if (!response.ok) {
            if (contentType.includes('application/json')) {
                const errJson = await response.json().catch(() => ({}));
                const detail = errJson && errJson.detail;
                const message = Array.isArray(detail)
                    ? detail.map(d => (d && d.msg) ? d.msg : JSON.stringify(d)).join('; ')
                    : (typeof detail === 'string' ? detail : 'Failed to translate transcript');
                throw new Error(message);
            }
            const errText = await response.text().catch(() => 'Failed to translate transcript');
            throw new Error(errText || 'Failed to translate transcript');
        }

        const translatedText = await response.text();

        // Show result
        resultText.textContent = translatedText;
        resultBox.style.display = 'block';
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        showError(error.message);
    } finally {
        // Reset button state
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Helper function to validate YouTube URL
function isValidYouTubeUrl(url) {
    if (!url || typeof url !== 'string') {
        return false;
    }
    
    // Remove any trailing whitespace and check
    url = url.trim();
    
    // Remove URL fragments and query parameters for validation
    const urlWithoutParams = url.split('?')[0].split('#')[0];
    
    const patterns = [
        // Standard YouTube watch URLs: https://www.youtube.com/watch?v=VIDEO_ID
        // Note: v= parameter is required, so we check the full URL
        /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
        // Short URLs: https://youtu.be/VIDEO_ID
        /^https?:\/\/youtu\.be\/[\w-]+/,
        // YouTube Shorts: https://www.youtube.com/shorts/VIDEO_ID
        /^https?:\/\/(www\.)?youtube\.com\/shorts\/[\w-]+/
    ];
    
    // Check both full URL (for watch URLs with params) and URL without params (for shorts)
    return patterns.some(pattern => pattern.test(url) || pattern.test(urlWithoutParams));
}

// Helper function to show error
function showError(message) {
    const errorBox = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    errorText.textContent = message;
    errorBox.style.display = 'flex';
    errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Helper function to hide error
function hideError() {
    const errorBox = document.getElementById('error-message');
    errorBox.style.display = 'none';
}

// Copy to clipboard function
function copyToClipboard(elementId, buttonElement) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show success feedback
        const originalText = buttonElement.textContent;
        buttonElement.textContent = '✓ Copied!';
        buttonElement.style.background = 'var(--success)';
        buttonElement.style.color = 'white';
        
        setTimeout(() => {
            buttonElement.textContent = originalText;
            buttonElement.style.background = '';
            buttonElement.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        showError('Failed to copy to clipboard');
    });
}


// Auto-fill URL from previous request if available
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/my_url/');
        if (response.ok) {
            const data = await response.json();
            if (data.url) {
                document.getElementById('video-url').value = data.url;
                document.getElementById('translate-url').value = data.url;
            }
        }
    } catch (error) {
        // Silently fail - not critical
        console.log('Could not load previous URL');
    }
});
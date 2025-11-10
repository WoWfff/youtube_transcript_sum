// History page handler
document.addEventListener('DOMContentLoaded', () => {
    const loadHistoryBtn = document.getElementById('load-history-btn');
    if (!loadHistoryBtn) {
        console.error('Load history button not found');
        return;
    }

    loadHistoryBtn.addEventListener('click', async () => {
        const btnText = loadHistoryBtn.querySelector('.btn-text');
        const btnLoader = loadHistoryBtn.querySelector('.btn-loader');
        const historyResult = document.getElementById('history-result');
        const historyVideos = document.getElementById('history-videos');
        const historyEmpty = document.getElementById('history-empty');
        const errorMessage = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');

        if (!btnText || !btnLoader || !historyResult || !historyVideos || !historyEmpty) {
            console.error('History elements not found');
            return;
        }

        // Show loading state
        loadHistoryBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        historyResult.style.display = 'none';
        historyEmpty.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';

        try {
            console.log('Fetching history from /summarizes/api');
            const response = await fetch('/summarizes/api', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            });

            console.log('Response status:', response.status);
            
            // Check if unauthorized
            if (response.status === 401) {
                throw new Error('Please login to view your history');
            }
            
            // Check Content-Type
            const contentType = response.headers.get('Content-Type') || '';
            console.log('Content-Type:', contentType);
            
            // Always read as text first, then parse as JSON if needed
            const responseText = await response.text();
            
            if (!response.ok) {
                if (response.status === 404) {
                    historyEmpty.style.display = 'block';
                    return;
                }

                // Handle error response
                let errorMsg = `Failed to load history (status: ${response.status})`;
                try {
                    if (contentType.includes('application/json')) {
                        const errJson = JSON.parse(responseText);
                        if (errJson && errJson.detail) {
                            errorMsg = typeof errJson.detail === 'string'
                                ? errJson.detail
                                : JSON.stringify(errJson.detail);
                        }
                    } else {
                        errorMsg = responseText || errorMsg;
                    }
                } catch (e) {
                    console.error('Error parsing error response:', e);
                    errorMsg = responseText || errorMsg;
                }

                if (errorMessage && errorText) {
                    errorText.textContent = errorMsg;
                    errorMessage.style.display = 'flex';
                }
                throw new Error(errorMsg);
            }

            // Check if response is JSON
            if (!contentType.includes('application/json')) {
                console.error('Expected JSON but got:', contentType);
                console.error('Response text:', responseText.substring(0, 200));
                throw new Error(`Server returned non-JSON response (${contentType}). Please check the API endpoint.`);
            }

            // Parse JSON
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse JSON:', e);
                console.error('Response text:', responseText.substring(0, 200));
                throw new Error('Failed to parse JSON response');
            }
            
            console.log('Received data:', data);

            // Handle null response (when user has no URLs)
            if (!data || data === null) {
                historyEmpty.style.display = 'block';
                return;
            }

            // Handle empty user_urls
            if (!data.user_urls || Object.keys(data.user_urls).length === 0) {
                historyEmpty.style.display = 'block';
                return;
            }

            // Clear previous results
            historyVideos.innerHTML = '';

            // Sort URLs by created_at (newest first)
            const urlEntries = Object.entries(data.user_urls).sort((a, b) => {
                const dateA = new Date(a[1].created_at);
                const dateB = new Date(b[1].created_at);
                return dateB - dateA;
            });

            // Create video cards
            urlEntries.forEach(([key, urlData]) => {
                const videoCard = createVideoCard(urlData);
                historyVideos.appendChild(videoCard);
            });

            historyResult.style.display = 'block';
            historyResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        } catch (error) {
            console.error('Error loading history:', error);
            if (errorMessage && errorText) {
                errorText.textContent = error.message || 'Failed to load video history';
                errorMessage.style.display = 'flex';
            }
        } finally {
            // Reset button state
            loadHistoryBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
    });

    // Auto-load history on page load
    loadHistoryBtn.click();

    // Clear history button handler
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', async () => {
            // Show confirmation dialog
            const confirmed = confirm(
                'Are you sure you want to delete all your summarizations?\n\n' +
                'This action cannot be undone. All your video summaries will be permanently deleted.'
            );

            if (!confirmed) {
                return;
            }

            const btnText = clearHistoryBtn.querySelector('.btn-text');
            const btnLoader = clearHistoryBtn.querySelector('.btn-loader');
            const errorMessage = document.getElementById('error-message');
            const errorText = document.getElementById('error-text');

            if (!btnText || !btnLoader) {
                console.error('Clear button elements not found');
                return;
            }

            // Show loading state
            clearHistoryBtn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'flex';
            if (errorMessage) errorMessage.style.display = 'none';

            try {
                console.log('Clearing summarizations...');
                const response = await fetch('/summarizes/api', {
                    method: 'DELETE',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                    }
                });

                console.log('Response status:', response.status);

                // Check if unauthorized
                if (response.status === 401) {
                    throw new Error('Please login to clear your history');
                }

                const contentType = response.headers.get('Content-Type') || '';
                console.log('Content-Type:', contentType);

                if (!response.ok) {
                    let errorMsg = `Failed to clear summarizations (status: ${response.status})`;
                    try {
                        if (contentType.includes('application/json')) {
                            const errJson = JSON.parse(await response.text());
                            console.error('Error response:', errJson);
                            if (errJson && errJson.detail) {
                                errorMsg = typeof errJson.detail === 'string'
                                    ? errJson.detail
                                    : JSON.stringify(errJson.detail);
                            }
                        } else {
                            const errText = await response.text();
                            console.error('Error text:', errText);
                            errorMsg = errText || errorMsg;
                        }
                    } catch (e) {
                        console.error('Error parsing response:', e);
                    }

                    if (errorMessage && errorText) {
                        errorText.textContent = errorMsg;
                        errorMessage.style.display = 'flex';
                    }
                    throw new Error(errorMsg);
                }

                // Check if response is JSON
                if (!contentType.includes('application/json')) {
                    const text = await response.text();
                    console.error('Expected JSON but got:', contentType);
                    console.error('Response text:', text.substring(0, 200));
                    throw new Error('Server returned non-JSON response. Please check the API endpoint.');
                }

                // Parse JSON
                let data;
                try {
                    const responseText = await response.text();
                    data = JSON.parse(responseText);
                } catch (e) {
                    console.error('Failed to parse JSON:', e);
                    throw new Error('Failed to parse JSON response');
                }

                console.log('Cleared successfully:', data);

                // Show success message
                if (errorMessage && errorText) {
                    errorText.textContent = 'Summarizations cleared successfully!';
                    errorMessage.style.display = 'flex';
                    errorMessage.className = 'error-box success-box';
                    setTimeout(() => {
                        errorMessage.style.display = 'none';
                        errorMessage.className = 'error-box';
                    }, 3000);
                }

                // Clear the displayed history
                const historyResult = document.getElementById('history-result');
                const historyVideos = document.getElementById('history-videos');
                const historyEmpty = document.getElementById('history-empty');

                if (historyResult) historyResult.style.display = 'none';
                if (historyVideos) historyVideos.innerHTML = '';
                if (historyEmpty) historyEmpty.style.display = 'block';

            } catch (error) {
                console.error('Error clearing history:', error);
                if (errorMessage && errorText) {
                    errorText.textContent = error.message || 'Failed to clear summarizations';
                    errorMessage.style.display = 'flex';
                }
            } finally {
                // Reset button state
                clearHistoryBtn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            }
        });
    }
});

// Helper function to create video card
function createVideoCard(urlData) {
    const card = document.createElement('div');
    card.className = 'video-card';

    const thumbnail = document.createElement('div');
    thumbnail.className = 'video-thumbnail';

    const img = document.createElement('img');
    img.src = urlData.thumbnail_url || 'https://via.placeholder.com/320x180?text=No+Thumbnail';
    img.alt = 'Video thumbnail';
    img.onerror = function() {
        this.src = 'https://via.placeholder.com/320x180?text=No+Thumbnail';
    };

    const overlay = document.createElement('div');
    overlay.className = 'video-overlay';

    thumbnail.appendChild(img);
    thumbnail.appendChild(overlay);

    const info = document.createElement('div');
    info.className = 'video-info';

    const link = document.createElement('a');
    link.href = urlData.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.className = 'video-link';
    link.textContent = urlData.url;
    link.title = urlData.url;

    const date = document.createElement('div');
    date.className = 'video-date';
    const dateObj = new Date(urlData.created_at);
    date.textContent = dateObj.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    info.appendChild(link);
    info.appendChild(date);

    // Add transcript section if transcript exists
    // Note: checking both 'transcript' and 'transcipt' (typo in backend)
    const transcriptText = urlData.transcript || urlData.transcipt;
    if (transcriptText && transcriptText.trim()) {
        const transcriptSection = createTranscriptSection(transcriptText);
        info.appendChild(transcriptSection);
    }

    card.appendChild(thumbnail);
    card.appendChild(info);

    // Make the thumbnail clickable
    thumbnail.style.cursor = 'pointer';
    thumbnail.addEventListener('click', (e) => {
        e.stopPropagation();
        window.open(urlData.url, '_blank');
    });

    link.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    return card;
}

// Helper function to create transcript section with expand/collapse
function createTranscriptSection(transcriptText) {
    const transcriptWrapper = document.createElement('div');
    transcriptWrapper.className = 'video-transcript';

    const transcriptHeader = document.createElement('div');
    transcriptHeader.className = 'transcript-header';

    const headerText = document.createElement('span');
    headerText.textContent = '📄 Transcript';

    const copyBtn = document.createElement('button');
    copyBtn.className = 'transcript-copy-btn';
    copyBtn.title = 'Copy transcript';
    copyBtn.innerHTML = '📋';
    copyBtn.type = 'button';

    copyBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        try {
            await navigator.clipboard.writeText(transcriptText);
            copyBtn.innerHTML = '✓';
            copyBtn.style.color = 'var(--success)';
            setTimeout(() => {
                copyBtn.innerHTML = '📋';
                copyBtn.style.color = '';
            }, 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
            const errorMessage = document.getElementById('error-message');
            const errorText = document.getElementById('error-text');
            if (errorMessage && errorText) {
                errorText.textContent = 'Failed to copy transcript to clipboard';
                errorMessage.style.display = 'flex';
            }
        }
    });

    transcriptHeader.appendChild(headerText);
    transcriptHeader.appendChild(copyBtn);

    const transcriptContent = document.createElement('div');
    transcriptContent.className = 'transcript-content';

    const transcriptPreview = document.createElement('div');
    transcriptPreview.className = 'transcript-preview';

    const transcriptFull = document.createElement('div');
    transcriptFull.className = 'transcript-full';
    transcriptFull.style.display = 'none';
    transcriptFull.textContent = transcriptText;

    // Set preview text (first 300 characters)
    const previewLength = 300;
    const previewText = transcriptText.length > previewLength
        ? transcriptText.substring(0, previewLength) + '...'
        : transcriptText;
    transcriptPreview.textContent = previewText;

    const expandBtn = document.createElement('button');
    expandBtn.className = 'transcript-toggle-btn';
    expandBtn.textContent = transcriptText.length > previewLength ? 'Show more' : '';
    expandBtn.type = 'button';

    // Toggle functionality
    expandBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isExpanded = transcriptFull.style.display !== 'none';

        if (isExpanded) {
            // Collapse
            transcriptFull.style.display = 'none';
            transcriptPreview.style.display = 'block';
            expandBtn.textContent = 'Show more';
            transcriptWrapper.classList.remove('expanded');
        } else {
            // Expand
            transcriptPreview.style.display = 'none';
            transcriptFull.style.display = 'block';
            expandBtn.textContent = 'Show less';
            transcriptWrapper.classList.add('expanded');
        }
    });

    // Hide expand button if text is short
    if (transcriptText.length <= previewLength) {
        expandBtn.style.display = 'none';
    }

    transcriptContent.appendChild(transcriptPreview);
    transcriptContent.appendChild(transcriptFull);

    transcriptWrapper.appendChild(transcriptHeader);
    transcriptWrapper.appendChild(transcriptContent);
    transcriptWrapper.appendChild(expandBtn);

    return transcriptWrapper;
}


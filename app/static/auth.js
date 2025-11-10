// Authentication logic

let currentUser = null;

// Check authentication status on page load
async function checkAuthStatus() {
    try {
        const response = await fetch('/auth/me', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const user = await response.json();
            currentUser = user;
            updateAuthUI(user);
            return true;
        } else {
            currentUser = null;
            updateAuthUI(null);
            return false;
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        currentUser = null;
        updateAuthUI(null);
        return false;
    }
}

// Update UI based on auth status
function updateAuthUI(user) {
    const authBtn = document.getElementById('auth-btn');
    const userInfo = document.getElementById('user-info');
    const usernameDisplay = document.getElementById('username-display');

    if (user) {
        authBtn.style.display = 'none';
        userInfo.style.display = 'flex';
        usernameDisplay.textContent = `👤 ${user.username}`;
    } else {
        authBtn.style.display = 'inline-block';
        userInfo.style.display = 'none';
    }
}

// Modal management
const authModal = document.getElementById('auth-modal');
const authBtn = document.getElementById('auth-btn');
const closeModal = document.getElementById('close-modal');
const authTabs = document.querySelectorAll('.auth-tab-btn');
const authForms = document.querySelectorAll('.auth-form');

// Open modal
authBtn?.addEventListener('click', () => {
    authModal.style.display = 'flex';
    switchAuthTab('login');
});

// Close modal
closeModal?.addEventListener('click', () => {
    authModal.style.display = 'none';
    hideAuthError();
});

// Close modal on outside click
authModal?.addEventListener('click', (e) => {
    if (e.target === authModal) {
        authModal.style.display = 'none';
        hideAuthError();
    }
});

// Switch between login and register tabs
authTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.authTab;
        switchAuthTab(tabName);
    });
});

function switchAuthTab(tabName) {
    // Update tab buttons
    authTabs.forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-auth-tab="${tabName}"]`).classList.add('active');

    // Update forms
    authForms.forEach(f => f.classList.remove('active'));
    document.getElementById(`${tabName}-form`).classList.add('active');

    // Update modal title
    const modalTitle = document.getElementById('modal-title');
    modalTitle.textContent = tabName === 'login' ? 'Login' : 'Register';

    // Clear forms and errors
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    hideAuthError();
}

// Login form handler
const loginForm = document.getElementById('login-form');
loginForm?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const submitBtn = document.getElementById('login-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    if (!username || !password) {
        showAuthError('Please fill in all fields');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    hideAuthError();

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            currentUser = data;
            updateAuthUI(data);
            authModal.style.display = 'none';
            loginForm.reset();
            showSuccess('Login successful!');
        } else {
            showAuthError(data.detail || 'Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAuthError('An error occurred during login. Please try again.');
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Register form handler
const registerForm = document.getElementById('register-form');
registerForm?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;
    const submitBtn = document.getElementById('register-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');

    if (!username || !password || !passwordConfirm) {
        showAuthError('Please fill in all fields');
        return;
    }

    if (password !== passwordConfirm) {
        showAuthError('Passwords do not match');
        return;
    }

    if (password.length < 6) {
        showAuthError('Password must be at least 6 characters long');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    hideAuthError();

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Auto-login after registration
            const loginResponse = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            if (loginResponse.ok) {
                const userData = await loginResponse.json();
                currentUser = userData;
                updateAuthUI(userData);
                authModal.style.display = 'none';
                registerForm.reset();
                showSuccess('Registration successful! You are now logged in.');
            } else {
                showAuthError('Registration successful, but auto-login failed. Please login manually.');
            }
        } else {
            showAuthError(data.detail || 'Registration failed. Username may already be taken.');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAuthError('An error occurred during registration. Please try again.');
    } finally {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
});

// Logout handler
const logoutBtn = document.getElementById('logout-btn');
logoutBtn?.addEventListener('click', async () => {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            currentUser = null;
            updateAuthUI(null);
            showSuccess('Logged out successfully');
        } else {
            showAuthError('Logout failed. Please try again.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        showAuthError('An error occurred during logout. Please try again.');
    }
});

// Show/hide auth error
function showAuthError(message) {
    const errorBox = document.getElementById('auth-error');
    const errorText = document.getElementById('auth-error-text');
    errorText.textContent = message;
    errorBox.style.display = 'flex';
}

function hideAuthError() {
    const errorBox = document.getElementById('auth-error');
    errorBox.style.display = 'none';
}

// Show success message (simple alert for now)
function showSuccess(message) {
    // You can replace this with a better notification system
    const successBox = document.createElement('div');
    successBox.className = 'success-box';
    successBox.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 2000;
        animation: slideIn 0.3s ease;
    `;
    successBox.textContent = message;
    document.body.appendChild(successBox);

    setTimeout(() => {
        successBox.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => successBox.remove(), 300);
    }, 3000);
}

// Check auth status when page loads
document.addEventListener('DOMContentLoaded', () => {
    checkAuthStatus();
});

// Export for use in other scripts
window.checkAuthStatus = checkAuthStatus;
window.currentUser = () => currentUser;


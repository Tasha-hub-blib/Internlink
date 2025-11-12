// ==================== GLOBAL VARIABLES ====================
// Store the current logged-in user data
let currentUser = null;

// Store user's profile data
let userProfile = null;

// Store user's applications
let userApplications = [];

// API base URL - change this to your Flask server URL
const API_URL = 'http://localhost:5000';

// ==================== INITIALIZATION ====================
// This runs when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in (stored in browser session)
    checkLoginStatus();
});

// ==================== AUTHENTICATION FUNCTIONS ====================

/**
 * Check if user is already logged in by checking sessionStorage
 */
function checkLoginStatus() {
    const storedUser = sessionStorage.getItem('currentUser');
    
    if (storedUser) {
        // User is logged in
        currentUser = JSON.parse(storedUser);
        showMainApp();
        loadUserData();
    } else {
        // User is not logged in - show login form
        showLoginForm();
    }
}

/**
 * Show/hide different auth forms (login or signup)
 */
function showAuthForm(formType) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    
    if (formType === 'login') {
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        signupForm.classList.remove('hidden');
    }
    
    // Clear any error messages
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('signup-error').classList.add('hidden');
}

/**
 * Handle user login
 */
async function loginUser(event) {
    event.preventDefault(); // Prevent form from submitting normally
    
    // Get form values
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        // Send login request to backend
        const response = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Login successful
            currentUser = data.user;
            
            // Store user in session storage (persists until browser is closed)
            sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            // Show main application
            showMainApp();
            loadUserData();
            
        } else {
            // Login failed - show error message
            errorDiv.textContent = data.message || 'Login failed. Please try again.';
            errorDiv.classList.remove('hidden');
        }
        
    } catch (error) {
        // Network or server error
        console.error('Login error:', error);
        errorDiv.textContent = 'Unable to connect to server. Please try again later.';
        errorDiv.classList.remove('hidden');
    }
}

/**
 * Handle user signup/registration
 */
async function signupUser(event) {
    event.preventDefault(); // Prevent form from submitting normally
    
    // Get form values
    const firstName = document.getElementById('signup-firstname').value;
    const lastName = document.getElementById('signup-lastname').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;
    const errorDiv = document.getElementById('signup-error');
    
    // Validate passwords match
    if (password !== confirmPassword) {
        errorDiv.textContent = 'Passwords do not match!';
        errorDiv.classList.remove('hidden');
        return;
    }
    
    // Validate password length
    if (password.length < 8) {
        errorDiv.textContent = 'Password must be at least 8 characters long!';
        errorDiv.classList.remove('hidden');
        return;
    }
    
    try {
        // Send signup request to backend
        const response = await fetch(`${API_URL}/api/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Signup successful
            currentUser = data.user;
            
            // Store user in session storage
            sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            // Show main application
            showMainApp();
            loadUserData();
            
        } else {
            // Signup failed - show error message
            errorDiv.textContent = data.message || 'Signup failed. Please try again.';
            errorDiv.classList.remove('hidden');
        }
        
    } catch (error) {
        // Network or server error
        console.error('Signup error:', error);
        errorDiv.textContent = 'Unable to connect to server. Please try again later.';
        errorDiv.classList.remove('hidden');
    }
}

/**
 * Handle user logout
 */
function logout() {
    // Clear user data
    currentUser = null;
    userProfile = null;
    userApplications = [];
    
    // Clear session storage
    sessionStorage.removeItem('currentUser');
    
    // Show login form
    showLoginForm();
    
    // Reset forms
    document.getElementById('login-form').reset();
    document.getElementById('signup-form').reset();
}

// ==================== UI DISPLAY FUNCTIONS ====================

/**
 * Show the login container and hide the main app
 */
function showLoginForm() {
    document.getElementById('login-container').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
}

/**
 * Show the main app and hide the login container
 */
function showMainApp() {
    document.getElementById('login-container').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
    
    // Update username in navigation
    if (currentUser) {
        document.getElementById('nav-username').textContent = 
            `${currentUser.first_name} ${currentUser.last_name}`;
        document.getElementById('welcome-user-name').textContent = 
            `Welcome back, ${currentUser.first_name}!`;
    }
    
    // Show home section by default
    showSection('home');
}

/**
 * Show specific section and hide others
 */
function showSection(sectionName) {
    // Get all sections
    const sections = document.querySelectorAll('main section');
    
    // Hide all sections
    sections.forEach(section => {
        section.classList.add('hidden');
    });
    
    // Show the requested section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.remove('hidden');
    }
    
    // Load section-specific data
    if (sectionName === 'profile') {
        displayProfile();
    } else if (sectionName === 'applications') {
        displayApplications();
    }
}

// ==================== DATA LOADING FUNCTIONS ====================

/**
 * Load user's profile and applications from backend
 */
async function loadUserData() {
    if (!currentUser) return;
    
    try {
        // Load user profile
        const profileResponse = await fetch(`${API_URL}/api/profile/${currentUser.id}`);
        if (profileResponse.ok) {
            userProfile = await profileResponse.json();
            
            // Pre-fill registration form with profile data
            if (userProfile) {
                document.getElementById('firstName').value = currentUser.first_name;
                document.getElementById('lastName').value = currentUser.last_name;
                document.getElementById('email').value = currentUser.email;
                document.getElementById('phone').value = userProfile.phone || '';
                document.getElementById('university').value = userProfile.university || '';
                document.getElementById('course').value = userProfile.course || '';
                document.getElementById('year').value = userProfile.year || '';
                document.getElementById('gpa').value = userProfile.gpa || '';
                document.getElementById('skills').value = userProfile.skills || '';
                document.getElementById('interests').value = userProfile.interests || '';
            }
        }
        
        // Load user applications
        const appsResponse = await fetch(`${API_URL}/api/applications/${currentUser.id}`);
        if (appsResponse.ok) {
            userApplications = await appsResponse.json();
        }
        
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

/**
 * Handle profile registration/update
 */
async function registerStudent(event) {
    event.preventDefault(); // Prevent form from submitting normally
    
    // Get form values
    const profileData = {
        user_id: currentUser.id,
        phone: document.getElementById('phone').value,
        university: document.getElementById('university').value,
        course: document.getElementById('course').value,
        year: document.getElementById('year').value,
        gpa: document.getElementById('gpa').value,
        skills: document.getElementById('skills').value,
        interests: document.getElementById('interests').value
    };
    
    try {
        // Send profile data to backend
        const response = await fetch(`${API_URL}/api/profile`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(profileData)
        });
        
        if (response.ok) {
            userProfile = await response.json();
            alert('Profile saved successfully!');
            showSection('profile');
        } else {
            const data = await response.json();
            alert(data.message || 'Failed to save profile. Please try again.');
        }
        
    } catch (error) {
        console.error('Error saving profile:', error);
        alert('Unable to connect to server. Please try again later.');
    }
}

/**
 * Handle internship application
 */
async function applyInternship(position, company) {
    if (!currentUser) {
        alert('Please login to apply for internships');
        return;
    }
    
    // Check if profile is complete
    if (!userProfile || !userProfile.university) {
        alert('Please complete your profile before applying for internships');
        showSection('register');
        return;
    }
    
    // Check if already applied
    const alreadyApplied = userApplications.some(
        app => app.position === position && app.company === company
    );
    
    if (alreadyApplied) {
        alert('You have already applied for this internship!');
        return;
    }
    
    try {
        // Send application to backend
        const response = await fetch(`${API_URL}/api/apply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: currentUser.id,
                position: position,
                company: company
            })
        });
        
        if (response.ok) {
            const newApplication = await response.json();
            userApplications.push(newApplication);
            alert('Application submitted successfully!');
            showSection('applications');
        } else {
            const data = await response.json();
            alert(data.message || 'Failed to submit application. Please try again.');
        }
        
    } catch (error) {
        console.error('Error submitting application:', error);
        alert('Unable to connect to server. Please try again later.');
    }
}

// ==================== DISPLAY FUNCTIONS ====================

/**
 * Display user profile
 */
function displayProfile() {
    const profileDisplay = document.getElementById('profile-display');
    
    if (!userProfile || !userProfile.university) {
        profileDisplay.innerHTML = `
            <p style="text-align: center; color: #999; padding: 2rem;">
                Please complete your profile to view information.
            </p>
        `;
        return;
    }
    
    profileDisplay.innerHTML = `
        <h3>Personal Information</h3>
        <p><strong>Name:</strong> ${currentUser.first_name} ${currentUser.last_name}</p>
        <p><strong>Email:</strong> ${currentUser.email}</p>
        <p><strong>Phone:</strong> ${userProfile.phone}</p>
        
        <h3 style="margin-top: 2rem;">Academic Information</h3>
        <p><strong>University:</strong> ${userProfile.university}</p>
        <p><strong>Course:</strong> ${userProfile.course}</p>
        <p><strong>Year of Study:</strong> Year ${userProfile.year}</p>
        <p><strong>GPA:</strong> ${userProfile.gpa}</p>
        
        <h3 style="margin-top: 2rem;">Skills & Interests</h3>
        <p><strong>Skills:</strong> ${userProfile.skills}</p>
        <p><strong>Interests:</strong> ${userProfile.interests}</p>
    `;
}

/**
 * Display user applications
 */
function displayApplications() {
    const tbody = document.getElementById('applications-tbody');
    
    if (userApplications.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 2rem; color: #999;">
                    No applications yet. Start applying to internships!
                </td>
            </tr>
        `;
        return;
    }
    
    // Build table rows for each application
    tbody.innerHTML = userApplications.map(app => `
        <tr>
            <td>${app.position}</td>
            <td>${app.company}</td>
            <td>${new Date(app.date_applied).toLocaleDateString()}</td>
            <td>
                <span class="status-${app.status.toLowerCase()}">
                    ${app.status}
                </span>
            </td>
        </tr>
    `).join('');
}
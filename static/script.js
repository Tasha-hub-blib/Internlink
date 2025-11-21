let currentUser = null;
let userProfile = null;
let userApplications = [];
let resetStep = 1; 
let resetEmail = '';
let resetCode = '';

const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : window.location.origin; 

document.addEventListener('DOMContentLoaded', function() {
    checkLoginStatus();
});

// Mobile Menu Toggle Function - Updated to work properly
function setupMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger && navLinks) {
        // Remove any existing event listeners by cloning
        const newHamburger = hamburger.cloneNode(true);
        hamburger.parentNode.replaceChild(newHamburger, hamburger);
        
        // Add click event to hamburger
        newHamburger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.toggle('active');
            navLinks.classList.toggle('active');
            console.log('Menu toggled'); // Debug log
        });
        
        // Close menu when clicking on a link
        const navItems = navLinks.querySelectorAll('a');
        navItems.forEach(link => {
            link.addEventListener('click', () => {
                newHamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!newHamburger.contains(e.target) && !navLinks.contains(e.target)) {
                newHamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }
}

function checkLoginStatus() {
    const storedUser = sessionStorage.getItem('currentUser');
    
    if (storedUser) {
        currentUser = JSON.parse(storedUser);
        showMainApp();
        loadUserData();
    } else {
        showLoginForm();
    }
}

function showAuthForm(formType) {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const forgotForm = document.getElementById('forgot-password-form');
    
    loginForm.classList.add('hidden');
    signupForm.classList.add('hidden');
    if (forgotForm) forgotForm.classList.add('hidden');
    
    if (formType === 'login') {
        loginForm.classList.remove('hidden');
    } else if (formType === 'signup') {
        signupForm.classList.remove('hidden');
    } else if (formType === 'forgot') {
        forgotForm.classList.remove('hidden');
        resetPasswordForm(); 
    }
    
    document.getElementById('login-error').classList.add('hidden');
    document.getElementById('signup-error').classList.add('hidden');
    if (document.getElementById('forgot-error')) {
        document.getElementById('forgot-error').classList.add('hidden');
    }
    if (document.getElementById('forgot-success')) {
        document.getElementById('forgot-success').classList.add('hidden');
    }
}

function showForgotPassword() {
    showAuthForm('forgot');
    return false;
}

function resetPasswordForm() {
    resetStep = 1;
    resetEmail = '';
    resetCode = '';
    
    document.getElementById('reset-code-group').classList.add('hidden');
    document.getElementById('new-password-group').classList.add('hidden');
    document.getElementById('confirm-new-password-group').classList.add('hidden');
    
    document.getElementById('reset-email').value = '';
    document.getElementById('reset-code').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('confirm-new-password').value = '';
    
    document.getElementById('reset-submit-btn').textContent = 'Send Reset Code';
    
    document.getElementById('forgot-error').classList.add('hidden');
    document.getElementById('forgot-success').classList.add('hidden');
}

async function resetPassword(event) {
    event.preventDefault();
    
    const errorDiv = document.getElementById('forgot-error');
    const successDiv = document.getElementById('forgot-success');
    
    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');
    
    try {
        if (resetStep === 1) {
            resetEmail = document.getElementById('reset-email').value;
            
            const response = await fetch(`${API_URL}/api/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: resetEmail })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                successDiv.textContent = data.message || 'Reset code sent! Check your email.';
                successDiv.classList.remove('hidden');
                
                resetStep = 2;
                resetCode = data.reset_code; 
                
                document.getElementById('reset-code-group').classList.remove('hidden');
                document.getElementById('reset-email').readOnly = true;
                document.getElementById('reset-submit-btn').textContent = 'Verify Code';
                
            } else {
                errorDiv.textContent = data.message || 'Failed to send reset code. Please try again.';
                errorDiv.classList.remove('hidden');
            }
            
        } else if (resetStep === 2) {
            const enteredCode = document.getElementById('reset-code').value;
            
            const response = await fetch(`${API_URL}/api/verify-reset-code`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email: resetEmail,
                    code: enteredCode 
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                successDiv.textContent = 'Code verified! Enter your new password.';
                successDiv.classList.remove('hidden');
                
                resetStep = 3;
                
                document.getElementById('new-password-group').classList.remove('hidden');
                document.getElementById('confirm-new-password-group').classList.remove('hidden');
                document.getElementById('reset-code').readOnly = true;
                document.getElementById('reset-submit-btn').textContent = 'Reset Password';
                
            } else {
                errorDiv.textContent = data.message || 'Invalid code. Please try again.';
                errorDiv.classList.remove('hidden');
            }
            
        } else if (resetStep === 3) {
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-new-password').value;
            
            if (newPassword !== confirmPassword) {
                errorDiv.textContent = 'Passwords do not match!';
                errorDiv.classList.remove('hidden');
                return;
            }
            
            if (newPassword.length < 8) {
                errorDiv.textContent = 'Password must be at least 8 characters!';
                errorDiv.classList.remove('hidden');
                return;
            }
            
            const response = await fetch(`${API_URL}/api/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email: resetEmail,
                    code: document.getElementById('reset-code').value,
                    new_password: newPassword 
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                successDiv.textContent = 'Password reset successful! Redirecting to login...';
                successDiv.classList.remove('hidden');
                
                setTimeout(() => {
                    showAuthForm('login');
                }, 2000);
                
            } else {
                errorDiv.textContent = data.message || 'Failed to reset password. Please try again.';
                errorDiv.classList.remove('hidden');
            }
        }
        
    } catch (error) {
        console.error('Reset password error:', error);
        errorDiv.textContent = 'Unable to connect to server. Please try again later.';
        errorDiv.classList.remove('hidden');
    }
}

async function loginUser(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
            showMainApp();
            loadUserData();
        } else {
            errorDiv.textContent = data.message || 'Login failed. Please try again.';
            errorDiv.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'Unable to connect to server. Please try again later.';
        errorDiv.classList.remove('hidden');
    }
}

async function signupUser(event) {
    event.preventDefault();
    
    const firstName = document.getElementById('signup-firstname').value;
    const lastName = document.getElementById('signup-lastname').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;
    const errorDiv = document.getElementById('signup-error');
    
    if (password !== confirmPassword) {
        errorDiv.textContent = 'Passwords do not match!';
        errorDiv.classList.remove('hidden');
        return;
    }
    
    if (password.length < 8) {
        errorDiv.textContent = 'Password must be at least 8 characters long!';
        errorDiv.classList.remove('hidden');
        return;
    }
    
    try {
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
            currentUser = data.user;
            sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
            showMainApp();
            loadUserData();
        } else {
            errorDiv.textContent = data.message || 'Signup failed. Please try again.';
            errorDiv.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Signup error:', error);
        errorDiv.textContent = 'Unable to connect to server. Please try again later.';
        errorDiv.classList.remove('hidden');
    }
}

function logout() {
    currentUser = null;
    userProfile = null;
    userApplications = [];
    sessionStorage.removeItem('currentUser');
    showLoginForm();
    document.getElementById('login-form').reset();
    document.getElementById('signup-form').reset();
}

function showLoginForm() {
    document.getElementById('login-container').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
}

function showMainApp() {
    document.getElementById('login-container').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
    
    if (currentUser) {
        document.getElementById('nav-username').textContent = 
            `${currentUser.first_name} ${currentUser.last_name}`;
        document.getElementById('welcome-user-name').textContent = 
            `Welcome back, ${currentUser.first_name}!`;
    }
    
    showSection('home');
    
    // Initialize mobile menu after a short delay to ensure DOM is ready
    setTimeout(() => {
        setupMobileMenu();
    }, 100);
}

function showSection(sectionName) {
    const sections = document.querySelectorAll('main section');
    sections.forEach(section => {
        section.classList.add('hidden');
    });
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.remove('hidden');
    }
    
    if (sectionName === 'profile') {
        displayProfile();
    } else if (sectionName === 'applications') {
        displayApplications();
    }
}

async function loadUserData() {
    if (!currentUser) return;
    
    try {
        const profileResponse = await fetch(`${API_URL}/api/profile/${currentUser.id}`);
        if (profileResponse.ok) {
            userProfile = await profileResponse.json();
            
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
        
        const appsResponse = await fetch(`${API_URL}/api/applications/${currentUser.id}`);
        if (appsResponse.ok) {
            userApplications = await appsResponse.json();
        }
        
    } catch (error) {
        console.error('Error loading user data:', error);
    }
}

async function registerStudent(event) {
    event.preventDefault();
    
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

async function applyInternship(position, company) {
    if (!currentUser) {
        alert('Please login to apply for internships');
        return;
    }
    
    if (!userProfile || !userProfile.university) {
        alert('Please complete your profile before applying for internships');
        showSection('register');
        return;
    }
    
    const alreadyApplied = userApplications.some(
        app => app.position === position && app.company === company
    );
    
    if (alreadyApplied) {
        alert('You have already applied for this internship!');
        return;
    }
    
    try {
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
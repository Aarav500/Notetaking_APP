/**
 * Ideater - AI-Powered IDEATION ENGINE
 * Main JavaScript File
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize Mermaid diagrams
    initMermaid();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Setup dark mode toggle
    setupDarkMode();
    
    // Add animation classes to elements
    animateElements();
    
    // Setup module-specific functionality
    setupModules();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Mermaid diagrams
 */
function initMermaid() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {
                curve: 'basis'
            }
        });
    }
}

/**
 * Setup form handlers
 */
function setupFormHandlers() {
    // Project creation form
    const projectForm = document.getElementById('project-form');
    if (projectForm) {
        projectForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(projectForm);
            const projectData = {
                title: formData.get('title'),
                description: formData.get('description'),
                original_idea: formData.get('original_idea')
            };
            
            // Send project data to the API
            fetch('/api/projects/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify(projectData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to create project');
                }
                return response.json();
            })
            .then(data => {
                // Redirect to the project page
                window.location.href = `/projects/${data.id}`;
            })
            .catch(error => {
                showAlert('error', error.message);
            });
        });
    }
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            const loginData = {
                username: formData.get('username'),
                password: formData.get('password')
            };
            
            // Send login data to the API
            fetch('/api/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    username: loginData.username,
                    password: loginData.password
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Invalid username or password');
                }
                return response.json();
            })
            .then(data => {
                // Save the token to localStorage
                localStorage.setItem('token', data.access_token);
                
                // Redirect to the dashboard
                window.location.href = '/projects';
            })
            .catch(error => {
                showAlert('error', error.message);
            });
        });
    }
    
    // Registration form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(registerForm);
            const registerData = {
                username: formData.get('username'),
                email: formData.get('email'),
                password: formData.get('password')
            };
            
            // Send registration data to the API
            fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registerData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Registration failed');
                }
                return response.json();
            })
            .then(data => {
                // Show success message
                showAlert('success', 'Registration successful! Please log in.');
                
                // Redirect to login page
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            })
            .catch(error => {
                showAlert('error', error.message);
            });
        });
    }
}

/**
 * Setup dark mode toggle
 */
function setupDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        // Check if user has a preference
        const darkMode = localStorage.getItem('darkMode') === 'true';
        
        // Set initial state
        if (darkMode) {
            document.body.classList.add('dark-mode');
            darkModeToggle.checked = true;
        }
        
        // Toggle dark mode on change
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('darkMode', 'true');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('darkMode', 'false');
            }
        });
    }
}

/**
 * Add animation classes to elements
 */
function animateElements() {
    // Add fade-in class to hero section
    const heroSection = document.querySelector('.row.align-items-center.mb-5');
    if (heroSection) {
        heroSection.classList.add('fade-in');
    }
    
    // Add slide-in-up class to feature cards with delay
    const featureCards = document.querySelectorAll('.card');
    if (featureCards.length > 0) {
        featureCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('slide-in-up');
            }, index * 100);
        });
    }
}

/**
 * Setup module-specific functionality
 */
function setupModules() {
    // Idea Expander module
    setupIdeaExpander();
    
    // Architecture Bot module
    setupArchitectureBot();
    
    // Flowchart View module
    setupFlowchartView();
    
    // Code Breakdown module
    setupCodeBreakdown();
    
    // MVP Generator module
    setupMVPGenerator();
    
    // Test Plan Generator module
    setupTestPlanGenerator();
    
    // Roadmap Assistant module
    setupRoadmapAssistant();
    
    // Whiteboard Collaboration module
    setupWhiteboardCollaboration();
}

/**
 * Setup Idea Expander module
 */
function setupIdeaExpander() {
    const ideaForm = document.getElementById('idea-expander-form');
    if (ideaForm) {
        ideaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(ideaForm);
            const ideaData = {
                project_id: formData.get('project_id'),
                module_type: 'idea_expander',
                data: {
                    original_idea: formData.get('original_idea')
                }
            };
            
            // Show loading state
            const submitButton = ideaForm.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            submitButton.disabled = true;
            
            // Send data to the API
            fetch('/api/modules/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${getToken()}`
                },
                body: JSON.stringify(ideaData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to create module');
                }
                return response.json();
            })
            .then(data => {
                // Process the module
                return fetch(`/api/modules/${data.id}/process`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${getToken()}`
                    },
                    body: JSON.stringify({})
                });
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to process module');
                }
                return response.json();
            })
            .then(data => {
                // Redirect to the module page
                window.location.href = `/modules/idea-expander/${data.id}`;
            })
            .catch(error => {
                showAlert('error', error.message);
                
                // Reset button
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
            });
        });
    }
}

/**
 * Setup Architecture Bot module
 */
function setupArchitectureBot() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Setup Flowchart View module
 */
function setupFlowchartView() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Setup Code Breakdown module
 */
function setupCodeBreakdown() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Setup MVP Generator module
 */
function setupMVPGenerator() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Setup Test Plan Generator module
 */
function setupTestPlanGenerator() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Setup Roadmap Assistant module
 */
function setupRoadmapAssistant() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Setup Whiteboard Collaboration module
 */
function setupWhiteboardCollaboration() {
    // Similar implementation to Idea Expander
    // This is a placeholder for the actual implementation
}

/**
 * Get the authentication token from localStorage
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Show an alert message
 */
function showAlert(type, message) {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to the page
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        alertContainer.appendChild(alertElement);
    } else {
        // If no container exists, create one at the top of the main content
        const mainContent = document.querySelector('main');
        if (mainContent) {
            const container = document.createElement('div');
            container.id = 'alert-container';
            container.appendChild(alertElement);
            mainContent.insertBefore(container, mainContent.firstChild);
        }
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertElement.remove();
    }, 5000);
}
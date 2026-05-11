/**
 * Bank Management System - Main JavaScript File
 * Handles client-side interactions and validations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Format currency inputs
    const amountInputs = document.querySelectorAll('input[name="amount"]');
    amountInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            let value = parseFloat(this.value);
            if (!isNaN(value) && value > 0) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span>Processing...</span>';
                
                // Re-enable after 5 seconds (in case of error)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 5000);
            }
        });
    });

    // Save original button text
    document.querySelectorAll('button[type="submit"]').forEach(function(btn) {
        btn.setAttribute('data-original-text', btn.innerHTML);
    });

    // Password strength indicator (registration form)
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthIndicator(strength);
        });
    }

    // Confirm password validation
    const confirmPassword = document.getElementById('confirm_password');
    if (confirmPassword && passwordInput) {
        confirmPassword.addEventListener('input', function() {
            if (this.value !== passwordInput.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }

    // Phone number formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
        });
    }

    // Account number formatting
    const accountNumberInput = document.getElementById('to_account_number');
    if (accountNumberInput) {
        accountNumberInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
        });
    }
});

/**
 * Calculate password strength
 * @param {string} password - The password to check
 * @returns {string} - 'weak', 'medium', or 'strong'
 */
function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    if (score <= 2) return 'weak';
    if (score <= 4) return 'medium';
    return 'strong';
}

/**
 * Update password strength indicator UI
 * @param {string} strength - 'weak', 'medium', or 'strong'
 */
function updatePasswordStrengthIndicator(strength) {
    let indicator = document.getElementById('password-strength');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'password-strength';
        indicator.style.marginTop = '0.5rem';
        indicator.style.fontSize = '0.75rem';
        const passwordGroup = document.getElementById('password').parentElement;
        passwordGroup.appendChild(indicator);
    }
    
    const colors = {
        weak: '#ef4444',
        medium: '#f59e0b',
        strong: '#22c55e'
    };
    
    const labels = {
        weak: 'Weak password',
        medium: 'Medium strength',
        strong: 'Strong password'
    };
    
    indicator.textContent = labels[strength];
    indicator.style.color = colors[strength];
}

/**
 * Format number as Indian currency
 * @param {number} amount - The amount to format
 * @returns {string} - Formatted string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(amount);
}

/**
 * Confirm dangerous actions
 * @param {string} message - Confirmation message
 * @returns {boolean} - User's choice
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

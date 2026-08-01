// Main JavaScript for The Egerton Advertiser

document.addEventListener('DOMContentLoaded', function() {
    // Initialize date display
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    // Initialize notifications
    initializeNotifications();
    
    // Initialize scroll to top button
    initializeScrollTop();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize popovers
    initializePopovers();
    
    // Initialize auto-dismiss alerts
    initializeAlerts();
});

// Update date and time
function updateDateTime() {
    const now = new Date();
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    };
    
    const dateElements = document.querySelectorAll('.current-date');
    dateElements.forEach(el => {
        el.textContent = now.toLocaleDateString('en-US', options);
    });
}

// Notifications
function initializeNotifications() {
    const notificationDropdown = document.getElementById('notificationDropdown');
    if (notificationDropdown) {
        notificationDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            loadNotifications();
        });
    }
}

function loadNotifications() {
    const container = document.getElementById('notificationList');
    if (!container) return;
    
    fetch('/notifications/api/recent/')
        .then(response => response.json())
        .then(data => {
            let html = '<li class="dropdown-header">Notifications</li><li><hr class="dropdown-divider"></li>';
            
            if (data.notifications && data.notifications.length > 0) {
                data.notifications.forEach(notification => {
                    const unreadClass = notification.is_read ? '' : 'bg-light';
                    html += `
                        <li class="notification-item ${unreadClass}">
                            <a href="/notifications/${notification.id}/" class="dropdown-item">
                                <div class="notification-title">${notification.title}</div>
                                <div class="notification-message">${notification.message}</div>
                                <div class="notification-time">${notification.created_at}</div>
                            </a>
                        </li>
                    `;
                });
                
                html += '<li><hr class="dropdown-divider"></li>';
                html += '<li class="text-center"><a href="/notifications/" class="dropdown-item">View All Notifications</a></li>';
            } else {
                html += '<li class="text-center py-3">No notifications</li>';
            }
            
            container.innerHTML = html;
            
            // Update badge
            const badge = document.getElementById('notificationBadge');
            if (badge) {
                badge.textContent = data.unread_count || 0;
                if (data.unread_count > 0) {
                    badge.style.display = 'inline';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => {
            console.error('Error loading notifications:', error);
        });
}

// Scroll to top button
function initializeScrollTop() {
    const button = document.createElement('button');
    button.className = 'scroll-top';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(button);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            button.style.display = 'block';
        } else {
            button.style.display = 'none';
        }
    });
    
    button.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Tooltips
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

// Popovers
function initializePopovers() {
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => {
        new bootstrap.Popover(popover);
    });
}

// Auto-dismiss alerts
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
}

// Search form
function initializeSearch() {
    const searchForms = document.querySelectorAll('form[action*="search"]');
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = this.querySelector('input[type="search"]');
            if (input && input.value.trim().length < 2) {
                e.preventDefault();
                showAlert('Please enter at least 2 characters to search.', 'warning');
            }
        });
    });
}

// Show alert
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Handle AJAX form submissions
function initializeAjaxForms() {
    const forms = document.querySelectorAll('[data-ajax="true"]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = this.action || window.location.href;
            const method = this.method || 'POST';
            const formData = new FormData(this);
            
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message || 'Success!', 'success');
                    if (data.redirect) {
                        setTimeout(() => window.location.href = data.redirect, 1000);
                    }
                } else {
                    showAlert(data.error || 'An error occurred.', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred. Please try again.', 'danger');
            });
        });
    });
}

// Infinite scroll for article lists
function initializeInfiniteScroll() {
    const container = document.getElementById('infinite-scroll-container');
    if (!container) return;
    
    let page = 1;
    let loading = false;
    let hasMore = true;
    
    const loadMore = function() {
        if (loading || !hasMore) return;
        
        loading = true;
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'block';
        
        page++;
        const url = new URL(window.location.href);
        url.searchParams.set('page', page);
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newContent = doc.getElementById('infinite-scroll-container');
            
            if (newContent) {
                container.innerHTML += newContent.innerHTML;
            }
            
            const nextPage = doc.querySelector('[data-page]');
            if (nextPage && nextPage.dataset.page) {
                hasMore = true;
            } else {
                hasMore = false;
            }
            
            loading = false;
            if (loader) loader.style.display = 'none';
        })
        .catch(error => {
            console.error('Error loading more content:', error);
            loading = false;
            if (loader) loader.style.display = 'none';
        });
    };
    
    // Intersection Observer
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadMore();
            }
        });
    });
    
    const sentinel = document.getElementById('scroll-sentinel');
    if (sentinel) {
        observer.observe(sentinel);
    }
}

// Initialize all
document.addEventListener('DOMContentLoaded', function() {
    initializeSearch();
    initializeAjaxForms();
    initializeInfiniteScroll();
});
// JavaScript for JFS 2025 Bewertungsapp

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Rating form handling
    const ratingForm = document.getElementById('rating-form');
    if (ratingForm) {
        const ratingInputs = ratingForm.querySelectorAll('.rating-input');
        ratingInputs.forEach(input => {
            input.addEventListener('change', function() {
                ratingForm.submit();
            });
        });
    }
    
    // Filter form handling
    const topicFilter = document.getElementById('topic-filter');
    if (topicFilter) {
        topicFilter.addEventListener('change', function() {
            document.getElementById('filter-form').submit();
        });
    }
});

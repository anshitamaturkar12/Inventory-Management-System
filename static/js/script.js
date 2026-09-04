// ==========================================================================
// Inventory Management System - Client-side Interactive Scripts
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {
    // 1. Live Date in Topbar
    const liveDateEl = document.getElementById('liveDate');
    if (liveDateEl) {
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        liveDateEl.textContent = new Date().toLocaleDateString('en-US', options);
    }

    // 2. Mobile Sidebar Toggle
    const sidebar = document.getElementById('sidebar');
    const openSidebarBtn = document.getElementById('openSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');

    if (openSidebarBtn && sidebar) {
        openSidebarBtn.addEventListener('click', function () {
            sidebar.classList.add('open');
        });
    }

    if (closeSidebarBtn && sidebar) {
        closeSidebarBtn.addEventListener('click', function () {
            sidebar.classList.remove('open');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (e) {
        if (sidebar && sidebar.classList.contains('open')) {
            if (!sidebar.contains(e.target) && e.target !== openSidebarBtn) {
                sidebar.classList.remove('open');
            }
        }
    });

    // 3. Auto-dismiss Flash Alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 6000);
    });

    // 4. Client-side input guard: Prevent negative values on number fields
    const numberInputs = document.querySelectorAll('input[type="number"][min="0"]');
    numberInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            if (parseFloat(this.value) < 0) {
                this.value = 0;
            }
        });
    });
});

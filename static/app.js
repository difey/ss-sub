document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(sec => sec.classList.remove('active'));

            item.classList.add('active');
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Toast Notification System
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }

    // --- Subscriptions Section ---
    const subsList = document.getElementById('subs-list');
    const addSubForm = document.getElementById('add-sub-form');
    const btnRefresh = document.getElementById('btn-refresh');
    const btnDownload = document.getElementById('btn-download');

    async function fetchSubscriptions() {
        try {
            const res = await fetch('/subscription/list');
            if (!res.ok) throw new Error('Failed to fetch subscriptions');
            const data = await res.json();
            renderSubscriptions(data);
        } catch (e) {
            showToast(e.message, 'error');
            subsList.innerHTML = '<div class="empty-state">Failed to load subscriptions.</div>';
        }
    }

    function renderSubscriptions(subs) {
        if (subs.length === 0) {
            subsList.innerHTML = '<div class="empty-state">No subscriptions added yet.</div>';
            return;
        }

        subsList.innerHTML = '';
        subs.forEach(sub => {
            const div = document.createElement('div');
            div.className = 'sub-item';
            div.innerHTML = `
                <div class="sub-info">
                    <div class="sub-name">${escapeHtml(sub.name) || 'Unnamed Subscription'}</div>
                    <div class="sub-url" title="${escapeHtml(sub.url)}">${escapeHtml(sub.url)}</div>
                </div>
                <div class="sub-actions">
                    <button class="btn btn-danger btn-delete" data-id="${escapeHtml(sub.id)}">Delete</button>
                </div>
            `;
            subsList.appendChild(div);
        });

        // Attach delete events
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-id');
                try {
                    const res = await fetch(`/subscription/${id}`, { method: 'DELETE' });
                    if (!res.ok) throw new Error('Failed to delete');
                    showToast('Subscription deleted', 'success');
                    fetchSubscriptions();
                } catch (err) {
                    showToast(err.message, 'error');
                }
            });
        });
    }

    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    addSubForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const urlInput = document.getElementById('sub-url');
        const nameInput = document.getElementById('sub-name');

        const payload = {
            url: urlInput.value,
            name: nameInput.value || null
        };

        try {
            const res = await fetch('/subscription/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Failed to add subscription');
            }

            showToast('Subscription added successfully', 'success');
            urlInput.value = '';
            nameInput.value = '';
            fetchSubscriptions();
        } catch (err) {
            showToast(err.message, 'error');
        }
    });

    btnRefresh.addEventListener('click', async () => {
        btnRefresh.disabled = true;
        btnRefresh.textContent = 'Refreshing...';
        try {
            const res = await fetch('/subscription/refresh', { method: 'POST' });
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Merge failed');
            }
            showToast('Refresh & Merge successful', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnRefresh.disabled = false;
            btnRefresh.textContent = 'Refresh & Merge';
        }
    });

    btnDownload.addEventListener('click', () => {
        window.location.href = '/subscription/result';
    });

    // --- Rules Section ---
    const rulesInput = document.getElementById('rules-input');
    const btnSaveRules = document.getElementById('btn-save-rules');

    async function fetchRules() {
        try {
            const res = await fetch('/rules/');
            if (!res.ok) throw new Error('Failed to fetch rules');
            const data = await res.json();
            rulesInput.value = data.rules || '';
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    btnSaveRules.addEventListener('click', async () => {
        btnSaveRules.disabled = true;
        btnSaveRules.textContent = 'Saving...';
        try {
            const res = await fetch('/rules/update', {
                method: 'POST',
                headers: { 'Content-Type': 'text/plain' },
                body: rulesInput.value
            });
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Failed to save rules');
            }
            showToast('Custom rules saved successfully', 'success');
        } catch (err) {
            showToast(err.message, 'error');
        } finally {
            btnSaveRules.disabled = false;
            btnSaveRules.textContent = 'Save Rules';
        }
    });

    // Initial fetch
    fetchSubscriptions();
    fetchRules();
});

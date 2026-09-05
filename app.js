/* ==========================================================================
   FRANCABEL ENTERPRISE - INTERACTIVE APP LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFilterTabs();
});

/* Mobile Menu Toggle */
function initNavigation() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-open');
        });
    }
}

/* Service Category Filter Tabs */
function initFilterTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const cards = document.querySelectorAll('.service-card');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');

            cards.forEach(card => {
                if (filter === 'all') {
                    card.style.display = 'flex';
                } else {
                    const category = card.getAttribute('data-category');
                    if (category === filter) {
                        card.style.display = 'flex';
                    } else {
                        card.style.display = 'none';
                    }
                }
            });
        });
    });
}

/* Modal Open / Close Logic */
function openModal(serviceName) {
    const modal = document.getElementById('inquiryModal');
    const select = document.getElementById('serviceType');
    const title = document.getElementById('modalTitle');

    if (select && serviceName) {
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].value === serviceName) {
                select.selectedIndex = i;
                break;
            }
        }
    }

    if (title && serviceName) {
        title.innerText = `Inquiry: ${serviceName}`;
    }

    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal() {
    const modal = document.getElementById('inquiryModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

/* Close modal when clicking outside card */
window.addEventListener('click', (e) => {
    const modal = document.getElementById('inquiryModal');
    if (e.target === modal) {
        closeModal();
    }
});

/* Direct Form Submission -> mailto dispatch */
function handleFormSubmit(event) {
    event.preventDefault();

    const service = document.getElementById('serviceType').value;
    const name = document.getElementById('clientName').value;
    const email = document.getElementById('clientEmail').value;
    const details = document.getElementById('clientDetails').value;

    const subject = encodeURIComponent(`Francabel Service Request: ${service}`);
    const body = encodeURIComponent(
        `Name/Organization: ${name}\n` +
        `Client Email: ${email}\n` +
        `Service Requested: ${service}\n\n` +
        `Details / Scope:\n${details}\n`
    );

    const mailtoUrl = `mailto:eduardo@francabel.com?subject=${subject}&body=${body}`;
    window.location.href = mailtoUrl;

    closeModal();
    showToast('Dispatching inquiry to eduardo@francabel.com...');
}

/* Copy Email to Clipboard */
function copyEmail() {
    const emailStr = 'eduardo@francabel.com';
    navigator.clipboard.writeText(emailStr).then(() => {
        showToast('Copied eduardo@francabel.com to clipboard!');
    }).catch(() => {
        showToast('Email: eduardo@francabel.com');
    });
}

/* Toast Message */
function showToast(msg) {
    const toast = document.getElementById('toast');
    if (toast) {
        toast.innerText = msg;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

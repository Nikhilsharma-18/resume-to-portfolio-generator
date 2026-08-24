/* =========================================================
   PORTFOLIO INTERACTIVE JAVASCRIPT & EXPORT HANDLERS
========================================================= */

// Toggle Download Dropdown Menu
function toggleDownloadMenu(event, btn) {
    if (event) {
        event.stopPropagation();
    }
    const dropdown = btn ? btn.closest('.download-dropdown') : document.querySelector('.download-dropdown');
    if (!dropdown) return;
    
    const menu = dropdown.querySelector('.download-menu');
    if (!menu) return;
    
    const isOpen = menu.classList.contains('show');
    
    // Close all open menus first
    document.querySelectorAll('.download-menu').forEach(m => m.classList.remove('show'));
    
    if (!isOpen) {
        menu.classList.add('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.download-dropdown')) {
        document.querySelectorAll('.download-menu').forEach(m => m.classList.remove('show'));
    }
});

// Show Toast Notification
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container no-print';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-info');
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 20);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Generate sanitized filename
function getSafeFilename(ext) {
    const rawName = (document.querySelector('.logo-name') || document.querySelector('.hero h1') || { textContent: 'my' }).textContent.trim();
    const safeName = rawName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'my';
    return `${safeName}-portfolio.${ext}`;
}

// Share Portfolio
async function sharePortfolio(btn) {
    const shareUrl = window.location.href;
    const rawName = (document.querySelector('.hero h1') || { textContent: 'Developer' }).textContent.trim();
    const title = `${rawName} — Portfolio`;
    const text = `Check out ${rawName}'s professional portfolio!`;

    const shareData = {
        title: title,
        text: text,
        url: shareUrl
    };

    if (navigator.share) {
        try {
            if (btn) btn.classList.add('loading');
            await navigator.share(shareData);
        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error('Web Share error:', err);
                fallbackCopyUrl(shareUrl);
            }
        } finally {
            if (btn) btn.classList.remove('loading');
        }
    } else {
        fallbackCopyUrl(shareUrl);
    }
}

// Copy URL fallback for desktop/unsupported browsers
function fallbackCopyUrl(url) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url)
            .then(() => {
                showToast('Portfolio link copied!');
            })
            .catch(() => {
                execCopyFallback(url);
            });
    } else {
        execCopyFallback(url);
    }
}

function execCopyFallback(text) {
    const input = document.createElement('input');
    input.value = text;
    document.body.appendChild(input);
    input.select();
    try {
        document.execCommand('copy');
        showToast('Portfolio link copied!');
    } catch (err) {
        showToast('Could not copy link automatically.', 'error');
    }
    document.body.removeChild(input);
}

// Download Standalone HTML (Embedded CSS + JS)
function downloadHTML(btn) {
    const filename = getSafeFilename('html');
    const portfolioId = window.PORTFOLIO_ID || (document.body.dataset.portfolioId || "");

    if (portfolioId) {
        const a = document.createElement('a');
        a.href = `/portfolio/${portfolioId}/export/html`;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast('Downloading standalone portfolio HTML...');
        return;
    }

    // Client-side fallback if portfolio_id is missing
    try {
        const clone = document.documentElement.cloneNode(true);
        clone.querySelectorAll('.no-print, .action-toolbar, #toast-container').forEach(el => el.remove());
        const htmlStr = "<!DOCTYPE html>\n" + clone.outerHTML;
        const blob = new Blob([htmlStr], { type: 'text/html;charset=utf-8' });
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
        showToast('Portfolio HTML downloaded!');
    } catch (err) {
        console.error('HTML Download error:', err);
        showToast('Failed to download HTML portfolio.', 'error');
    }
}

// Download Complete Web Package (ZIP Archive containing index.html, style.css, script.js)
function downloadZip(btn) {
    const filename = getSafeFilename('zip');
    const portfolioId = window.PORTFOLIO_ID || (document.body.dataset.portfolioId || "");

    if (portfolioId) {
        const a = document.createElement('a');
        a.href = `/portfolio/${portfolioId}/export/zip`;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast('Downloading complete portfolio ZIP package...');
        return;
    }

    // Fallback: Download HTML if zip route is unlinked
    downloadHTML(btn);
}

// Download PDF
async function downloadPDF(btn) {
    const targetBtn = btn || document.querySelector('.btn-download');
    if (targetBtn && (targetBtn.classList.contains('loading') || targetBtn.disabled)) return;
    
    if (targetBtn) {
        targetBtn.classList.add('loading');
        targetBtn.disabled = true;
    }

    showToast('Generating PDF portfolio...', 'info');

    const filename = getSafeFilename('pdf');
    const element = document.body;

    const hiddenEls = document.querySelectorAll('.no-print, .action-toolbar, .toast-container');
    hiddenEls.forEach(el => el.style.setProperty('display', 'none', 'important'));

    const opt = {
        margin:       [8, 8, 8, 8],
        filename:     filename,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false, scrollY: 0 },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
        if (window.html2pdf) {
            await html2pdf().set(opt).from(element).save();
            showToast('PDF downloaded successfully!');
        } else {
            window.print();
        }
    } catch (err) {
        console.error('PDF Generation error:', err);
        showToast('Opening print dialog...', 'info');
        window.print();
    } finally {
        hiddenEls.forEach(el => el.style.removeProperty('display'));
        if (targetBtn) {
            targetBtn.classList.remove('loading');
            targetBtn.disabled = false;
        }
    }
}

// Smooth scrolling and Active Navbar Highlight
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-links a[href^="#"]');
    const sections = document.querySelectorAll('section[id], header[id]');

    function highlightNav() {
        let scrollY = window.pageYOffset;
        sections.forEach(current => {
            const sectionHeight = current.offsetHeight;
            const sectionTop = current.offsetTop - 100;
            const sectionId = current.getAttribute('id');
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', highlightNav);
});

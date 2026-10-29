/**
 * EstateEase - Main Client Interactivity Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // 2. Scroll Reveal Animations (respects reduced motion)
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!prefersReducedMotion) {
        const revealElements = document.querySelectorAll('.reveal-fade-up');
        if (revealElements.length > 0) {
            const revealObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach((entry, index) => {
                    if (entry.isIntersecting) {
                        // Stagger effect
                        setTimeout(() => {
                            entry.target.classList.add('is-revealed');
                        }, (index % 4) * 80);
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.12,
                rootMargin: '0px 0px -40px 0px'
            });

            revealElements.forEach(el => revealObserver.observe(el));
        }
    } else {
        document.querySelectorAll('.reveal-fade-up').forEach(el => el.classList.add('is-revealed'));
    }

    // 3. Animated Number Counters
    const counterElements = document.querySelectorAll('[data-counter-target]');
    if (counterElements.length > 0 && !prefersReducedMotion) {
        const counterObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseFloat(entry.target.getAttribute('data-counter-target'));
                    const prefix = entry.target.getAttribute('data-counter-prefix') || '';
                    const suffix = entry.target.getAttribute('data-counter-suffix') || '';
                    const isDecimal = target % 1 !== 0;
                    const duration = 1200;
                    const steps = 40;
                    const increment = target / steps;
                    let current = 0;

                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        const formatted = isDecimal ? current.toFixed(1) : Math.floor(current).toLocaleString();
                        entry.target.textContent = `${prefix}${formatted}${suffix}`;
                    }, duration / steps);

                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        counterElements.forEach(el => counterObserver.observe(el));
    }

    // 4. Mobile Menu Navigation Drawer Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            const isExpanded = mobileMenuBtn.getAttribute('aria-expanded') === 'true';
            mobileMenuBtn.setAttribute('aria-expanded', !isExpanded);
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 5. Interactive Mortgage Calculator
    const homePriceInput = document.getElementById('calc-home-price');
    const downPaymentPct = document.getElementById('calc-down-payment');
    const interestRateInput = document.getElementById('calc-interest-rate');
    const loanTermSelect = document.getElementById('calc-loan-term');
    const calcResultOutput = document.getElementById('calc-monthly-payment');

    function updateMortgageCalculation() {
        if (!homePriceInput || !downPaymentPct || !interestRateInput || !loanTermSelect || !calcResultOutput) return;

        const price = parseFloat(homePriceInput.value) || 0;
        const downPct = parseFloat(downPaymentPct.value) || 20;
        const rate = (parseFloat(interestRateInput.value) || 6.5) / 100 / 12;
        const years = parseInt(loanTermSelect.value) || 30;
        const totalMonths = years * 12;

        const loanPrincipal = price * (1 - downPct / 100);

        let monthlyPayment = 0;
        if (loanPrincipal > 0 && rate > 0) {
            monthlyPayment = loanPrincipal * (rate * Math.pow(1 + rate, totalMonths)) / (Math.pow(1 + rate, totalMonths) - 1);
        }

        // Add approximate taxes and insurance (1.2% property tax + 0.5% home insurance annually)
        const monthlyTaxesAndInsurance = (price * 0.015) / 12;
        const totalEstimatedMonthly = Math.round(monthlyPayment + monthlyTaxesAndInsurance);

        calcResultOutput.textContent = `$${totalEstimatedMonthly.toLocaleString()}`;

        // Also update sub-breakdown if labels exist
        const principalInterestEl = document.getElementById('calc-principal-interest');
        const taxEl = document.getElementById('calc-tax-insurance');
        if (principalInterestEl) principalInterestEl.textContent = `$${Math.round(monthlyPayment).toLocaleString()}`;
        if (taxEl) taxEl.textContent = `$${Math.round(monthlyTaxesAndInsurance).toLocaleString()}`;
    }

    if (homePriceInput) {
        [homePriceInput, downPaymentPct, interestRateInput, loanTermSelect].forEach(input => {
            if (input) input.addEventListener('input', updateMortgageCalculation);
        });
        updateMortgageCalculation();
    }

    // 6. Favorites Toggle via AJAX
    document.querySelectorAll('.favorite-toggle-btn').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            const propertyId = button.getAttribute('data-property-id');
            if (!propertyId) return;

            try {
                const response = await fetch(`/properties/${propertyId}/favorite`, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });

                if (response.status === 401 || response.redirected) {
                    window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }

                const data = await response.json();
                if (data.status === 'added') {
                    button.classList.add('text-rose-500', 'fill-rose-500');
                    button.classList.remove('text-slate-400');
                    showToast(data.message, 'success');
                } else {
                    button.classList.remove('text-rose-500', 'fill-rose-500');
                    button.classList.add('text-slate-400');
                    showToast(data.message, 'info');
                }
            } catch (err) {
                console.error(err);
                showToast('Unable to update saved property. Please log in.', 'error');
            }
        });
    });

    // 7. Interactive Inquiry Form Submission via AJAX
    const inquiryForm = document.getElementById('property-inquiry-form');
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = inquiryForm.querySelector('button[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : 'Send Inquiry';
            
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="inline-block animate-spin mr-2">⟳</span> Sending...`;
            }

            const formData = new FormData(inquiryForm);
            const propertyId = inquiryForm.getAttribute('data-property-id');

            try {
                const response = await fetch(`/api/properties/${propertyId}/inquiry`, {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();

                if (result.success) {
                    showToast(result.message, 'success');
                    inquiryForm.reset();
                    // Close modal if inside a modal
                    const modal = inquiryForm.closest('.inquiry-modal-container');
                    if (modal) modal.classList.add('hidden');
                } else {
                    showToast(result.message || 'Submission error. Please verify fields.', 'error');
                }
            } catch (err) {
                showToast('Failed to deliver inquiry. Please try again.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            }
        });
    }

    // 8. Image Gallery Lightbox Modal
    const galleryThumbs = document.querySelectorAll('.gallery-thumb-trigger');
    const mainGalleryImage = document.getElementById('main-gallery-image');
    if (mainGalleryImage && galleryThumbs.length > 0) {
        galleryThumbs.forEach(thumb => {
            thumb.addEventListener('click', () => {
                const newSrc = thumb.getAttribute('data-image-src');
                if (newSrc) {
                    mainGalleryImage.style.opacity = '0.5';
                    setTimeout(() => {
                        mainGalleryImage.src = newSrc;
                        mainGalleryImage.style.opacity = '1';
                    }, 150);
                    galleryThumbs.forEach(t => t.classList.remove('ring-2', 'ring-gold'));
                    thumb.classList.add('ring-2', 'ring-gold');
                }
            });
        });
    }

    // 9. Multi-Image File Input Live Preview
    const imageInput = document.getElementById('property-images-input');
    const previewContainer = document.getElementById('image-preview-grid');
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', () => {
            previewContainer.innerHTML = '';
            const files = Array.from(imageInput.files);
            if (files.length === 0) return;

            files.forEach((file, index) => {
                if (!file.type.startsWith('image/')) return;
                const reader = new FileReader();
                reader.onload = (e) => {
                    const card = document.createElement('div');
                    card.className = 'relative group rounded-xl overflow-hidden shadow-sm border border-slate-200 aspect-[4/3] bg-slate-100';
                    card.innerHTML = `
                        <img src="${e.target.result}" alt="Preview ${index + 1}" class="w-full h-full object-cover">
                        <span class="absolute bottom-2 left-2 bg-slate-900/80 text-white text-[10px] px-2 py-0.5 rounded-full backdrop-blur-sm">
                            ${index === 0 ? 'Primary' : `Image ${index + 1}`}
                        </span>
                    `;
                    previewContainer.appendChild(card);
                };
                reader.readAsDataURL(file);
            });
        });
    }
});

// Toast notification helper
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgClasses = {
        success: 'bg-emerald-950 border-emerald-600 text-emerald-100',
        error: 'bg-rose-950 border-rose-600 text-rose-100',
        warning: 'bg-amber-950 border-amber-600 text-amber-100',
        info: 'bg-slate-900 border-slate-700 text-slate-100'
    }[type] || 'bg-slate-900 border-slate-700 text-slate-100';

    const iconSvg = {
        success: '<svg class="w-5 h-5 text-emerald-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>',
        error: '<svg class="w-5 h-5 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>',
        warning: '<svg class="w-5 h-5 text-amber-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>',
        info: '<svg class="w-5 h-5 text-blue-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
    }[type] || '';

    toast.className = `toast flex items-start gap-3 p-4 rounded-xl border shadow-xl backdrop-blur-md ${bgClasses}`;
    toast.innerHTML = `
        ${iconSvg}
        <div class="text-sm font-medium flex-1">${message}</div>
        <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
    `;

    container.appendChild(toast);
    setTimeout(() => toast.classList.add('toast-show'), 10);

    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => toast.remove(), 350);
    }, 4500);
}

// Confirmation modal trigger for destructive operations (delete property)
function confirmDeleteModal(deleteFormId, propertyTitle) {
    const existing = document.getElementById('confirmation-modal-backdrop');
    if (existing) existing.remove();

    const backdrop = document.createElement('div');
    backdrop.id = 'confirmation-modal-backdrop';
    backdrop.className = 'fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm';
    backdrop.innerHTML = `
        <div class="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 transform transition-all animate-in fade-in zoom-in duration-200">
            <div class="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mb-4">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
            </div>
            <h3 class="text-lg font-bold text-slate-900">Delete Property Listing?</h3>
            <p class="text-sm text-slate-600 mt-2">Are you sure you want to delete <span class="font-semibold text-slate-800">"${propertyTitle}"</span>? This action cannot be undone and will permanently remove all associated photos.</p>
            <div class="mt-6 flex items-center justify-end gap-3">
                <button type="button" onclick="document.getElementById('confirmation-modal-backdrop').remove()" class="px-4 py-2.5 rounded-lg border border-slate-300 text-slate-700 font-medium hover:bg-slate-50 transition text-sm">
                    Cancel
                </button>
                <button type="button" onclick="document.getElementById('${deleteFormId}').submit()" class="px-5 py-2.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-medium transition text-sm shadow-md shadow-rose-600/20">
                    Confirm Delete
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(backdrop);
}


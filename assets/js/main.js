/**
 * PCW CONTRACTING SERVICES - MAIN SCRIPT
 * Handles navigation, mobile drawer accordions, FAQ toggles,
 * capabilities filtering, and preserved webhook estimate submission.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Lucide Icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }

  // 2. Sticky Header Scroll Effect
  const header = document.querySelector('.site-header');
  if (header) {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  // 3. Mobile Navigation Drawer & Accordions
  const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const mobileCloseBtn = document.querySelector('.mobile-close-btn');

  function openMobileNav() {
    if (!mobileDrawer) return;
    mobileDrawer.classList.add('is-open');
    mobileDrawer.setAttribute('aria-hidden', 'false');
    if (mobileNavToggle) mobileNavToggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  function closeMobileNav() {
    if (!mobileDrawer) return;
    mobileDrawer.classList.remove('is-open');
    mobileDrawer.setAttribute('aria-hidden', 'true');
    if (mobileNavToggle) mobileNavToggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  if (mobileNavToggle) {
    mobileNavToggle.addEventListener('click', openMobileNav);
  }
  if (mobileCloseBtn) {
    mobileCloseBtn.addEventListener('click', closeMobileNav);
  }
  if (mobileDrawer) {
    mobileDrawer.addEventListener('click', (e) => {
      if (e.target === mobileDrawer) closeMobileNav();
    });
  }

  // Keyboard trap & Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (mobileDrawer && mobileDrawer.classList.contains('is-open')) {
        closeMobileNav();
      } else {
        const activeDropdown = document.activeElement ? document.activeElement.closest('.nav-item') : null;
        if (activeDropdown) {
          const trigger = activeDropdown.querySelector('.nav-link[aria-haspopup="true"]');
          if (trigger) {
            trigger.setAttribute('aria-expanded', 'false');
            trigger.focus();
          }
        }
      }
    }
  });

  // Desktop Dropdown Keyboard Accessibility & ARIA sync
  const navItems = document.querySelectorAll('.desktop-nav .nav-item');
  navItems.forEach((item) => {
    const trigger = item.querySelector('.nav-link[aria-haspopup="true"]');
    if (trigger) {
      item.addEventListener('focusin', () => {
        trigger.setAttribute('aria-expanded', 'true');
      });
      item.addEventListener('focusout', (e) => {
        if (!item.contains(e.relatedTarget)) {
          trigger.setAttribute('aria-expanded', 'false');
        }
      });
      item.addEventListener('mouseenter', () => {
        trigger.setAttribute('aria-expanded', 'true');
      });
      item.addEventListener('mouseleave', () => {
        if (!item.contains(document.activeElement)) {
          trigger.setAttribute('aria-expanded', 'false');
        }
      });
    }
  });

  // Mobile Accordion toggles
  const accordionToggles = document.querySelectorAll('.mobile-accordion-toggle');
  accordionToggles.forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      const targetId = toggle.getAttribute('aria-controls');
      const targetContent = document.getElementById(targetId);

      toggle.setAttribute('aria-expanded', !isExpanded);
      if (targetContent) {
        targetContent.classList.toggle('is-open', !isExpanded);
      }
      const icon = toggle.querySelector('i');
      if (icon) {
        icon.style.transform = !isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
      }
    });
  });

  // 4. Safe FAQ Accordions
  const faqQuestions = document.querySelectorAll('.faq-question');
  faqQuestions.forEach((btn) => {
    btn.addEventListener('click', () => {
      const parentItem = btn.closest('.faq-item');
      if (!parentItem) return;
      const isActive = parentItem.classList.contains('is-active');

      // Close sibling items in the same FAQ block
      const siblingItems = parentItem.parentElement.querySelectorAll('.faq-item');
      siblingItems.forEach((item) => item.classList.remove('is-active'));

      if (!isActive) {
        parentItem.classList.add('is-active');
      }
    });
  });

  // 5. Work Gallery Filtering Tabs
  const filterBtns = document.querySelectorAll('.gallery-filter-btn');
  const workCards = document.querySelectorAll('.work-card');

  if (filterBtns.length > 0 && workCards.length > 0) {
    filterBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        filterBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        const filterVal = btn.getAttribute('data-filter');
        workCards.forEach((card) => {
          const category = card.getAttribute('data-category');
          if (filterVal === 'all' || category === filterVal) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  // 6. Pre-select service from URL query parameter on Contact Form
  const urlParams = new URLSearchParams(window.location.search);
  const serviceParam = urlParams.get('service');
  if (serviceParam) {
    const serviceSelect = document.getElementById('contact-service');
    if (serviceSelect) {
      for (let i = 0; i < serviceSelect.options.length; i++) {
        if (serviceSelect.options[i].value.toLowerCase() === serviceParam.toLowerCase() ||
            serviceSelect.options[i].text.toLowerCase() === serviceParam.toLowerCase()) {
          serviceSelect.selectedIndex = i;
          break;
        }
      }
    }
  }
});

/**
 * EXACT PRESERVED WEBHOOK SUBMISSION HANDLER
 * Target: https://161-97-173-78.sslip.io/webhook/pcw-estimate-request
 * Payload Keys: name, email, phone, service, message, source_url
 */
async function handleFormSubmit(event) {
  event.preventDefault();

  const form = document.getElementById('pcw-contact-form');
  if (!form) return;

  const submitButton = form.querySelector('button[type="submit"]');
  const originalButtonHtml = submitButton ? submitButton.innerHTML : 'Submit Estimate Request';

  const payload = {
    name: document.getElementById('contact-name').value.trim(),
    email: document.getElementById('contact-email').value.trim(),
    phone: document.getElementById('contact-phone').value.trim(),
    service: document.getElementById('contact-service').value,
    message: document.getElementById('contact-message').value.trim(),
    source_url: window.location.href
  };

  if (submitButton) {
    submitButton.disabled = true;
    submitButton.setAttribute('aria-busy', 'true');
    submitButton.innerHTML = 'Submitting Request...';
  }

  try {
    const response = await fetch('https://161-97-173-78.sslip.io/webhook/pcw-estimate-request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Estimate request failed with status ${response.status}`);
    }

    form.reset();
    const toast = document.getElementById('success-toast');
    if (toast) {
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 6000);
    } else {
      window.alert('Thank you! Your estimate request has been received. A PCW technical estimator will follow up with you within 24 business hours.');
    }
  } catch (error) {
    console.error('PCW estimate request error:', error);
    window.alert('We could not submit your request right now. Please call PCW Contracting Services directly at (949) 548-9969.');
  } finally {
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.removeAttribute('aria-busy');
      submitButton.innerHTML = originalButtonHtml;
      if (typeof lucide !== 'undefined') lucide.createIcons();
    }
  }
}


/**
 * OptiCrop — Global JavaScript Utilities
 */
(function () {
  'use strict';

  const OptiCrop = {
    /**
     * Initialize all global behaviors on DOM ready
     */
    init() {
      this.initNavbarScroll();
      this.initFlashAutoDismiss();
      this.initScrollAnimations();
      this.initActiveNavLink();
      this.initTooltips();
    },

    /**
     * Navbar background on scroll
     */
    initNavbarScroll() {
      const nav = document.querySelector('.opticrop-nav');
      if (!nav) return;

      const onScroll = () => {
        nav.classList.toggle('scrolled', window.scrollY > 40);
      };

      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    },

    /**
     * Auto-dismiss flash messages after 5 seconds
     */
    initFlashAutoDismiss() {
      document.querySelectorAll('.flash-container .alert').forEach((alert) => {
        setTimeout(() => {
          const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
          bsAlert.close();
        }, 5000);
      });
    },

    /**
     * Intersection Observer for custom scroll animations
     */
    initScrollAnimations() {
      const animated = document.querySelectorAll('.fade-up, .fade-in, .scale-in, .slide-left, .slide-right');
      if (!animated.length) return;

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible');
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
      );

      animated.forEach((el) => observer.observe(el));
    },

    /**
     * Highlight active nav link based on current path
     */
    initActiveNavLink() {
      const path = window.location.pathname;
      document.querySelectorAll('.navbar-nav .nav-link').forEach((link) => {
        const href = link.getAttribute('href');
        if (href === path || (href !== '/' && path.startsWith(href))) {
          link.classList.add('active');
        }
      });
    },

    /**
     * Bootstrap tooltips
     */
    initTooltips() {
      const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
      tooltipEls.forEach((el) => new bootstrap.Tooltip(el));
    },

    /**
     * Show loading overlay
     */
    showLoading(message = 'Processing...') {
      let overlay = document.getElementById('opticrop-loading');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'opticrop-loading';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
          <div class="loading-spinner"></div>
          <p class="loading-text">${message}</p>
        `;
        document.body.appendChild(overlay);
      } else {
        overlay.querySelector('.loading-text').textContent = message;
      }
      requestAnimationFrame(() => overlay.classList.add('active'));
    },

    /**
     * Hide loading overlay
     */
    hideLoading() {
      const overlay = document.getElementById('opticrop-loading');
      if (overlay) overlay.classList.remove('active');
    },

    /**
     * Format number with commas
     */
    formatNumber(num) {
      return new Intl.NumberFormat().format(num);
    },

    /**
     * Format percentage
     */
    formatPercent(value, decimals = 1) {
      if (value == null) return 'N/A';
      return `${(value * 100).toFixed(decimals)}%`;
    },

    /**
     * Animate counting up a number
     */
    animateCounter(element, target, duration = 1500) {
      const start = 0;
      const startTime = performance.now();

      const step = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);
        element.textContent = this.formatNumber(current);
        if (progress < 1) requestAnimationFrame(step);
      };

      requestAnimationFrame(step);
    },

    /**
     * Debounce utility
     */
    debounce(fn, delay = 300) {
      let timer;
      return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
      };
    },

    /**
     * Fetch JSON with error handling
     */
    async fetchJSON(url, options = {}) {
      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const message = data.error || data.errors?.join(', ') || `Request failed (${response.status})`;
        throw new Error(message);
      }

      return data;
    },

    /**
     * Capitalize first letter
     */
    capitalize(str) {
      if (!str) return '';
      return str.charAt(0).toUpperCase() + str.slice(1);
    },

    /**
     * Get crop emoji map (fallback)
     */
    cropEmojis: {
      rice: '🌾', maize: '🌽', chickpea: '🌰', kidneybeans: '🫘',
      pigeonpeas: '🟤', mothbeans: '🟡', mungbean: '🟢', blackgram: '⚫',
      lentil: '🫘', pomegranate: '🍑', banana: '🍌', mango: '🥭',
      grapes: '🍇', watermelon: '🍉', muskmelon: '🍈', apple: '🍎',
      orange: '🍊', papaya: '🍐', coconut: '🥥', cotton: '🌸',
      jute: '🌿', coffee: '☕',
    },

    getCropEmoji(crop) {
      return this.cropEmojis[crop?.toLowerCase()] || '🌿';
    },
  };

  window.OptiCrop = OptiCrop;

  document.addEventListener('DOMContentLoaded', () => OptiCrop.init());
})();

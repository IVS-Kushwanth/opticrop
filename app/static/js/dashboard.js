/**
 * OptiCrop — Dashboard Interactivity
 */
(function () {
  'use strict';

  function initCounterAnimations() {
    document.querySelectorAll('[data-count]').forEach((el) => {
      const target = parseInt(el.dataset.count, 10);
      if (!isNaN(target)) {
        OptiCrop.animateCounter(el, target);
      }
    });
  }

  function initHistoryFilters() {
    const table = document.getElementById('history-table');
    if (!table) return;

    const cropFilter = document.getElementById('filter-crop');
    const algoFilter = document.getElementById('filter-algorithm');
    const searchInput = document.getElementById('filter-search');
    const rows = table.querySelectorAll('tbody tr');

    function applyFilters() {
      const cropVal = cropFilter?.value?.toLowerCase() || '';
      const algoVal = algoFilter?.value?.toLowerCase() || '';
      const searchVal = searchInput?.value?.toLowerCase() || '';

      let visibleCount = 0;

      rows.forEach((row) => {
        const crop = row.dataset.crop?.toLowerCase() || '';
        const algo = row.dataset.algorithm?.toLowerCase() || '';
        const text = row.textContent.toLowerCase();

        const matchCrop = !cropVal || crop === cropVal;
        const matchAlgo = !algoVal || algo === algoVal;
        const matchSearch = !searchVal || text.includes(searchVal);

        const visible = matchCrop && matchAlgo && matchSearch;
        row.style.display = visible ? '' : 'none';
        if (visible) visibleCount++;
      });

      const emptyState = document.getElementById('history-empty-filter');
      if (emptyState) {
        emptyState.classList.toggle('d-none', visibleCount > 0);
      }
    }

    cropFilter?.addEventListener('change', applyFilters);
    algoFilter?.addEventListener('change', applyFilters);
    searchInput?.addEventListener('input', OptiCrop.debounce(applyFilters, 250));
  }

  async function initAnalyticsCharts() {
    const analyticsPage = document.getElementById('analytics-page');
    if (!analyticsPage) return;

    const loadingEl = document.getElementById('analytics-loading');
    const chartsEl = document.getElementById('analytics-charts');

    try {
      const stats = await OptiCrop.fetchJSON('/api/v1/stats');

      if (loadingEl) loadingEl.classList.add('d-none');
      if (chartsEl) chartsEl.classList.remove('d-none');

      updateMiniStats(stats);

      OptiCropCharts.createAccuracyChart('chart-accuracy', stats.model_accuracies || {});
      OptiCropCharts.createFeatureImportanceChart('chart-features', stats.feature_importance || {});
      OptiCropCharts.createCropDistributionChart('chart-crops', stats.crop_distribution || {});
      OptiCropCharts.createTimelineChart('chart-timeline', stats.prediction_timeline || {});
      OptiCropCharts.createAlgorithmUsageChart('chart-algorithms', stats.algorithm_usage || {});

      if (stats.confusion_matrix) {
        OptiCropCharts.createConfusionMatrixChart('chart-confusion', stats.confusion_matrix);
      }
    } catch (err) {
      if (loadingEl) {
        loadingEl.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
      }
    }
  }

  function updateMiniStats(stats) {
    const totalEl = document.getElementById('stat-total-predictions');
    const cropCountEl = document.getElementById('stat-unique-crops');
    const algoCountEl = document.getElementById('stat-algorithms-used');
    const bestModelEl = document.getElementById('stat-best-model');

    if (totalEl && stats.total_predictions != null) {
      OptiCrop.animateCounter(totalEl, stats.total_predictions);
    }

    if (cropCountEl && stats.crop_distribution) {
      OptiCrop.animateCounter(cropCountEl, Object.keys(stats.crop_distribution).length);
    }

    if (algoCountEl && stats.algorithm_usage) {
      OptiCrop.animateCounter(algoCountEl, Object.keys(stats.algorithm_usage).length);
    }

    if (bestModelEl && stats.model_accuracies) {
      const best = Object.entries(stats.model_accuracies).reduce(
        (max, [name, acc]) => (acc > max.acc ? { name, acc } : max),
        { name: '—', acc: 0 }
      );
      bestModelEl.textContent = best.name;
    }
  }

  function initComparePage() {
    const form = document.getElementById('compare-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      OptiCrop.showLoading('Running all algorithms...');

      const formData = new FormData(form);
      const payload = {};
      formData.forEach((val, key) => { payload[key] = parseFloat(val); });

      try {
        const results = await OptiCrop.fetchJSON('/compare', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        renderComparePageResults(results);
      } catch (err) {
        document.getElementById('compare-results').innerHTML =
          `<div class="alert alert-danger">${err.message}</div>`;
      } finally {
        OptiCrop.hideLoading();
      }
    });
  }

  function renderComparePageResults(results) {
    const container = document.getElementById('compare-results');
    if (!container) return;

    const cards = Object.entries(results)
      .map(([algo, r]) => {
        const conf = r.confidence != null
          ? `<span class="confidence-badge">${OptiCrop.formatPercent(r.confidence)}</span>`
          : '<span class="text-muted-custom">N/A</span>';

        return `
          <div class="col-md-6 col-lg-4" data-aos="fade-up">
            <div class="glass-card p-4 h-100 hover-lift">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <span class="algo-badge">${algo.replace('_', ' ')}</span>
                ${conf}
              </div>
              <div class="text-center">
                <div class="result-crop-emoji" style="font-size:3rem">${r.emoji || OptiCrop.getCropEmoji(r.crop)}</div>
                <h4 class="result-crop-name" style="font-size:1.5rem">${OptiCrop.capitalize(r.crop)}</h4>
              </div>
              <p class="text-muted-custom small mt-2 mb-0">${r.description || ''}</p>
              <div class="d-flex gap-3 mt-3 small text-muted-custom">
                <span><i class="fas fa-calendar"></i> ${r.season || '—'}</span>
                <span><i class="fas fa-tint"></i> ${r.water || '—'}</span>
              </div>
            </div>
          </div>
        `;
      })
      .join('');

    container.innerHTML = `<div class="row g-4">${cards}</div>`;
    AOS.refresh();
  }

  document.addEventListener('DOMContentLoaded', () => {
    initCounterAnimations();
    initHistoryFilters();
    initAnalyticsCharts();
    initComparePage();
  });
})();

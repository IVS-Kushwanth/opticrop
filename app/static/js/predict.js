/**
 * OptiCrop — Prediction Form AJAX & Interactions
 */
(function () {
  'use strict';

  const SAMPLE_PRESETS = {
    rice: { nitrogen: 90, phosphorous: 42, potassium: 43, temperature: 25, humidity: 80, ph: 6.5, rainfall: 200 },
    maize: { nitrogen: 85, phosphorous: 58, potassium: 41, temperature: 28, humidity: 65, ph: 7.0, rainfall: 120 },
    cotton: { nitrogen: 120, phosphorous: 45, potassium: 35, temperature: 32, humidity: 55, ph: 7.2, rainfall: 80 },
    coffee: { nitrogen: 100, phosphorous: 35, potassium: 40, temperature: 22, humidity: 75, ph: 6.0, rainfall: 150 },
    apple: { nitrogen: 20, phosphorous: 130, potassium: 280, temperature: 15, humidity: 60, ph: 6.5, rainfall: 100 },
  };

  const FIELD_MAP = {
    nitrogen: 'nitrogen',
    phosphorous: 'phosphorous',
    potassium: 'potassium',
    temperature: 'temperature',
    humidity: 'humidity',
    ph: 'ph',
    rainfall: 'rainfall',
  };

  function getFormValues(form) {
    const values = {};
    Object.keys(FIELD_MAP).forEach((key) => {
      const input = form.querySelector(`[name="${key}"]`);
      values[key] = input ? parseFloat(input.value) : null;
    });
    return values;
  }

  function setFormValues(form, values) {
    Object.entries(values).forEach(([key, val]) => {
      const input = form.querySelector(`[name="${key}"]`);
      if (input) input.value = val;
    });
  }

  function initSamplePresets() {
    document.querySelectorAll('.sample-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const preset = btn.dataset.preset;
        const form = document.getElementById('predict-form');
        if (form && SAMPLE_PRESETS[preset]) {
          setFormValues(form, SAMPLE_PRESETS[preset]);
          document.querySelectorAll('.sample-btn').forEach((b) => b.classList.remove('active'));
          btn.classList.add('active');
        }
      });
    });
  }

  function initAjaxPredict() {
    const form = document.getElementById('predict-form');
    const ajaxBtn = document.getElementById('ajax-predict-btn');
    if (!form || !ajaxBtn) return;

    ajaxBtn.addEventListener('click', async (e) => {
      e.preventDefault();

      const algorithm = form.querySelector('input[name="algorithm"]:checked')?.value || 'random_forest';
      const values = getFormValues(form);

      OptiCrop.showLoading('Analyzing soil & climate data...');

      try {
        const result = await OptiCrop.fetchJSON(`/predict/${algorithm}`, {
          method: 'POST',
          body: JSON.stringify(values),
        });

        showAjaxResult(result);
      } catch (err) {
        showAjaxError(err.message);
      } finally {
        OptiCrop.hideLoading();
      }
    });
  }

  function showAjaxResult(result) {
    const container = document.getElementById('ajax-result-preview');
    if (!container) return;

    if (result.error) {
      container.innerHTML = `<div class="model-error-banner">${result.error}</div>`;
      container.classList.remove('d-none');
      return;
    }

    const confidence = result.confidence
      ? `<span class="confidence-badge"><i class="fas fa-chart-line"></i> ${OptiCrop.formatPercent(result.confidence)}</span>`
      : '';

    let probBars = '';
    if (result.probabilities) {
      probBars = Object.entries(result.probabilities)
        .map(([crop, prob]) => `
          <div class="probability-bar">
            <div class="prob-label">
              <span>${OptiCrop.getCropEmoji(crop)} ${OptiCrop.capitalize(crop)}</span>
              <span>${OptiCrop.formatPercent(prob)}</span>
            </div>
            <div class="progress">
              <div class="progress-bar" style="width: ${prob * 100}%"></div>
            </div>
          </div>
        `)
        .join('');
    }

    container.innerHTML = `
      <div class="glass-card p-4 mt-3" data-aos="fade-up">
        <div class="text-center mb-3">
          <div class="result-crop-emoji">${result.emoji || OptiCrop.getCropEmoji(result.crop)}</div>
          <h3 class="result-crop-name">${OptiCrop.capitalize(result.crop)}</h3>
          ${confidence}
        </div>
        ${probBars ? `<div class="mt-3">${probBars}</div>` : ''}
        <p class="text-muted-custom text-center mt-3 mb-0 small">${result.description || ''}</p>
      </div>
    `;
    container.classList.remove('d-none');
  }

  function showAjaxError(message) {
    const container = document.getElementById('ajax-result-preview');
    if (container) {
      container.innerHTML = `<div class="alert alert-danger mt-3">${message}</div>`;
      container.classList.remove('d-none');
    }
  }

  function initCompareModal() {
    const compareBtn = document.getElementById('compare-modal-btn');
    const compareModal = document.getElementById('compareModal');
    if (!compareBtn || !compareModal) return;

    compareBtn.addEventListener('click', async () => {
      const form = document.getElementById('predict-form');
      if (!form) return;

      const values = getFormValues(form);
      const modalBody = compareModal.querySelector('.compare-results-body');
      modalBody.innerHTML = '<div class="text-center py-4"><div class="loading-spinner mx-auto"></div><p class="loading-text mt-2">Comparing all algorithms...</p></div>';

      const modal = bootstrap.Modal.getOrCreateInstance(compareModal);
      modal.show();

      try {
        const results = await OptiCrop.fetchJSON('/compare', {
          method: 'POST',
          body: JSON.stringify({
            nitrogen: values.nitrogen,
            phosphorous: values.phosphorous,
            potassium: values.potassium,
            temperature: values.temperature,
            humidity: values.humidity,
            ph: values.ph,
            rainfall: values.rainfall,
          }),
        });

        renderCompareTable(modalBody, results);
      } catch (err) {
        modalBody.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
      }
    });
  }

  function renderCompareTable(container, results) {
    const algos = Object.keys(results);
    let maxConf = -1;
    let winner = null;

    algos.forEach((algo) => {
      const conf = results[algo].confidence;
      if (conf != null && conf > maxConf) {
        maxConf = conf;
        winner = algo;
      }
    });

    const rows = algos
      .map((algo) => {
        const r = results[algo];
        const isWinner = algo === winner;
        const conf = r.confidence != null ? OptiCrop.formatPercent(r.confidence) : 'N/A';
        return `
          <tr class="${isWinner ? 'compare-winner' : ''}">
            <td>${algo.replace('_', ' ')}</td>
            <td>${r.emoji || OptiCrop.getCropEmoji(r.crop)} ${OptiCrop.capitalize(r.crop)}</td>
            <td>${conf}</td>
            <td>${r.season || '—'}</td>
            <td>${r.water || '—'}</td>
          </tr>
        `;
      })
      .join('');

    container.innerHTML = `
      <div class="table-responsive">
        <table class="compare-table">
          <thead>
            <tr>
              <th>Algorithm</th>
              <th>Predicted Crop</th>
              <th>Confidence</th>
              <th>Season</th>
              <th>Water Need</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  function initFormValidation() {
    const form = document.getElementById('predict-form');
    if (!form) return;

    form.addEventListener('submit', () => {
      OptiCrop.showLoading('Running prediction...');
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initSamplePresets();
    initAjaxPredict();
    initCompareModal();
    initFormValidation();
  });
})();

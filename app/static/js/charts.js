/**
 * OptiCrop — Chart.js Visualization Helpers
 */
(function () {
  'use strict';

  const CHART_COLORS = {
    primary: '#1a472a',
    accent: '#74c69d',
    accentLight: '#95d5b2',
    gold: '#f4a261',
    goldDark: '#e76f51',
    palette: ['#74c69d', '#40916c', '#f4a261', '#e76f51', '#2d6a4f', '#95d5b2', '#52b788', '#b7e4c7'],
  };

  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#a8c5b0',
          font: { family: 'Inter, sans-serif', size: 11 },
          padding: 16,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(13, 27, 18, 0.92)',
        titleColor: '#e8f5e9',
        bodyColor: '#a8c5b0',
        borderColor: 'rgba(116, 198, 157, 0.3)',
        borderWidth: 1,
        cornerRadius: 8,
        padding: 12,
      },
    },
  };

  const OptiCropCharts = {
    instances: {},

    /**
     * Shared scale config for dark theme
     */
    darkScales() {
      const axisStyle = {
        ticks: { color: '#6b8f7a', font: { size: 10 } },
        grid: { color: 'rgba(116, 198, 157, 0.08)' },
      };
      return {
        x: { ...axisStyle },
        y: { ...axisStyle, beginAtZero: true },
      };
    },

    /**
     * Model accuracy bar chart
     */
    createAccuracyChart(canvasId, accuracies) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return null;

      const labels = Object.keys(accuracies);
      const data = Object.values(accuracies).map((v) => (v * 100).toFixed(1));

      return this._create(canvasId, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Accuracy (%)',
            data,
            backgroundColor: CHART_COLORS.palette.map((c) => c + 'cc'),
            borderColor: CHART_COLORS.palette,
            borderWidth: 1,
            borderRadius: 6,
          }],
        },
        options: {
          ...defaultOptions,
          scales: {
            ...this.darkScales(),
            y: { ...this.darkScales().y, max: 100 },
          },
          plugins: {
            ...defaultOptions.plugins,
            legend: { display: false },
          },
        },
      });
    },

    /**
     * Feature importance horizontal bar
     */
    createFeatureImportanceChart(canvasId, importance) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return null;

      const sorted = Object.entries(importance).sort((a, b) => b[1] - a[1]);
      const labels = sorted.map(([k]) => k);
      const data = sorted.map(([, v]) => (v * 100).toFixed(1));

      return this._create(canvasId, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Importance (%)',
            data,
            backgroundColor: CHART_COLORS.accent + 'aa',
            borderColor: CHART_COLORS.accent,
            borderWidth: 1,
            borderRadius: 4,
          }],
        },
        options: {
          indexAxis: 'y',
          ...defaultOptions,
          scales: this.darkScales(),
          plugins: { ...defaultOptions.plugins, legend: { display: false } },
        },
      });
    },

    /**
     * Crop distribution doughnut
     */
    createCropDistributionChart(canvasId, distribution) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return null;

      const labels = Object.keys(distribution);
      const data = Object.values(distribution);

      return this._create(canvasId, {
        type: 'doughnut',
        data: {
          labels: labels.map((l) => l.charAt(0).toUpperCase() + l.slice(1)),
          datasets: [{
            data,
            backgroundColor: CHART_COLORS.palette,
            borderColor: '#0d1b12',
            borderWidth: 2,
          }],
        },
        options: {
          ...defaultOptions,
          cutout: '60%',
        },
      });
    },

    /**
     * Prediction timeline line chart
     */
    createTimelineChart(canvasId, timeline) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return null;

      const labels = Object.keys(timeline);
      const data = Object.values(timeline);

      return this._create(canvasId, {
        type: 'line',
        data: {
          labels: labels.map((d) => d.slice(5)),
          datasets: [{
            label: 'Predictions',
            data,
            borderColor: CHART_COLORS.accent,
            backgroundColor: CHART_COLORS.accent + '33',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: CHART_COLORS.gold,
            pointRadius: 3,
            pointHoverRadius: 6,
          }],
        },
        options: {
          ...defaultOptions,
          scales: this.darkScales(),
          plugins: { ...defaultOptions.plugins, legend: { display: false } },
        },
      });
    },

    /**
     * Algorithm usage pie chart
     */
    createAlgorithmUsageChart(canvasId, usage) {
      const ctx = document.getElementById(canvasId);
      if (!ctx) return null;

      const labels = Object.keys(usage).map((a) => a.replace('_', ' '));
      const data = Object.values(usage);

      return this._create(canvasId, {
        type: 'pie',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: CHART_COLORS.palette,
            borderColor: '#0d1b12',
            borderWidth: 2,
          }],
        },
        options: defaultOptions,
      });
    },

    /**
     * Confusion matrix heatmap-style bar
     */
    createConfusionMatrixChart(canvasId, confusionData) {
      const ctx = document.getElementById(canvasId);
      if (!ctx || !confusionData) return null;

      const labels = confusionData.labels || [];
      const matrix = confusionData.matrix || [];

      const datasets = labels.map((label, i) => ({
        label: label.charAt(0).toUpperCase() + label.slice(1),
        data: matrix[i] || [],
        backgroundColor: CHART_COLORS.palette[i % CHART_COLORS.palette.length] + 'cc',
        borderRadius: 2,
      }));

      return this._create(canvasId, {
        type: 'bar',
        data: { labels, datasets },
        options: {
          ...defaultOptions,
          scales: {
            x: { stacked: true, ...this.darkScales().x },
            y: { stacked: true, ...this.darkScales().y, max: 100 },
          },
        },
      });
    },

    /**
     * Destroy all chart instances
     */
    destroyAll() {
      Object.values(this.instances).forEach((chart) => chart.destroy());
      this.instances = {};
    },

    _create(id, config) {
      if (this.instances[id]) {
        this.instances[id].destroy();
      }
      const chart = new Chart(document.getElementById(id), config);
      this.instances[id] = chart;
      return chart;
    },
  };

  window.OptiCropCharts = OptiCropCharts;
})();

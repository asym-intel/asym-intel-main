/* ============================================================
   Asymmetric Intelligence Monitor — charts.js
   Chart.js wrappers. Requires Chart.js to be loaded first.
   All charts use --monitor-accent CSS var by default.
   Exposes:
     window.AsymCharts.line(canvasId, labels, datasets, options)
     window.AsymCharts.bar(canvasId, labels, datasets, options)
     window.AsymCharts.gauge(canvasId, value, min, max, options)
   ============================================================ */
(function () {
  'use strict';

  /* ── Get CSS var value ── */
  function getCSSVar(name) {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(name).trim();
  }

  function getAccent() {
    return getCSSVar('--monitor-accent') || '#4f98a3';
  }

  function getTextMuted() {
    return getCSSVar('--color-text-muted') || '#8a857c';
  }

  function getBorderColor() {
    return getCSSVar('--color-border') || '#d8d4cd';
  }

  function getSurface() {
    return getCSSVar('--color-surface') || '#ffffff';
  }

  /* ── Safe canvas getter ── */
  function getCanvas(canvasId) {
    if (!canvasId) return null;
    var canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.warn('AsymCharts: canvas #' + canvasId + ' not found');
      return null;
    }
    if (typeof Chart === 'undefined') {
      console.warn('AsymCharts: Chart.js is not loaded');
      return null;
    }
    // Destroy existing chart if any
    var existing = Chart.getChart(canvas);
    if (existing) existing.destroy();
    return canvas;
  }

  /* ── Default base config ── */
  function baseConfig() {
    return {
      plugins: {
        legend: {
          labels: {
            color: getTextMuted(),
            font: { family: "'Satoshi', sans-serif", size: 11 }
          }
        },
        tooltip: {
          backgroundColor: getSurface(),
          titleColor: getCSSVar('--color-text') || '#1a1917',
          bodyColor: getTextMuted(),
          borderColor: getBorderColor(),
          borderWidth: 1
        }
      },
      scales: {
        x: {
          ticks: { color: getTextMuted(), font: { family: "'Satoshi', sans-serif", size: 11 } },
          grid: { color: getBorderColor() }
        },
        y: {
          ticks: { color: getTextMuted(), font: { family: "'Satoshi', sans-serif", size: 11 } },
          grid: { color: getBorderColor() }
        }
      }
    };
  }

  /* ── Merge options ── */
  function mergeDeep(target, source) {
    if (!source) return target;
    Object.keys(source).forEach(function (key) {
      if (source[key] !== null && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        target[key] = target[key] || {};
        mergeDeep(target[key], source[key]);
      } else {
        target[key] = source[key];
      }
    });
    return target;
  }

  /* ── Line Chart ── */
  function line(canvasId, labels, datasets, options) {
    var canvas = getCanvas(canvasId);
    if (!canvas) return null;

    var accent = getAccent();
    // Apply default accent colour to datasets that don't specify one
    var processedDatasets = datasets.map(function (ds, i) {
      return mergeDeep({
        borderColor: accent,
        backgroundColor: accent.replace(')', ', 0.1)').replace('rgb', 'rgba'),
        tension: 0.3,
        pointBackgroundColor: accent,
        pointRadius: 4,
        fill: false
      }, ds);
    });

    var cfg = mergeDeep(baseConfig(), {
      type: 'line',
      data: { labels: labels, datasets: processedDatasets },
      options: { responsive: true, maintainAspectRatio: true }
    });
    if (options) mergeDeep(cfg.options, options);

    return new Chart(canvas, cfg);
  }

  /* ── Bar Chart ── */
  function bar(canvasId, labels, datasets, options) {
    var canvas = getCanvas(canvasId);
    if (!canvas) return null;

    var accent = getAccent();
    var processedDatasets = datasets.map(function (ds) {
      return mergeDeep({
        backgroundColor: accent.replace(')', ', 0.7)').replace('rgb', 'rgba'),
        borderColor: accent,
        borderWidth: 1
      }, ds);
    });

    var cfg = mergeDeep(baseConfig(), {
      type: 'bar',
      data: { labels: labels, datasets: processedDatasets },
      options: { responsive: true, maintainAspectRatio: true }
    });
    if (options) mergeDeep(cfg.options, options);

    return new Chart(canvas, cfg);
  }

  /* ── Gauge (doughnut-based) ── */
  function gauge(canvasId, value, min, max, options) {
    var canvas = getCanvas(canvasId);
    if (!canvas) return null;

    min = min != null ? min : 0;
    max = max != null ? max : 100;
    var accent = getAccent();
    var pct = Math.max(0, Math.min(1, (value - min) / (max - min)));
    var filled = pct;
    var empty = 1 - pct;

    var cfg = {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [filled, empty],
          backgroundColor: [accent, getBorderColor()],
          borderWidth: 0,
          circumference: 180,
          rotation: -90
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        }
      },
      plugins: [{
        id: 'gaugeLabel',
        afterDraw: function (chart) {
          var ctx = chart.ctx;
          var cx = chart.chartArea.left + chart.chartArea.width / 2;
          var cy = chart.chartArea.bottom;
          ctx.save();
          ctx.font = 'bold 20px Satoshi, sans-serif';
          ctx.fillStyle = getCSSVar('--color-text') || '#1a1917';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'bottom';
          ctx.fillText(String(value), cx, cy);
          ctx.restore();
        }
      }]
    };

    if (options) mergeDeep(cfg.options, options);
    return new Chart(canvas, cfg);
  }

  // Public API
  window.AsymCharts = { line: line, bar: bar, gauge: gauge };
})();

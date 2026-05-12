/* ============================================================
   Asymmetric Intelligence — Shared Monitor Design System
   shared/js/chip-filter.js  ·  Version 1.0  ·  12 May 2026
   Universal chip-filter primitive (FE-CHIP-FILTER-PRIMITIVE)
   P12 (PI-1 strict) · P13 · P5 · P6

   URL state contract: ?filter-<group>=<comma-separated-values>
   Selection model: within-group OR, cross-group AND.
   aria-pressed is the DOM source of truth; URL is write-side mirror.
   Uses history.replaceState (not pushState) — no history pile-up.
   ============================================================ */

(function () {
  'use strict';

  /* ── Utilities ──────────────────────────────────────────────── */

  /**
   * Parse all filter-* query parameters from the current URL.
   * Returns a Map<groupName, Set<value>>.
   */
  function parseUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const state = new Map();
    for (const [key, raw] of params.entries()) {
      if (key.startsWith('filter-')) {
        const group = key.slice('filter-'.length);
        const values = raw.split(',').map(v => v.trim()).filter(Boolean);
        if (values.length) state.set(group, new Set(values));
      }
    }
    return state;
  }

  /**
   * Write current selection state back to the URL via replaceState.
   * Only writes filter-* keys; leaves all other query params untouched.
   */
  function writeUrlParams(state) {
    const params = new URLSearchParams(window.location.search);
    // Remove all existing filter-* params first
    for (const key of [...params.keys()]) {
      if (key.startsWith('filter-')) params.delete(key);
    }
    // Write current selections
    for (const [group, values] of state.entries()) {
      if (values.size) {
        params.set('filter-' + group, [...values].join(','));
      }
    }
    const qs = params.toString();
    const newUrl = window.location.pathname + (qs ? '?' + qs : '') + window.location.hash;
    history.replaceState(null, '', newUrl);
  }

  /**
   * Collect selected values per group from chip DOM.
   * Returns Map<groupName, Set<value>>.
   */
  function readDomState(filterEl) {
    const state = new Map();
    filterEl.querySelectorAll('[data-group]').forEach(function (groupEl) {
      const group = groupEl.dataset.group;
      const selected = new Set();
      groupEl.querySelectorAll('.chip[aria-pressed="true"]').forEach(function (chip) {
        selected.add(chip.dataset.value);
      });
      state.set(group, selected);
    });
    return state;
  }

  /**
   * Apply the current selection to target list children.
   * Show/hide items using .chip-filter--hidden class.
   * Cross-group: AND.  Within-group: OR.
   * Empty group selection = wildcard (that group doesn't filter).
   */
  function applyFilter(filterEl, targetEl) {
    if (!targetEl) return;

    const domState = readDomState(filterEl);
    const items = targetEl.children;
    let visibleCount = 0;

    Array.from(items).forEach(function (item) {
      if (item.classList.contains('chip-filter__empty')) return;

      let pass = true;

      for (const [group, selected] of domState.entries()) {
        if (!selected.size) continue; // empty = wildcard
        const itemValue = item.dataset[group];
        // Support multi-value data attrs: data-jurisdiction="MT GI"
        const itemValues = itemValue ? itemValue.split(/[\s,]+/).filter(Boolean) : [];
        const matches = itemValues.some(function (v) { return selected.has(v); });
        if (!matches) {
          pass = false;
          break;
        }
      }

      if (pass) {
        item.classList.remove('chip-filter--hidden');
        visibleCount++;
      } else {
        item.classList.add('chip-filter--hidden');
      }
    });

    // Empty-state handling
    let emptyEl = targetEl.querySelector('.chip-filter__empty');
    if (visibleCount === 0) {
      if (!emptyEl) {
        emptyEl = document.createElement('li');
        emptyEl.className = 'chip-filter__empty';
        emptyEl.textContent = 'No items match these filters.';
        targetEl.appendChild(emptyEl);
      }
      emptyEl.hidden = false;
    } else if (emptyEl) {
      emptyEl.hidden = true;
    }
  }

  /**
   * Determine whether any chip is selected across the whole filter.
   */
  function hasActiveSelection(filterEl) {
    return filterEl.querySelector('.chip[aria-pressed="true"]') !== null;
  }

  /**
   * Update visibility of the reset button.
   */
  function syncResetButton(filterEl) {
    const resetBtn = filterEl.querySelector('.chip-filter__reset');
    if (!resetBtn) return;
    resetBtn.hidden = !hasActiveSelection(filterEl);
  }

  /* ── Per-instance initialisation ───────────────────────────── */

  function initInstance(filterEl) {
    const targetSelector = filterEl.dataset.target;
    const useUrlState = filterEl.dataset.urlState === 'true';
    const targetEl = targetSelector ? document.querySelector(targetSelector) : null;

    // Step 1: Restore selection from URL params (if url-state enabled)
    if (useUrlState) {
      const urlState = parseUrlParams();
      filterEl.querySelectorAll('[data-group]').forEach(function (groupEl) {
        const group = groupEl.dataset.group;
        const urlGroupValues = urlState.get(group);
        if (!urlGroupValues) return;
        groupEl.querySelectorAll('.chip').forEach(function (chip) {
          if (urlGroupValues.has(chip.dataset.value)) {
            chip.setAttribute('aria-pressed', 'true');
          }
        });
      });
    }

    // Step 2: Apply initial filter from restored state
    applyFilter(filterEl, targetEl);
    syncResetButton(filterEl);

    // Step 3: Wire chip click handlers
    filterEl.querySelectorAll('.chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        if (chip.getAttribute('aria-disabled') === 'true' || chip.disabled) return;
        const pressed = chip.getAttribute('aria-pressed') === 'true';
        chip.setAttribute('aria-pressed', String(!pressed));
        applyFilter(filterEl, targetEl);
        syncResetButton(filterEl);
        if (useUrlState) writeUrlParams(readDomState(filterEl));
      });

      // Keyboard: Space already triggers click for <button>; no extra handler needed.
    });

    // Step 4: Wire reset button
    const resetBtn = filterEl.querySelector('.chip-filter__reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        filterEl.querySelectorAll('.chip[aria-pressed="true"]').forEach(function (chip) {
          chip.setAttribute('aria-pressed', 'false');
        });
        applyFilter(filterEl, targetEl);
        syncResetButton(filterEl);
        if (useUrlState) writeUrlParams(new Map());
      });
    }
  }

  /* ── Public API ─────────────────────────────────────────────── */

  /**
   * applyAll() — re-run filter logic on every [data-chip-filter] on the page.
   */
  function applyAll() {
    document.querySelectorAll('[data-chip-filter]').forEach(function (filterEl) {
      const targetSelector = filterEl.dataset.target;
      const targetEl = targetSelector ? document.querySelector(targetSelector) : null;
      applyFilter(filterEl, targetEl);
      syncResetButton(filterEl);
    });
  }

  /**
   * applyOne(filterEl) — re-run filter logic for a specific filter element.
   */
  function applyOne(filterEl) {
    const targetSelector = filterEl.dataset.target;
    const targetEl = targetSelector ? document.querySelector(targetSelector) : null;
    applyFilter(filterEl, targetEl);
    syncResetButton(filterEl);
  }

  /**
   * resetOne(filterEl) — clear all selections for a specific filter element.
   */
  function resetOne(filterEl) {
    filterEl.querySelectorAll('.chip[aria-pressed="true"]').forEach(function (chip) {
      chip.setAttribute('aria-pressed', 'false');
    });
    const useUrlState = filterEl.dataset.urlState === 'true';
    const targetSelector = filterEl.dataset.target;
    const targetEl = targetSelector ? document.querySelector(targetSelector) : null;
    applyFilter(filterEl, targetEl);
    syncResetButton(filterEl);
    if (useUrlState) writeUrlParams(new Map());
  }

  /* ── Boot ───────────────────────────────────────────────────── */

  function boot() {
    document.querySelectorAll('[data-chip-filter]').forEach(initInstance);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  /* ── Export ─────────────────────────────────────────────────── */
  window.AsymChipFilter = {
    applyAll: applyAll,
    applyOne: applyOne,
    resetOne: resetOne,
  };

}());

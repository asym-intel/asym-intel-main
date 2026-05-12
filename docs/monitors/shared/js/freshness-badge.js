/* ============================================================
   Asymmetric Intelligence — Shared Monitor Design System
   shared/js/freshness-badge.js  ·  BRIEF-FE-FRESHNESS-BADGE-PRIMITIVE
   Relative-time formatter for universal freshness affordance.
   Consumes: <span class="freshness-badge" data-updated="<ISO-8601 UTC>">
   Authority: P3 (provenance-as-trust-affordance), PI-1 strict.
   ============================================================ */

(function () {
  'use strict';

  /**
   * fmtRelative — compute human-readable relative time and day count.
   * @param {string} isoTimestamp — ISO-8601 UTC string from _meta.last_updated.
   * @returns {{ text: string, days: number } | null}
   *   null when timestamp is absent, unparseable, or in the future beyond
   *   a 60-second clock-skew tolerance (PI-1: absent/invalid → element hidden).
   */
  function fmtRelative(isoTimestamp) {
    if (!isoTimestamp) return null;

    var updated = new Date(isoTimestamp);
    if (isNaN(updated.getTime())) return null;          // Unparseable → hide

    var now = new Date();
    var seconds = Math.floor((now - updated) / 1000);

    // Future-dated timestamp guard (D17 clock-skew defence — BRIEF §6)
    if (seconds < -60) {
      // eslint-disable-next-line no-console
      console.warn('[AsymFreshnessBadge] Future-dated timestamp detected:', isoTimestamp);
      return null;                                       // PI-1: hide badge
    }

    if (seconds < 60)    return { text: 'Updated just now',                              days: 0 };
    if (seconds < 3600)  return { text: 'Updated ' + Math.floor(seconds / 60) + ' min ago',   days: 0 };
    if (seconds < 86400) return { text: 'Updated ' + Math.floor(seconds / 3600) + ' hours ago', days: 0 };

    var days = Math.floor(seconds / 86400);
    if (days === 1)  return { text: 'Updated yesterday',                    days: 1 };
    if (days < 30)   return { text: 'Updated ' + days + ' days ago',        days: days };
    if (days < 60)   return { text: 'Updated 1 month ago',                  days: days };
    return               { text: 'Updated ' + Math.floor(days / 30) + ' months ago', days: days };
  }

  /**
   * stateFromDays — map elapsed days to freshness state class.
   * Thresholds: fresh ≤7d, stale 8–30d, aged >30d.
   * @param {number} days
   * @returns {'fresh'|'stale'|'aged'}
   */
  function stateFromDays(days) {
    if (days <= 7)  return 'fresh';
    if (days <= 30) return 'stale';
    return 'aged';
  }

  /**
   * applyOne — update a single freshness badge element.
   * PI-1: if data-updated is absent or invalid, function returns early;
   * the CSS [data-updated=""] / :not([data-updated]) rule handles visual hide.
   * @param {HTMLElement} el
   */
  function applyOne(el) {
    var iso = el.getAttribute('data-updated');
    var fmt = fmtRelative(iso);
    if (!fmt) return;   // PI-1: bad/absent field → CSS hides, JS does nothing

    el.textContent = fmt.text;
    el.classList.remove(
      'freshness-badge--fresh',
      'freshness-badge--stale',
      'freshness-badge--aged'
    );
    el.classList.add('freshness-badge--' + stateFromDays(fmt.days));
    el.setAttribute('title', 'Last updated ' + new Date(iso).toUTCString());
  }

  /**
   * applyAll — update every freshness badge on the page.
   * O(n) over badge count; safe on surfaces up to ~1 000 cards (see BRIEF §6).
   */
  function applyAll() {
    var badges = document.querySelectorAll('.freshness-badge[data-updated]');
    badges.forEach(applyOne);
  }

  // ─── Initialise on DOM ready ──────────────────────────────
  document.addEventListener('DOMContentLoaded', applyAll);

  // ─── 60-second live-update tick ──────────────────────────
  // Keeps relative text current for surfaces left open in browser.
  setInterval(applyAll, 60000);

  // ─── Public API (for consumer-side imperative calls) ─────
  window.AsymFreshnessBadge = {
    applyAll:  applyAll,
    applyOne:  applyOne
  };

})();

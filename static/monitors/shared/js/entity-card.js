/* ============================================================
   Asymmetric Intelligence — Shared Monitor Design System
   shared/js/entity-card.js  ·  BRIEF-L2-FE-ENTITY-CARD-PRIMITIVE
   Composer for the entity-card primitive. Consumes a JSON
   descriptor and emits the card DOM. Hosts freshness-badge.
   Authority: P1 (schema-driven projection), P5 (universal
   composition primitive), P12 (product not library), P13
   (no per-page edits).
   ============================================================ */

(function () {
  'use strict';

  // ─── Safe HTML escape (delegating consumers stay XSS-honest) ────────
  function escHtml(s) {
    if (s == null) return '';
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  /**
   * compose — build a single entity-card element from a JSON descriptor.
   *
   * Descriptor shape (all fields except `headline` are optional):
   * {
   *   headline:   string                                  // REQUIRED — missing → null returned
   *   subhead:    string
   *   eyebrow:    string                                  // e.g. ISO2 code, kicker
   *   adornment:  string                                  // small leading glyph / flag emoji
   *   href:       string                                  // makes the card an <a>
   *   state:      'pending' | undefined                   // dims and disables hover
   *   id:         string                                  // optional dom id
   *   testId:     string                                  // data-testid hook
   *   freshness:  { updatedAt: ISO-8601 UTC string }      // forwarded to freshness-badge
   *   meta:       Array<string|{html:string}>             // small meta items (right of badge)
   *   body:       string | HTMLElement                    // free-form body slot (consumer chips, etc.)
   *   cta:        { label: string, href?: string }        // optional call-to-action
   *   attrs:      Record<string,string>                   // extra data-* hooks for the host element
   * }
   *
   * PI-1 strict: returns null when descriptor is missing or
   * `headline` is empty — caller MUST handle the null. The
   * freshness-badge is omitted internally when `freshness.updatedAt`
   * is absent or empty, per BRIEF-FE-FRESHNESS-BADGE-PRIMITIVE.
   *
   * @param {object} d
   * @returns {HTMLElement|null}
   */
  function compose(d) {
    if (!d || typeof d !== 'object') return null;
    var headline = d.headline != null ? String(d.headline).trim() : '';
    if (!headline) return null;                   // PI-1: omit card entirely

    var hasHref = typeof d.href === 'string' && d.href.length > 0;
    var isPending = d.state === 'pending';

    // Anchor host iff href present AND not pending (pending cards must not link).
    var tag = hasHref && !isPending ? 'a' : 'div';
    var host = document.createElement(tag);
    host.className = 'entity-card';
    host.setAttribute('data-entity-card', '');
    if (tag === 'a') {
      host.href = d.href;
      host.setAttribute('data-entity-card-interactive', 'true');
    }
    if (isPending) host.setAttribute('data-entity-card-state', 'pending');
    if (d.id) host.id = d.id;
    if (d.testId) host.setAttribute('data-testid', d.testId);
    if (d.attrs && typeof d.attrs === 'object') {
      Object.keys(d.attrs).forEach(function (k) {
        // Only allow data-* hooks; reject style/class/event injection.
        if (k.indexOf('data-') === 0) host.setAttribute(k, d.attrs[k]);
      });
    }

    var parts = [];

    // ─── Header: adornment + (eyebrow + headline + subhead) ─────────
    var headerHtml = '<div class="entity-card__header">';
    if (d.adornment) {
      headerHtml += '<span class="entity-card__adornment" aria-hidden="true">'
        + escHtml(d.adornment) + '</span>';
    }
    headerHtml += '<div class="entity-card__titleblock">';
    if (d.eyebrow) {
      headerHtml += '<span class="entity-card__eyebrow">' + escHtml(d.eyebrow) + '</span>';
    }
    headerHtml += '<h3 class="entity-card__headline">' + escHtml(headline) + '</h3>';
    if (d.subhead) {
      headerHtml += '<p class="entity-card__subhead">' + escHtml(d.subhead) + '</p>';
    }
    headerHtml += '</div></div>';
    parts.push(headerHtml);

    // ─── Body slot ──────────────────────────────────────────────────
    var bodyEl = null;
    if (d.body instanceof HTMLElement) {
      bodyEl = document.createElement('div');
      bodyEl.className = 'entity-card__body';
      bodyEl.appendChild(d.body);
    } else if (typeof d.body === 'string' && d.body.length) {
      parts.push('<div class="entity-card__body">' + d.body + '</div>');
    }

    // ─── Meta row (freshness-badge + small items) ───────────────────
    var metaItems = [];
    var freshIso = d.freshness && d.freshness.updatedAt;
    if (freshIso) {
      // Reuses freshness-badge primitive contract. freshness-badge.js
      // will populate textContent + state class on DOMContentLoaded
      // and on its 60-second tick.
      metaItems.push(
        '<span class="freshness-badge" data-updated="' + escHtml(freshIso) + '"></span>'
      );
    }
    if (Array.isArray(d.meta)) {
      d.meta.forEach(function (item) {
        if (item == null) return;
        if (typeof item === 'string') {
          metaItems.push('<span>' + escHtml(item) + '</span>');
        } else if (typeof item === 'object' && typeof item.html === 'string') {
          metaItems.push('<span>' + item.html + '</span>');
        }
      });
    }
    if (metaItems.length) {
      parts.push('<div class="entity-card__meta">' + metaItems.join('') + '</div>');
    }

    // ─── CTA ────────────────────────────────────────────────────────
    if (d.cta && d.cta.label) {
      if (d.cta.href && tag === 'div') {
        parts.push(
          '<a class="entity-card__cta" href="' + escHtml(d.cta.href) + '">'
          + escHtml(d.cta.label) + '</a>'
        );
      } else {
        parts.push(
          '<span class="entity-card__cta">' + escHtml(d.cta.label) + '</span>'
        );
      }
    }

    host.innerHTML = parts.join('');

    // Insert body HTMLElement after innerHTML render (order: after header).
    if (bodyEl) {
      var headerNode = host.querySelector('.entity-card__header');
      if (headerNode && headerNode.nextSibling) {
        host.insertBefore(bodyEl, headerNode.nextSibling);
      } else {
        host.appendChild(bodyEl);
      }
    }

    return host;
  }

  /**
   * renderInto — compose each descriptor in `items` and append to `mount`.
   * Skips descriptors that fail the PI-1 contract (missing headline).
   * After mounting, kicks the freshness-badge tick so newly-inserted
   * badges populate without waiting for the next 60-second cycle.
   *
   * @param {HTMLElement} mount
   * @param {Array<object>} items
   * @returns {number} number of cards rendered
   */
  function renderInto(mount, items) {
    if (!mount || !Array.isArray(items)) return 0;
    mount.innerHTML = '';
    var rendered = 0;
    items.forEach(function (d) {
      var el = compose(d);
      if (el) {
        mount.appendChild(el);
        rendered += 1;
      }
    });
    // Kick freshness-badge to format any newly-inserted badges immediately.
    if (window.AsymFreshnessBadge && typeof window.AsymFreshnessBadge.applyAll === 'function') {
      window.AsymFreshnessBadge.applyAll();
    }
    return rendered;
  }

  // ─── Public API ─────────────────────────────────────────────────
  window.AsymEntityCard = {
    compose:    compose,
    renderInto: renderInto
  };

})();

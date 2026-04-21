/*!
 * monitor-urls.js — Canonical monitor registry resolver (JS).
 *
 * Single source of truth: static/monitors/monitor-registry.json
 * ENGINE-RULES §17: URLs to engine assets MUST come from this resolver,
 * never from string concatenation.
 *
 * This module supports two loading patterns:
 *   (1) Runtime fetch: await MonitorRegistry.load()
 *   (2) Pre-seeded:    MonitorRegistry.init(window.__MONITOR_REGISTRY__)
 *
 * Pattern (2) is used by nav.js, where tools/inline_registry_into_navjs.py
 * substitutes the JSON at build time — zero runtime fetch, zero CORS.
 *
 * Usage:
 *   await MonitorRegistry.load();
 *   MonitorRegistry.url('WDM');   // https://asym-intel.info/monitors/democratic-integrity/
 *   MonitorRegistry.all();        // [{abbr, slug, name, accent, url, ...}, ...]
 */
(function (global) {
  'use strict';

  var REGISTRY_URL = 'https://asym-intel.info/monitors/monitor-registry.json';
  var SCHEMA_VERSION = '2.0';

  var _data = null;

  function init(data) {
    if (!data || data.schema_version !== SCHEMA_VERSION) {
      throw new Error(
        'MonitorRegistry: schema_version mismatch (expected ' +
        SCHEMA_VERSION + ', got ' + (data && data.schema_version) + ')'
      );
    }
    if (!Array.isArray(data.monitors) || data.monitors.length === 0) {
      throw new Error('MonitorRegistry: monitors[] missing or empty');
    }
    _data = data;
    return data;
  }

  function load(url) {
    if (_data) return Promise.resolve(_data);
    return fetch(url || REGISTRY_URL, { cache: 'default' })
      .then(function (r) {
        if (!r.ok) throw new Error('fetch ' + r.status);
        return r.json();
      })
      .then(init);
  }

  function requireLoaded() {
    if (!_data) {
      throw new Error('MonitorRegistry not loaded. Call load() or init() first.');
    }
    return _data;
  }

  function all() {
    return requireLoaded().monitors.slice();
  }

  function abbrs() {
    return requireLoaded().monitors.map(function (m) { return m.abbr; });
  }

  function slugs() {
    return requireLoaded().monitors.map(function (m) { return m.slug; });
  }

  function _findBy(key, value) {
    var list = requireLoaded().monitors;
    for (var i = 0; i < list.length; i++) {
      if (list[i][key] === value) return list[i];
    }
    return null;
  }

  function byAbbr(abbr) {
    var m = _findBy('abbr', String(abbr || '').toUpperCase());
    if (!m) throw new Error('No monitor with abbr=' + abbr);
    return m;
  }

  function bySlug(slug) {
    var m = _findBy('slug', slug);
    if (!m) throw new Error('No monitor with slug=' + slug);
    return m;
  }

  /* Safe lookups (null on miss instead of throw) — for UI code that must
     never crash when an unknown slug appears in data. Mirrors the pattern
     used in /static/synthesis/index.html :: resolveMonitor. */
  function bySlugSafe(slug) {
    if (!_data || !slug) return null;
    var list = _data.monitors;
    for (var i = 0; i < list.length; i++) {
      if (list[i].slug === slug) return list[i];
    }
    return null;
  }
  function byAbbrSafe(abbr) {
    if (!_data || !abbr) return null;
    var key = String(abbr).toUpperCase();
    var list = _data.monitors;
    for (var i = 0; i < list.length; i++) {
      if (list[i].abbr === key) return list[i];
    }
    return null;
  }

  /* Slug → display name. Returns the monitor's canonical `name` from the
     registry, or a defensive titlecased fallback so the UI never leaks a
     raw slug. Used by cross-monitor flag cards and any component that
     receives slugs from publisher data. */
  function nameFromSlug(slug) {
    var m = bySlugSafe(slug);
    if (m) return m.name;
    if (!slug) return '';
    return String(slug).replace(/-/g, ' ').replace(/\b\w/g, function(c){ return c.toUpperCase(); });
  }

  function url(abbr)    { return byAbbr(abbr).url; }
  function slug(abbr)   { return byAbbr(abbr).slug; }
  function name(abbr)   { return byAbbr(abbr).name; }
  function accent(abbr) { return byAbbr(abbr).accent; }
  function svgUrl(abbr) { return byAbbr(abbr).svg_url; }

  var API = {
    SCHEMA_VERSION: SCHEMA_VERSION,
    REGISTRY_URL: REGISTRY_URL,
    init: init,
    load: load,
    all: all,
    abbrs: abbrs,
    slugs: slugs,
    byAbbr: byAbbr,
    byAbbrSafe: byAbbrSafe,
    bySlug: bySlug,
    bySlugSafe: bySlugSafe,
    nameFromSlug: nameFromSlug,
    url: url,
    slug: slug,
    name: name,
    accent: accent,
    svgUrl: svgUrl
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  global.MonitorRegistry = API;
})(typeof window !== 'undefined' ? window : this);

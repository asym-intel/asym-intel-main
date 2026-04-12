/* ─────────────────────────────────────────────────────────────────
   wdm-map.js  —  WDM Leaflet Choropleth Map
   Extracted Sprint 1 from wdm-dashboard inline IIFE.

   Exposes:
     window._wdmMapReady(heatmapData)
       Accept flat array (schema v2: [{country,health_status,…}])
       OR legacy object ({rapid_decay:[…], watchlist:[…], recovery:[…]})

     window._wdmInitMap(containerId?)
       Initialise Leaflet map. containerId defaults to 'wdm-map'.
       Safe to call multiple times — idempotent via mapInitialised flag.

   Depends on:
     • Leaflet 1.9.4  (CSS + JS loaded by dashboard <head>)
     • AsymRenderer.sourceLink  (optional — graceful no-op if absent)
     • GeoJSON: natural-earth ne_110m_admin_0_countries via jsDelivr CDN

   Blueprint v2.1 constraints:
     • This file is WDM-only. Do NOT add to shared renderer bundle.
     • Path: static/monitors/democratic-integrity/assets/wdm-map.js
     • Toggle button: #map-toggle  (data-active="map"|"table")
     • Map container: #wdm-map
     • Table fallback clone source: #heatmap-table → #geo-table-view
   ───────────────────────────────────────────────────────────────── */

(function () {
  'use strict';

  /* ── Country name / ISO-A3 → ISO 3166-1 alpha-2 ────────── */
  var ISO_MAP = {
    /* Full names */
    'United States': 'US', 'Hungary': 'HU', 'Serbia': 'RS',
    'India': 'IN', 'Philippines': 'PH', 'Georgia': 'GE',
    'Tunisia': 'TN', 'Nicaragua': 'NI', 'El Salvador': 'SV',
    'Venezuela': 'VE', 'Bolivia': 'BO', 'Mexico': 'MX',
    'Colombia': 'CO', 'Iran': 'IR', 'Tanzania': 'TZ',
    'Uganda': 'UG', 'DRC': 'CD', 'Kazakhstan': 'KZ',
    'Bangladesh': 'BD', 'Slovakia': 'SK', 'Poland': 'PL',
    'Italy': 'IT', 'Romania': 'RO', 'South Korea': 'KR',
    'Israel': 'IL', 'Iraq': 'IQ', "Côte d'Ivoire": 'CI',
    'Benin': 'BJ', 'United Kingdom': 'GB', 'Turkey': 'TR',
    'Canada': 'CA', 'France': 'FR', 'Nepal': 'NP',
    'Pakistan': 'PK', 'Guinea-Bissau': 'GW', 'Malawi': 'MW',
    'Senegal': 'SN', 'Paraguay': 'PY', 'Moldova': 'MD',
    'Angola': 'AO', 'Gabon': 'GA',
    /* ISO-A3 codes (schema v2 uses these in country field) */
    'USA': 'US', 'CAN': 'CA', 'IND': 'IN', 'PHL': 'PH',
    'GEO': 'GE', 'PAK': 'PK', 'NPL': 'NP', 'GNB': 'GW',
    'FRA': 'FR', 'ROU': 'RO', 'MWI': 'MW', 'SEN': 'SN',
    'PRY': 'PY', 'MDA': 'MD', 'AGO': 'AO', 'GAB': 'GA',
    'HUN': 'HU', 'SRB': 'RS', 'TUN': 'TN', 'NIC': 'NI',
    'SLV': 'SV', 'VEN': 'VE', 'BOL': 'BO', 'MEX': 'MX',
    'COL': 'CO', 'IRN': 'IR', 'TZA': 'TZ', 'UGA': 'UG',
    'COD': 'CD', 'KAZ': 'KZ', 'BGD': 'BD', 'SVK': 'SK',
    'POL': 'PL', 'ITA': 'IT', 'KOR': 'KR', 'ISR': 'IL',
    'IRQ': 'IQ', 'CIV': 'CI', 'BEN': 'BJ', 'GBR': 'GB',
    'TUR': 'TR'
  };

  /* ── Tier display config ─────────────────────────────────── */
  var TIER_COLORS = {
    rapid_decay: '#dc2626',
    recovery:    '#22c55e',
    watchlist:   '#f59e0b',
    unmonitored: '#e5e7eb'
  };

  var TIER_LABELS = {
    rapid_decay: 'Rapid Decay',
    recovery:    'Recovery',
    watchlist:   'Watchlist',
    unmonitored: 'Unmonitored'
  };

  /* ── Flat-array heatmap normalisation ───────────────────────
   * Schema v2 heatmap is a flat array of country objects with:
   *   { country, health_status, health_delta, severity_score, … }
   *
   * health_status normalisation → tier:
   *   'Crisis'                                   → rapid_decay
   *   'Backsliding' + health_delta 'Declining'   → rapid_decay
   *   'Backsliding' + health_delta 'Improving'   → watchlist
   *   'Constrained' + health_delta 'Declining'   → watchlist
   *   'Constrained'/'Consolidated' + 'Improving' → recovery
   * ──────────────────────────────────────────────────────────── */
  function normaliseTier(country) {
    var status = (country.health_status || '').toLowerCase();
    var delta  = (country.health_delta  || '').toLowerCase();
    if (status === 'crisis') return 'rapid_decay';
    if (status === 'backsliding') {
      return delta === 'improving' ? 'watchlist' : 'rapid_decay';
    }
    if (status === 'constrained') {
      return delta === 'improving' ? 'recovery' : 'watchlist';
    }
    if (status === 'consolidated') {
      return delta === 'improving' ? 'recovery' : 'watchlist';
    }
    /* Fallback: use tier field if present */
    if (country.tier) return country.tier;
    return 'unmonitored';
  }

  /* ── Internal state ──────────────────────────────────────── */
  var countryData   = {};   // iso2 → {country, tier, …}
  var mapInitialised = false;
  var wdmMap        = null;
  var geoLayer      = null;
  var pendingHeatmap = null; // queued until map init

  /* ── Helpers ─────────────────────────────────────────────── */
  function escHtml(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function tierLabel(tier) { return TIER_LABELS[tier] || tier; }

  function opacityForScore(score) {
    var s = parseFloat(score) || 0;
    if (s > 1) s = s / 10;   // normalise 0-10 → 0-1
    return 0.4 + (s * 0.45); // 0.40 – 0.85
  }

  /* ── Load country data from heatmap ─────────────────────── */
  function loadCountryData(heatmap) {
    countryData = {};

    /* Flat array (schema v2) */
    if (Array.isArray(heatmap)) {
      heatmap.forEach(function (c) {
        var iso = ISO_MAP[c.country] || ISO_MAP[c.country_name];
        if (!iso) return;
        countryData[iso] = {
          country:        c.country,
          tier:           normaliseTier(c),
          severity_score: c.severity_score || c.health_score || '',
          severity_arrow: c.severity_arrow || c.health_delta || '',
          lead_signal:    c.lead_signal || c.summary || c.narrative || '',
          source_url:     c.source_url || ''
        };
      });
      return;
    }

    /* Legacy object shape {rapid_decay:[], watchlist:[], recovery:[]} */
    if (heatmap && typeof heatmap === 'object') {
      var legacyTiers = {
        rapid_decay: heatmap.rapid_decay || [],
        watchlist:   heatmap.watchlist   || [],
        recovery:    heatmap.recovery    || []
      };
      Object.keys(legacyTiers).forEach(function (tier) {
        (legacyTiers[tier] || []).forEach(function (c) {
          var iso = ISO_MAP[c.country];
          if (!iso) return;
          countryData[iso] = {
            country:        c.country,
            tier:           tier,
            severity_score: c.severity_score || '',
            severity_arrow: c.severity_arrow || '',
            lead_signal:    c.lead_signal || c.summary || '',
            source_url:     c.source_url || ''
          };
        });
      });
    }
  }

  /* ── Leaflet style + feature callbacks ──────────────────── */
  function getStyle(feature) {
    var iso  = feature.properties.ISO_A2;
    var info = countryData[iso];
    if (!info) {
      return { fillColor: TIER_COLORS.unmonitored, fillOpacity: 0.45, color: '#adb5bd', weight: 0.5 };
    }
    var opacity = info.tier === 'rapid_decay'
      ? opacityForScore(info.severity_score)
      : 0.72;
    return {
      fillColor:   TIER_COLORS[info.tier] || TIER_COLORS.unmonitored,
      fillOpacity: opacity,
      color:       '#ffffff',
      weight:      0.6
    };
  }

  function onEachFeature(feature, layer) {
    var iso  = feature.properties.ISO_A2;
    var info = countryData[iso];
    if (!info) return;

    var signal = (info.lead_signal || '').slice(0, 100);
    var sourceLinkHtml = '';
    if (info.source_url &&
        typeof window.AsymRenderer !== 'undefined' &&
        typeof window.AsymRenderer.sourceLink === 'function') {
      sourceLinkHtml = ' ' + window.AsymRenderer.sourceLink(info.source_url);
    }

    var popup =
      '<div class="wdm-popup-name">' + escHtml(info.country) + '</div>' +
      '<div class="wdm-popup-tier wdm-popup-tier--' + escHtml(info.tier) + '">' +
        escHtml(tierLabel(info.tier)) +
      '</div>' +
      '<div class="wdm-popup-row">Score: <strong>' + escHtml(info.severity_score) + '</strong> ' +
        escHtml(info.severity_arrow) +
      '</div>' +
      (signal
        ? '<div class="wdm-popup-signal">' + escHtml(signal) +
          (info.lead_signal && info.lead_signal.length > 100 ? '\u2026' : '') + '</div>'
        : '') +
      sourceLinkHtml;

    layer.bindPopup(popup, { maxWidth: 240, className: 'wdm-country-popup' });
    layer.on('mouseover', function () { layer.setStyle({ weight: 1.5, color: '#334155' }); });
    layer.on('mouseout',  function () { geoLayer && geoLayer.resetStyle(layer); });
  }

  /* ── Map initialisation ──────────────────────────────────── */
  function initMap(containerId) {
    if (mapInitialised) return;
    mapInitialised = true;

    var cid = containerId || 'wdm-map';
    var isMobile = window.matchMedia && window.matchMedia('(max-width:640px)').matches;

    if (typeof L === 'undefined') {
      console.error('[wdm-map] Leaflet (L) not found. Ensure Leaflet CDN is loaded before wdm-map.js.');
      return;
    }

    wdmMap = L.map(cid, {
      center:             [20, 10],
      zoom:               2,
      minZoom:            1,
      maxZoom:            6,
      scrollWheelZoom:    !isMobile,
      zoomControl:        true,
      attributionControl: false
    });

    /* Clean choropleth background — no tile layer */
    wdmMap.getContainer().style.background = '#f0f0f0';

    /* GeoJSON — Natural Earth 110m via jsDelivr */
    var geoUrl = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
    /* Fallback to nvkelso natural-earth if world-atlas topojson unavailable */
    var geoUrlFallback = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson';

    fetch(geoUrlFallback)
      .then(function (r) { return r.json(); })
      .then(function (geo) {
        geoLayer = L.geoJSON(geo, {
          style:         getStyle,
          onEachFeature: onEachFeature
        }).addTo(wdmMap);
        wdmMap.fitBounds(geoLayer.getBounds(), { padding: [4, 4] });

        /* If heatmap data arrived before map init, apply it now */
        if (pendingHeatmap !== null) {
          loadCountryData(pendingHeatmap);
          pendingHeatmap = null;
          geoLayer.setStyle(getStyle);
        }
      })
      .catch(function (err) {
        console.error('[wdm-map] GeoJSON load error', err);
      });

    /* Map legend (Leaflet control) */
    var legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
      var div   = L.DomUtil.create('div', 'wdm-map-legend');
      var tiers = ['rapid_decay', 'watchlist', 'recovery', 'unmonitored'];
      div.innerHTML = tiers.map(function (t) {
        return '<div><span class="wdm-map-legend-swatch" style="background:' +
          TIER_COLORS[t] + '"></span>' + TIER_LABELS[t] + '</div>';
      }).join('');
      return div;
    };
    legend.addTo(wdmMap);
  }

  /* ── Map/Table toggle ────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var btn      = document.getElementById('map-toggle');
    var mapDiv   = document.getElementById('wdm-map');
    var geoTable = document.getElementById('geo-table-view');

    if (!btn || !mapDiv) return;

    btn.addEventListener('click', function () {
      var isMap = btn.getAttribute('data-active') === 'map';
      if (isMap) {
        /* Switch to table view */
        mapDiv.style.display = 'none';
        var src = document.getElementById('heatmap-table');
        if (geoTable && src) { geoTable.innerHTML = src.innerHTML; geoTable.style.display = ''; }
        btn.setAttribute('data-active',    'table');
        btn.setAttribute('aria-pressed',   'false');
        btn.textContent = 'Map view';
      } else {
        /* Switch to map view */
        if (geoTable) geoTable.style.display = 'none';
        mapDiv.style.display = 'block';
        btn.setAttribute('data-active',    'map');
        btn.setAttribute('aria-pressed',   'true');
        btn.textContent = 'Table view';
        initMap();
        setTimeout(function () { if (wdmMap) wdmMap.invalidateSize(); }, 120);
      }
    });

    /* Map is default view — initialise immediately */
    initMap();
    setTimeout(function () { if (wdmMap) wdmMap.invalidateSize(); }, 250);
  });

  /* ── Public API ──────────────────────────────────────────── */

  /**
   * Called by the data pipeline once heatmap data is loaded.
   * Accepts flat array (v2 schema) OR legacy {rapid_decay,watchlist,recovery} object.
   * If map is not yet initialised, queues the data for later.
   */
  window._wdmMapReady = function (heatmapData) {
    if (!mapInitialised) {
      /* Map not yet init — queue and let DOMContentLoaded handle it */
      pendingHeatmap = heatmapData;
      return;
    }
    loadCountryData(heatmapData);
    if (geoLayer) {
      geoLayer.setStyle(getStyle);
    }
  };

  /**
   * Explicitly initialise the Leaflet map.
   * @param {string} [containerId='wdm-map']
   */
  window._wdmInitMap = function (containerId) {
    initMap(containerId);
  };

}());

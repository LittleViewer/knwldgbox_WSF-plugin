<template>
  <div class="monitoring-map-container glass-panel">
    <div class="map-header" v-if="!previewMode">
      <div class="header-left">
        <h2 class="title">{{ t('map.title') }}</h2>
        <p class="subtitle">{{ t('map.subtitle') }}</p>
      </div>
      <div class="header-right">
        <span class="pulse-indicator">
          <span class="pulse"></span> {{ t('map.live') }}
        </span>
      </div>
    </div>

    <div class="map-wrapper">
      <div ref="mapContainer" class="leaflet-map"></div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, shallowRef, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import DOMPurify from 'dompurify';

const { t } = useI18n();

const props = defineProps({
  locations: {
    type: Array,
    default: () => []
  },
  previewMode: {
    type: Boolean,
    default: false
  }
});

const map = shallowRef(null);
const mapContainer = ref(null);
const markers = shallowRef([]);
let tiles = null;
let observer = null;

onMounted(() => {
  initMap();
  setTimeout(() => {
    if (map.value) map.value.invalidateSize();
  }, 400);

  if (props.locations.length > 0) {
    props.locations.forEach(loc => addMarker(loc));
  }
});

watch(() => props.locations, (newLocations) => {
  markers.value.forEach(m => {
    if (map.value) map.value.removeLayer(m);
  });
  markers.value = [];
  newLocations.forEach(loc => addMarker(loc));
}, { deep: true });

onUnmounted(() => {
  if (observer) observer.disconnect();
  if (map.value) map.value.remove();
});

function initMap() {
  if (!mapContainer.value) return;

  map.value = L.map(mapContainer.value, {
    center: [25, 0],
    zoom: 2.5,
    minZoom: 2,
    zoomControl: false,
    attributionControl: false,
    maxBounds: [[-90, -180], [90, 180]],
    maxBoundsViscosity: 1.0
  });

  const isLight = document.body.classList.contains('light-mode');
  const tileUrl = isLight
    ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
    : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';

  tiles = L.tileLayer(tileUrl, {
    subdomains: 'abcd',
    maxZoom: 19,
    noWrap: true,
    bounds: [[-90, -180], [90, 180]]
  }).addTo(map.value);

  observer = new MutationObserver(() => {
    const lightNow = document.body.classList.contains('light-mode');
    tiles.setUrl(lightNow
      ? 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
    );
  });
  observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });

  if (!props.previewMode) {
    L.control.zoom({ position: 'bottomright' }).addTo(map.value);
  }
}

function addMarker(loc) {
  if (!map.value) return;

  const icon = L.divIcon({
    className: 'custom-cyber-marker',
    html: `<div class="cyber-pin"><div class="cyber-pulse-ring"></div></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  });

  const marker = L.marker([loc.lat, loc.lng], { icon }).addTo(map.value);

  const titleHtml = loc.title ? `<h3 class="popup-title">${loc.title}</h3>` : '';
  const descHtml = loc.description ? `<p class="popup-desc">${loc.description}</p>` : '';
  const linkHtml = loc.link ? `<a href="${loc.link}" target="_blank" rel="noopener noreferrer" class="popup-source-link">View Source ↗</a>` : '';

  let mediaHtml = '';
  
  if (loc.sourceType === 'telegram' && loc.link && (loc.hasMedia || loc.mediaType)) {
    mediaHtml = `<div class="popup-media telegram-embed" style="margin-bottom:12px;"><iframe src="${loc.link}?embed=1&dark=1" width="100%" height="auto" frameborder="0" scrolling="no" style="border:none; overflow:hidden; min-height:200px;"></iframe></div>`;
  } else if (loc.sourceType === 'rss' && loc.media) {
    if (loc.media.match(/\\.(mp4|webm|ogg)/i)) {
      mediaHtml = `<div class="popup-media" style="margin-bottom:12px;"><video src="${loc.media}" controls style="width:100%; border-radius:4px; max-height:250px; background:#000;"></video></div>`;
    } else {
      mediaHtml = `<div class="popup-media" style="margin-bottom:12px;"><img src="${loc.media}" alt="Media" style="width:100%; border-radius:4px; max-height:250px; object-fit:cover;" onerror="this.style.display='none'"/></div>`;
    }
  }

  const rawHtml = `
    <div class="map-popup">
      ${titleHtml}
      ${mediaHtml}
      ${descHtml}
      ${linkHtml}
    </div>
  `;
  
  // Sanitize the entire HTML string, allowing tags and attributes for media
  const safeHtml = DOMPurify.sanitize(rawHtml, { 
    ADD_TAGS: ['iframe', 'video', 'img'],
    ADD_ATTR: ['target', 'rel', 'src', 'width', 'height', 'frameborder', 'scrolling', 'style', 'controls', 'alt', 'onerror']
  });

  marker.bindPopup(safeHtml, { className: 'cyber-popup-wrapper', minWidth: 280 });

  markers.value = [...markers.value, marker];
}
</script>

<style scoped>
.monitoring-map-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--overlay-10);
  border-bottom: 1px solid var(--border-color);
  z-index: 10;
}

.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 10px;
}

.subtitle {
  margin: 4px 0 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.pulse-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--accent-orange);
  font-weight: 600;
  background: rgba(var(--accent-rgb), 0.1);
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid rgba(var(--accent-rgb), 0.2);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pulse {
  width: 8px;
  height: 8px;
  background-color: var(--accent-orange);
  border-radius: 50%;
  animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
  0%   { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0.7); }
  70%  { transform: scale(1);    box-shadow: 0 0 0 6px rgba(var(--accent-rgb), 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(var(--accent-rgb), 0); }
}

.map-wrapper {
  flex-grow: 1;
  position: relative;
  min-height: 450px;
}

.leaflet-map {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* --- Leaflet overrides (deep selectors) --- */

:deep(.leaflet-container) {
  background: var(--bg-panel);
  font-family: inherit;
}

:deep(.custom-cyber-marker) {
  background: transparent;
  border: none;
}

:deep(.cyber-pin) {
  width: 12px;
  height: 12px;
  background-color: var(--accent-orange);
  border-radius: 50%;
  position: relative;
  box-shadow: 0 0 10px var(--accent-orange), 0 0 20px var(--accent-orange);
}

:deep(.cyber-pulse-ring) {
  position: absolute;
  top: -6px;
  left: -6px;
  width: 24px;
  height: 24px;
  border: 2px solid var(--accent-orange);
  border-radius: 50%;
  animation: cyber-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

@keyframes cyber-ring {
  0%   { transform: scale(0.5); opacity: 1; border-width: 2px; }
  100% { transform: scale(2.5); opacity: 0; border-width: 0; }
}

:deep(.cyber-popup-wrapper .leaflet-popup-content-wrapper) {
  background: var(--bg-panel);
  border: 1px solid rgba(var(--accent-rgb), 0.4);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
}

:deep(.cyber-popup-wrapper .leaflet-popup-tip) {
  background: var(--bg-panel);
  border-top: 1px solid rgba(var(--accent-rgb), 0.4);
  border-left: 1px solid rgba(var(--accent-rgb), 0.4);
}

:deep(.cyber-popup-wrapper .leaflet-popup-content) {
  margin: 14px 18px;
}

:deep(.popup-title) {
  margin: 0 0 5px 0;
  color: var(--accent-orange);
  font-size: 14px;
  font-weight: 600;
}

:deep(.popup-desc) {
  margin: 0;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.4;
}

:deep(.popup-source-link) {
  display: inline-block;
  margin-top: 8px;
  color: var(--accent-orange);
  text-decoration: none;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

:deep(.leaflet-control-zoom a) {
  background: var(--overlay-10) !important;
  color: var(--text-main) !important;
  border-color: var(--border-color) !important;
}

:deep(.leaflet-control-zoom a:hover) {
  background: var(--bg-panel-hover) !important;
}
</style>

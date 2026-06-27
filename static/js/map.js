/**
 * Shared Leaflet map utilities for village maps and gallery GPS pins.
 */
window.CSPMap = (function () {
  const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const ATTRIBUTION = 'Â© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  const DEFAULT_CENTER = [18.0, 83.0];   // Andhra Pradesh
  const DEFAULT_ZOOM = 11;

  const ACCENT_COLORS = ['#8CC7C4', '#2C687B', '#8CC7C4', '#DB1A1A'];

  function createIcon(color, size = 24) {
    return L.divIcon({
      className: '',
      iconSize: [size, size],
      iconAnchor: [size / 2, size],
      popupAnchor: [0, -size],
      html: `<svg width="${size}" height="${size * 1.3}" viewBox="0 0 24 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="12" cy="30" rx="5" ry="2" fill="rgba(0,0,0,0.3)"/>
        <path d="M12 0C7.03 0 3 4.03 3 9c0 6.75 9 21 9 21s9-14.25 9-21C21 4.03 16.97 0 12 0z" fill="${color}"/>
        <circle cx="12" cy="9" r="4" fill="white" opacity="0.9"/>
      </svg>`,
    });
  }

  function initVillagesMap(mapId, villages) {
    const el = document.getElementById(mapId);
    if (!el || !L) return null;

    const map = L.map(mapId, { zoomControl: true, attributionControl: true });
    L.tileLayer(TILE_URL, { attribution: ATTRIBUTION, maxZoom: 18 }).addTo(map);

    const markers = [];
    villages.forEach((v, i) => {
      if (!v.lat || !v.lng) return;
      const icon = createIcon(v.color || ACCENT_COLORS[i % ACCENT_COLORS.length]);
      const marker = L.marker([v.lat, v.lng], { icon }).addTo(map);
      marker.bindPopup(`
        <div style="min-width:140px;font-family:Inter,sans-serif">
          <div style="font-weight:600;font-size:14px;margin-bottom:4px">${v.name}</div>
          <div style="font-size:12px;color:#64748b">${v.survey_count || 0} responses</div>
          ${v.url ? `<a href="${v.url}" style="font-size:12px;color:#8CC7C4">View details â†’</a>` : ''}
        </div>
      `, { maxWidth: 200 });
      markers.push(marker);
    });

    if (markers.length) {
      const group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.2));
    } else {
      map.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    }

    return map;
  }

  function initSingleVillageMap(mapId, lat, lng, label, color) {
    const el = document.getElementById(mapId);
    if (!el || !L || !lat || !lng) return null;

    const map = L.map(mapId).setView([lat, lng], 13);
    L.tileLayer(TILE_URL, { attribution: ATTRIBUTION, maxZoom: 18 }).addTo(map);

    const icon = createIcon(color || ACCENT_COLORS[0], 28);
    L.marker([lat, lng], { icon }).addTo(map).bindPopup(label || '').openPopup();
    return map;
  }

  function initGalleryMap(mapId, photos) {
    const el = document.getElementById(mapId);
    if (!el || !L) return null;

    const map = L.map(mapId).setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    L.tileLayer(TILE_URL, { attribution: ATTRIBUTION, maxZoom: 18 }).addTo(map);

    const markers = photos
      .filter((p) => p.lat && p.lng)
      .map((p) => {
        const icon = createIcon('#8CC7C4', 20);
        const m = L.marker([p.lat, p.lng], { icon }).addTo(map);
        m.bindPopup(`<img src="${p.thumbnail || p.url}" style="width:120px;height:80px;object-fit:cover;border-radius:6px" loading="lazy"><div style="font-size:12px;margin-top:4px">${p.caption || ''}</div>`, { maxWidth: 150 });
        return m;
      });

    if (markers.length) {
      const group = L.featureGroup(markers);
      map.fitBounds(group.getBounds().pad(0.2));
    }

    return map;
  }

  return { initVillagesMap, initSingleVillageMap, initGalleryMap };
})();


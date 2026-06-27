/**
 * Analytics Dashboard â€” ECharts chart renderers.
 * Receives data from /analytics/data/ and renders all charts.
 */
'use strict';

const DARK_THEME = {
  backgroundColor: 'transparent',
  textStyle: { color: '#6E8A93', fontFamily: 'Inter, sans-serif' },
  categoryAxis: { axisLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.05)' } }, axisLabel: { color: '#6E8A93' } },
  valueAxis: { axisLine: { lineStyle: { color: 'rgba(148,163,184,0.1)' } }, splitLine: { lineStyle: { color: 'rgba(148,163,184,0.05)' } }, axisLabel: { color: '#6E8A93' } },
};

const PALETTE = ['#8CC7C4','#2C687B','#8CC7C4','#DB1A1A','#DB1A1A','#2C687B','#DB1A1A','#DB1A1A'];
const tooltipStyle = {
  backgroundColor: 'rgba(15,23,42,0.95)',
  borderColor: 'rgba(6,182,212,0.2)',
  textStyle: { color: '#FFF6F6', fontFamily: 'Inter, sans-serif', fontSize: 12 },
};

function mkChart(id) {
  const el = document.getElementById(id);
  if (!el) return null;
  const existing = echarts.getInstanceByDom(el);
  if (existing) existing.dispose();
  const chart = echarts.init(el, null, { renderer: 'canvas' });
  window.addEventListener('resize', () => chart.resize());
  return chart;
}

// â”€â”€ Village Comparison â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderVillageComparison(data) {
  const chart = mkChart('chart-village');
  if (!chart || !data.length) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'axis', ...tooltipStyle, axisPointer: { type: 'shadow' } },
    legend: { data: ['Surveys', 'Internet Users'], textStyle: { color: '#6E8A93' }, top: 0 },
    grid: { left: 8, right: 8, bottom: 8, top: 40, containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.village), ...DARK_THEME.categoryAxis },
    yAxis: { type: 'value', ...DARK_THEME.valueAxis },
    series: [
      {
        name: 'Surveys', type: 'bar', barWidth: '35%', barGap: '20%',
        data: data.map(d => d.total),
        itemStyle: { color: PALETTE[0], borderRadius: [4,4,0,0] },
      },
      {
        name: 'Internet Users', type: 'bar', barWidth: '35%',
        data: data.map(d => d.internet_users),
        itemStyle: { color: PALETTE[2], borderRadius: [4,4,0,0] },
      },
    ],
  });
}

// â”€â”€ Age vs Internet Usage â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderAgeInternet(data) {
  const chart = mkChart('chart-age-internet');
  if (!chart || !data.categories) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'axis', ...tooltipStyle, axisPointer: { type: 'shadow' } },
    legend: { data: ['Internet Users', 'Non-Users'], textStyle: { color: '#6E8A93' }, top: 0 },
    grid: { left: 8, right: 8, bottom: 8, top: 40, containLabel: true },
    xAxis: { type: 'category', data: data.categories, ...DARK_THEME.categoryAxis },
    yAxis: { type: 'value', ...DARK_THEME.valueAxis },
    series: [
      { name: 'Internet Users', type: 'bar', stack: 'total', data: data.internet_yes, itemStyle: { color: PALETTE[0], borderRadius: [0,0,0,0] } },
      { name: 'Non-Users', type: 'bar', stack: 'total', data: data.internet_no, itemStyle: { color: 'rgba(148,163,184,0.2)', borderRadius: [4,4,0,0] } },
    ],
  });
}

// â”€â”€ Education vs Awareness â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderEduAwareness(data) {
  const chart = mkChart('chart-edu-awareness');
  if (!chart || !data.categories) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'axis', ...tooltipStyle, formatter: '{b}: {c} / 5' },
    grid: { left: 8, right: 8, bottom: 8, top: 20, containLabel: true },
    xAxis: { type: 'category', data: data.categories, ...DARK_THEME.categoryAxis },
    yAxis: { type: 'value', min: 0, max: 5, ...DARK_THEME.valueAxis,
      axisLabel: { formatter: (v) => ['', 'Very Low', 'Low', 'Moderate', 'High', 'Very High'][v] || '' } },
    series: [{
      type: 'line', smooth: true, data: data.avg_awareness,
      lineStyle: { width: 3, color: PALETTE[1] },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${PALETTE[1]}40` }, { offset: 1, color: `${PALETTE[1]}05` }] } },
      symbol: 'circle', symbolSize: 8,
      itemStyle: { color: PALETTE[1], borderColor: '#fff', borderWidth: 2 },
    }],
  });
}

// â”€â”€ Device Distribution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderDevices(data) {
  const chart = mkChart('chart-devices');
  if (!chart || !data.length) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'item', ...tooltipStyle, formatter: '{b}: {c} ({d}%)' },
    legend: { show: false },
    series: [{
      type: 'pie', radius: ['40%', '72%'], avoidLabelOverlap: false,
      data: data.map((d, i) => ({ name: d.name, value: d.value, itemStyle: { color: PALETTE[i % PALETTE.length] } })),
      label: { color: '#6E8A93', fontSize: 11, formatter: '{b}\n{d}%' },
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
    }],
  });
}

// â”€â”€ Internet Purposes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderPurposes(data) {
  const chart = mkChart('chart-purposes');
  if (!chart || !data.length) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'item', ...tooltipStyle },
    grid: { left: 0, right: 16, bottom: 0, top: 0, containLabel: true },
    xAxis: { type: 'value', ...DARK_THEME.valueAxis },
    yAxis: { type: 'category', data: data.map(d => d.name), ...DARK_THEME.categoryAxis },
    series: [{
      type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: PALETTE[i % PALETTE.length], borderRadius: [0,4,4,0] } })),
    }],
  });
}

// â”€â”€ Connection Types â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderConnection(data) {
  const chart = mkChart('chart-connection');
  if (!chart || !data.length) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'item', ...tooltipStyle, formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie', radius: ['35%', '65%'],
      data: data.map((d, i) => ({ name: d.name, value: d.value, itemStyle: { color: PALETTE[i % PALETTE.length] } })),
      label: { color: '#6E8A93', fontSize: 10 },
    }],
  });
}

// â”€â”€ Hours Distribution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderHours(data) {
  const chart = mkChart('chart-hours');
  if (!chart || !data.length) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'item', ...tooltipStyle },
    grid: { left: 0, right: 16, bottom: 0, top: 0, containLabel: true },
    xAxis: { type: 'value', ...DARK_THEME.valueAxis },
    yAxis: { type: 'category', data: data.map(d => d.name), ...DARK_THEME.categoryAxis },
    series: [{
      type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: PALETTE[(i + 3) % PALETTE.length], borderRadius: [0,4,4,0] } })),
    }],
  });
}

// â”€â”€ Fraud by Village â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderFraud(data) {
  const chart = mkChart('chart-fraud');
  if (!chart || !data.villages) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'axis', ...tooltipStyle, axisPointer: { type: 'shadow' } },
    legend: { data: ['Experienced', 'Not Sure', 'Not Experienced'], textStyle: { color: '#6E8A93' }, top: 0 },
    grid: { left: 8, right: 8, bottom: 8, top: 40, containLabel: true },
    xAxis: { type: 'category', data: data.villages, ...DARK_THEME.categoryAxis },
    yAxis: { type: 'value', ...DARK_THEME.valueAxis },
    series: [
      { name: 'Experienced', type: 'bar', stack: 'f', data: data.yes, itemStyle: { color: PALETTE[4] } },
      { name: 'Not Sure', type: 'bar', stack: 'f', data: data.not_sure, itemStyle: { color: PALETTE[3] } },
      { name: 'Not Experienced', type: 'bar', stack: 'f', data: data.no, itemStyle: { color: PALETTE[2], borderRadius: [4,4,0,0] } },
    ],
  });
}

// â”€â”€ OTP Awareness â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderOtp(data) {
  const chart = mkChart('chart-otp');
  if (!chart || !data.length) return;
  const colors = [PALETTE[2], PALETTE[3], PALETTE[4]];
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'item', ...tooltipStyle, formatter: '{b}: {c} ({d}%)' },
    series: [{
      type: 'pie', radius: ['35%', '68%'],
      data: data.map((d, i) => ({ name: d.name, value: d.value, itemStyle: { color: colors[i % colors.length] } })),
      label: { color: '#6E8A93', fontSize: 10, formatter: '{b}\n{d}%' },
    }],
  });
}

// â”€â”€ Daily Trend â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderTrend(data) {
  const chart = mkChart('chart-trend');
  if (!chart || !data.dates) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { trigger: 'axis', ...tooltipStyle },
    grid: { left: 8, right: 8, bottom: 8, top: 10, containLabel: true },
    xAxis: { type: 'category', data: data.dates, ...DARK_THEME.categoryAxis, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', ...DARK_THEME.valueAxis, minInterval: 1 },
    series: [{
      type: 'line', smooth: true, data: data.counts,
      lineStyle: { width: 2.5, color: PALETTE[0] },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: `${PALETTE[0]}40` }, { offset: 1, color: `${PALETTE[0]}03` }] } },
      symbol: 'none',
    }],
  });
}

// â”€â”€ Awareness Heatmap â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderHeatmap(data) {
  const chart = mkChart('chart-heatmap');
  if (!chart || !data.villages) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { ...tooltipStyle, formatter: (p) => `${data.villages[p.data[0]]} / ${data.age_groups[p.data[1]]}<br>Score: ${p.data[2]}` },
    grid: { left: 8, right: 8, bottom: 8, top: 10, containLabel: true },
    xAxis: { type: 'category', data: data.villages, ...DARK_THEME.categoryAxis, splitArea: { show: true } },
    yAxis: { type: 'category', data: data.age_groups, ...DARK_THEME.categoryAxis, splitArea: { show: true } },
    visualMap: { min: 1, max: 5, calculable: true, orient: 'horizontal', left: 'center', bottom: 0, textStyle: { color: '#6E8A93' }, inRange: { color: ['#DB1A1A','#DB1A1A','#8CC7C4','#8CC7C4','#059669'] } },
    series: [{ type: 'heatmap', data: data.data, label: { show: true, color: '#fff', fontSize: 10 }, emphasis: { itemStyle: { shadowBlur: 10 } } }],
  });
}

// â”€â”€ Occupation Bubble Chart â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function renderOccupation(data) {
  const chart = mkChart('chart-occupation');
  if (!chart || !data.length) return;
  chart.setOption({
    ...DARK_THEME,
    tooltip: { ...tooltipStyle, formatter: (p) => `${p.data[3]}<br>Avg Awareness: ${p.data[0]}/5<br>Internet: ${p.data[1]}%<br>Count: ${p.data[2]}` },
    grid: { left: 8, right: 8, bottom: 8, top: 10, containLabel: true },
    xAxis: { type: 'value', name: 'Avg Awareness', min: 0, max: 5, ...DARK_THEME.valueAxis },
    yAxis: { type: 'value', name: 'Internet %', min: 0, max: 100, ...DARK_THEME.valueAxis },
    series: [{
      type: 'scatter',
      data: data.map((d, i) => ({
        value: [d.avg_awareness, d.internet_pct, d.count, d.label],
        symbolSize: Math.max(16, Math.min(60, d.count * 3)),
        itemStyle: { color: PALETTE[i % PALETTE.length], opacity: 0.8 },
        label: { show: true, formatter: (p) => p.data.value[3], color: '#FFF6F6', fontSize: 10, position: 'top' },
      })),
    }],
  });
}

// â”€â”€ Metric Cards â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function updateMetricCards(data) {
  const vcs = data.village_comparison || [];
  const total = vcs.reduce((s, v) => s + (v.total || 0), 0);
  const internet = vcs.reduce((s, v) => s + (v.internet_users || 0), 0);
  const fraud = (data.fraud_by_village?.yes || []).reduce((s, n) => s + n, 0);
  const otp = data.otp_awareness?.find(d => d.name === 'Yes, I know this')?.value || 0;

  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('m-total', total.toLocaleString());
  set('m-internet', total ? `${Math.round(internet/total*100)}%` : 'â€”');
  set('m-fraud', fraud);
  set('m-otp', otp);
}

// â”€â”€ Main load function (called from template) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
window.loadAnalytics = async function(village = 'all') {
  try {
    const res = await fetch(`/analytics/data/?village=${village}`);
    const data = await res.json();
    updateMetricCards(data);
    renderVillageComparison(data.village_comparison);
    renderAgeInternet(data.age_vs_internet);
    renderEduAwareness(data.education_vs_awareness);
    renderDevices(data.device_distribution);
    renderPurposes(data.purposes);
    renderConnection(data.connection_types);
    renderHours(data.hours_distribution);
    renderFraud(data.fraud_by_village);
    renderOtp(data.otp_awareness);
    renderTrend(data.daily_trend);
    renderHeatmap(data.awareness_heatmap);
    renderOccupation(data.occupation_vs_awareness);
  } catch (err) {
    console.error('Analytics load failed:', err);
  }
};

window.refreshAnalytics = function() {
  const sel = document.getElementById('village-filter');
  loadAnalytics(sel ? sel.value : 'all');
};

// â”€â”€ Auto-insights â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
window.loadInsights = async function() {
  const container = document.getElementById('insights-container');
  if (!container) return;
  try {
    const res = await fetch('/analytics/insights/');
    const data = await res.json();
    const icons = { danger: 'ðŸ”´', warning: 'âš ï¸', info: 'ðŸ’¡', success: 'âœ…' };
    const colorMap = {
      danger: 'insight-danger border', warning: 'insight-warning border',
      info: 'insight-info border', success: 'insight-success border',
    };
    if (!data.insights.length) { container.innerHTML = ''; return; }
    container.innerHTML = `
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        ${data.insights.map((ins, i) => `
          <div class="insight-card rounded-xl p-4 ${colorMap[ins.severity] || 'border border-white/10 bg-white/2'}"
               style="animation-delay: ${i*80}ms">
            <div class="flex items-start gap-3">
              <span class="text-lg">${ins.icon}</span>
              <div>
                <div class="text-xs font-semibold text-slate-300 mb-1">${ins.title}</div>
                <p class="text-xs text-slate-400 leading-relaxed">${ins.text}</p>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    container.innerHTML = '';
  }
};


/* ── Shared API helper ──────────────────────────────── */
const API = {
  async _fetch(url, opts = {}) {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...opts.headers },
      credentials: 'same-origin',
      ...opts,
    });
    if (res.status === 401) {
      window.location.href = '/login';
      throw new Error('Unauthorized');
    }
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(err.error || 'Request failed');
    }
    return res.json();
  },
  get(url) { return this._fetch(url); },
  post(url, body) { return this._fetch(url, { method: 'POST', body: JSON.stringify(body) }); },
  put(url, body) { return this._fetch(url, { method: 'PUT', body: JSON.stringify(body) }); },
  del(url) { return this._fetch(url, { method: 'DELETE' }); },

  // Auth
  verifyPin(pin) { return this.post('/api/auth/verify', { pin }); },
  checkAuth() { return this.get('/api/auth/check'); },
  logout() { return this.post('/api/auth/logout'); },

  // CS2
  cs2Sync() { return this.post('/api/cs2/sync'); },
  cs2Matches() { return this.get('/api/cs2/matches'); },
  cs2DeleteMatch(id) { return this.del(`/api/cs2/matches/${id}`); },
  cs2Comments() { return this.get('/api/cs2/comments'); },
  cs2AddComment(comment) { return this.post('/api/cs2/comments', { comment }); },
  cs2DeleteComment(id) { return this.del(`/api/cs2/comments/${id}`); },
  cs2Profile() { return this.get('/api/cs2/profile'); },
  cs2Training() { return this.get('/api/cs2/training'); },
  cs2AddTraining(data) { return this.post('/api/cs2/training', data); },
  cs2DeleteTraining(id) { return this.del(`/api/cs2/training/${id}`); },

  // Gym
  gymWeight(date) { return this.get('/api/gym/weight' + (date ? `?date=${date}` : '')); },
  gymAddWeight(data) { return this.post('/api/gym/weight', data); },
  gymDeleteWeight(id) { return this.del(`/api/gym/weight/${id}`); },
  gymWeightExercises() { return this.get('/api/gym/weight/exercises'); },
  gymCardio(date) { return this.get('/api/gym/cardio' + (date ? `?date=${date}` : '')); },
  gymAddCardio(data) { return this.post('/api/gym/cardio', data); },
  gymDeleteCardio(id) { return this.del(`/api/gym/cardio/${id}`); },
  gymCardioExercises() { return this.get('/api/gym/cardio/exercises'); },
  gymExercises(type) { return this.get('/api/gym/exercises' + (type ? `?type=${type}` : '')); },
  gymAddExercise(data) { return this.post('/api/gym/exercises', data); },
  gymUpdateExercise(id, data) { return this.put(`/api/gym/exercises/${id}`, data); },
  gymDeleteExercise(id) { return this.del(`/api/gym/exercises/${id}`); },
  gymYoutubeSearch(q) { return this.get(`/api/gym/youtube-search?q=${encodeURIComponent(q)}`); },

  // Weight
  weightAll() { return this.get('/api/weight'); },
  weightAdd(data) { return this.post('/api/weight', data); },
  weightDelete(id) { return this.del(`/api/weight/${id}`); },

  // Mental
  mentalAll() { return this.get('/api/mental'); },
  mentalAdd(data) { return this.post('/api/mental', data); },
  mentalDelete(id) { return this.del(`/api/mental/${id}`); },
};

/* ── Helpers ───────────────────────────────────────── */
function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function formatDate(d) {
  return new Date(d + 'T00:00:00').toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatDateTime(d) {
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function $(sel, parent) { return (parent || document).querySelector(sel); }
function $$(sel, parent) { return [...(parent || document).querySelectorAll(sel)]; }

function el(tag, attrs, ...children) {
  const e = document.createElement(tag);
  if (attrs) Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'className') e.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(e.style, v);
    else if (k.startsWith('on')) e.addEventListener(k.slice(2).toLowerCase(), v);
    else e.setAttribute(k, v);
  });
  children.forEach(c => {
    if (c == null) return;
    if (typeof c === 'string' || typeof c === 'number') e.appendChild(document.createTextNode(c));
    else e.appendChild(c);
  });
  return e;
}

/* ── Tab switching ─────────────────────────────────── */
function initTabs(container) {
  const buttons = $$('.tab-btn', container || document);
  const panels = $$('.tab-panel', container || document);
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.tab;
      const panel = $(`#tab-${target}`, container || document);
      if (panel) panel.classList.add('active');
    });
  });
}

/* ── SVG Icons (inline) ──────────────────────────────── */
const ICONS = {
  crosshair: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>`,
  dumbbell: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6.5 6.5 11 11"/><path d="m21 21-1-1"/><path d="m3 3 1 1"/><path d="m18 22 4-4"/><path d="m2 6 4-4"/><path d="m3 10 7-7"/><path d="m14 21 7-7"/></svg>`,
  scale: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>`,
  brain: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/></svg>`,
  dashboard: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>`,
  arrowRight: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>`,
  refresh: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>`,
  trash: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>`,
  plus: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>`,
  send: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>`,
  menu: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>`,
  lock: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`,
  trendUp: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>`,
  trendDown: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/></svg>`,
  timer: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/></svg>`,
  msg: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/></svg>`,
};

function icon(name, size) {
  const s = size || 16;
  const wrapper = document.createElement('span');
  wrapper.innerHTML = (ICONS[name] || '').replace(/width="24"/g, `width="${s}"`).replace(/height="24"/g, `height="${s}"`);
  wrapper.style.display = 'inline-flex';
  wrapper.style.flexShrink = '0';
  return wrapper;
}

/* ── Period / Time Filtering ──────────────────────────── */
const PERIODS = [
  { key: '1', label: 'Today' },
  { key: '7', label: '7 Days' },
  { key: '30', label: '30 Days' },
  { key: '90', label: '90 Days' },
  { key: 'all', label: 'All Time' },
];

function buildPeriodFilter(containerId, onChange, defaultKey) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = PERIODS.map(p =>
    `<button class="period-btn${p.key === (defaultKey || 'all') ? ' active' : ''}" data-period="${p.key}">${p.label}</button>`
  ).join('');
  container.addEventListener('click', e => {
    const btn = e.target.closest('.period-btn');
    if (!btn) return;
    $$('.period-btn', container).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    onChange(btn.dataset.period);
  });
}

function filterByPeriod(items, period, dateField) {
  if (period === 'all') return items;
  const field = dateField || 'date';
  const days = parseInt(period);
  const cutoff = new Date();
  cutoff.setHours(0, 0, 0, 0);
  cutoff.setDate(cutoff.getDate() - (days - 1));
  return items.filter(item => {
    const d = field === 'timestamp' ? new Date(item[field]) : new Date(item[field] + 'T00:00:00');
    return d >= cutoff;
  });
}


/* ── Chart.js defaults (dark theme) ──────────────────── */
function setChartDefaults() {
  if (typeof Chart === 'undefined') return;
  Chart.defaults.color = '#a1a1aa';
  Chart.defaults.borderColor = '#27272a';
  Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  Chart.defaults.font.size = 12;
  Chart.defaults.plugins.tooltip.backgroundColor = '#18181b';
  Chart.defaults.plugins.tooltip.borderColor = '#27272a';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.titleColor = '#a1a1aa';
  Chart.defaults.plugins.tooltip.bodyColor = '#fafafa';
  Chart.defaults.plugins.legend.labels.boxWidth = 12;
}

document.addEventListener('DOMContentLoaded', setChartDefaults);

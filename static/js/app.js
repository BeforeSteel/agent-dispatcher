// Agent Dispatcher - Frontend Logic & i18n

let agentsData = [];
let currentFilter = 'all';
let searchQuery = '';
let currentLogAgentId = null;
let currentLang = localStorage.getItem('agents_lang') || 'uk';
let i18nDict = {};

// Fallback translations if API fails
const fallbackI18n = {
  uk: {
    "status.running": "Працює", "status.stopped": "Зупинено", "status.ready": "CLI Ready", "status.failed": "Помилка",
    "card.memory": "Пам'ять", "card.cpu": "CPU", "card.uptime": "Аптайм",
    "btn.start": "Запустити", "btn.stop": "Стоп", "btn.restart": "Перезапустити", "btn.logs": "Логи", "btn.open_ui": "Відкрити інтерфейс",
    "btn.scan": "Сканувати", "btn.add": "Додати", "btn.start_all": "Старт всі", "btn.stop_all": "Стоп всі", "btn.theme": "Перемкнути тему (світла/темна)",
    "tab.all": "Всі", "tab.running": "Активні", "tab.web": "Веб-додатки", "tab.cli": "CLI Агенти",
    "search.placeholder": "Пошук агента...",
  },
  en: {
    "status.running": "Running", "status.stopped": "Stopped", "status.ready": "CLI Ready", "status.failed": "Failed",
    "card.memory": "Memory", "card.cpu": "CPU", "card.uptime": "Uptime",
    "btn.start": "Start", "btn.stop": "Stop", "btn.restart": "Restart", "btn.logs": "Logs", "btn.open_ui": "Open Web UI",
    "btn.scan": "Scan", "btn.add": "Add Agent", "btn.start_all": "Start All", "btn.stop_all": "Stop All", "btn.theme": "Toggle theme (light/dark)",
    "tab.all": "All", "tab.running": "Running", "tab.web": "Web Apps", "tab.cli": "CLI Agents",
    "search.placeholder": "Search agent...",
  },
  ru: {
    "status.running": "Работает", "status.stopped": "Остановлен", "status.ready": "CLI Ready", "status.failed": "Ошибка",
    "card.memory": "Память", "card.cpu": "CPU", "card.uptime": "Аптайм",
    "btn.start": "Запустить", "btn.stop": "Стоп", "btn.restart": "Перезапуск", "btn.logs": "Логи", "btn.open_ui": "Открыть интерфейс",
    "btn.scan": "Сканировать", "btn.add": "Добавить", "btn.start_all": "Старт все", "btn.stop_all": "Стоп все", "btn.theme": "Переключить тему (светлая/темная)",
    "tab.all": "Все", "tab.running": "Активные", "tab.web": "Веб-приложения", "tab.cli": "CLI Агенты",
    "search.placeholder": "Поиск агента...",
  }
};

function t(key) {
  if (i18nDict[currentLang] && i18nDict[currentLang][key]) {
    return i18nDict[currentLang][key];
  }
  if (fallbackI18n[currentLang] && fallbackI18n[currentLang][key]) {
    return fallbackI18n[currentLang][key];
  }
  if (fallbackI18n['uk'] && fallbackI18n['uk'][key]) {
    return fallbackI18n['uk'][key];
  }
  return key;
}

// Translate a key and fill {placeholders}
function tf(key, vars = {}) {
  return Object.entries(vars).reduce((str, [name, value]) => str.split(`{${name}}`).join(value), t(key));
}

// Escape untrusted text (agent names, README descriptions, logs) before it goes into innerHTML
function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[ch]));
}

function getAgentName(agent) {
  if (!agent) return '';
  const key = `agent.${agent.id}.name`;
  const translated = t(key);
  if (translated !== key) return translated;
  if (agent.name_i18n && agent.name_i18n[currentLang]) {
    return agent.name_i18n[currentLang];
  }
  return agent.name || agent.id;
}

function getAgentDesc(agent) {
  if (!agent) return '';
  const key = `agent.${agent.id}.desc`;
  const translated = t(key);
  if (translated !== key) return translated;
  if (agent.description_i18n && agent.description_i18n[currentLang]) {
    return agent.description_i18n[currentLang];
  }
  return agent.description || '—';
}

async function loadI18n() {
  try {
    const res = await fetch('/api/i18n');
    const data = await res.json();
    if (data.translations) {
      i18nDict = data.translations;
    }
    if (!localStorage.getItem('agents_lang') && data.current) {
      currentLang = data.current;
    }
  } catch (e) {
    console.warn('Using fallback i18n:', e);
  }
  applyTranslations();
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    el.title = t(key);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = t(key);
  });
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    const key = el.getAttribute('data-i18n-aria');
    el.setAttribute('aria-label', t(key));
  });
  document.querySelectorAll('#logs-line-count option').forEach(opt => {
    opt.textContent = tf('modal.logs.lines', { n: opt.value });
  });

  document.documentElement.lang = currentLang;
  const codeEl = document.getElementById('current-lang-code');
  if (codeEl) {
    codeEl.textContent = { en: 'EN', ru: 'RU' }[currentLang] || 'UA';
  }
  document.querySelectorAll('[data-lang-option]').forEach(el => {
    el.classList.toggle('is-current', el.dataset.langOption === currentLang);
  });
}

// Theme Toggle (Light / Dark)
let currentTheme = localStorage.getItem('agents_theme') || 'dark';

// Sun/moon visibility is handled by `dark:` classes in the markup; this only renders the static icons
function updateThemeIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

function toggleTheme() {
  const htmlEl = document.documentElement;
  if (htmlEl.classList.contains('dark')) {
    htmlEl.classList.remove('dark');
    currentTheme = 'light';
  } else {
    htmlEl.classList.add('dark');
    currentTheme = 'dark';
  }
  localStorage.setItem('agents_theme', currentTheme);
  updateThemeIcons();
}

function toggleLangMenu() {
  const menu = document.getElementById('lang-menu');
  if (menu) menu.classList.toggle('hidden');
}

document.addEventListener('click', (e) => {
  const wrapper = document.getElementById('lang-dropdown-wrapper');
  const menu = document.getElementById('lang-menu');
  if (wrapper && menu && !wrapper.contains(e.target)) {
    menu.classList.add('hidden');
  }
});

document.addEventListener('keydown', (e) => {
  if (e.key !== 'Escape') return;
  const langMenu = document.getElementById('lang-menu');
  if (langMenu) langMenu.classList.add('hidden');
  document.querySelectorAll('.modal-backdrop.open').forEach(modal => closeModal(modal.id));
});

async function changeLang(lang) {
  currentLang = lang;
  localStorage.setItem('agents_lang', lang);
  const langMenu = document.getElementById('lang-menu');
  if (langMenu) langMenu.classList.add('hidden');
  applyTranslations();
  updateSystemStats(lastSystemStats);
  renderCards();
  try {
    await fetch('/api/lang', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang: lang })
    });
  } catch (e) {}
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  updateThemeIcons();
  loadI18n();
  fetchStatus();
  setInterval(() => {
    fetchStatus(false);
  }, 3500);
});

// Toast notifications
const TOAST_STYLES = {
  success: {
    icon: 'circle-check',
    classes: 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/90 dark:text-emerald-200 dark:border-emerald-800'
  },
  error: {
    icon: 'circle-alert',
    classes: 'bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-950/90 dark:text-rose-200 dark:border-rose-800'
  },
  info: {
    icon: 'info',
    classes: 'bg-white text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-200 dark:border-slate-700'
  }
};

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const style = TOAST_STYLES[type] || TOAST_STYLES.info;
  const toast = document.createElement('div');
  toast.className = `px-4 py-2.5 rounded-xl border shadow-xl text-xs flex items-center gap-2 pointer-events-auto transition transform duration-200 translate-y-2 opacity-0 ${style.classes}`;
  toast.innerHTML = `<i data-lucide="${style.icon}" class="w-4 h-4 shrink-0"></i><span class="min-w-0 break-words"></span>`;
  toast.lastElementChild.textContent = message;
  container.appendChild(toast);
  lucide.createIcons();

  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 200);
  }, 3200);
}

// Fetch live status
async function fetchStatus(manual = false) {
  const refreshBtn = document.getElementById('refresh-btn');
  const refreshIcon = refreshBtn && refreshBtn.querySelector('svg, i');
  if (manual && refreshIcon) {
    refreshIcon.classList.add('animate-spin');
  }

  try {
    const res = await fetch(`/api/status?lang=${encodeURIComponent(currentLang)}`);
    const data = await res.json();
    if (data.ok) {
      agentsData = data.agents || [];
      updateSystemStats(data.system);
      renderCards();
      updateCounters();
    }
  } catch (err) {
    console.error('Failed to fetch status:', err);
  } finally {
    if (manual && refreshIcon) {
      setTimeout(() => refreshIcon.classList.remove('animate-spin'), 300);
    }
  }
}

// Update system metric tiles (CPU, RAM, Host + GPU)
let lastSystemStats = null;

function setStatBar(id, percent, warnAt = 60, critAt = 85) {
  const bar = document.getElementById(id);
  if (!bar) return;
  const pct = Math.max(0, Math.min(100, Number(percent) || 0));
  bar.style.width = `${pct}%`;
  bar.dataset.level = pct >= critAt ? 'crit' : (pct >= warnAt ? 'warn' : 'ok');
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function updateSystemStats(sys) {
  if (!sys) return;
  lastSystemStats = sys;

  if (sys.cpu_percent !== undefined) {
    setText('stat-cpu', `${sys.cpu_percent}%`);
    setStatBar('stat-cpu-bar', sys.cpu_percent);
    if (sys.cpu_count) setText('stat-cpu-sub', `${sys.cpu_count} ${t('stats.cores')}`);
  }
  if (sys.memory_used_gb !== undefined) {
    setText('stat-ram', `${sys.memory_used_gb} GB`);
    setStatBar('stat-ram-bar', sys.memory_percent);
    setText('stat-ram-sub', `${t('stats.of')} ${sys.memory_total_gb} GB · ${Math.round(sys.memory_percent)}%`);
  }
  if (sys.hostname) {
    setText('stat-host', sys.hostname);
    const ips = sys.ips || {};
    const addr = ips.tailscale || ips.lan;
    setText('stat-host-sub', addr || ' ');
  }

  // GPU tiles: load %, VRAM, temperature (hidden when no GPU is present)
  const gpu = sys.gpu && sys.gpu.available ? sys.gpu : null;
  document.querySelectorAll('[data-gpu]').forEach(tile => tile.classList.toggle('hidden', !gpu));
  const statsGrid = document.getElementById('stats-grid');
  if (statsGrid) statsGrid.dataset.tiles = gpu ? '6' : '3';
  if (!gpu) return;

  if (gpu.gpu_util_percent !== undefined) {
    setText('stat-gpu-load', `${gpu.gpu_util_percent}%`);
    setStatBar('stat-gpu-load-bar', gpu.gpu_util_percent, 50, 85);
    setText('stat-gpu-sub', gpu.name || ' ');
  }
  if (gpu.mem_used_gb !== undefined) {
    setText('stat-gpu-vram', `${gpu.mem_used_gb} GB`);
    setStatBar('stat-gpu-vram-bar', gpu.mem_percent, 70, 90);
    setText('stat-gpu-vram-sub', `${t('stats.of')} ${gpu.mem_total_gb} GB · ${Math.round(gpu.mem_percent)}%`);
  }
  if (gpu.temperature_c !== undefined) {
    setText('stat-gpu-temp', `${gpu.temperature_c}°C`);
    setStatBar('stat-gpu-temp-bar', gpu.temperature_c, 70, 80);
    setText('stat-gpu-power', gpu.power_w ? `${gpu.power_w} W / ${gpu.power_limit_w} W` : ' ');
  }
}

// Filter / search matching
function matchesFilter(agent, filter) {
  if (filter === 'running') return !!agent.is_running;
  if (filter === 'web_app') return !!agent.port || agent.category === 'web_app';
  if (filter === 'cli') return agent.type === 'cli';
  return true;
}

// Update filter counters
function updateCounters() {
  ['all', 'running', 'web_app', 'cli'].forEach(filter => {
    const el = document.getElementById(`count-${filter}`);
    if (el) el.textContent = agentsData.filter(a => matchesFilter(a, filter)).length;
  });
}

// Filter and search
function setFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.tab-btn').forEach(btn => {
    const isActive = btn.dataset.tab === filter;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-selected', isActive);
  });
  renderCards();
}

function onSearchChange() {
  const input = document.getElementById('search-input');
  searchQuery = (input ? input.value : '').toLowerCase().trim();
  renderCards();
}

// Render cards (skips the DOM swap when nothing visible changed, so hover/focus survive polling)
let lastGridHTML = '';

function renderCards() {
  const grid = document.getElementById('agents-grid');
  if (!grid) return;

  const filtered = agentsData.filter(agent => {
    if (!matchesFilter(agent, currentFilter)) return false;

    // Filter by search
    if (searchQuery) {
      const matchId = (agent.id || '').toLowerCase().includes(searchQuery);
      const matchName = (getAgentName(agent) || agent.name || '').toLowerCase().includes(searchQuery);
      const matchDesc = (getAgentDesc(agent) || agent.description || '').toLowerCase().includes(searchQuery);
      if (!matchId && !matchName && !matchDesc) return false;
    }
    return true;
  });

  const html = filtered.length === 0
    ? `
      <div class="col-span-full py-16 text-center text-slate-500 dark:text-slate-400">
        <i data-lucide="package-search" class="w-10 h-10 mx-auto text-slate-400 dark:text-slate-600 mb-3"></i>
        <p class="text-sm">${esc(t('state.empty'))}</p>
      </div>
    `
    : filtered.map(agent => buildCardHTML(agent)).join('');

  if (html === lastGridHTML) return;
  lastGridHTML = html;
  grid.innerHTML = html;
  lucide.createIcons();
}

// Status badge
function buildStatusBadge(agent) {
  const base = 'inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap px-2 py-0.5 rounded-full text-xs font-medium border';
  const hint = agent.error_message ? ` title="${esc(agent.error_message)}"` : '';

  if (agent.is_running) {
    return `
      <span class="${base} bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/25">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        ${t('status.running')}
      </span>`;
  }
  if (agent.status === 'MISSING') {
    return `
      <span class="${base} bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/25"${hint}>
        <i data-lucide="triangle-alert" class="w-3 h-3"></i>
        ${t('status.missing')}
      </span>`;
  }
  if (agent.status === 'FAILED') {
    return `
      <span class="${base} bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/25"${hint}>
        <i data-lucide="circle-alert" class="w-3 h-3"></i>
        ${t('status.failed')}
      </span>`;
  }
  if (agent.type === 'cli') {
    return `
      <span class="${base} bg-cyan-500/10 text-cyan-700 dark:text-cyan-400 border-cyan-500/25">
        <i data-lucide="zap" class="w-3 h-3"></i>
        ${t('status.ready')}
      </span>`;
  }
  return `
    <span class="${base} bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700">
      <span class="w-1.5 h-1.5 rounded-full bg-slate-400 dark:bg-slate-500"></span>
      ${t('status.stopped')}
    </span>`;
}

const TYPE_CHIP_COLORS = {
  daemon: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
  systemd: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
  docker: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
  cli: 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border-cyan-500/20'
};
const TYPE_CHIP_FALLBACK = 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 border-slate-200 dark:border-slate-700';

// Single card template
function buildCardHTML(agent) {
  const isRunning = agent.is_running;
  const isCli = agent.type === 'cli';
  const name = esc(getAgentName(agent));
  const idArg = esc(JSON.stringify(agent.id));

  const typeClass = TYPE_CHIP_COLORS[agent.type] || TYPE_CHIP_FALLBACK;
  const portChip = agent.port
    ? `<span class="font-mono text-[10px] px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">:${esc(agent.port)}</span>`
    : '';

  // Metrics
  let metricsHTML = '';
  if (isRunning) {
    const memory = agent.memory_mb ? `${agent.memory_mb.toFixed(0)} MB` : '—';
    const cpu = agent.cpu_percent != null ? `${agent.cpu_percent}%` : '—';
    metricsHTML = `
      <div class="mt-3 grid grid-cols-3 gap-2 py-2 px-3 bg-slate-50 dark:bg-slate-950/60 rounded-xl border border-slate-200 dark:border-slate-800/80 text-xs">
        <div class="min-w-0">
          <span class="text-slate-400 dark:text-slate-500 block text-[10px]">${t('card.memory')}</span>
          <span class="font-mono text-slate-700 dark:text-slate-200">${esc(memory)}</span>
        </div>
        <div class="min-w-0">
          <span class="text-slate-400 dark:text-slate-500 block text-[10px]">${t('card.cpu')}</span>
          <span class="font-mono text-slate-700 dark:text-slate-200">${esc(cpu)}</span>
        </div>
        <div class="min-w-0">
          <span class="text-slate-400 dark:text-slate-500 block text-[10px]">${t('card.uptime')}</span>
          <span class="font-mono text-slate-700 dark:text-slate-200 truncate block">${esc(agent.uptime || '—')}</span>
        </div>
      </div>
    `;
  }

  // Open-UI link: only live when the service is running, otherwise it would lead to a dead page
  let urlButton = '';
  if (agent.port) {
    const mainUrl = agent.urls && agent.urls.length > 0 ? agent.urls[0].url : `http://localhost:${agent.port}`;
    const openTitle = esc(t('btn.open_ui'));
    urlButton = isRunning
      ? `
      <a href="${esc(mainUrl)}" target="_blank" rel="noopener" title="${openTitle}" aria-label="${openTitle}" class="icon-btn hover:!text-blue-600 dark:hover:!text-blue-400">
        <i data-lucide="external-link" class="w-4 h-4"></i>
      </a>`
      : `
      <span aria-disabled="true" title="${openTitle}" class="icon-btn !shadow-none opacity-40 cursor-not-allowed hover:!bg-slate-100 dark:hover:!bg-slate-800">
        <i data-lucide="external-link" class="w-4 h-4"></i>
      </span>`;
  }

  const logsButton = `
    <button onclick="openLogsModal(${idArg})" class="icon-btn" title="${esc(t('btn.logs'))}" aria-label="${esc(t('btn.logs'))}">
      <i data-lucide="file-text" class="w-4 h-4"></i>
    </button>`;
  const actionBase = 'flex-1 h-9 px-3 inline-flex items-center justify-center gap-1.5 rounded-lg border text-xs font-medium transition';

  // Action buttons
  let controlButtons = '';
  if (isCli) {
    controlButtons = `
      <div class="flex w-full items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/60 px-2.5 py-2 font-mono text-xs text-slate-600 dark:text-slate-300">
        <i data-lucide="terminal" class="w-3.5 h-3.5 shrink-0 text-cyan-500 dark:text-cyan-400"></i>
        <span class="truncate">agents run ${esc(agent.id)}</span>
      </div>
    `;
  } else if (isRunning) {
    controlButtons = `
      <div class="flex items-center gap-2 w-full">
        <button onclick="stopAgent(${idArg})" class="${actionBase} bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 dark:text-rose-300 border-rose-500/30">
          <i data-lucide="square" class="w-3.5 h-3.5"></i>
          <span>${t('btn.stop')}</span>
        </button>
        <button onclick="restartAgent(${idArg})" class="icon-btn" title="${esc(t('btn.restart'))}" aria-label="${esc(t('btn.restart'))}">
          <i data-lucide="rotate-cw" class="w-4 h-4"></i>
        </button>
        ${logsButton}
        ${urlButton}
      </div>
    `;
  } else {
    controlButtons = `
      <div class="flex items-center gap-2 w-full">
        <button onclick="startAgent(${idArg})" class="${actionBase} bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 dark:text-emerald-300 border-emerald-500/30">
          <i data-lucide="play" class="w-3.5 h-3.5"></i>
          <span>${t('btn.start')}</span>
        </button>
        ${logsButton}
        ${urlButton}
      </div>
    `;
  }

  const borderClass = isRunning
    ? 'border-emerald-500/30 dark:border-emerald-500/25'
    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700';

  return `
    <article class="flex flex-col gap-4 bg-white dark:bg-slate-900 border ${borderClass} rounded-2xl p-4 shadow-sm transition">
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <h3 class="font-bold text-slate-900 dark:text-white text-sm tracking-tight leading-snug line-clamp-2 break-words" title="${name}">${name}</h3>
            <div class="mt-1.5 flex flex-wrap items-center gap-1.5">
              <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border ${typeClass}">${esc(agent.type)}</span>
              <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500">${esc(agent.id)}</span>
              ${portChip}
            </div>
          </div>
          ${buildStatusBadge(agent)}
        </div>
        <p class="mt-3 text-xs leading-relaxed text-slate-500 dark:text-slate-400 line-clamp-2" title="${esc(getAgentDesc(agent))}">${esc(getAgentDesc(agent))}</p>
        ${metricsHTML}
      </div>

      <div class="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
        ${controlButtons}
      </div>
    </article>
  `;
}

// Agent Actions
async function runAgentAction(id, action, progressKey) {
  showToast(tf(progressKey, { id }), 'info');
  try {
    const res = await fetch(`/api/agents/${encodeURIComponent(id)}/${action}`, { method: 'POST' });
    const data = await res.json();
    showToast(data.message, data.ok ? 'success' : 'error');
    if (data.ok) fetchStatus();
  } catch (err) {
    showToast(tf('toast.error', { err }), 'error');
  }
}

function startAgent(id) { return runAgentAction(id, 'start', 'toast.starting'); }
function stopAgent(id) { return runAgentAction(id, 'stop', 'toast.stopping'); }
function restartAgent(id) { return runAgentAction(id, 'restart', 'toast.restarting'); }

async function batchAction(action) {
  showToast(t('toast.batch_running'), 'info');
  try {
    const res = await fetch(`/api/batch/${action}`, { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showToast(t('toast.batch_done'), 'success');
      fetchStatus();
    }
  } catch (err) {
    showToast(tf('toast.error', { err }), 'error');
  }
}

// Modal helpers
let backdropMouseDown = false;

document.addEventListener('mousedown', (e) => {
  backdropMouseDown = e.target.classList.contains('modal-backdrop');
});

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add('open');
  document.body.classList.add('overflow-hidden');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('open');
  if (!document.querySelector('.modal-backdrop.open')) {
    document.body.classList.remove('overflow-hidden');
  }
}

// Close only on a real click on the dimmed area, not when a text selection drag ends there
function onBackdropClick(event, modalId) {
  if (event.target === event.currentTarget && backdropMouseDown) closeModal(modalId);
}

// Log Viewer
const ANSI_COLORS = {
  30: '#64748b', 31: '#f87171', 32: '#4ade80', 33: '#fbbf24', 34: '#60a5fa', 35: '#c084fc', 36: '#22d3ee', 37: '#e2e8f0',
  90: '#94a3b8', 91: '#fca5a5', 92: '#86efac', 93: '#fde68a', 94: '#93c5fd', 95: '#d8b4fe', 96: '#67e8f9', 97: '#f8fafc'
};

// Turn ANSI SGR color codes in raw log text into styled spans (other escape sequences are dropped)
function ansiToHtml(raw) {
  const parts = esc(raw).split(/\x1b\[([0-9;?]*)([A-Za-z])/);
  let fg = null;
  let bold = false;
  let html = '';

  for (let i = 0; i < parts.length; i += 3) {
    const text = parts[i];
    if (text) {
      const style = [fg ? `color:${fg}` : '', bold ? 'font-weight:600' : ''].filter(Boolean).join(';');
      html += style ? `<span style="${style}">${text}</span>` : text;
    }
    if (parts[i + 2] !== 'm') continue;

    const codes = (parts[i + 1] || '0').split(';').map(Number);
    for (let c = 0; c < codes.length; c++) {
      const code = codes[c];
      if (code === 0) { fg = null; bold = false; }
      else if (code === 1) bold = true;
      else if (code === 22) bold = false;
      else if (code === 39) fg = null;
      else if (ANSI_COLORS[code]) fg = ANSI_COLORS[code];
      else if (code === 38 || code === 48) c += codes[c + 1] === 5 ? 2 : 4; // skip 256-color / truecolor args
    }
  }
  return html;
}

function openLogsModal(id) {
  currentLogAgentId = id;
  const title = document.getElementById('modal-logs-title');
  const container = document.getElementById('logs-content');
  const ag = agentsData.find(a => a.id === id);
  const agentName = ag ? getAgentName(ag) : id;
  if (title) title.textContent = `${t('modal.logs.title')}: ${agentName}`;
  if (container) container.textContent = t('modal.logs.loading');
  openModal('modal-logs');
  fetchLogs(id);
}

async function fetchLogs(id) {
  if (!id) return;
  const container = document.getElementById('logs-content');
  const countSelect = document.getElementById('logs-line-count');
  const lines = countSelect ? countSelect.value : 50;

  try {
    const res = await fetch(`/api/agents/${encodeURIComponent(id)}/logs?lines=${lines}`);
    const data = await res.json();
    if (data.ok && container) {
      const text = (data.lines || []).join('\n');
      if (text.trim()) {
        container.innerHTML = ansiToHtml(text);
      } else {
        container.textContent = t('modal.logs.empty');
      }
      container.scrollTop = container.scrollHeight;
    }
  } catch (err) {
    if (container) container.textContent = tf('modal.logs.error', { err });
  }
}

// Discovery Scan
let scanCandidates = [];

function buildScanRowHTML(c, index) {
  const typeClass = TYPE_CHIP_COLORS[c.type] || TYPE_CHIP_FALLBACK;
  // The same app can be found under another id (project folder vs systemd unit): name the registered one
  const registeredLabel = c.registered_as && c.registered_as !== c.id
    ? tf('modal.scan.registered_as', { id: c.registered_as })
    : t('modal.scan.registered');
  const action = c.is_registered
    ? `<span class="inline-flex max-w-[11rem] items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-xs leading-tight">
        <i data-lucide="check" class="w-3.5 h-3.5 shrink-0 text-emerald-500"></i><span class="break-words min-w-0">${esc(registeredLabel)}</span>
      </span>`
    : `<button onclick="registerFromScan(${index})" class="btn-primary">
        <i data-lucide="plus" class="w-3.5 h-3.5"></i>${esc(t('modal.scan.add'))}
      </button>`;

  return `
    <div class="p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-200 dark:border-slate-800 flex items-start sm:items-center justify-between gap-3 text-xs ${c.is_registered ? 'opacity-70' : ''}">
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span class="font-bold text-sm text-slate-900 dark:text-white break-words">${esc(c.name)}</span>
          <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border ${typeClass}">${esc(c.type)}</span>
          ${c.port ? `<span class="font-mono text-[10px] px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400">:${esc(c.port)}</span>` : ''}
        </div>
        <p class="mt-1 text-slate-600 dark:text-slate-400 line-clamp-2 break-words">${esc(c.description || '—')}</p>
        <p class="mt-1.5 flex items-center gap-1.5 font-mono text-[10px] text-slate-400 dark:text-slate-500" title="${esc(c.working_dir || '')}">
          <span class="shrink-0 rounded bg-slate-200 dark:bg-slate-800 px-1 py-px">${esc(c.id)}</span>
          <span class="truncate">${esc(c.working_dir || '')}</span>
        </p>
      </div>
      <div class="shrink-0">${action}</div>
    </div>
  `;
}

async function openScanModal() {
  const container = document.getElementById('scan-results-container');
  openModal('modal-scan');

  if (container) {
    container.innerHTML = `
      <div class="flex flex-col items-center gap-2 py-10 text-sm text-center text-slate-400 dark:text-slate-500">
        <i data-lucide="loader-circle" class="w-6 h-6 animate-spin text-blue-500"></i>
        <span>${esc(t('modal.scan.loading'))}</span>
      </div>`;
    lucide.createIcons();
  }

  try {
    const res = await fetch('/api/scan');
    const data = await res.json();
    if (data.ok && container) {
      // Not-yet-registered candidates first; sort is stable so the scan order is kept within each group
      scanCandidates = (data.candidates || []).slice().sort((a, b) => Number(!!a.is_registered) - Number(!!b.is_registered));
      if (scanCandidates.length === 0) {
        container.innerHTML = `<p class="text-center text-slate-400 py-6 text-xs">${esc(t('modal.scan.empty'))}</p>`;
        return;
      }

      container.innerHTML = scanCandidates.map((c, i) => buildScanRowHTML(c, i)).join('');
      lucide.createIcons();
    }
  } catch (err) {
    if (container) container.innerHTML = `<p class="text-rose-500 dark:text-rose-400 text-center py-6 text-xs">${esc(tf('modal.scan.error', { err }))}</p>`;
  }
}

async function registerFromScan(index) {
  const cand = scanCandidates[index];
  if (!cand) return;
  try {
    const res = await fetch('/api/agents/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cand)
    });
    const data = await res.json();
    if (data.ok) {
      showToast(tf('toast.added', { name: cand.name }), 'success');
      openScanModal();
      fetchStatus();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast(tf('toast.error', { err }), 'error');
  }
}

// Add Custom Modal
function openAddModal() {
  openModal('modal-add');
  setTimeout(() => {
    const first = document.getElementById('add-id');
    if (first) first.focus();
  }, 50);
}

async function submitAddAgent(e) {
  e.preventDefault();
  const id = document.getElementById('add-id').value.trim();
  const name = document.getElementById('add-name').value.trim();
  const desc = document.getElementById('add-desc').value.trim();
  const type = document.getElementById('add-type').value;
  const portVal = document.getElementById('add-port').value.trim();
  const port = portVal ? parseInt(portVal) : null;
  const dir = document.getElementById('add-dir').value.trim() || null;
  const cmd = document.getElementById('add-cmd').value.trim() || null;

  const payload = {
    id: id,
    name: name,
    description: desc,
    type: type,
    category: port ? 'web_app' : (type === 'cli' ? 'cli_tool' : 'daemon'),
    port: port,
    working_dir: dir,
    start_cmd: cmd
  };

  try {
    const res = await fetch('/api/agents/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.ok) {
      showToast(tf('toast.added', { name }), 'success');
      document.getElementById('add-agent-form').reset();
      closeModal('modal-add');
      fetchStatus();
    } else {
      showToast(data.message, 'error');
    }
  } catch (err) {
    showToast(tf('toast.error', { err }), 'error');
  }
}

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
    "btn.scan": "Сканувати", "btn.add": "Додати", "btn.start_all": "Старт всі", "btn.stop_all": "Стоп всі",
    "tab.all": "Всі", "tab.running": "🟢 Активні", "tab.web": "🌐 Веб-додатки", "tab.cli": "⚡ CLI Агенти",
    "search.placeholder": "Пошук агента...",
  },
  en: {
    "status.running": "Running", "status.stopped": "Stopped", "status.ready": "CLI Ready", "status.failed": "Failed",
    "card.memory": "Memory", "card.cpu": "CPU", "card.uptime": "Uptime",
    "btn.start": "Start", "btn.stop": "Stop", "btn.restart": "Restart", "btn.logs": "Logs", "btn.open_ui": "Open Web UI",
    "btn.scan": "Scan", "btn.add": "Add Agent", "btn.start_all": "Start All", "btn.stop_all": "Stop All",
    "tab.all": "All", "tab.running": "🟢 Running", "tab.web": "🌐 Web Apps", "tab.cli": "⚡ CLI Agents",
    "search.placeholder": "Search agent...",
  },
  ru: {
    "status.running": "Работает", "status.stopped": "Остановлен", "status.ready": "CLI Ready", "status.failed": "Ошибка",
    "card.memory": "Память", "card.cpu": "CPU", "card.uptime": "Аптайм",
    "btn.start": "Запустить", "btn.stop": "Стоп", "btn.restart": "Перезапуск", "btn.logs": "Логи", "btn.open_ui": "Открыть интерфейс",
    "btn.scan": "Сканировать", "btn.add": "Добавить", "btn.start_all": "Старт все", "btn.stop_all": "Стоп все",
    "tab.all": "Все", "tab.running": "🟢 Активные", "tab.web": "🌐 Веб-приложения", "tab.cli": "⚡ CLI Агенты",
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
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = t(key);
  });

  const flagEl = document.getElementById('current-lang-flag');
  const codeEl = document.getElementById('current-lang-code');
  if (flagEl && codeEl) {
    if (currentLang === 'en') {
      flagEl.textContent = '🇬🇧';
      codeEl.textContent = 'EN';
    } else if (currentLang === 'ru') {
      flagEl.textContent = '🌐';
      codeEl.textContent = 'RU';
    } else {
      flagEl.textContent = '🇺🇦';
      codeEl.textContent = 'UA';
    }
  }
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

async function changeLang(lang) {
  currentLang = lang;
  localStorage.setItem('agents_lang', lang);
  toggleLangMenu();
  applyTranslations();
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
  loadI18n();
  fetchStatus();
  setInterval(() => {
    fetchStatus(false);
  }, 3500);
});

// Toast notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  const colors = {
    success: 'bg-emerald-900/90 text-emerald-200 border-emerald-700',
    error: 'bg-rose-900/90 text-rose-200 border-rose-700',
    info: 'bg-slate-800 text-slate-200 border-slate-700'
  };
  toast.className = `px-4 py-2.5 rounded-xl border shadow-xl text-xs flex items-center space-x-2 pointer-events-auto transition transform duration-200 translate-y-2 opacity-0 ${colors[type] || colors.info}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

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
  if (manual && refreshBtn) {
    refreshBtn.classList.add('animate-spin');
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
    if (manual && refreshBtn) {
      setTimeout(() => refreshBtn.classList.remove('animate-spin'), 300);
    }
  }
}

// Update Topbar system metrics (CPU, RAM, Host + GPU)
function updateSystemStats(sys) {
  if (!sys) return;
  const cpuEl = document.getElementById('stat-cpu');
  const ramEl = document.getElementById('stat-ram');
  const hostEl = document.getElementById('stat-host');

  if (cpuEl && sys.cpu_percent !== undefined) {
    cpuEl.textContent = `${sys.cpu_percent}%`;
  }
  if (ramEl && sys.memory_used_gb !== undefined) {
    ramEl.textContent = `${sys.memory_used_gb}/${sys.memory_total_gb} GB`;
  }
  if (hostEl && sys.hostname) {
    hostEl.textContent = sys.hostname;
  }

  // GPU 3 Основних Параметри (Load %, VRAM, Temperature)
  const gpuBar = document.getElementById('gpu-monitor-bar');
  const gpuLoadEl = document.getElementById('stat-gpu-load');
  const gpuVramEl = document.getElementById('stat-gpu-vram');
  const gpuTempEl = document.getElementById('stat-gpu-temp');

  if (sys.gpu && sys.gpu.available) {
    if (gpuBar) {
      gpuBar.classList.remove('hidden');
      const powerStr = sys.gpu.power_w ? ` • ${sys.gpu.power_w}W / ${sys.gpu.power_limit_w}W` : '';
      gpuBar.title = `${sys.gpu.name}${powerStr}`;
    }
    // Параметр 1: Завантаження GPU %
    if (gpuLoadEl && sys.gpu.gpu_util_percent !== undefined) {
      gpuLoadEl.textContent = `${sys.gpu.gpu_util_percent}%`;
      if (sys.gpu.gpu_util_percent >= 85) {
        gpuLoadEl.className = 'font-mono font-bold text-rose-400';
      } else if (sys.gpu.gpu_util_percent >= 50) {
        gpuLoadEl.className = 'font-mono font-bold text-amber-400';
      } else {
        gpuLoadEl.className = 'font-mono font-bold text-emerald-300';
      }
    }
    // Параметр 2: Відеопам'ять VRAM
    if (gpuVramEl && sys.gpu.mem_used_gb !== undefined) {
      gpuVramEl.textContent = `${sys.gpu.mem_used_gb} / ${sys.gpu.mem_total_gb} GB`;
    }
    // Параметр 3: Температура
    if (gpuTempEl && sys.gpu.temperature_c !== undefined) {
      gpuTempEl.textContent = `${sys.gpu.temperature_c}°C`;
      if (sys.gpu.temperature_c >= 80) {
        gpuTempEl.className = 'font-mono font-medium text-rose-400';
      } else if (sys.gpu.temperature_c >= 70) {
        gpuTempEl.className = 'font-mono font-medium text-amber-400';
      } else {
        gpuTempEl.className = 'font-mono font-medium text-amber-300';
      }
    }
  } else if (gpuBar) {
    gpuBar.classList.add('hidden');
  }
}

// Update filter counters
function updateCounters() {
  const countAll = document.getElementById('count-all');
  const countRunning = document.getElementById('count-running');

  if (countAll) countAll.textContent = agentsData.length;
  if (countRunning) {
    const active = agentsData.filter(a => a.is_running).length;
    countRunning.textContent = active;
  }
}

// Filter and search
function setFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.tab-btn').forEach(btn => {
    if (btn.dataset.tab === filter) {
      btn.className = 'tab-btn active px-3 py-1.5 rounded-lg font-medium transition text-white bg-blue-600';
    } else {
      btn.className = 'tab-btn px-3 py-1.5 rounded-lg font-medium transition text-slate-400 hover:text-white';
    }
  });
  renderCards();
}

function onSearchChange() {
  const input = document.getElementById('search-input');
  searchQuery = (input ? input.value : '').toLowerCase().trim();
  renderCards();
}

// Render cards
function renderCards() {
  const grid = document.getElementById('agents-grid');
  if (!grid) return;

  const filtered = agentsData.filter(agent => {
    // Filter by tab
    if (currentFilter === 'running' && !agent.is_running) return false;
    if (currentFilter === 'web_app' && !agent.port && agent.category !== 'web_app') return false;
    if (currentFilter === 'cli' && agent.type !== 'cli') return false;

    // Filter by search
    if (searchQuery) {
      const matchId = (agent.id || '').toLowerCase().includes(searchQuery);
      const matchName = (getAgentName(agent) || agent.name || '').toLowerCase().includes(searchQuery);
      const matchDesc = (getAgentDesc(agent) || agent.description || '').toLowerCase().includes(searchQuery);
      if (!matchId && !matchName && !matchDesc) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-500">
        <i data-lucide="package-search" class="w-10 h-10 mx-auto text-slate-600 mb-3"></i>
        <p class="text-sm">Жодного агента не знайдено за заданими критеріями.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  grid.innerHTML = filtered.map(agent => buildCardHTML(agent)).join('');
  lucide.createIcons();
}

// Single card template
function buildCardHTML(agent) {
  const isRunning = agent.is_running;
  const isCli = agent.type === 'cli';

  // Status badge
  let statusBadge = '';
  if (isRunning) {
    statusBadge = `
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
        ${t('status.running')}
      </span>`;
  } else if (isCli) {
    statusBadge = `
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
        <i data-lucide="zap" class="w-3 h-3 mr-1"></i>
        ${t('status.ready')}
      </span>`;
  } else if (agent.status === 'FAILED') {
    statusBadge = `
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
        ${t('status.failed')}
      </span>`;
  } else {
    statusBadge = `
      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
        ${t('status.stopped')}
      </span>`;
  }

  // Type tag
  const typeColors = {
    daemon: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    systemd: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    docker: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    cli: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
  };
  const typeClass = typeColors[agent.type] || 'bg-slate-800 text-slate-400 border-slate-700';

  // Metrics
  let metricsHTML = '';
  if (isRunning) {
    metricsHTML = `
      <div class="grid grid-cols-3 gap-2 py-2 px-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs">
        <div>
          <span class="text-slate-500 block text-[10px]">${t('card.memory')}</span>
          <span class="font-mono text-slate-200">${agent.memory_mb ? agent.memory_mb.toFixed(0) + ' MB' : 'active'}</span>
        </div>
        <div>
          <span class="text-slate-500 block text-[10px]">${t('card.cpu')}</span>
          <span class="font-mono text-slate-200">${agent.cpu_percent !== null ? agent.cpu_percent + '%' : '0%'}</span>
        </div>
        <div>
          <span class="text-slate-500 block text-[10px]">${t('card.uptime')}</span>
          <span class="font-mono text-slate-200">${agent.uptime || '—'}</span>
        </div>
      </div>
    `;
  }

  // URL link if port
  let urlButton = '';
  if (agent.port) {
    const mainUrl = agent.urls && agent.urls.length > 0 ? agent.urls[0].url : `http://localhost:${agent.port}`;
    urlButton = `
      <a href="${mainUrl}" target="_blank" title="${t('btn.open_ui')}" class="p-2 bg-slate-800 hover:bg-blue-600/30 hover:text-blue-400 text-slate-300 rounded-lg border border-slate-700 transition flex items-center justify-center">
        <i data-lucide="external-link" class="w-4 h-4"></i>
      </a>
    `;
  }

  // Action buttons
  let controlButtons = '';
  if (isCli) {
    controlButtons = `
      <div class="text-xs text-slate-400 font-mono flex items-center space-x-1">
        <i data-lucide="terminal" class="w-3.5 h-3.5 text-cyan-400"></i>
        <span>agents run ${agent.id}</span>
      </div>
    `;
  } else if (isRunning) {
    controlButtons = `
      <div class="flex items-center space-x-2 w-full">
        <button onclick="stopAgent('${agent.id}')" class="flex-1 py-1.5 px-3 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs font-medium rounded-lg border border-rose-500/30 transition flex items-center justify-center space-x-1.5">
          <i data-lucide="square" class="w-3.5 h-3.5"></i>
          <span>${t('btn.stop')}</span>
        </button>
        <button onclick="restartAgent('${agent.id}')" class="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition" title="${t('btn.restart')}">
          <i data-lucide="rotate-cw" class="w-4 h-4"></i>
        </button>
        <button onclick="openLogsModal('${agent.id}')" class="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition" title="${t('btn.logs')}">
          <i data-lucide="file-text" class="w-4 h-4"></i>
        </button>
        ${urlButton}
      </div>
    `;
  } else {
    controlButtons = `
      <div class="flex items-center space-x-2 w-full">
        <button onclick="startAgent('${agent.id}')" class="flex-1 py-1.5 px-3 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 text-xs font-medium rounded-lg border border-emerald-500/30 transition flex items-center justify-center space-x-1.5">
          <i data-lucide="play" class="w-3.5 h-3.5"></i>
          <span>${t('btn.start')}</span>
        </button>
        <button onclick="openLogsModal('${agent.id}')" class="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition" title="${t('btn.logs')}">
          <i data-lucide="file-text" class="w-4 h-4"></i>
        </button>
        ${urlButton}
      </div>
    `;
  }

  return `
    <div class="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-4 shadow-sm transition flex flex-col justify-between space-y-4">
      <div>
        <div class="flex items-start justify-between gap-2 mb-2">
          <div>
            <div class="flex items-center space-x-2">
              <h3 class="font-bold text-white text-sm tracking-tight" title="${getAgentName(agent)}">${getAgentName(agent)}</h3>
              <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded border ${typeClass}">${agent.type}</span>
            </div>
            <span class="text-xs font-mono text-slate-500">ID: ${agent.id}</span>
          </div>
          <div>${statusBadge}</div>
        </div>
        <p class="text-xs text-slate-400 line-clamp-2 mb-3">${getAgentDesc(agent)}</p>
        ${metricsHTML}
      </div>

      <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between">
        ${controlButtons}
      </div>
    </div>
  `;
}

// Agent Actions
async function startAgent(id) {
  showToast(`Запуск ${id}...`, 'info');
  try {
    const res = await fetch(`/api/agents/${id}/start`, { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showToast(`✅ ${data.message}`, 'success');
      fetchStatus();
    } else {
      showToast(`❌ ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Помилка: ${err}`, 'error');
  }
}

async function stopAgent(id) {
  showToast(`Зупинка ${id}...`, 'info');
  try {
    const res = await fetch(`/api/agents/${id}/stop`, { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showToast(`✅ ${data.message}`, 'success');
      fetchStatus();
    } else {
      showToast(`❌ ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Помилка: ${err}`, 'error');
  }
}

async function restartAgent(id) {
  showToast(`Перезапуск ${id}...`, 'info');
  try {
    const res = await fetch(`/api/agents/${id}/restart`, { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showToast(`✅ ${data.message}`, 'success');
      fetchStatus();
    } else {
      showToast(`❌ ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Помилка: ${err}`, 'error');
  }
}

async function batchAction(action) {
  showToast(`Виконується дія: ${action}...`, 'info');
  try {
    const res = await fetch(`/api/batch/${action}`, { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showToast('Групову дію виконано!', 'success');
      fetchStatus();
    }
  } catch (err) {
    showToast(`Помилка: ${err}`, 'error');
  }
}

// Log Viewer
function openLogsModal(id) {
  currentLogAgentId = id;
  const modal = document.getElementById('modal-logs');
  const title = document.getElementById('modal-logs-title');
  const ag = agentsData.find(a => a.id === id);
  const agentName = ag ? getAgentName(ag) : id;
  if (title) title.textContent = `${t('modal.logs.title')}: ${agentName}`;
  if (modal) modal.classList.remove('hidden');
  fetchLogs(id);
}

async function fetchLogs(id) {
  if (!id) return;
  const container = document.getElementById('logs-content');
  const countSelect = document.getElementById('logs-line-count');
  const lines = countSelect ? countSelect.value : 50;

  try {
    const res = await fetch(`/api/agents/${id}/logs?lines=${lines}`);
    const data = await res.json();
    if (data.ok && container) {
      const text = (data.lines || []).join('\n') || 'Логи порожні.';
      container.textContent = text;
      container.scrollTop = container.scrollHeight;
    }
  } catch (err) {
    if (container) container.textContent = `Помилка завантаження логів: ${err}`;
  }
}

// Discovery Scan
async function openScanModal() {
  const modal = document.getElementById('modal-scan');
  const container = document.getElementById('scan-results-container');
  if (modal) modal.classList.remove('hidden');

  if (container) {
    container.innerHTML = `
      <div class="text-center py-8 text-slate-500">
        <i data-lucide="loader-2" class="w-6 h-6 animate-spin text-blue-500 mx-auto mb-2"></i>
        Пошук мікрододатків у системних директоріях...
      </div>`;
    lucide.createIcons();
  }

  try {
    const res = await fetch('/api/scan');
    const data = await res.json();
    if (data.ok && container) {
      const candidates = data.candidates || [];
      if (candidates.length === 0) {
        container.innerHTML = `<p class="text-center text-slate-400 py-6 text-xs">Мікрододатків не знайдено.</p>`;
        return;
      }

      container.innerHTML = candidates.map(c => {
        const isReg = c.is_registered;
        return `
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between gap-3 text-xs">
            <div>
              <div class="flex items-center space-x-2">
                <span class="font-bold text-white">${c.name}</span>
                <span class="font-mono text-slate-500 text-[10px]">(${c.id})</span>
                <span class="px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] uppercase font-mono">${c.type}</span>
                ${c.port ? `<span class="text-blue-400 font-mono text-[10px]">:${c.port}</span>` : ''}
              </div>
              <p class="text-slate-400 text-xs mt-0.5">${c.description || '—'}</p>
              <span class="font-mono text-[10px] text-slate-600 block mt-1">${c.working_dir || ''}</span>
            </div>
            <div>
              ${isReg
                ? `<span class="px-2 py-1 rounded bg-slate-800 text-slate-500 text-xs">Вже у реєстрі</span>`
                : `<button onclick='registerFromScan(${JSON.stringify(c)})' class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition font-medium text-xs">
                    Додати
                  </button>`
              }
            </div>
          </div>
        `;
      }).join('');
      lucide.createIcons();
    }
  } catch (err) {
    if (container) container.innerHTML = `<p class="text-rose-400 text-center py-6 text-xs">Помилка сканування: ${err}</p>`;
  }
}

async function registerFromScan(cand) {
  try {
    const res = await fetch('/api/agents/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cand)
    });
    const data = await res.json();
    if (data.ok) {
      showToast(`✅ Додано ${cand.name}`, 'success');
      openScanModal();
      fetchStatus();
    } else {
      showToast(`❌ ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Помилка: ${err}`, 'error');
  }
}

// Add Custom Modal
function openAddModal() {
  const modal = document.getElementById('modal-add');
  if (modal) modal.classList.remove('hidden');
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
      showToast(`✅ Агента '${name}' успішно додано!`, 'success');
      closeModal('modal-add');
      fetchStatus();
    } else {
      showToast(`❌ ${data.message}`, 'error');
    }
  } catch (err) {
    showToast(`Помилка: ${err}`, 'error');
  }
}

// Modal helper
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('hidden');
}

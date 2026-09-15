/* ============================================================
   OmniArk 主控台 —— SPA 前端逻辑
   - fetch 封装（X-Requested-With / 401 跳登录 / 错误 Toast）
   - hash 路由器
   - 仪表盘 / 服务器 / 详情 / 创建 / 设置 / API 帮助
   ============================================================ */
(function () {
  'use strict';

  /* ------------------------------------------------------------ 工具 */

  const $ = (sel) => document.querySelector(sel);
  const app = () => document.getElementById('app');

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function toast(type, message) {
    const container = document.getElementById('toast-container');
    const el = document.createElement('div');
    el.className = 'toast toast-' + type;
    el.setAttribute('role', 'alert');
    el.innerHTML =
      '<div class="d-flex">' +
      '<div class="toast-body">' + escapeHtml(message) + '</div>' +
      '<button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="关闭"></button>' +
      '</div>';
    container.appendChild(el);
    const instance = new bootstrap.Toast(el, { delay: 4000 });
    el.addEventListener('hidden.bs.toast', () => el.remove());
    instance.show();
  }

  /* 确认弹窗（Promise<boolean>） */
  function confirmAction(title, messageHtml, okText) {
    return new Promise((resolve) => {
      const modalEl = document.getElementById('confirm-modal');
      const okBtn = document.getElementById('confirm-modal-ok');
      document.getElementById('confirm-modal-title').textContent = title;
      document.getElementById('confirm-modal-body').innerHTML = messageHtml;
      okBtn.textContent = okText || '确认';
      const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
      let settled = false;
      const done = (value) => {
        if (settled) return;
        settled = true;
        okBtn.removeEventListener('click', onOk);
        modalEl.removeEventListener('hidden.bs.modal', onHide);
        resolve(value);
      };
      const onOk = () => { done(true); modal.hide(); };
      const onHide = () => done(false);
      okBtn.addEventListener('click', onOk);
      modalEl.addEventListener('hidden.bs.modal', onHide);
      modal.show();
    });
  }

  /* 全局加载遮罩 */
  function showLoading(text) {
    document.getElementById('loading-text').textContent = text || '处理中，请稍候…';
    document.getElementById('loading-overlay').classList.remove('d-none');
  }
  function hideLoading() {
    document.getElementById('loading-overlay').classList.add('d-none');
  }

  /* 按钮 loading 态 */
  function btnLoading(btn, on) {
    if (!btn) return;
    if (on) {
      btn.dataset.origHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>处理中';
    } else {
      btn.disabled = false;
      if (btn.dataset.origHtml) btn.innerHTML = btn.dataset.origHtml;
    }
  }

  /* ------------------------------------------------------------ fetch 封装 */

  /* 基础封装：自动加 X-Requested-With，401 跳登录 */
  async function api(path, options) {
    const opts = options || {};
    opts.headers = Object.assign({ 'X-Requested-With': 'XMLHttpRequest' }, opts.headers);
    let resp;
    try {
      resp = await fetch(path, opts);
    } catch (err) {
      toast('danger', '网络错误：' + err.message);
      throw err;
    }
    if (resp.status === 401) {
      window.location.href = '/login';
      throw new Error('未授权，正在跳转登录页');
    }
    return resp;
  }

  /* JSON 封装：HTTP 错误与 success:false 统一 Toast 并抛错 */
  async function apiJson(path, options) {
    const resp = await api(path, options);
    const data = await resp.json().catch(() => null);
    if (!resp.ok) {
      const msg = (data && (data.error || data.message)) || ('请求失败（HTTP ' + resp.status + '）');
      toast('danger', msg);
      throw new Error(msg);
    }
    if (data && data.success === false) {
      const msg = data.error || data.message || '操作失败';
      toast('warning', msg);
      throw new Error(msg);
    }
    return data;
  }

  /* 静默 JSON：不弹 Toast（用于"空数据"属正常情况的接口） */
  async function fetchQuiet(path) {
    const resp = await api(path);
    return { ok: resp.ok, status: resp.status, data: await resp.json().catch(() => null) };
  }

  function postJson(path, body) {
    return apiJson(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {}),
    });
  }

  /* POST 后触发浏览器下载（Excel 导出） */
  async function downloadFile(path) {
    const resp = await api(path, { method: 'POST' });
    if (!resp.ok) {
      const data = await resp.json().catch(() => null);
      toast('danger', (data && data.error) || '导出失败（HTTP ' + resp.status + '）');
      return;
    }
    const blob = await resp.blob();
    const dispo = resp.headers.get('Content-Disposition') || '';
    let filename = 'export.xlsx';
    const match = dispo.match(/filename\*?=(?:UTF-8'')?"?([^";]+)/i);
    if (match) filename = decodeURIComponent(match[1]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    toast('success', '导出成功，文件已开始下载');
  }

  /* ------------------------------------------------------------ 轮询与图表管理 */

  let timers = [];
  function every(ms, fn) { timers.push(setInterval(fn, ms)); }
  function stopTimers() { timers.forEach(clearInterval); timers = []; }

  let storageChart = null;
  function destroyChart() {
    if (storageChart) { storageChart.destroy(); storageChart = null; }
  }

  function progressClass(pct) {
    if (pct >= 90) return 'danger';
    if (pct >= 70) return 'warn';
    return '';
  }

  function statusBadge(status) {
    if (status === 'running') {
      return '<span class="badge-status running"><span class="dot"></span>运行中</span>';
    }
    return '<span class="badge-status stopped"><span class="dot"></span>已停止</span>';
  }

  function emptyState(icon, text) {
    return '<div class="empty-state"><i class="bi ' + icon + '"></i><p>' +
      escapeHtml(text) + '</p></div>';
  }

  /* ------------------------------------------------------------ 权限感知 UI */

  /* 当前登录用户（SPA 启动时从 /api/account/me 获取） */
  let currentUser = null;

  function isAdmin() {
    return !!currentUser && currentUser.role === 'admin';
  }

  /* 生成 admin-only 按钮的属性串（创建动态按钮时使用） */
  function adminOnlyAttr() {
    return isAdmin()
      ? 'data-admin-only'
      : 'data-admin-only disabled title="需要管理员权限"';
  }

  /* 依据当前角色统一刷新界面上的 admin-only 控件与导航 */
  function applyPermissions() {
    if (!currentUser) return; /* 尚未获取身份信息，保持默认 */
    const admin = isAdmin();
    const accNav = document.querySelector('.nav-item[data-route="accounts"]');
    if (accNav) accNav.style.display = admin ? '' : 'none';
    document.querySelectorAll('[data-admin-only]').forEach((el) => {
      el.disabled = !admin;
      if (admin) el.removeAttribute('title');
      else el.title = '需要管理员权限';
    });
    /* 终端命令框需结合服务器运行状态，交给 loadDetailStatus 判定 */
    if (currentServer && document.getElementById('command-input')) {
      loadDetailStatus(currentServer);
    }
  }

  async function loadAccount() {
    const r = await fetchQuiet('/api/account/me');
    if (!r.ok || !r.data) return;
    currentUser = r.data;
    document.getElementById('sidebar-account-name').textContent =
      currentUser.account || '未知账号';
    const roleEl = document.getElementById('sidebar-account-role');
    if (isAdmin()) {
      roleEl.textContent = '管理员';
      roleEl.className = 'role-badge role-admin';
    } else {
      roleEl.textContent = '普通用户';
      roleEl.className = 'role-badge role-user';
    }
    document.getElementById('sidebar-account').style.display = 'flex';
    applyPermissions();
  }

  /* ------------------------------------------------------------ 路由器 */

  const TITLES = {
    dashboard: '仪表盘', console: '总控台', servers: '服务器', create: '创建服务器',
    settings: '设置', java: 'Java 管理', accounts: '账号管理', help: 'API 帮助',
  };

  function setTitle(text) {
    document.getElementById('page-title').textContent = text;
    document.title = text + ' | OmniArk 主控台';
  }

  function setActiveNav(key) {
    document.querySelectorAll('.sidebar-nav .nav-item').forEach((item) => {
      item.classList.toggle('active', item.dataset.route === key);
    });
  }

  function router() {
    stopTimers();
    destroyChart();
    const hash = location.hash.replace(/^#\/?/, '');
    const seg = hash.split('/').filter(Boolean).map(decodeURIComponent);
    const page = seg[0] || 'dashboard';

    if (page === 'servers' && seg[1]) {
      setActiveNav('servers');
      renderServerDetail(seg[1]);
      return;
    }
    setActiveNav(page);
    setTitle(TITLES[page] || '仪表盘');
    switch (page) {
      case 'console': renderConsole(); break;
      case 'servers': renderServers(); break;
      case 'create': renderCreate(); break;
      case 'settings': renderSettings(); break;
      case 'java': renderJava(); break;
      case 'accounts': renderAccounts(); break;
      case 'help': renderHelp(); break;
      case 'dashboard': renderDashboard(); break;
      default:
        location.hash = '#/dashboard';
    }
    applyPermissions();
  }

  /* ------------------------------------------------------------ 仪表盘 */

  function renderDashboard() {
    app().innerHTML =
      '<div class="row g-3 mb-3">' +
        resourceCard('cpu', 'CPU 占用', 'bi-cpu') +
        resourceCard('ram', '内存占用', 'bi-memory') +
        resourceCard('disk', '磁盘占用', 'bi-device-hdd') +
      '</div>' +
      '<div class="row g-3">' +
        '<div class="col-lg-7"><div class="card-panel">' +
          '<div class="card-panel-title"><i class="bi bi-hdd-stack"></i>服务器概览</div>' +
          '<div id="overview-body"><div class="text-secondary">加载中…</div></div>' +
        '</div></div>' +
        '<div class="col-lg-5"><div class="card-panel">' +
          '<div class="card-panel-title"><i class="bi bi-clock-history"></i>最近启动</div>' +
          '<div id="latest-body"><div class="text-secondary">加载中…</div></div>' +
        '</div></div>' +
      '</div>';

    loadResources();
    every(5000, loadResources);
    loadOverview();
    loadLatest();
  }

  function resourceCard(key, title, icon) {
    return '<div class="col-md-4"><div class="card-panel">' +
      '<div class="card-panel-title"><i class="bi ' + icon + '"></i>' + title + '</div>' +
      '<div class="stat-value" id="' + key + '-value">--%</div>' +
      '<div class="progress-track"><div class="progress-fill" id="' + key + '-bar" style="width:0%"></div></div>' +
      '<div class="stat-sub" id="' + key + '-sub">加载中…</div>' +
      '</div></div>';
  }

  function updateResource(key, pct, sub) {
    const value = document.getElementById(key + '-value');
    if (!value) return;
    value.textContent = pct.toFixed(1) + '%';
    const bar = document.getElementById(key + '-bar');
    bar.style.width = Math.min(100, pct) + '%';
    bar.className = 'progress-fill ' + progressClass(pct);
    document.getElementById(key + '-sub').textContent = sub;
  }

  async function loadResources() {
    const results = await Promise.allSettled([
      fetchQuiet('/api/program/get/CPU/Usage'),
      fetchQuiet('/api/program/get/RAM/Usage'),
      fetchQuiet('/api/program/disk_usage'),
    ]);
    const cpu = results[0].status === 'fulfilled' && results[0].value.ok ? results[0].value.data : null;
    const ram = results[1].status === 'fulfilled' && results[1].value.ok ? results[1].value.data : null;
    const disk = results[2].status === 'fulfilled' && results[2].value.ok ? results[2].value.data : null;

    if (cpu) updateResource('cpu', Number(cpu.percent) || 0,
      '频率 ' + (cpu.freq_current || 0) + ' / ' + (cpu.freq_max || 0) + ' MHz');
    if (ram) updateResource('ram', Number(ram.percent) || 0,
      (ram.used_mb || 0) + ' / ' + (ram.total_mb || 0) + ' MB');
    if (disk) updateResource('disk', Number(disk.used_percent) || 0,
      '已用 ' + (disk.used_gb || 0) + ' GB，可用 ' + (disk.free_gb || 0) + ' GB');
    if (!cpu && !ram && !disk) toast('warning', '无法获取系统资源数据');
  }

  async function loadOverview() {
    const body = document.getElementById('overview-body');
    if (!body) return;
    let list;
    try {
      list = await apiJson('/api/server/list');
    } catch (err) {
      body.innerHTML = emptyState('bi-exclamation-circle', '无法加载服务器列表');
      return;
    }
    const names = list.serverlist || [];
    if (!names.length) {
      body.innerHTML = emptyState('bi-inbox', '还没有服务器，去「创建服务器」新建一台吧');
      return;
    }
    const statuses = await Promise.all(names.map(async (name) => {
      const r = await fetchQuiet('/api/server/status/' + encodeURIComponent(name));
      return r.ok && r.data ? r.data.status : 'stopped';
    }));
    const running = statuses.filter((s) => s === 'running').length;
    let html = '<p class="stat-sub mb-3">共 <strong>' + (list.serverCount || names.length) +
      '</strong> 台服务器，<strong style="color:var(--success)">' + running + '</strong> 台运行中</p>';
    html += '<ul class="dark-list">';
    names.forEach((name, i) => {
      html += '<li><i class="bi bi-server"></i>' +
        '<a class="server-card-name" href="#/servers/' + encodeURIComponent(name) + '">' +
        escapeHtml(name) + '</a>' +
        '<span class="ms-auto">' + statusBadge(statuses[i]) + '</span></li>';
    });
    html += '</ul>';
    body.innerHTML = html;
  }

  async function loadLatest() {
    const body = document.getElementById('latest-body');
    if (!body) return;
    const r = await fetchQuiet('/api/server/latest');
    if (!r.ok || !r.data) {
      body.innerHTML = emptyState('bi-clock', '暂无最近启动记录');
      return;
    }
    const d = r.data;
    body.innerHTML =
      '<div class="server-card-meta" style="grid-template-columns:auto 1fr">' +
      '<span class="label">名称</span><a class="server-card-name" href="#/servers/' +
        encodeURIComponent(d.name) + '">' + escapeHtml(d.name) + '</a>' +
      '<span class="label">版本</span><span class="value">' + escapeHtml(d.version) + '</span>' +
      '<span class="label">大小</span><span class="value">' + escapeHtml(d.size) + '</span>' +
      '<span class="label">启动次数</span><span class="value">' + escapeHtml(d.startCount) + '</span>' +
      '<span class="label">最近启动</span><span class="value">' + escapeHtml(d.LatestStartedTime) + '</span>' +
      '</div>';
  }

  /* ------------------------------------------------------------ 总控台 */

  let consoleLogServer = ''; /* 实时日志当前选中的服务器 */

  function renderConsole() {
    consoleLogServer = '';
    app().innerHTML =
      '<div class="d-flex align-items-center gap-2 mb-3 flex-wrap">' +
        '<h2 class="section-title mb-0"><i class="bi bi-grid-1x2-fill"></i>服务器总控台</h2>' +
        '<div class="ms-auto">' +
          '<button class="btn btn-outline-secondary btn-sm" id="console-refresh">' +
            '<i class="bi bi-arrow-clockwise"></i> 刷新</button>' +
        '</div>' +
      '</div>' +
      '<div class="card-panel mb-3">' +
        '<div class="card-panel-title"><i class="bi bi-hdd-stack"></i>实时状态总表</div>' +
        '<div class="table-responsive"><table class="dark-table">' +
          '<thead><tr>' +
            '<th>名称</th><th>状态</th><th>版本</th><th>大小</th>' +
            '<th>启动次数</th><th>在线人数</th><th>最近启动时间</th><th>操作</th>' +
          '</tr></thead>' +
          '<tbody id="console-body">' +
            '<tr><td colspan="8" class="text-secondary">加载中…</td></tr>' +
          '</tbody>' +
        '</table></div>' +
      '</div>' +
      '<div class="card-panel">' +
        '<div class="d-flex align-items-center gap-2 mb-3 flex-wrap">' +
          '<div class="card-panel-title mb-0"><i class="bi bi-terminal"></i>实时日志</div>' +
          '<select class="form-select form-select-sm ms-auto console-log-select" ' +
            'id="console-log-select" aria-label="选择服务器"></select>' +
        '</div>' +
        '<div class="terminal-box" id="console-logs" style="height:320px">' +
          '<div class="text-secondary">选择一台运行中的服务器查看日志</div>' +
        '</div>' +
      '</div>';

    document.getElementById('console-refresh').addEventListener('click', loadConsoleTable);
    document.getElementById('console-log-select').addEventListener('change', (e) => {
      consoleLogServer = e.target.value;
      loadConsoleLogs();
    });
    loadConsoleTable();
    every(5000, loadConsoleTable);   /* 状态总表 5 秒自动刷新 */
    every(3000, loadConsoleLogs);    /* 日志 3 秒轮询（离开页面由路由器清理） */
  }

  async function loadConsoleTable() {
    const body = document.getElementById('console-body');
    if (!body) return;
    let list;
    try {
      list = await apiJson('/api/server/list');
    } catch (err) {
      body.innerHTML =
        '<tr><td colspan="8" class="text-secondary">无法加载服务器列表</td></tr>';
      return;
    }
    const names = list.serverlist || [];
    if (!names.length) {
      body.innerHTML =
        '<tr><td colspan="8" class="text-secondary">还没有服务器，去「创建服务器」新建一台吧</td></tr>';
      updateConsoleLogSelect([]);
      return;
    }
    const rows = await Promise.all(names.map(async (name) => {
      const enc = encodeURIComponent(name);
      const [statusR, infoR] = await Promise.all([
        fetchQuiet('/api/server/status/' + enc),
        fetchQuiet('/api/server/info/' + enc),
      ]);
      const status = statusR.ok && statusR.data ? statusR.data.status : 'stopped';
      const info = infoR.ok && infoR.data ? infoR.data : {};
      let online = '-';
      if (status === 'running') {
        const pR = await fetchQuiet('/api/server/players/' + enc);
        if (pR.ok && pR.data && Array.isArray(pR.data.players)) {
          online = String(pR.data.players[0]);
        }
      }
      return { name: name, status: status, info: info, online: online };
    }));
    if (!body.isConnected) return;

    body.innerHTML = '';
    const runningNames = [];
    rows.forEach((row) => {
      if (row.status === 'running') runningNames.push(row.name);
      const tr = document.createElement('tr');
      tr.innerHTML =
        '<td><a class="server-card-name" href="#/servers/' + encodeURIComponent(row.name) +
          '">' + escapeHtml(row.name) + '</a></td>' +
        '<td>' + statusBadge(row.status) + '</td>' +
        '<td>' + escapeHtml(row.info.version || '未知') + '</td>' +
        '<td>' + escapeHtml(row.info.size || '未知') + '</td>' +
        '<td>' + (row.info.startCount != null ? escapeHtml(row.info.startCount) : '—') + '</td>' +
        '<td>' + escapeHtml(row.online) + '</td>' +
        '<td>' + escapeHtml(row.info.LatestStartedTime || '从未启动') + '</td>' +
        '<td><div class="d-flex gap-1 flex-wrap">' +
          '<button class="btn btn-success btn-sm" data-action="start">' +
            '<i class="bi bi-play-fill"></i> 启动</button>' +
          '<button class="btn btn-outline-danger btn-sm" data-action="stop">' +
            '<i class="bi bi-stop-fill"></i> 停止</button>' +
          '<button class="btn btn-outline-warning btn-sm" data-action="restart">' +
            '<i class="bi bi-arrow-repeat"></i> 重启</button>' +
        '</div></td>';
      tr.querySelectorAll('button[data-action]').forEach((btn) => {
        btn.addEventListener('click', () => consoleAction(row.name, btn.dataset.action, btn));
      });
      body.appendChild(tr);
    });
    updateConsoleLogSelect(runningNames);
  }

  /* 运行中的服务器填充实况日志下拉，尽量保留当前选择 */
  function updateConsoleLogSelect(runningNames) {
    const sel = document.getElementById('console-log-select');
    if (!sel) return;
    if (!runningNames.length) {
      sel.innerHTML = '<option value="">（暂无运行中的服务器）</option>';
      sel.disabled = true;
      consoleLogServer = '';
      return;
    }
    sel.disabled = false;
    if (!runningNames.includes(consoleLogServer)) consoleLogServer = runningNames[0];
    sel.innerHTML = runningNames.map((n) =>
      '<option value="' + escapeHtml(n) + '"' +
      (n === consoleLogServer ? ' selected' : '') + '>' + escapeHtml(n) + '</option>'
    ).join('');
  }

  async function loadConsoleLogs() {
    const box = document.getElementById('console-logs');
    if (!box) return;
    if (!consoleLogServer) {
      box.innerHTML =
        '<div class="text-secondary">暂无运行中的服务器，启动一台后可在此查看实时日志</div>';
      return;
    }
    const r = await fetchQuiet('/api/server/terminal/' + encodeURIComponent(consoleLogServer));
    if (!r.ok || !r.data) {
      box.innerHTML = '<div class="text-secondary">无法获取终端日志</div>';
      return;
    }
    let lines = r.data.logs;
    if (!Array.isArray(lines)) lines = String(lines == null ? '' : lines).split('\n');
    const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 60;
    box.textContent = lines.join('\n') || '（暂无日志）';
    if (nearBottom) box.scrollTop = box.scrollHeight;
  }

  /* 启动 / 停止 / 重启（与服务器列表相同的逻辑与 loading 态） */
  async function consoleAction(name, action, btn) {
    if (action === 'stop') {
      const ok = await confirmAction(
        '停止服务器',
        '确定要停止服务器 <strong>' + escapeHtml(name) + '</strong> 吗？',
        '确认停止');
      if (!ok) return;
    }
    const messages = { start: '启动指令已发送', stop: '停止指令已发送', restart: '重启指令已发送' };
    btnLoading(btn, true);
    try {
      await apiJson('/api/server/' + encodeURIComponent(name) + '/' + action, { method: 'POST' });
      toast('success', '服务器「' + name + '」' + messages[action]);
      setTimeout(() => loadConsoleTable(), 2500);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  /* ------------------------------------------------------------ 服务器列表 */

  function renderServers() {
    app().innerHTML =
      '<div class="d-flex align-items-center gap-2 mb-3 flex-wrap">' +
        '<h2 class="section-title mb-0"><i class="bi bi-hdd-stack"></i>服务器列表</h2>' +
        '<div class="ms-auto d-flex gap-2">' +
          '<button class="btn btn-accent-outline btn-sm" id="export-all-btn">' +
            '<i class="bi bi-file-earmark-excel"></i> 导出全部</button>' +
          '<button class="btn btn-outline-secondary btn-sm" id="refresh-btn">' +
            '<i class="bi bi-arrow-clockwise"></i> 刷新</button>' +
          '<a class="btn btn-primary btn-sm" href="#/create">' +
            '<i class="bi bi-plus-lg"></i> 新建服务器</a>' +
        '</div>' +
      '</div>' +
      '<div class="server-grid" id="server-grid">' +
        '<div class="text-secondary">加载中…</div>' +
      '</div>';

    document.getElementById('refresh-btn').addEventListener('click', renderServers);
    document.getElementById('export-all-btn').addEventListener('click', (e) => {
      const btn = e.currentTarget;
      btnLoading(btn, true);
      downloadFile('/api/server/list/excel').finally(() => btnLoading(btn, false));
    });
    loadServerCards();
  }

  async function loadServerCards() {
    const grid = document.getElementById('server-grid');
    let list;
    try {
      list = await apiJson('/api/server/list');
    } catch (err) {
      grid.innerHTML = emptyState('bi-exclamation-circle', '无法加载服务器列表');
      return;
    }
    const names = list.serverlist || [];
    if (!names.length) {
      grid.innerHTML = emptyState('bi-inbox', '还没有服务器，点击右上角「新建服务器」开始');
      return;
    }
    grid.innerHTML = '';
    names.forEach((name) => {
      const card = document.createElement('div');
      card.className = 'server-card';
      card.id = 'card-' + name;
      card.innerHTML =
        '<div class="server-card-head">' +
          '<a class="server-card-name" href="#/servers/' + encodeURIComponent(name) + '">' +
            escapeHtml(name) + '</a>' +
          '<span data-role="status">' + statusBadge('stopped') + '</span>' +
        '</div>' +
        '<div class="server-card-meta">' +
          '<span class="label">版本</span><span class="value" data-role="version">…</span>' +
          '<span class="label">大小</span><span class="value" data-role="size">…</span>' +
          '<span class="label">启动次数</span><span class="value" data-role="count">…</span>' +
          '<span class="label">最近启动</span><span class="value" data-role="latest">…</span>' +
        '</div>' +
        '<div class="server-card-actions">' +
          '<button class="btn btn-success btn-sm" data-action="start"><i class="bi bi-play-fill"></i> 启动</button>' +
          '<button class="btn btn-outline-warning btn-sm" data-action="restart"><i class="bi bi-arrow-repeat"></i> 重启</button>' +
          '<button class="btn btn-outline-danger btn-sm" data-action="stop"><i class="bi bi-stop-fill"></i> 停止</button>' +
          '<button class="btn btn-danger btn-sm" data-action="delete" ' + adminOnlyAttr() + '><i class="bi bi-trash"></i> 删除</button>' +
          '<button class="btn btn-outline-secondary btn-sm" data-action="excel"><i class="bi bi-file-earmark-excel"></i> 导出</button>' +
        '</div>';
      grid.appendChild(card);
      fillServerCard(card, name);
    });
  }

  async function fillServerCard(card, name) {
    const enc = encodeURIComponent(name);
    const [infoR, statusR] = await Promise.all([
      fetchQuiet('/api/server/info/' + enc),
      fetchQuiet('/api/server/status/' + enc),
    ]);
    if (infoR.ok && infoR.data) {
      const d = infoR.data;
      card.querySelector('[data-role="version"]').textContent = d.version || '未知';
      card.querySelector('[data-role="size"]').textContent = d.size || '未知';
      card.querySelector('[data-role="count"]').textContent = d.startCount != null ? d.startCount : '—';
      card.querySelector('[data-role="latest"]').textContent = d.LatestStartedTime || '从未启动';
    } else {
      card.querySelector('[data-role="version"]').textContent = '读取失败';
    }
    if (statusR.ok && statusR.data) {
      card.querySelector('[data-role="status"]').innerHTML = statusBadge(statusR.data.status);
    }
    card.querySelectorAll('button[data-action]').forEach((btn) => {
      btn.addEventListener('click', () => serverAction(name, btn.dataset.action, btn));
    });
  }

  async function serverAction(name, action, btn) {
    const enc = encodeURIComponent(name);
    if (action === 'delete') {
      const ok = await confirmAction(
        '删除服务器',
        '确定要删除服务器 <strong>' + escapeHtml(name) + '</strong> 吗？<br>' +
        '<span style="color:var(--danger)">该操作会删除服务器全部文件，不可恢复！</span>',
        '确认删除');
      if (!ok) return;
      btnLoading(btn, true);
      try {
        await apiJson('/api/server/delete/' + enc, { method: 'POST' });
        toast('success', '服务器「' + name + '」已删除');
        renderServers();
      } catch (err) { /* 错误已 Toast */ }
      return;
    }
    if (action === 'stop') {
      const ok = await confirmAction(
        '停止服务器',
        '确定要停止服务器 <strong>' + escapeHtml(name) + '</strong> 吗？',
        '确认停止');
      if (!ok) return;
    }
    if (action === 'excel') {
      btnLoading(btn, true);
      try { await downloadFile('/api/server/info/' + enc + '/excel'); }
      finally { btnLoading(btn, false); }
      return;
    }
    /* start / stop / restart */
    const messages = { start: '启动指令已发送', stop: '停止指令已发送', restart: '重启指令已发送' };
    btnLoading(btn, true);
    try {
      await apiJson('/api/server/' + enc + '/' + action, { method: 'POST' });
      toast('success', '服务器「' + name + '」' + messages[action]);
      setTimeout(() => { refreshCardStatus(name); }, 2500);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function refreshCardStatus(name) {
    const card = document.getElementById('card-' + name);
    if (!card) return;
    const r = await fetchQuiet('/api/server/status/' + encodeURIComponent(name));
    if (r.ok && r.data) {
      card.querySelector('[data-role="status"]').innerHTML = statusBadge(r.data.status);
    }
  }

  /* ------------------------------------------------------------ 服务器详情 */

  let currentServer = null;

  function renderServerDetail(name) {
    currentServer = name;
    setTitle('服务器：' + name);
    app().innerHTML =
      '<div class="detail-header">' +
        '<a href="#/servers" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> 返回</a>' +
        '<h2>' + escapeHtml(name) + '</h2>' +
        '<span id="detail-status">' + statusBadge('stopped') + '</span>' +
        '<div class="ms-auto d-flex gap-2 flex-wrap">' +
          '<button class="btn btn-success btn-sm" id="detail-start"><i class="bi bi-play-fill"></i> 启动</button>' +
          '<button class="btn btn-outline-warning btn-sm" id="detail-restart"><i class="bi bi-arrow-repeat"></i> 重启</button>' +
          '<button class="btn btn-outline-danger btn-sm" id="detail-stop"><i class="bi bi-stop-fill"></i> 停止</button>' +
        '</div>' +
      '</div>' +
      '<div class="d-flex gap-2 mb-3 flex-wrap">' +
        '<a class="btn btn-accent-outline btn-sm" href="/server/settings/' + encodeURIComponent(name) + '">' +
          '<i class="bi bi-sliders"></i> 服务器设置</a>' +
        '<a class="btn btn-accent-outline btn-sm" href="/manager/' + encodeURIComponent(name) + '">' +
          '<i class="bi bi-folder2-open"></i> 文件管理</a>' +
        '<a class="btn btn-accent-outline btn-sm" href="/server/' + encodeURIComponent(name) + '/storage_chart">' +
          '<i class="bi bi-graph-up"></i> 存储图表页</a>' +
      '</div>' +
      '<ul class="nav nav-tabs" role="tablist">' +
        '<li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-terminal" type="button">终端</button></li>' +
        '<li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-players" type="button">在线玩家</button></li>' +
        '<li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-lists" type="button">名单管理</button></li>' +
        '<li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-history" type="button">历史玩家</button></li>' +
        '<li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-storage" type="button">存储图表</button></li>' +
        '<li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-backups" type="button">备份</button></li>' +
      '</ul>' +
      '<div class="tab-content pt-3">' +
        '<div class="tab-pane fade show active" id="tab-terminal">' +
          '<div class="terminal-box mb-2" id="terminal-logs"><div class="text-secondary">日志加载中…</div></div>' +
          '<div class="input-group terminal-input-group">' +
            '<span class="input-group-text"><i class="bi bi-chevron-right"></i></span>' +
            '<input type="text" class="form-control" id="command-input" placeholder="输入服务器命令（无需以 / 开头）" disabled>' +
            '<button class="btn btn-primary" id="command-send" disabled>发送</button>' +
          '</div>' +
          '<div class="stat-sub mt-1" id="command-hint">仅服务器运行时可发送命令</div>' +
        '</div>' +
        '<div class="tab-pane fade" id="tab-players"><div class="card-panel"><div id="players-body">加载中…</div></div></div>' +
        '<div class="tab-pane fade" id="tab-lists">' +
          '<div class="row g-3">' +
            '<div class="col-md-4"><div class="card-panel"><div class="card-panel-title"><i class="bi bi-shield-check"></i>白名单</div><div id="whitelist-body">加载中…</div></div></div>' +
            '<div class="col-md-4"><div class="card-panel"><div class="card-panel-title"><i class="bi bi-person-x"></i>封禁玩家</div><div id="banned-players-body">加载中…</div></div></div>' +
            '<div class="col-md-4"><div class="card-panel"><div class="card-panel-title"><i class="bi bi-hdd-network"></i>封禁 IP</div><div id="banned-ips-body">加载中…</div></div></div>' +
          '</div>' +
        '</div>' +
        '<div class="tab-pane fade" id="tab-history"><div class="card-panel"><div class="card-panel-title"><i class="bi bi-people"></i>历史玩家</div><div id="history-body">加载中…</div></div></div>' +
        '<div class="tab-pane fade" id="tab-storage"><div class="card-panel"><div class="card-panel-title"><i class="bi bi-graph-up"></i>存储占用趋势</div><div id="storage-body" style="height:340px"><canvas id="storage-chart"></canvas></div></div></div>' +
        '<div class="tab-pane fade" id="tab-backups"><div class="card-panel">' +
          '<div class="d-flex align-items-center gap-2 mb-3 flex-wrap">' +
            '<div class="card-panel-title mb-0"><i class="bi bi-archive"></i>备份列表</div>' +
            '<button class="btn btn-primary btn-sm ms-auto" id="backup-create-btn" data-admin-only>' +
              '<i class="bi bi-plus-lg"></i> 手动备份</button>' +
          '</div>' +
          '<div id="backups-body"><div class="text-secondary">切换到本标签页后加载…</div></div>' +
        '</div></div>' +
      '</div>';

    /* 顶部操作 */
    document.getElementById('detail-start').addEventListener('click', (e) =>
      detailAction(name, 'start', e.currentTarget));
    document.getElementById('detail-restart').addEventListener('click', (e) =>
      detailAction(name, 'restart', e.currentTarget));
    document.getElementById('detail-stop').addEventListener('click', (e) =>
      detailAction(name, 'stop', e.currentTarget));

    /* 命令发送 */
    const input = document.getElementById('command-input');
    const sendBtn = document.getElementById('command-send');
    const send = () => sendCommand(name);
    sendBtn.addEventListener('click', send);
    input.addEventListener('keydown', (e) => { if (e.key === 'Enter') send(); });

    /* 存储图表：切到该标签页时才初始化 Chart.js */
    let chartInited = false;
    document.querySelector('[data-bs-target="#tab-storage"]').addEventListener('shown.bs.tab', () => {
      if (!chartInited) { chartInited = true; loadStorageChart(name); }
    });

    /* 备份：切到该标签页时才加载列表 */
    let backupsInited = false;
    document.querySelector('[data-bs-target="#tab-backups"]').addEventListener('shown.bs.tab', () => {
      if (!backupsInited) { backupsInited = true; loadBackups(name); }
    });
    document.getElementById('backup-create-btn').addEventListener('click', (e) =>
      backupCreate(name, e.currentTarget));

    loadDetailStatus(name);
    loadTerminalLogs(name);
    loadPlayers(name);
    loadLists(name);
    loadHistory(name);
    applyPermissions();
    every(3000, () => loadTerminalLogs(name));
    every(5000, () => loadDetailStatus(name));
  }

  async function detailAction(name, action, btn) {
    if (action === 'stop') {
      const ok = await confirmAction('停止服务器',
        '确定要停止服务器 <strong>' + escapeHtml(name) + '</strong> 吗？', '确认停止');
      if (!ok) return;
    }
    const messages = { start: '启动指令已发送', stop: '停止指令已发送', restart: '重启指令已发送' };
    btnLoading(btn, true);
    try {
      await apiJson('/api/server/' + encodeURIComponent(name) + '/' + action, { method: 'POST' });
      toast('success', '服务器「' + name + '」' + messages[action]);
      setTimeout(() => loadDetailStatus(name), 2500);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function loadDetailStatus(name) {
    if (currentServer !== name) return;
    const r = await fetchQuiet('/api/server/status/' + encodeURIComponent(name));
    const badge = document.getElementById('detail-status');
    if (!badge) return;
    if (r.ok && r.data) {
      const running = r.data.status === 'running';
      const admin = isAdmin();
      const canCommand = running && admin;
      badge.innerHTML = statusBadge(r.data.status);
      const input = document.getElementById('command-input');
      const sendBtn = document.getElementById('command-send');
      input.disabled = !canCommand;
      sendBtn.disabled = !canCommand;
      if (admin) {
        input.removeAttribute('title');
        sendBtn.removeAttribute('title');
      } else {
        input.title = '需要管理员权限';
        sendBtn.title = '需要管理员权限';
      }
      document.getElementById('command-hint').textContent = !admin
        ? '发送命令需要管理员权限'
        : (running ? '命令将通过 RCON 执行' : '仅服务器运行时可发送命令');
    }
  }

  async function loadTerminalLogs(name) {
    if (currentServer !== name) return;
    const box = document.getElementById('terminal-logs');
    if (!box) return;
    const r = await fetchQuiet('/api/server/get/' + encodeURIComponent(name) + '/terminal/logs');
    if (!r.ok || !r.data) {
      box.innerHTML = '<div class="text-secondary">无法获取终端日志</div>';
      return;
    }
    /* 兼容纯文本与 {logs:[...]} 两种返回 */
    let lines = r.data.logs;
    if (!Array.isArray(lines)) lines = String(lines == null ? '' : lines).split('\n');
    const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 60;
    box.textContent = lines.join('\n') || '（暂无日志）';
    if (nearBottom) box.scrollTop = box.scrollHeight;
  }

  async function sendCommand(name) {
    const input = document.getElementById('command-input');
    const btn = document.getElementById('command-send');
    const command = input.value.trim();
    if (!command) return;
    btnLoading(btn, true);
    try {
      const data = await postJson('/api/server/' + encodeURIComponent(name) + '/command', { command: command });
      toast('success', data.message || '命令已执行');
      input.value = '';
      setTimeout(() => loadTerminalLogs(name), 800);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); input.focus(); }
  }

  async function loadPlayers(name) {
    const body = document.getElementById('players-body');
    if (!body || currentServer !== name) return;
    const r = await fetchQuiet('/api/server/players/' + encodeURIComponent(name));
    if (!r.ok || !r.data) {
      body.innerHTML = emptyState('bi-exclamation-circle', '无法获取玩家信息');
      return;
    }
    const players = r.data.players;
    if (!players) {
      body.innerHTML = emptyState('bi-moon', '服务器未运行，暂无在线玩家');
      return;
    }
    const online = players[0], max = players[1], names = players[2] || [];
    let html = '<p class="stat-sub mb-2">在线 <strong style="color:var(--success)">' + online +
      '</strong> / ' + max + ' 人</p>';
    if (names.length) {
      html += '<ul class="dark-list">';
      names.forEach((p) => {
        html += '<li><i class="bi bi-person-circle"></i>' + escapeHtml(p) + '</li>';
      });
      html += '</ul>';
    } else {
      html += '<div class="text-secondary">当前没有玩家在线</div>';
    }
    body.innerHTML = html;
  }

  function renderNameList(el, items, emptyText, icon) {
    if (!items || !items.length) {
      el.innerHTML = '<div class="text-secondary">' + escapeHtml(emptyText) + '</div>';
      return;
    }
    let html = '<ul class="dark-list">';
    items.forEach((item) => {
      const text = typeof item === 'object' ? (item.name || JSON.stringify(item)) : item;
      html += '<li><i class="bi ' + icon + '"></i>' + escapeHtml(text) + '</li>';
    });
    html += '</ul>';
    el.innerHTML = html;
  }

  async function loadLists(name) {
    if (currentServer !== name) return;
    const enc = encodeURIComponent(name);
    const whiteBody = document.getElementById('whitelist-body');
    const bannedPBody = document.getElementById('banned-players-body');
    const bannedIBody = document.getElementById('banned-ips-body');
    if (!whiteBody) return;

    const [whiteR, bannedPR, bannedIR] = await Promise.all([
      fetchQuiet('/api/server/get/white-list/' + enc),
      fetchQuiet('/api/server/get/banned/players/' + enc),
      fetchQuiet('/api/server/get/banned/ips/' + enc),
    ]);
    if (!whiteBody.isConnected) return;

    if (whiteR.ok && whiteR.data && whiteR.data.success !== false) {
      renderNameList(whiteBody, whiteR.data.WhiteList, '白名单为空', 'bi-person-check');
    } else {
      whiteBody.innerHTML = '<div class="text-secondary">白名单未启用</div>';
    }
    renderNameList(bannedPBody,
      bannedPR.ok && bannedPR.data ? bannedPR.data.BannedPlayerList : null,
      '暂无封禁玩家', 'bi-person-x');
    renderNameList(bannedIBody,
      bannedIR.ok && bannedIR.data ? bannedIR.data.BannedIPList : null,
      '暂无封禁 IP', 'bi-hdd-network');
  }

  async function loadHistory(name) {
    const body = document.getElementById('history-body');
    if (!body || currentServer !== name) return;
    const r = await fetchQuiet('/api/server/get/history/players/' + encodeURIComponent(name));
    if (!r.ok || !r.data || r.data.success === false) {
      body.innerHTML = '<div class="text-secondary">暂无历史玩家记录</div>';
      return;
    }
    renderNameList(body, r.data.HistoryPlayerList, '暂无历史玩家记录', 'bi-person');
  }

  async function loadStorageChart(name) {
    const body = document.getElementById('storage-body');
    if (!body || currentServer !== name) return;
    const r = await fetchQuiet('/api/server/' + encodeURIComponent(name) + '/storage_info');
    if (!r.ok || !r.data || !r.data.values || !r.data.values.length) {
      body.innerHTML = emptyState('bi-graph-up', '暂无存储占用数据');
      return;
    }
    if (typeof Chart === 'undefined') {
      body.innerHTML = emptyState('bi-exclamation-circle', 'Chart.js 加载失败，请检查网络');
      return;
    }
    destroyChart();
    const ctx = document.getElementById('storage-chart').getContext('2d');
    storageChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: r.data.labels,
        datasets: [{
          label: '存储占用（' + (r.data.type || 'MB') + '）',
          data: r.data.values,
          borderColor: '#4f8cff',
          backgroundColor: 'rgba(79, 140, 255, 0.15)',
          fill: true,
          tension: 0.3,
          pointRadius: 3,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#e6e9ef' } } },
        scales: {
          x: { ticks: { color: '#9aa4b2' }, grid: { color: '#2d3542' } },
          y: { ticks: { color: '#9aa4b2' }, grid: { color: '#2d3542' }, beginAtZero: true },
        },
      },
    });
  }

  /* ------------------------------------------------------------ 备份管理 */

  const BACKUP_SOURCES = {
    native: { text: 'OmniArk 备份', cls: 'native' },
    mod: { text: 'FTB 模组', cls: 'mod' },
    plugin: { text: 'eBackup 插件', cls: 'plugin' },
  };

  function backupSourceBadge(source) {
    const meta = BACKUP_SOURCES[source] || { text: source || '未知来源', cls: 'native' };
    return '<span class="badge-source ' + meta.cls + '">' + escapeHtml(meta.text) + '</span>';
  }

  async function loadBackups(name) {
    const body = document.getElementById('backups-body');
    if (!body || currentServer !== name) return;
    const r = await fetchQuiet('/api/server/' + encodeURIComponent(name) + '/backups');
    if (!r.ok || !r.data) {
      body.innerHTML = emptyState('bi-exclamation-circle', '无法获取备份列表');
      return;
    }
    const backups = r.data.backups || [];
    if (!backups.length) {
      body.innerHTML = emptyState('bi-archive', '暂无备份，点击右上角手动创建');
      return;
    }
    body.innerHTML =
      '<div class="table-responsive"><table class="dark-table">' +
        '<thead><tr>' +
          '<th>文件名</th><th style="width:120px">来源</th>' +
          '<th style="width:100px">大小</th><th style="width:170px">时间</th>' +
          '<th style="width:150px">操作</th>' +
        '</tr></thead><tbody id="backups-tbody"></tbody>' +
      '</table></div>';
    const tbody = document.getElementById('backups-tbody');
    backups.forEach((b) => {
      const tr = document.createElement('tr');
      tr.innerHTML =
        '<td><code>' + escapeHtml(b.name) + '</code></td>' +
        '<td>' + backupSourceBadge(b.source) + '</td>' +
        '<td>' + escapeHtml(b.size != null ? b.size : '—') + '</td>' +
        '<td>' + escapeHtml(b.mtime || '—') + '</td>' +
        '<td><div class="d-flex gap-1 flex-wrap">' +
          '<button class="btn btn-accent-outline btn-sm" data-action="restore" ' + adminOnlyAttr() + '>' +
            '<i class="bi bi-arrow-counterclockwise"></i> 恢复</button>' +
          '<button class="btn btn-outline-danger btn-sm" data-action="delete" ' + adminOnlyAttr() + '>' +
            '<i class="bi bi-trash"></i> 删除</button>' +
        '</div></td>';
      tr.querySelector('[data-action="restore"]').addEventListener('click', (e) =>
        backupRestore(name, b.name, e.currentTarget));
      tr.querySelector('[data-action="delete"]').addEventListener('click', (e) =>
        backupDelete(name, b.name, e.currentTarget));
      tbody.appendChild(tr);
    });
  }

  async function backupCreate(name, btn) {
    btnLoading(btn, true);
    try {
      const data = await postJson('/api/server/' + encodeURIComponent(name) + '/backups/create');
      toast('success', '备份已创建：' + (data.file || ''));
      loadBackups(name);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function backupRestore(name, file, btn) {
    const ok = await confirmAction(
      '恢复备份（回档）',
      '确定要将服务器 <strong>' + escapeHtml(name) + '</strong> 回档到备份 ' +
      '<code>' + escapeHtml(file) + '</code> 吗？<br>' +
      '<span style="color:var(--warning)"><i class="bi bi-exclamation-triangle"></i> ' +
      '回档前会自动备份当前存档。</span>',
      '确认回档');
    if (!ok) return;
    btnLoading(btn, true);
    try {
      const data = await postJson('/api/server/' + encodeURIComponent(name) + '/backups/restore',
        { file: file });
      toast('success', data.message || '回档完成，回档前存档已自动备份');
      loadBackups(name);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function backupDelete(name, file, btn) {
    const ok = await confirmAction(
      '删除备份',
      '确定要删除备份 <code>' + escapeHtml(file) + '</code> 吗？<br>' +
      '<span style="color:var(--danger)">该操作不可恢复！</span>',
      '确认删除');
    if (!ok) return;
    btnLoading(btn, true);
    try {
      await postJson('/api/server/' + encodeURIComponent(name) + '/backups/delete',
        { file: file });
      toast('success', '备份「' + file + '」已删除');
      loadBackups(name);
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  /* ------------------------------------------------------------ 创建服务器 */

  function renderCreate() {
    app().innerHTML =
      '<div class="row justify-content-center"><div class="col-lg-8 col-xl-6">' +
      '<div class="card-panel">' +
        '<div class="card-panel-title"><i class="bi bi-plus-square"></i>创建新的 Minecraft 服务器</div>' +
        '<form id="create-form" method="POST" action="/server/create" novalidate>' +
          '<div class="mb-3">' +
            '<label class="form-label" for="serverName">服务器名称</label>' +
            '<input type="text" class="form-control" id="serverName" name="serverName" ' +
              'placeholder="例如：我的生存服" required>' +
          '</div>' +
          '<div class="row g-3 mb-3">' +
            '<div class="col-md-6">' +
              '<label class="form-label" for="coreType">核心类型</label>' +
              '<select class="form-select" id="coreType" name="coreType">' +
                '<option value="official" selected>官方原版（official）</option>' +
                '<option value="forge">Forge</option>' +
                '<option value="fabric">Fabric</option>' +
                '<option value="mohist">Mohist</option>' +
              '</select>' +
            '</div>' +
            '<div class="col-md-6">' +
              '<label class="form-label" for="coreVersion">游戏版本</label>' +
              '<input type="text" class="form-control" id="coreVersion" name="coreVersion" ' +
                'list="version-list" placeholder="输入以搜索版本，如 1.20" required autocomplete="off">' +
              '<datalist id="version-list"></datalist>' +
              '<div class="stat-sub mt-1" id="version-hint">正在加载版本列表…</div>' +
            '</div>' +
          '</div>' +
          '<div class="row g-3 mb-3">' +
            '<div class="col-md-6">' +
              '<label class="form-label" for="port">端口</label>' +
              '<input type="number" class="form-control" id="port" name="port" ' +
                'value="25565" min="1024" max="65535" required>' +
            '</div>' +
            '<div class="col-md-6">' +
              '<label class="form-label" for="gameMode">默认游戏模式</label>' +
              '<select class="form-select" id="gameMode" name="gameMode">' +
                '<option value="survival" selected>生存模式（survival）</option>' +
                '<option value="creative">创造模式（creative）</option>' +
                '<option value="adventure">冒险模式（adventure）</option>' +
                '<option value="spectator">旁观模式（spectator）</option>' +
              '</select>' +
            '</div>' +
          '</div>' +
          '<div class="row g-3 mb-4">' +
            '<div class="col-md-6">' +
              '<input type="hidden" name="pvpEnabled" value="false">' +
              '<div class="form-check form-switch">' +
                '<input class="form-check-input" type="checkbox" id="pvpEnabled" name="pvpEnabled" value="true" checked>' +
                '<label class="form-check-label" for="pvpEnabled">启用 PVP</label>' +
              '</div>' +
            '</div>' +
            '<div class="col-md-6">' +
              '<input type="hidden" name="onlineMode" value="false">' +
              '<div class="form-check form-switch">' +
                '<input class="form-check-input" type="checkbox" id="onlineMode" name="onlineMode" value="true" checked>' +
                '<label class="form-check-label" for="onlineMode">正版验证（online-mode）</label>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<button type="submit" class="btn btn-primary w-100" id="create-submit" data-admin-only>' +
            '<i class="bi bi-rocket-takeoff"></i> 创建服务器</button>' +
        '</form>' +
      '</div></div></div>';

    /* 复选框开关：勾选时表单同时提交 true/false，后端以包含 true 为准，
       未勾选时仅有 hidden 的 false。 */
    ['pvpEnabled', 'onlineMode'].forEach((id) => {
      const box = document.getElementById(id);
      box.addEventListener('change', () => {
        box.closest('.col-md-6').querySelector('input[type="hidden"]').value =
          box.checked ? 'true' : 'false';
      });
    });

    /* 版本可搜索下拉 */
    loadVersions();

    /* 提交：校验 + 加载遮罩，随后走原生表单提交到 /server/create */
    document.getElementById('create-form').addEventListener('submit', (e) => {
      if (!isAdmin()) {
        e.preventDefault();
        toast('warning', '创建服务器需要管理员权限');
        return;
      }
      const name = document.getElementById('serverName').value.trim();
      const version = document.getElementById('coreVersion').value.trim();
      const port = parseInt(document.getElementById('port').value, 10);
      if (!name || !version) {
        e.preventDefault();
        toast('warning', '服务器名称与游戏版本不能为空');
        return;
      }
      if (!Number.isInteger(port) || port < 1024 || port > 65535) {
        e.preventDefault();
        toast('warning', '端口号必须是 1024-65535 之间的整数');
        return;
      }
      showLoading('正在创建并下载服务器核心，可能需要几分钟，请勿关闭页面…');
    });
  }

  async function loadVersions() {
    const listEl = document.getElementById('version-list');
    const hint = document.getElementById('version-hint');
    const r = await fetchQuiet('/api/program/minecraft_version');
    if (!listEl) return;
    if (!r.ok || !r.data || !Array.isArray(r.data.minecraft_version)) {
      hint.textContent = '版本列表加载失败，可手动输入版本号';
      toast('warning', 'Minecraft 版本列表获取失败，请手动输入版本');
      return;
    }
    listEl.innerHTML = r.data.minecraft_version
      .map((v) => '<option value="' + escapeHtml(v) + '"></option>').join('');
    hint.textContent = '共 ' + r.data.minecraft_version.length + ' 个版本可选，输入关键字筛选';
  }

  /* ------------------------------------------------------------ 设置 */

  function renderSettings() {
    app().innerHTML =
      '<div class="row g-3">' +
        '<div class="col-lg-6"><div class="card-panel">' +
          '<div class="card-panel-title"><i class="bi bi-memory"></i>运行内存</div>' +
          '<div class="mb-3"><label class="form-label" for="set-min_memory">最小内存 Xms（MB）</label>' +
            '<input type="number" class="form-control" id="set-min_memory" min="256"></div>' +
          '<div class="mb-3"><label class="form-label" for="set-max_memory">最大内存 Xmx（MB）</label>' +
            '<input type="number" class="form-control" id="set-max_memory" min="256"></div>' +
          '<div class="mb-3"><label class="form-label" for="set-server_port">Web 面板端口</label>' +
            '<input type="number" class="form-control" id="set-server_port" min="1024" max="65535"></div>' +
        '</div></div>' +
        '<div class="col-lg-6"><div class="card-panel">' +
          '<div class="card-panel-title"><i class="bi bi-toggle-on"></i>启动行为</div>' +
          switchRow('set-nogui_enabled', '以 nogui 模式启动服务器') +
          switchRow('set-auto_start', '启动面板时自动启动服务器') +
          switchRow('set-test_versions', '显示 Minecraft 测试版本') +
          '<div class="mb-3 mt-3"><label class="form-label" for="set-eula_wait_time">EULA 等待时间（秒）</label>' +
            '<input type="number" class="form-control" id="set-eula_wait_time" min="0"></div>' +
        '</div></div>' +
        '<div class="col-lg-6"><div class="card-panel">' +
          '<div class="card-panel-title"><i class="bi bi-cloud-download"></i>更新与存储</div>' +
          '<div class="mb-3"><label class="form-label" for="set-update_source">自动更新源</label>' +
            '<input type="text" class="form-control" id="set-update_source"></div>' +
          '<div class="mb-3"><label class="form-label" for="set-storage_update_time">存储统计间隔（秒）</label>' +
            '<input type="number" class="form-control" id="set-storage_update_time" min="10"></div>' +
        '</div></div>' +
        '<div class="col-12">' +
          '<button class="btn btn-primary" id="settings-save" data-admin-only><i class="bi bi-check-lg"></i> 保存设置</button>' +
        '</div>' +
      '</div>';

    document.getElementById('settings-save').addEventListener('click', (e) =>
      saveSettings(e.currentTarget));
    loadSettings();
  }

  function switchRow(id, label) {
    return '<div class="form-check form-switch mb-2">' +
      '<input class="form-check-input" type="checkbox" id="' + id + '">' +
      '<label class="form-check-label" for="' + id + '">' + escapeHtml(label) + '</label>' +
      '</div>';
  }

  const SETTINGS_KEYS = ['min_memory', 'max_memory', 'nogui_enabled', 'eula_wait_time',
    'auto_start', 'update_source', 'test_versions', 'storage_update_time', 'server_port'];
  const SETTINGS_SWITCHES = ['nogui_enabled', 'auto_start', 'test_versions'];

  async function loadSettings() {
    let data;
    try {
      data = await apiJson('/api/program/get/settings');
    } catch (err) {
      toast('danger', '读取设置失败');
      return;
    }
    SETTINGS_KEYS.forEach((key) => {
      const el = document.getElementById('set-' + key);
      if (!el || data[key] == null) return;
      if (SETTINGS_SWITCHES.includes(key)) {
        el.checked = Boolean(data[key]);
      } else {
        el.value = data[key];
      }
    });
  }

  async function saveSettings(btn) {
    const payload = {};
    SETTINGS_KEYS.forEach((key) => {
      const el = document.getElementById('set-' + key);
      if (!el) return;
      if (SETTINGS_SWITCHES.includes(key)) {
        payload[key] = el.checked;
      } else if (el.type === 'number') {
        payload[key] = el.value === '' ? null : Number(el.value);
      } else {
        payload[key] = el.value;
      }
    });
    btnLoading(btn, true);
    try {
      await postJson('/api/program/set/settings', payload);
      toast('success', '设置已保存');
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  /* ------------------------------------------------------------ Java 管理 */

  function javaValidBadge(valid) {
    return valid
      ? '<span class="badge-status running"><span class="dot"></span>有效</span>'
      : '<span class="badge-status stopped"><span class="dot"></span>失效</span>';
  }

  function renderJava() {
    app().innerHTML =
      '<div class="d-flex align-items-center gap-2 mb-3 flex-wrap">' +
        '<h2 class="section-title mb-0"><i class="bi bi-cup-hot"></i>Java 管理</h2>' +
        '<div class="ms-auto">' +
          '<button class="btn btn-outline-secondary btn-sm" id="java-refresh">' +
            '<i class="bi bi-arrow-clockwise"></i> 刷新</button>' +
        '</div>' +
      '</div>' +
      '<div class="row g-3">' +
        '<div class="col-12"><div class="card-panel">' +
          '<div class="card-panel-title"><i class="bi bi-diagram-2"></i>版本映射</div>' +
          '<div class="table-responsive"><table class="dark-table">' +
            '<thead><tr>' +
              '<th style="width:110px">版本键</th><th>java.exe 路径</th>' +
              '<th style="width:90px">状态</th><th style="width:90px">操作</th>' +
            '</tr></thead>' +
            '<tbody id="java-mapping-body">' +
              '<tr><td colspan="4" class="text-secondary">加载中…</td></tr>' +
            '</tbody>' +
          '</table></div>' +
        '</div></div>' +
        '<div class="col-lg-5"><div class="card-panel h-100">' +
          '<div class="card-panel-title"><i class="bi bi-plus-lg"></i>添加 Java</div>' +
          '<div class="mb-2">' +
            '<label class="form-label" for="java-add-path">java.exe 路径</label>' +
            '<input type="text" class="form-control" id="java-add-path" ' +
              'placeholder="如 C:\\Program Files\\Java\\jdk-21\\bin\\java.exe">' +
          '</div>' +
          '<div class="d-flex gap-2 flex-wrap">' +
            '<button class="btn btn-primary btn-sm" id="java-add-btn" data-admin-only>' +
              '<i class="bi bi-plus-lg"></i> 添加</button>' +
            '<button class="btn btn-accent-outline btn-sm" id="java-rescan-btn" data-admin-only>' +
              '<i class="bi bi-arrow-repeat"></i> 一键重扫描</button>' +
          '</div>' +
          '<div class="stat-sub mt-2" id="java-auto-hint">支持自动安装的版本：…</div>' +
        '</div></div>' +
        '<div class="col-lg-7"><div class="card-panel h-100">' +
          '<div class="card-panel-title"><i class="bi bi-search"></i>系统检测到的 Java</div>' +
          '<div class="table-responsive"><table class="dark-table">' +
            '<thead><tr>' +
              '<th>路径</th><th style="width:110px">版本</th>' +
              '<th style="width:80px">主版本</th><th style="width:150px">操作</th>' +
            '</tr></thead>' +
            '<tbody id="java-installations-body">' +
              '<tr><td colspan="4" class="text-secondary">加载中…</td></tr>' +
            '</tbody>' +
          '</table></div>' +
        '</div></div>' +
      '</div>';

    document.getElementById('java-refresh').addEventListener('click', renderJava);
    document.getElementById('java-add-btn').addEventListener('click', (e) => {
      javaAdd(document.getElementById('java-add-path').value.trim(), e.currentTarget);
    });
    document.getElementById('java-add-path').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        javaAdd(e.currentTarget.value.trim(), document.getElementById('java-add-btn'));
      }
    });
    document.getElementById('java-rescan-btn').addEventListener('click', (e) =>
      javaRescan(e.currentTarget));
    loadJavaData();
  }

  async function loadJavaData() {
    const mappingBody = document.getElementById('java-mapping-body');
    if (!mappingBody) return;
    let data;
    try {
      data = await apiJson('/api/java/list');
    } catch (err) {
      mappingBody.innerHTML =
        '<tr><td colspan="4" class="text-secondary">无法加载 Java 配置</td></tr>';
      return;
    }

    /* 版本映射表 */
    const configured = data.configured || [];
    if (!configured.length) {
      mappingBody.innerHTML =
        '<tr><td colspan="4" class="text-secondary">暂无版本映射，可添加或重扫描</td></tr>';
    } else {
      mappingBody.innerHTML = '';
      configured.forEach((item) => {
        const tr = document.createElement('tr');
        tr.innerHTML =
          '<td><strong>' + escapeHtml(item.key) + '</strong></td>' +
          '<td>' + (item.path
            ? '<code>' + escapeHtml(item.path) + '</code>'
            : '<span class="text-secondary">（未配置）</span>') + '</td>' +
          '<td>' + javaValidBadge(item.valid) + '</td>' +
          '<td><button class="btn btn-outline-danger btn-sm" data-action="remove" ' + adminOnlyAttr() + '>' +
            '<i class="bi bi-trash"></i> 移除</button></td>';
        tr.querySelector('[data-action="remove"]').addEventListener('click', (e) =>
          javaRemove(item.key, e.currentTarget));
        mappingBody.appendChild(tr);
      });
    }

    /* 系统检测到的 Java */
    const instBody = document.getElementById('java-installations-body');
    const installations = data.installations || [];
    if (!installations.length) {
      instBody.innerHTML =
        '<tr><td colspan="4" class="text-secondary">未在系统中检测到 Java 安装</td></tr>';
    } else {
      instBody.innerHTML = '';
      installations.forEach((inst) => {
        const major = inst.major != null ? String(inst.major) : '未知';
        const tr = document.createElement('tr');
        tr.innerHTML =
          '<td><code>' + escapeHtml(inst.path) + '</code></td>' +
          '<td>' + escapeHtml(inst.version) + '</td>' +
          '<td>' + escapeHtml(major) + '</td>' +
          '<td><button class="btn btn-accent-outline btn-sm" data-action="use" ' + adminOnlyAttr() + '>' +
            '<i class="bi bi-check2-circle"></i> 设为该版本默认</button></td>';
        tr.querySelector('[data-action="use"]').addEventListener('click', (e) =>
          javaAdd(inst.path, e.currentTarget));
        instBody.appendChild(tr);
      });
    }

    /* 自动安装支持版本提示 */
    const hint = document.getElementById('java-auto-hint');
    const supported = data.auto_install_supported || [];
    hint.textContent = supported.length
      ? '支持自动安装的版本：' + supported.join('、')
      : '当前环境不支持自动安装';
  }

  async function javaAdd(path, btn) {
    if (!path) {
      toast('warning', '请输入 java.exe 路径');
      return;
    }
    btnLoading(btn, true);
    try {
      const data = await postJson('/api/java/add', { path: path });
      toast('success', '已添加 Java ' + data.major + '（' + data.version + '）');
      renderJava();
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function javaRemove(key, btn) {
    const ok = await confirmAction(
      '移除 Java 映射',
      '确定要移除版本键 <strong>' + escapeHtml(key) + '</strong> 对应的 Java 路径吗？',
      '确认移除');
    if (!ok) return;
    btnLoading(btn, true);
    try {
      await postJson('/api/java/remove', { key: key });
      toast('success', '版本键「' + key + '」的映射已移除');
      loadJavaData();
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function javaRescan(btn) {
    btnLoading(btn, true);
    try {
      const data = await postJson('/api/java/rescan');
      const filled = data.filled || [];
      toast('success', filled.length
        ? '重扫描完成，已回填版本：' + filled.join('、')
        : '重扫描完成，没有需要回填的空缺槽位');
      loadJavaData();
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  /* ------------------------------------------------------------ 账号管理 */

  function renderAccounts() {
    app().innerHTML =
      '<div class="d-flex align-items-center gap-2 mb-3 flex-wrap">' +
        '<h2 class="section-title mb-0"><i class="bi bi-person-gear"></i>账号管理</h2>' +
        '<div class="ms-auto d-flex gap-2">' +
          '<button class="btn btn-outline-secondary btn-sm" id="accounts-refresh">' +
            '<i class="bi bi-arrow-clockwise"></i> 刷新</button>' +
          '<button class="btn btn-primary btn-sm" id="account-create-open">' +
            '<i class="bi bi-person-plus"></i> 新建账号</button>' +
        '</div>' +
      '</div>' +
      '<div class="card-panel">' +
        '<div class="card-panel-title"><i class="bi bi-people"></i>管理员账号</div>' +
        '<div class="table-responsive"><table class="dark-table">' +
          '<thead><tr><th>账号名称</th><th style="width:200px">操作</th></tr></thead>' +
          '<tbody id="accounts-body">' +
            '<tr><td colspan="2" class="text-secondary">加载中…</td></tr>' +
          '</tbody>' +
        '</table></div>' +
        '<p class="stat-sub mt-2 mb-0">最后一个管理员账号无法删除。</p>' +
      '</div>' +

      /* 新建账号弹窗 */
      '<div class="modal fade" id="account-create-modal" tabindex="-1" aria-hidden="true">' +
        '<div class="modal-dialog modal-dialog-centered"><div class="modal-content">' +
          '<div class="modal-header">' +
            '<h5 class="modal-title">新建账号</h5>' +
            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>' +
          '</div>' +
          '<div class="modal-body">' +
            '<div class="mb-3"><label class="form-label" for="acc-new-name">账号</label>' +
              '<input type="text" class="form-control" id="acc-new-name" autocomplete="off"></div>' +
            '<div class="mb-3"><label class="form-label" for="acc-new-pass">密码</label>' +
              '<input type="password" class="form-control" id="acc-new-pass" autocomplete="new-password"></div>' +
            '<div class="mb-1"><label class="form-label" for="acc-new-pass2">确认密码</label>' +
              '<input type="password" class="form-control" id="acc-new-pass2" autocomplete="new-password"></div>' +
          '</div>' +
          '<div class="modal-footer">' +
            '<button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">取消</button>' +
            '<button type="button" class="btn btn-primary" id="account-create-submit">创建</button>' +
          '</div>' +
        '</div></div>' +
      '</div>' +

      /* 修改密码弹窗 */
      '<div class="modal fade" id="account-pass-modal" tabindex="-1" aria-hidden="true">' +
        '<div class="modal-dialog modal-dialog-centered"><div class="modal-content">' +
          '<div class="modal-header">' +
            '<h5 class="modal-title">修改密码：<span id="acc-pass-name"></span></h5>' +
            '<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>' +
          '</div>' +
          '<div class="modal-body">' +
            '<div class="mb-3"><label class="form-label" for="acc-old-pass">旧密码</label>' +
              '<input type="password" class="form-control" id="acc-old-pass" autocomplete="current-password"></div>' +
            '<div class="mb-3"><label class="form-label" for="acc-new-pass1">新密码</label>' +
              '<input type="password" class="form-control" id="acc-new-pass1" autocomplete="new-password"></div>' +
            '<div class="mb-1"><label class="form-label" for="acc-new-pass3">确认新密码</label>' +
              '<input type="password" class="form-control" id="acc-new-pass3" autocomplete="new-password"></div>' +
          '</div>' +
          '<div class="modal-footer">' +
            '<button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">取消</button>' +
            '<button type="button" class="btn btn-primary" id="account-pass-submit">保存</button>' +
          '</div>' +
        '</div></div>' +
      '</div>';

    document.getElementById('accounts-refresh').addEventListener('click', renderAccounts);
    document.getElementById('account-create-open').addEventListener('click', () => {
      ['acc-new-name', 'acc-new-pass', 'acc-new-pass2'].forEach((id) => {
        document.getElementById(id).value = '';
      });
      bootstrap.Modal.getOrCreateInstance(document.getElementById('account-create-modal')).show();
    });
    document.getElementById('account-create-submit').addEventListener('click', (e) =>
      accountCreate(e.currentTarget));
    loadAccounts();
  }

  async function loadAccounts() {
    const body = document.getElementById('accounts-body');
    if (!body) return;
    let data;
    try {
      data = await apiJson('/api/account/list');
    } catch (err) {
      body.innerHTML =
        '<tr><td colspan="2" class="text-secondary">无法加载账号列表</td></tr>';
      return;
    }
    const accounts = data.accounts || [];
    if (!accounts.length) {
      body.innerHTML =
        '<tr><td colspan="2" class="text-secondary">暂无管理员账号</td></tr>';
      return;
    }
    body.innerHTML = '';
    accounts.forEach((item) => {
      const name = typeof item === 'object' ? (item.account || item.name || JSON.stringify(item)) : item;
      const tr = document.createElement('tr');
      tr.innerHTML =
        '<td><i class="bi bi-person-circle me-1"></i><strong>' + escapeHtml(name) + '</strong></td>' +
        '<td><div class="d-flex gap-2">' +
          '<button class="btn btn-accent-outline btn-sm" data-action="pass">' +
            '<i class="bi bi-key"></i> 改密</button>' +
          '<button class="btn btn-outline-danger btn-sm" data-action="delete">' +
            '<i class="bi bi-trash"></i> 删除</button>' +
        '</div></td>';
      tr.querySelector('[data-action="pass"]').addEventListener('click', () => {
        document.getElementById('acc-pass-name').textContent = name;
        ['acc-old-pass', 'acc-new-pass1', 'acc-new-pass3'].forEach((id) => {
          document.getElementById(id).value = '';
        });
        bootstrap.Modal.getOrCreateInstance(document.getElementById('account-pass-modal')).show();
        const submit = document.getElementById('account-pass-submit');
        submit.onclick = () => accountChangePassword(name, submit);
      });
      tr.querySelector('[data-action="delete"]').addEventListener('click', (e) =>
        accountDelete(name, e.currentTarget));
      body.appendChild(tr);
    });
  }

  async function accountCreate(btn) {
    const account = document.getElementById('acc-new-name').value.trim();
    const password = document.getElementById('acc-new-pass').value;
    const password2 = document.getElementById('acc-new-pass2').value;
    if (!account || !password) {
      toast('warning', '账号与密码不能为空');
      return;
    }
    if (password !== password2) {
      toast('warning', '两次输入的密码不一致');
      return;
    }
    btnLoading(btn, true);
    try {
      await postJson('/api/account/create', { account: account, password: password });
      toast('success', '账号「' + account + '」已创建');
      bootstrap.Modal.getOrCreateInstance(document.getElementById('account-create-modal')).hide();
      loadAccounts();
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function accountChangePassword(account, btn) {
    const oldPassword = document.getElementById('acc-old-pass').value;
    const newPassword = document.getElementById('acc-new-pass1').value;
    const newPassword2 = document.getElementById('acc-new-pass3').value;
    if (!oldPassword || !newPassword) {
      toast('warning', '旧密码与新密码不能为空');
      return;
    }
    if (newPassword !== newPassword2) {
      toast('warning', '两次输入的新密码不一致');
      return;
    }
    btnLoading(btn, true);
    try {
      await postJson('/api/account/password', {
        account: account, old_password: oldPassword, new_password: newPassword,
      });
      toast('success', '账号「' + account + '」的密码已修改');
      bootstrap.Modal.getOrCreateInstance(document.getElementById('account-pass-modal')).hide();
    } catch (err) { /* 错误已 Toast */ }
    finally { btnLoading(btn, false); }
  }

  async function accountDelete(account, btn) {
    const ok = await confirmAction(
      '删除账号',
      '确定要删除管理员账号 <strong>' + escapeHtml(account) + '</strong> 吗？',
      '确认删除');
    if (!ok) return;
    btnLoading(btn, true);
    try {
      await postJson('/api/account/delete', { account: account });
      toast('success', '账号「' + account + '」已删除');
      loadAccounts();
    } catch (err) { /* 错误已 Toast（最后一个账号会被后端拒绝） */ }
    finally { btnLoading(btn, false); }
  }

  /* ------------------------------------------------------------ API 帮助 */

  const API_ROUTES = [
    { group: '程序信息', method: 'GET', path: '/api/program/version', desc: '获取程序版本号' },
    { group: '程序信息', method: 'GET', path: '/api/program/minecraft_version', desc: '获取 Minecraft 版本列表' },
    { group: '程序信息', method: 'GET', path: '/api/program/disk_usage', desc: '磁盘占用统计' },
    { group: '程序信息', method: 'GET', path: '/api/program/get/CPU/Usage', desc: 'CPU 占用率' },
    { group: '程序信息', method: 'GET', path: '/api/program/get/RAM/Usage', desc: '内存占用率' },
    { group: '程序信息', method: 'GET', path: '/api/program/get/settings', desc: '读取程序设置' },
    { group: '程序信息', method: 'POST', path: '/api/program/set/settings', desc: '保存程序设置（JSON 体）' },
    { group: '服务器', method: 'GET', path: '/api/server/list', desc: '服务器名列表与数量' },
    { group: '服务器', method: 'GET', path: '/api/server/status/<name>', desc: '服务器运行状态（一律 200）' },
    { group: '服务器', method: 'GET', path: '/api/server/info/<name>', desc: '版本/大小/启动次数等信息' },
    { group: '服务器', method: 'GET', path: '/api/server/latest', desc: '最近启动的服务器（无记录时 404）' },
    { group: '服务器', method: 'GET', path: '/api/server/players/<name>', desc: '在线玩家（未运行返回 null）' },
    { group: '服务器', method: 'POST', path: '/api/server/<name>/start', desc: '启动服务器', auth: true },
    { group: '服务器', method: 'POST', path: '/api/server/<name>/stop', desc: '停止服务器', auth: true },
    { group: '服务器', method: 'POST', path: '/api/server/<name>/restart', desc: '重启服务器', auth: true },
    { group: '服务器', method: 'POST', path: '/api/server/delete/<name>', desc: '删除服务器', auth: true },
    { group: '服务器', method: 'POST', path: '/api/server/<name>/command', desc: 'RCON 执行命令 {command}', auth: true },
    { group: '服务器', method: 'GET', path: '/api/server/get/<name>/terminal/logs', desc: '终端日志（{logs:[...]}）' },
    { group: '服务器', method: 'POST', path: '/api/server/info/<name>/excel', desc: '导出单台服务器 Excel' },
    { group: '服务器', method: 'POST', path: '/api/server/list/excel', desc: '导出全部服务器 Excel' },
    { group: '服务器', method: 'GET', path: '/api/server/<name>/storage_info', desc: '存储占用历史 {labels,values,type}' },
    { group: '终端（兼容）', method: 'GET', path: '/api/server/terminal/<name>', desc: '最近 1000 行终端日志' },
    { group: '终端（兼容）', method: 'POST', path: '/api/server/terminal/<name>', desc: 'RCON 执行命令 {command}', auth: true },
    { group: '服务器配置', method: 'GET', path: '/api/server/get/document/server.properties/<name>', desc: '读取 server.properties' },
    { group: '服务器配置', method: 'GET', path: '/api/server/get/run_memory/<name>', desc: '读取运行内存 {min,max}' },
    { group: '服务器配置', method: 'POST', path: '/api/server/set/settings/<name>', desc: '批量修改服务器设置（表单）' },
    { group: '玩家名单', method: 'GET', path: '/api/server/get/banned/players/<name>', desc: '封禁玩家列表' },
    { group: '玩家名单', method: 'GET', path: '/api/server/get/banned/ips/<name>', desc: '封禁 IP 列表' },
    { group: '玩家名单', method: 'GET', path: '/api/server/get/white-list/<name>', desc: '白名单（未启用时 success:false）' },
    { group: '玩家名单', method: 'GET', path: '/api/server/get/history/players/<name>', desc: '历史玩家（无记录时 success:false）' },
    { group: '文件管理', method: 'GET', path: '/api/manager/<server>/list?path=<rel>', desc: '列出目录内容' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/create/file', desc: '新建文件 {path}' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/create/folder', desc: '新建文件夹 {path}' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/delete/file', desc: '删除文件 {path}' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/delete/folder', desc: '删除文件夹 {path}' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/rename', desc: '重命名 {old_path, new_path}' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/copy', desc: '复制 {source_paths, target_path}' },
    { group: '文件管理', method: 'POST', path: '/api/manager/<server>/move', desc: '移动 {source_paths, target_path}' },
    { group: '文件管理', method: 'GET', path: '/api/get/directory?path=<abs>', desc: '旧版目录浏览（兼容接口）' },
    { group: 'Java 管理', method: 'GET', path: '/api/java/list', desc: '已配置映射与系统扫描到的 Java 安装' },
    { group: 'Java 管理', method: 'POST', path: '/api/java/add', desc: '添加 java.exe 路径 {path}（实测版本后写入槽位）', auth: true },
    { group: 'Java 管理', method: 'POST', path: '/api/java/remove', desc: '移除版本映射 {key 或 path}', auth: true },
    { group: 'Java 管理', method: 'POST', path: '/api/java/rescan', desc: '重扫描系统 Java 并回填空缺槽位', auth: true },
    { group: 'Java 管理', method: 'GET', path: '/api/java/check/<name>', desc: '查询服务器核心所需 Java 及解析结果' },
    { group: '备份管理', method: 'GET', path: '/api/server/<name>/backups', desc: '备份列表 {backups:[{name,source,size,mtime}]}（来源：native/mod/plugin）', auth: true },
    { group: '备份管理', method: 'POST', path: '/api/server/<name>/backups/create', desc: '手动创建原生备份（打包世界目录）', admin: true },
    { group: '备份管理', method: 'POST', path: '/api/server/<name>/backups/restore', desc: '回档 {file}（回档前自动备份当前存档）', admin: true },
    { group: '备份管理', method: 'POST', path: '/api/server/<name>/backups/delete', desc: '删除备份 {file}', admin: true },
    { group: '账号管理', method: 'GET', path: '/api/account/me', desc: '当前登录用户身份与角色 {account, role, super_admin}', auth: true },
    { group: '账号管理', method: 'GET', path: '/api/account/list', desc: '管理员账号列表 {accounts}', auth: true },
    { group: '账号管理', method: 'POST', path: '/api/account/create', desc: '新建账号 {account, password}', auth: true },
    { group: '账号管理', method: 'POST', path: '/api/account/delete', desc: '删除账号 {account}（最后一个账号会被拒绝）', auth: true },
    { group: '账号管理', method: 'POST', path: '/api/account/password', desc: '修改密码 {account, old_password, new_password}', auth: true },
    { group: '账号管理', method: 'POST', path: '/api/account/role', desc: '修改账户权限级别 {account, role}（Ksayus 不可降级）', admin: true },
    { group: '页面', method: 'GET', path: '/', desc: '主控台（SPA）' },
    { group: '页面', method: 'GET/POST', path: '/login', desc: '管理员登录' },
    { group: '页面', method: 'GET', path: '/logout', desc: '退出登录' },
    { group: '页面', method: 'GET/POST', path: '/server/create', desc: '创建服务器（表单字段见创建页）' },
    { group: '页面', method: 'GET', path: '/server/settings/<name>', desc: '服务器设置页' },
    { group: '页面', method: 'GET', path: '/manager/<name>', desc: '文件管理器页' },
    { group: '页面', method: 'GET', path: '/server/<name>/storage_chart', desc: '存储图表页' },
    { group: '杂项', method: 'GET', path: '/api', desc: 'API 欢迎页' },
    { group: '杂项', method: 'GET', path: '/api/static/ico', desc: '站点图标' },
  ];

  function renderHelp() {
    const groups = [];
    API_ROUTES.forEach((r) => { if (!groups.includes(r.group)) groups.push(r.group); });
    let html =
      '<div class="card-panel mb-3">' +
        '<div class="card-panel-title"><i class="bi bi-question-circle"></i>API 路由清单</div>' +
        '<input type="text" class="form-control" id="help-filter" placeholder="输入关键字过滤路由…">' +
        '<p class="stat-sub mt-2 mb-0">标注 <span class="auth-tag">需登录</span> 的接口要求会话鉴权，' +
        '标注 <span class="auth-tag">需管理员</span> 的接口额外要求 admin 角色（否则 403）；' +
        'AJAX 请求未登录时返回 401（请携带 X-Requested-With: XMLHttpRequest 头）。</p>' +
      '</div>';
    groups.forEach((group) => {
      html += '<div class="card-panel mb-3 help-group">' +
        '<div class="card-panel-title"><i class="bi bi-diagram-3"></i>' + escapeHtml(group) + '</div>' +
        '<div class="table-responsive"><table class="dark-table">' +
        '<thead><tr><th style="width:90px">方法</th><th>路径</th><th>说明</th></tr></thead><tbody>';
      API_ROUTES.filter((r) => r.group === group).forEach((r) => {
        const methodClass = r.method.indexOf('POST') >= 0 ? 'method-post' : 'method-get';
        html += '<tr class="help-row" data-search="' +
          escapeHtml((r.method + ' ' + r.path + ' ' + r.desc).toLowerCase()) + '">' +
          '<td><span class="method-badge ' + methodClass + '">' + escapeHtml(r.method) + '</span></td>' +
          '<td><code>' + escapeHtml(r.path) + '</code>' +
          (r.admin ? ' <span class="auth-tag"><i class="bi bi-shield-lock-fill"></i> 需管理员</span>'
            : (r.auth ? ' <span class="auth-tag"><i class="bi bi-lock-fill"></i> 需登录</span>' : '')) +
          '</td><td>' + escapeHtml(r.desc) + '</td></tr>';
      });
      html += '</tbody></table></div></div>';
    });
    app().innerHTML = html;

    document.getElementById('help-filter').addEventListener('input', (e) => {
      const kw = e.target.value.trim().toLowerCase();
      document.querySelectorAll('.help-row').forEach((row) => {
        row.style.display = !kw || row.dataset.search.includes(kw) ? '' : 'none';
      });
      document.querySelectorAll('.help-group').forEach((groupEl) => {
        const visible = Array.from(groupEl.querySelectorAll('.help-row'))
          .some((row) => row.style.display !== 'none');
        groupEl.style.display = visible ? '' : 'none';
      });
    });
  }

  /* ------------------------------------------------------------ 初始化 */

  async function loadVersion() {
    const r = await fetchQuiet('/api/program/version');
    if (r.ok && r.data && r.data.version) {
      document.getElementById('sidebar-version').textContent = r.data.version;
      document.getElementById('topbar-version').textContent = r.data.version;
    }
  }

  function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    document.getElementById('sidebar-toggle').addEventListener('click', () => {
      sidebar.classList.toggle('open');
      backdrop.classList.toggle('show');
    });
    backdrop.addEventListener('click', () => {
      sidebar.classList.remove('open');
      backdrop.classList.remove('show');
    });
    document.querySelectorAll('.sidebar-nav .nav-item').forEach((item) => {
      item.addEventListener('click', () => {
        sidebar.classList.remove('open');
        backdrop.classList.remove('show');
      });
    });
  }

  window.addEventListener('hashchange', router);
  document.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    loadVersion();
    loadAccount();
    if (!location.hash) location.hash = '#/dashboard';
    router();
  });
})();

/* =========================================================
 * OmniArk 文件管理器（manager.html）
 * API 契约（omniark/interfaces/web/routes/manager_api.py）：
 *   GET  /api/manager/<name>/list?path=<rel>
 *        → {success, path, entries:[{name, is_dir, size, modified}]}
 *   POST create/file | create/folder   {path}
 *   POST delete/file | delete/folder   {path}
 *   POST rename                        {old_path, new_path}  （new_path 为完整新路径）
 *   POST copy | move                   {source_paths: [...], target_path}
 * 所有路径均为服务器目录内的相对路径（"/" 分隔，根目录为 ""）。
 * ========================================================= */

(function () {
  'use strict';

  const SERVER_NAME = window.SERVER_NAME;
  const API = '/api/manager/' + encodeURIComponent(SERVER_NAME);

  let currentPath = '';            // 当前目录（相对路径）
  let entries = [];                // 当前目录条目
  const selected = new Set();      // 已选中的条目名

  // ---------- DOM ----------
  const tbody = document.getElementById('file-tbody');
  const breadcrumbEl = document.getElementById('breadcrumb');
  const loadingEl = document.getElementById('loading');
  const emptyEl = document.getElementById('empty');
  const statusCount = document.getElementById('status-count');
  const statusSelected = document.getElementById('status-selected');
  const checkAll = document.getElementById('check-all');

  const inputModal = new bootstrap.Modal(document.getElementById('inputModal'));
  const confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));

  // ---------- 工具 ----------
  function joinPath(base, name) {
    return base ? base + '/' + name : name;
  }

  function humanSize(bytes) {
    if (bytes === null || bytes === undefined) return '—';
    if (bytes < 1024) return bytes + ' B';
    const units = ['KB', 'MB', 'GB', 'TB'];
    let value = bytes;
    let unit = 'B';
    for (const u of units) {
      if (value < 1024) break;
      value /= 1024;
      unit = u;
    }
    return value.toFixed(value >= 100 ? 0 : 1) + ' ' + unit;
  }

  function setLoading(on) {
    loadingEl.style.display = on ? 'flex' : 'none';
  }

  function updateStatusbar() {
    statusCount.textContent = entries.length + ' 个项目';
    statusSelected.textContent = '已选择 ' + selected.size + ' 个项目';
    checkAll.checked = entries.length > 0 && selected.size === entries.length;
    checkAll.indeterminate = selected.size > 0 && selected.size < entries.length;
  }

  // ---------- 面包屑 ----------
  function renderBreadcrumb() {
    breadcrumbEl.textContent = '';

    const root = document.createElement('span');
    root.className = 'crumb' + (currentPath === '' ? ' current' : '');
    root.innerHTML = '<i class="bi bi-house-door"></i> 根目录';
    if (currentPath !== '') {
      root.addEventListener('click', () => navigateTo(''));
    }
    breadcrumbEl.appendChild(root);

    if (!currentPath) return;
    const parts = currentPath.split('/');
    parts.forEach((part, i) => {
      const sep = document.createElement('span');
      sep.className = 'sep';
      sep.textContent = '/';
      breadcrumbEl.appendChild(sep);

      const crumb = document.createElement('span');
      const isLast = i === parts.length - 1;
      crumb.className = 'crumb' + (isLast ? ' current' : '');
      crumb.textContent = part;
      if (!isLast) {
        const target = parts.slice(0, i + 1).join('/');
        crumb.addEventListener('click', () => navigateTo(target));
      }
      breadcrumbEl.appendChild(crumb);
    });
  }

  // ---------- 文件表格 ----------

  // 特殊文件：按文件名（小写）匹配图标与彩色徽章
  const SPECIAL_FILES = {
    'server.properties': { icon: 'bi-gear-fill', badge: '配置', cls: 'config' },
    'white-list.json': { icon: 'bi-list-check', badge: '白名单', cls: 'whitelist' },
    'whitelist.json': { icon: 'bi-list-check', badge: '白名单', cls: 'whitelist' },
    'ops.json': { icon: 'bi-shield-fill', badge: 'OP', cls: 'op' },
    'banned-players.json': { icon: 'bi-slash-circle', badge: '封禁', cls: 'ban' },
    'banned-ips.json': { icon: 'bi-slash-circle', badge: '封禁', cls: 'ban' },
    'eula.txt': { icon: 'bi-file-earmark-text', badge: '协议', cls: 'eula' },
    'start.bat': { icon: 'bi-terminal', badge: '脚本', cls: 'script' },
    'usercache.json': { icon: 'bi-people', badge: '缓存', cls: 'cache' },
    'omniark.pid': { icon: 'bi-cpu', badge: 'PID', cls: 'pid' },
  };
  const JAR_SPECIAL = { icon: 'bi-archive', badge: 'JAR', cls: 'jar' };

  /** 命中特殊文件时返回 {icon, badge, cls}，否则返回 null（目录恒为 null） */
  function specialFile(entry) {
    if (entry.is_dir) return null;
    const lower = entry.name.toLowerCase();
    if (SPECIAL_FILES[lower]) return SPECIAL_FILES[lower];
    if (lower.endsWith('.jar')) return JAR_SPECIAL;
    return null;
  }

  function fileIcon(entry) {
    if (entry.is_dir) return 'bi-folder-fill icon-dir';
    const special = specialFile(entry);
    if (special) return special.icon + ' icon-' + special.cls;
    const ext = (entry.name.split('.').pop() || '').toLowerCase();
    const map = {
      jar: 'bi-file-earmark-zip', zip: 'bi-file-earmark-zip',
      json: 'bi-file-earmark-code', yml: 'bi-file-earmark-code',
      yaml: 'bi-file-earmark-code', properties: 'bi-file-earmark-text',
      txt: 'bi-file-earmark-text', log: 'bi-file-earmark-text',
      png: 'bi-file-earmark-image', jpg: 'bi-file-earmark-image',
      jpeg: 'bi-file-earmark-image', gif: 'bi-file-earmark-image',
    };
    return (map[ext] || 'bi-file-earmark') + ' icon-file';
  }

  function renderTable() {
    tbody.textContent = '';
    // 目录优先，各自按名称排序
    const sorted = [...entries].sort((a, b) => {
      if (a.is_dir !== b.is_dir) return a.is_dir ? -1 : 1;
      return a.name.localeCompare(b.name, 'zh-CN');
    });

    for (const entry of sorted) {
      const special = specialFile(entry);
      const tr = document.createElement('tr');
      tr.dataset.name = entry.name;
      if (selected.has(entry.name)) tr.classList.add('selected');
      if (special) tr.classList.add('file-special');

      // 复选框
      const tdCheck = document.createElement('td');
      tdCheck.className = 'col-check';
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.className = 'file-check';
      checkbox.checked = selected.has(entry.name);
      checkbox.setAttribute('aria-label', '选择 ' + entry.name);
      checkbox.addEventListener('click', (e) => e.stopPropagation());
      checkbox.addEventListener('change', () => toggleSelect(entry.name, checkbox.checked));
      tdCheck.appendChild(checkbox);

      // 名称
      const tdName = document.createElement('td');
      const nameCell = document.createElement('div');
      nameCell.className = 'file-name-cell';
      const icon = document.createElement('i');
      icon.className = 'bi ' + fileIcon(entry);
      const nameText = document.createElement('span');
      nameText.className = 'name-text';
      nameText.textContent = entry.name;
      nameText.title = entry.name;
      nameCell.append(icon, nameText);
      if (special) {
        const badge = document.createElement('span');
        badge.className = 'file-badge badge-' + special.cls;
        badge.textContent = special.badge;
        nameCell.appendChild(badge);
      }
      tdName.appendChild(nameCell);

      // 大小 / 时间
      const tdSize = document.createElement('td');
      tdSize.className = 'file-size-cell col-size';
      tdSize.textContent = entry.is_dir ? '—' : humanSize(entry.size);
      const tdTime = document.createElement('td');
      tdTime.className = 'file-time-cell col-time';
      tdTime.textContent = entry.modified || '—';

      tr.append(tdCheck, tdName, tdSize, tdTime);

      // 单击行切换选中；双击目录进入
      tr.addEventListener('click', () => toggleSelect(entry.name, !selected.has(entry.name)));
      tr.addEventListener('dblclick', () => {
        if (entry.is_dir) navigateTo(joinPath(currentPath, entry.name));
      });

      tbody.appendChild(tr);
    }

    emptyEl.style.display = sorted.length === 0 ? 'block' : 'none';
    updateStatusbar();
  }

  function toggleSelect(name, on) {
    if (on) selected.add(name); else selected.delete(name);
    const row = tbody.querySelector(`tr[data-name="${CSS.escape(name)}"]`);
    if (row) {
      row.classList.toggle('selected', on);
      row.querySelector('.file-check').checked = on;
    }
    updateStatusbar();
  }

  // ---------- 目录加载 ----------
  async function loadDirectory(path) {
    setLoading(true);
    emptyEl.style.display = 'none';
    try {
      const data = await oaApi(`${API}/list?path=${encodeURIComponent(path)}`);
      currentPath = data.path || '';
      entries = data.entries || [];
      selected.clear();
      renderBreadcrumb();
      renderTable();
    } catch (err) {
      oaToast(`加载目录失败：${err.message}`, 'error');
      entries = [];
      renderTable();
    } finally {
      setLoading(false);
    }
  }

  function navigateTo(path) {
    loadDirectory(path);
  }

  // ---------- 通用 Modal ----------
  /**
   * 输入弹窗。resolve(null) 表示取消。
   */
  function askInput({ title, label, value = '', hint = '', placeholder = '' }) {
    return new Promise((resolve) => {
      const field = document.getElementById('input-modal-field');
      document.getElementById('input-modal-title').textContent = title;
      document.getElementById('input-modal-label').textContent = label;
      document.getElementById('input-modal-hint').textContent = hint;
      field.value = value;
      field.placeholder = placeholder;

      const confirmBtn = document.getElementById('input-modal-confirm');
      const modalEl = document.getElementById('inputModal');

      const cleanup = () => {
        confirmBtn.removeEventListener('click', onConfirm);
        field.removeEventListener('keydown', onKey);
        modalEl.removeEventListener('hidden.bs.modal', onCancel);
      };
      const onConfirm = () => {
        const v = field.value.trim();
        if (!v) { oaToast('输入不能为空', 'error'); return; }
        cleanup();
        inputModal.hide();
        resolve(v);
      };
      const onKey = (e) => { if (e.key === 'Enter') onConfirm(); };
      const onCancel = () => { cleanup(); resolve(null); };

      confirmBtn.addEventListener('click', onConfirm);
      field.addEventListener('keydown', onKey);
      modalEl.addEventListener('hidden.bs.modal', onCancel);
      inputModal.show();
      setTimeout(() => field.focus(), 300);
    });
  }

  /** 确认弹窗。resolve(true) 表示确认。 */
  function askConfirm({ title, body }) {
    return new Promise((resolve) => {
      document.getElementById('confirm-modal-title').textContent = title;
      document.getElementById('confirm-modal-body').textContent = body;

      const confirmBtn = document.getElementById('confirm-modal-confirm');
      const modalEl = document.getElementById('confirmModal');

      const cleanup = () => {
        confirmBtn.removeEventListener('click', onConfirm);
        modalEl.removeEventListener('hidden.bs.modal', onCancel);
      };
      const onConfirm = () => { cleanup(); confirmModal.hide(); resolve(true); };
      const onCancel = () => { cleanup(); resolve(false); };

      confirmBtn.addEventListener('click', onConfirm);
      modalEl.addEventListener('hidden.bs.modal', onCancel);
      confirmModal.show();
    });
  }

  // ---------- 操作 ----------
  function entryByName(name) {
    return entries.find((e) => e.name === name);
  }

  function selectedList() {
    return [...selected];
  }

  function requireSelection(min = 1, exact = false) {
    if (exact && selected.size !== min) {
      oaToast(`请选择 ${min} 个项目`, 'error');
      return null;
    }
    if (selected.size < min) {
      oaToast('请先勾选要操作的项目', 'error');
      return null;
    }
    return selectedList();
  }

  async function postAction(endpoint, body, refresh = true) {
    const data = await oaApi(`${API}/${endpoint}`, {
      method: 'POST',
      body: JSON.stringify(body),
    });
    if (data.message) oaToast(data.message, 'success');
    if (refresh) await loadDirectory(currentPath);
    return data;
  }

  // 新建文件 / 文件夹
  async function createItem(kind) {
    const isFile = kind === 'file';
    const name = await askInput({
      title: isFile ? '新建文件' : '新建文件夹',
      label: isFile ? '文件名' : '文件夹名',
      hint: '将在当前目录（/' + (currentPath || '') + '）下创建',
      placeholder: isFile ? 'example.txt' : '新建文件夹',
    });
    if (name === null) return;
    if (name.includes('/') || name.includes('\\')) {
      oaToast('名称不能包含路径分隔符', 'error');
      return;
    }
    try {
      await postAction(`create/${kind}`, { path: joinPath(currentPath, name) });
    } catch (err) {
      oaToast(`创建失败：${err.message}`, 'error');
    }
  }

  // 重命名（单选）
  async function renameItem() {
    const names = requireSelection(1, true);
    if (!names) return;
    const oldName = names[0];
    const newName = await askInput({
      title: '重命名',
      label: '新名称',
      value: oldName,
      hint: '仅修改名称，所在目录不变',
    });
    if (newName === null || newName === oldName) return;
    if (newName.includes('/') || newName.includes('\\')) {
      oaToast('新名称不能包含路径分隔符', 'error');
      return;
    }
    try {
      await postAction('rename', {
        old_path: joinPath(currentPath, oldName),
        new_path: joinPath(currentPath, newName),
      });
    } catch (err) {
      oaToast(`重命名失败：${err.message}`, 'error');
    }
  }

  // 复制 / 移动到目标目录
  async function transferItems(kind) {
    const names = requireSelection(1);
    if (!names) return;
    const verb = kind === 'copy' ? '复制' : '移动';
    const target = await askInput({
      title: `${verb}到…`,
      label: '目标目录（相对服务器根目录，留空为根目录）',
      value: currentPath,
      placeholder: '例如：plugins',
      hint: `将把选中的 ${names.length} 个项目${verb}到该目录下`,
    });
    if (target === null) return;
    const targetPath = target.replace(/^\/+|\/+$/g, '');
    try {
      await postAction(kind, {
        source_paths: names.map((n) => joinPath(currentPath, n)),
        target_path: targetPath,
      });
    } catch (err) {
      oaToast(`${verb}失败：${err.message}`, 'error');
      await loadDirectory(currentPath); // 部分成功也要刷新
    }
  }

  // 删除（需确认）
  async function deleteItems() {
    const names = requireSelection(1);
    if (!names) return;
    const ok = await askConfirm({
      title: '确认删除',
      body: `确定要删除选中的 ${names.length} 个项目吗？此操作不可恢复：\n` + names.join('、'),
    });
    if (!ok) return;

    let done = 0;
    let failed = 0;
    for (const name of names) {
      const entry = entryByName(name);
      const endpoint = entry && entry.is_dir ? 'delete/folder' : 'delete/file';
      try {
        await postAction('' + endpoint, { path: joinPath(currentPath, name) }, false);
        done++;
      } catch (err) {
        failed++;
        oaToast(`删除 ${name} 失败：${err.message}`, 'error');
      }
    }
    if (done > 0) oaToast(`已删除 ${done} 个项目`, failed ? 'info' : 'success');
    await loadDirectory(currentPath);
  }

  // ---------- 事件绑定 ----------
  document.getElementById('btn-new-file').addEventListener('click', () => createItem('file'));
  document.getElementById('btn-new-folder').addEventListener('click', () => createItem('folder'));
  document.getElementById('btn-rename').addEventListener('click', renameItem);
  document.getElementById('btn-copy').addEventListener('click', () => transferItems('copy'));
  document.getElementById('btn-move').addEventListener('click', () => transferItems('move'));
  document.getElementById('btn-delete').addEventListener('click', deleteItems);
  document.getElementById('btn-refresh').addEventListener('click', () => loadDirectory(currentPath));
  document.getElementById('btn-up').addEventListener('click', () => {
    if (!currentPath) {
      oaToast('已在根目录', 'info');
      return;
    }
    const parts = currentPath.split('/');
    parts.pop();
    navigateTo(parts.join('/'));
  });

  checkAll.addEventListener('change', () => {
    selected.clear();
    if (checkAll.checked) entries.forEach((e) => selected.add(e.name));
    renderTable();
  });

  // ---------- 初始化 ----------
  loadDirectory('');
})();

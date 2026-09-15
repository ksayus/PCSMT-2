/* =========================================================
 * OmniArk 创建服务器页（CreateServer.html）
 * - 核心版本：GET /api/program/minecraft_version → {minecraft_version: [...]}
 *   可搜索下拉（输入过滤 + 点击选择），选中值写入隐藏域 coreVersion
 * - 提交：同步 POST /server/create，提交时显示加载遮罩
 * ========================================================= */

(function () {
  'use strict';

  const filterInput = document.getElementById('version-filter');
  const hiddenInput = document.getElementById('coreVersion');
  const listEl = document.getElementById('version-list');
  const form = document.getElementById('create-form');

  let versions = [];

  // ---------- 可搜索下拉 ----------
  function renderList(keyword) {
    listEl.textContent = '';
    const kw = (keyword || '').trim().toLowerCase();
    const matched = kw
      ? versions.filter((v) => v.toLowerCase().includes(kw))
      : versions;

    if (matched.length === 0) {
      const item = document.createElement('div');
      item.className = 'version-item muted';
      item.textContent = versions.length === 0 ? '版本列表加载失败' : '无匹配版本';
      listEl.appendChild(item);
      return;
    }

    // 限制渲染数量，避免超长列表卡顿
    for (const v of matched.slice(0, 200)) {
      const item = document.createElement('div');
      item.className = 'version-item';
      item.textContent = v;
      item.addEventListener('mousedown', (e) => {
        // mousedown 先于 input blur，保证点击可选中
        e.preventDefault();
        selectVersion(v);
      });
      listEl.appendChild(item);
    }
  }

  function openList() {
    renderList(filterInput.value);
    listEl.classList.add('open');
  }

  function closeList() {
    listEl.classList.remove('open');
  }

  function selectVersion(v) {
    hiddenInput.value = v;
    filterInput.value = v;
    closeList();
  }

  filterInput.addEventListener('focus', openList);
  filterInput.addEventListener('input', () => {
    // 手动输入时清除已选值，只有点选才写入隐藏域
    hiddenInput.value = '';
    openList();
  });
  filterInput.addEventListener('blur', () => setTimeout(closeList, 120));
  filterInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      // 阻止在搜索框内回车误提交；精确匹配时直接选中
      e.preventDefault();
      const kw = filterInput.value.trim();
      const exact = versions.find((v) => v === kw);
      if (exact) selectVersion(exact);
    }
    if (e.key === 'Escape') closeList();
  });

  // ---------- 加载版本列表 ----------
  async function loadVersions() {
    try {
      const data = await oaApi('/api/program/minecraft_version');
      versions = data.minecraft_version || [];
      if (versions.length === 0) {
        filterInput.placeholder = '未获取到版本列表';
      }
    } catch (err) {
      filterInput.placeholder = '版本列表加载失败';
      oaToast('获取 Minecraft 版本列表失败：' + err.message, 'error');
    }
  }

  // ---------- 表单提交（同步 POST，显示加载遮罩） ----------
  form.addEventListener('submit', (event) => {
    // 版本必须从下拉中选择
    if (!hiddenInput.value) {
      event.preventDefault();
      oaToast('请从下拉列表中选择核心版本', 'error');
      filterInput.focus();
      return;
    }

    const port = Number(document.getElementById('port').value);
    if (!Number.isInteger(port) || port < 1024 || port > 65535) {
      event.preventDefault();
      oaToast('端口号必须是 1024-65535 之间的整数', 'error');
      return;
    }

    document.getElementById('loadingOverlay').classList.add('show');
    document.getElementById('create-btn').disabled = true;
  });

  // 若提交后页面因校验失败被退回（含浏览器前进/后退缓存），解除遮罩
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) {
      document.getElementById('loadingOverlay').classList.remove('show');
      document.getElementById('create-btn').disabled = false;
    }
  });

  loadVersions();
})();

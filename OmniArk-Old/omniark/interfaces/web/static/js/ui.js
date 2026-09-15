/* =========================================================
 * OmniArk 深色主题 —— 独立页面共享 JS
 * 提供：Toast 反馈（oaToast）、fetch 封装（oaApi）
 * 规范见 docs/frontend-design.md 第 4 节
 * ========================================================= */

(function () {
  'use strict';

  /** 确保页面中存在 Toast 容器 */
  function ensureToastContainer() {
    let container = document.querySelector('.oa-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'oa-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * 右上角 Toast 反馈（禁止 alert）
   * @param {string} message 文案
   * @param {'success'|'error'|'info'} type 类型
   * @param {number} duration 自动消失毫秒数
   */
  function oaToast(message, type = 'info', duration = 3500) {
    const container = ensureToastContainer();
    const toast = document.createElement('div');
    toast.className = `oa-toast oa-toast-${type}`;

    const icons = {
      success: 'bi-check-circle-fill',
      error: 'bi-x-circle-fill',
      info: 'bi-info-circle-fill',
    };

    const icon = document.createElement('i');
    icon.className = `bi ${icons[type] || icons.info}`;

    const text = document.createElement('span');
    text.textContent = message;

    const close = document.createElement('button');
    close.className = 'oa-toast-close';
    close.innerHTML = '<i class="bi bi-x"></i>';
    close.setAttribute('aria-label', '关闭');

    const dismiss = () => {
      toast.classList.add('oa-toast-out');
      setTimeout(() => toast.remove(), 260);
    };
    close.addEventListener('click', dismiss);

    toast.append(icon, text, close);
    container.appendChild(toast);
    if (duration > 0) setTimeout(dismiss, duration);
  }

  /**
   * fetch 统一封装：自动加 X-Requested-With、401 跳登录、解析 JSON。
   * 业务错误（success === false 或 HTTP 非 2xx）抛 Error，调用方负责 oaToast。
   * @param {string} path 请求路径
   * @param {RequestInit} options fetch 选项
   * @returns {Promise<any>} 解析后的 JSON
   */
  async function oaApi(path, options = {}) {
    const headers = Object.assign(
      { 'X-Requested-With': 'XMLHttpRequest' },
      options.headers || {}
    );
    // JSON 请求体自动补 Content-Type
    if (options.body && typeof options.body === 'string' && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    let response;
    try {
      response = await fetch(path, Object.assign({}, options, { headers }));
    } catch (err) {
      throw new Error('网络请求失败，请检查连接');
    }

    if (response.status === 401) {
      window.location.href = '/login';
      throw new Error('登录已过期');
    }

    let data = null;
    try {
      data = await response.json();
    } catch (err) {
      // 非 JSON 响应
    }

    if (!response.ok) {
      throw new Error((data && (data.error || data.message)) || `请求失败（HTTP ${response.status}）`);
    }
    if (data && data.success === false) {
      throw new Error(data.error || data.message || '操作失败');
    }
    return data;
  }

  window.oaToast = oaToast;
  window.oaApi = oaApi;
})();

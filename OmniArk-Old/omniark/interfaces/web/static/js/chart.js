/* =========================================================
 * OmniArk 存储占用图表页（chart_js.html）
 * 数据：GET /api/server/<name>/storage_info
 *       → {title, labels: [...], values: [...], type: 单位如 "MB"}
 *       无记录时返回 400 {success:false, error:"未找到信息"}
 * ========================================================= */

(function () {
  'use strict';

  const serverName = window.CHART_SERVER_NAME;

  function showEmpty(text) {
    document.getElementById('chart-box').style.display = 'none';
    const empty = document.getElementById('chart-empty');
    document.getElementById('chart-empty-text').textContent = text;
    empty.style.display = 'flex';
  }

  function setStat(id, value, unit) {
    const el = document.getElementById(id);
    el.textContent = '';
    el.appendChild(document.createTextNode(value));
    const unitEl = document.createElement('span');
    unitEl.className = 'unit';
    unitEl.textContent = unit;
    el.appendChild(unitEl);
  }

  async function init() {
    let data;
    try {
      data = await oaApi('/api/server/' + encodeURIComponent(serverName) + '/storage_info');
    } catch (err) {
      // 包括 "未找到信息"（400）在内的失败统一走空态
      showEmpty(err.message === '未找到信息' ? '暂无存储占用记录' : '加载失败：' + err.message);
      if (err.message !== '未找到信息') oaToast(err.message, 'error');
      return;
    }

    const labels = data.labels || [];
    const values = data.values || [];
    const unit = data.type || 'MB';

    if (values.length === 0) {
      showEmpty('暂无存储占用记录');
      return;
    }

    // 统计卡片：最新 / 最大 / 平均
    const latest = values[values.length - 1];
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    setStat('stat-latest', latest.toFixed(1), unit);
    setStat('stat-max', max.toFixed(1), unit);
    setStat('stat-avg', avg.toFixed(1), unit);

    // Chart.js 深色折线图
    const ctx = document.getElementById('storageChart').getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(79, 140, 255, 0.35)');
    gradient.addColorStop(1, 'rgba(79, 140, 255, 0.02)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: '存储大小 (' + unit + ')',
          data: values,
          borderColor: '#4f8cff',
          backgroundColor: gradient,
          borderWidth: 2,
          pointRadius: 3,
          pointBackgroundColor: '#4f8cff',
          tension: 0.3,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { labels: { color: '#9aa4b2' } },
          tooltip: {
            backgroundColor: '#1a1f27',
            borderColor: '#2d3542',
            borderWidth: 1,
            titleColor: '#e6e9ef',
            bodyColor: '#e6e9ef',
            callbacks: {
              label: (item) => ' ' + item.parsed.y + ' ' + unit,
            },
          },
        },
        scales: {
          x: {
            ticks: { color: '#9aa4b2', maxTicksLimit: 10 },
            grid: { color: 'rgba(45, 53, 66, 0.5)' },
          },
          y: {
            beginAtZero: true,
            ticks: {
              color: '#9aa4b2',
              callback: (v) => v + ' ' + unit,
            },
            grid: { color: 'rgba(45, 53, 66, 0.5)' },
          },
        },
      },
    });
  }

  init();
})();

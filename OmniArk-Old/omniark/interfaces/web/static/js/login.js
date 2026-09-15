/* OmniArk 登录页：表单校验 + 提交 loading 态 */
(function () {
  'use strict';

  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', function (event) {
    if (!form.checkValidity()) {
      event.preventDefault();
      event.stopPropagation();
    } else {
      /* 校验通过：按钮进入 loading 态，交由原生表单提交 */
      const btn = document.getElementById('login-btn');
      const text = btn.querySelector('.login-btn-text');
      const spinner = document.getElementById('login-spinner');
      btn.disabled = true;
      if (text) text.textContent = '正在登录…';
      if (spinner) spinner.classList.remove('d-none');
    }
    form.classList.add('was-validated');
  }, false);
})();

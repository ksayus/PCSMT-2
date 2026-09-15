<<<<<<< HEAD
// 页面内容映射
const pageContents = {
    home: `
        <div class="home-content">
            <h1>PCSMT2 控制台</h1>
            <p>欢迎使用 Minecraft 服务器管理工具</p>
            <div class="project-info">
                <p>本项目为开源项目</p>
                <div class="link-group">
                    <a target="_blank" rel="noopener" href="https://github.com/Ksayus/PCSMT-2">
                        <i class="fab fa-github"></i> Github 仓库
                    </a>
                    <br>
                    <a href="https://space.bilibili.com/558271819" target="_blank" rel="noopener">
                        <img src="/static/bilibili.png" width=16px height=16px></img> Bilibili 主页
                    </a>
                </div>
                <div class="version-info">
                    <i class="fas fa-code-branch"></i>
                    <span>版本号: <span id="program-version">加载中...</span></span>
                </div>
            </div>
        </div>
    `,

    help: `
        <div class="help-content">
            <h1>PCSMT API</h1>
            <table class="help-table">
                <thead>
                    <tr>
                        <th colspan="2">API 列表</th>
                        <th colspan="2">描述</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>/api</td>
                        <td>这是API的首页</td>
                    </tr>
                    <tr>
                        <td>/api/server</td>
                        <td>这是API Server的首页</td>
                    </tr>
                    <tr>
                        <td>/api/server/list</td>
                        <td>服务器列表</td>
                    </tr>
                    <tr>
                        <td>/api/server/info/{string:server_name}</td>
                        <td>指定服务器信息</td>
                    </tr>
                    <tr>
                        <td>/api/server/latest</td>
                        <td>上次启动服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/start</td>
                        <td>启动指定服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/stop</td>
                        <td>停止指定服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/status</td>
                        <td>获取服务器启动状态</td>
                    </tr>
                    <tr>
                        <td>/api/server/info/<string:server_name>/excel</td>
                        <td>生成并下载指定服务器的Excel表格</td>
                    </tr>
                    <tr>
                        <td>/api/server/list/excel</td>
                        <td>生成并下载所有服务器的Excel表格</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/storage_info</td>
                        <td>获取指定服务器的存储数据</td>
                    </tr>
                    <tr>
                        <td>/api/program</td>
                        <td>这是API Program的首页</td>
                    </tr>
                    <tr>
                        <td>/api/program/version</td>
                        <td>程序版本</td>
                    </tr>
                    <tr>
                        <td>/api/program/minecraft_version</td>
                        <td>获取Minecraft的所有版本</td>
                    </tr>
                    <tr>
                        <td>/api/program/disk_usage</td>
                        <td>获取程序所在硬盘使用状态</td>
                    </tr>
                    <tr>
                        <td>/api/program/get/settings</td>
                        <td>获取程序设置信息</td>
                    </tr>
                    <tr>
                        <td>/api/program/set/settings</td>
                        <td>设置程序设置信息</td>
                    </tr>
                    <tr>
                        <td>/api/static/ico</td>
                        <td>获取图标</td>
                    </tr>
                    <tr>
                        <td>/login</td>
                        <td>登录界面</td>
                    </tr>
                    <tr>
                        <td>/server/create</td>
                        <td>创建服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/storage_chart</td>
                        <td>渲染存储图表页面</td>
                    </tr>
                    <tr>
                        <td>/api/server/&lt;server_name&gt;/restart</td>
                        <td>重启指定服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/get/backups/&lt;server_name&gt;</td>
                        <td>获取服务器备份文件列表</td>
                    </tr>
                    <tr>
                        <td>/api/server/&lt;server_name&gt;/retracement</td>
                        <td>回档服务器（恢复备份）</td>
                    </tr>
                    <tr>
                        <td>/api/server/add</td>
                        <td>添加（导入）已有服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/&lt;server_name&gt;/redirect_path</td>
                        <td>重定向服务器路径</td>
                    </tr>
                    <tr>
                        <td>/api/server/&lt;server_name&gt;/op | /deop</td>
                        <td>给予/移除玩家OP权限</td>
                    </tr>
                    <tr>
                        <td>/api/server/&lt;server_name&gt;/ban/ip | /unban/ip</td>
                        <td>封禁/解封IP地址</td>
                    </tr>
                    <tr>
                        <td>/api/server/get/ops/&lt;server_name&gt;</td>
                        <td>获取OP玩家列表</td>
                    </tr>
                    <tr>
                        <td>/api/server/get/banned/ips/&lt;server_name&gt;</td>
                        <td>获取封禁IP列表</td>
                    </tr>
                    <tr>
                        <td>/api/program/clear_cache</td>
                        <td>清理程序缓存</td>
                    </tr>
                    <tr>
                        <td>/api/program/reset_settings</td>
                        <td>重置程序设置</td>
                    </tr>
                    <tr>
                        <td>/api/program/format_program</td>
                        <td>格式化程序</td>
                    </tr>
                    <tr>
                        <td>/api/program/check_update</td>
                        <td>检查程序更新</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,

    // 修改服务器列表页面的布局结构
    servers: `
        <div class="servers-content">
            <h1>服务器列表</h1>
            <div class="charts-container">
                <!-- 磁盘使用率 -->
                <div class="chart-item">
                    <div id="disk-usage-chart" style="width: 200px; height: 200px;"></div>
                    <div class="chart-label">磁盘使用率</div>
                    <div class="chart-stats">
                        <span id="disk-used">0GB</span> /
                        <span id="disk-total">0GB</span>
                    </div>
                </div>

                <!-- CPU使用率 -->
                <div class="chart-item">
                    <div id="cpu-usage-chart" style="width: 200px; height: 200px;"></div>
                    <div class="chart-label">CPU使用率</div>
                    <div class="chart-stats">
                        <span id="cpu-used">0MHz</span> /
                        <span id="cpu-total">0MHz</span>
                    </div>
                </div>

                <!-- 内存使用率 -->
                <div class="chart-item">
                    <div id="ram-usage-chart" style="width: 200px; height: 200px;"></div>
                    <div class="chart-label">内存使用率</div>
                    <div class="chart-stats">
                        <span id="ram-used">0GB</span> /
                        <span id="ram-total">0GB</span>
                    </div>
                </div>
            </div>
            <div class="server-container" id="server-list-container">
                <div class="loading">加载中...</div>
            </div>
        </div>
    `,

    server_info: (serverName) => `
        <div class="server-info-content">
            <!-- 左侧：服务器信息 -->
            <div class="server-info-left">
                <div class="server-card">
                    <table>
                        <tr>
                            <th id="Type-th">类型</th>
                            <td id="Info-td">信息</td>
                        </tr>
                        <tr>
                            <th>服务器名</th>
                            <td id="id-name">${serverName}</td>
                        </tr>
                        <tr>
                            <th>服务器版本</th>
                            <td id="id-version"></td>
                        </tr>
                        <tr>
                            <th>服务器大小</th>
                            <td id="id-size"></td>
                        </tr>
                        <tr>
                            <th>服务器启动次数</th>
                            <td id="id-start-counts"></td>
                        </tr>
                        <tr>
                            <th>上次启动时间</th>
                            <td id="id-latest-start-time"></td>
                        </tr>
                    </table>
                </div>
                <div class="button-group" id="button-group">
                    <button id="button-server" onclick="">检查中...</button>
                    <button class="restart-btn" onclick="restartServer('${serverName}')">
                        <i class="fas fa-redo"></i>重启服务器
                    </button>
                    <button class="backup-btn" onclick="showBackupDialog('${serverName}')">
                        <i class="fas fa-history"></i>回档服务器
                    </button>
                    <button id="storage-chart" onclick="ChartImage('${serverName}')">存储占用</button>
                    <button class="file-manager-btn" onclick="openFileManager('${serverName}')">
                        <i class="fas fa-folder-open"></i>文件管理器
                    </button>
                    <button class="download-btn" onclick="downloadServer('${serverName}')">
                        <i class="fas fa-file-download"></i>下载服务器信息
                    </button>
                    <button class="change-properties-btn" onclick="changeServerProperties('${serverName}')">
                        <i class="fas fa-cog"></i>修改服务器属性
                    </button>
                    <button class="redirect-btn" onclick="redirectServerPath('${serverName}')">
                        <i class="fas fa-exchange-alt"></i>重定向路径
                    </button>
                </div>
            </div>

            <!-- 中间：终端消息 -->
            <div class="server-info-center">
                <h3>服务器终端</h3>
                <div class="terminal-output" id="terminal-output-${serverName}">
                    <!-- 终端输出 -->
                </div>
                <div class="terminal-input">
                    <input type="text" id="command-input-${serverName}" placeholder="输入命令...">
                    <button onclick="sendCommand('${serverName}')">发送</button>
                </div>
            </div>

            <!-- 右侧：在线玩家列表及历史玩家抽屉 -->
            <div class="server-info-right">
                <h3>在线玩家</h3>
                <div class="player-list" id="player-list-${serverName}"></div>

                <h3>封禁玩家</h3>
                <div class="banned-player-list" id="banned-players-${serverName}">
                    <p>加载中...</p>
                </div>

                <h3>OP 玩家</h3>
                <div class="op-player-list" id="op-players-${serverName}">
                    <p>加载中...</p>
                </div>
                <div class="inline-add">
                    <input type="text" id="add-op-input-${serverName}" placeholder="玩家名">
                    <button onclick="opPlayerFromInput('${serverName}')">添加OP</button>
                </div>

                <h3>封禁 IP</h3>
                <div class="banned-ip-list" id="banned-ips-${serverName}">
                    <p>加载中...</p>
                </div>
                <div class="inline-add">
                    <input type="text" id="ban-ip-input-${serverName}" placeholder="IP 地址">
                    <button onclick="banIpFromInput('${serverName}')">封禁IP</button>
                </div>

                <h3>白名单玩家</h3>
                <div class="whitelist-player-list" id="whitelist-players-${serverName}">
                    <p>加载中...</p>
                </div>

                <!-- 历史玩家下拉框 -->
                <div class="history-players-dropdown">
                    <div class="dropdown-header" onclick="toggleHistoryPlayersDropdown('${serverName}')">
                        <h3>历史玩家</h3>
                        <span class="dropdown-toggle">▼</span>
                    </div>
                    <div class="dropdown-content-history-player" id="history-players-content-${serverName}" style="display: none;">
                        <p>加载中...</p>
                    </div>
                </div>
            </div>
        </div>
`,

    server_latest: `
        <div class="server-latest-content">
            <div class="server-card">
                <table>
                    <tr>
                        <th id="Type-th">类型</th>
                        <td id="Info-td">信息</td>
                    </tr>
                    <tr>
                        <th>服务器名</th>
                        <td id="id-name"></td>
                    </tr>
                    <tr>
                        <th>服务器版本</th>
                        <td id="id-version"></td>
                    </tr>
                    <tr>
                        <th>服务器大小</th>
                        <td id="id-size"></td>
                    </tr>
                    <tr>
                        <th>服务器启动次数</th>
                        <td id="id-start-counts"></td>
                    </tr>
                    <tr>
                        <th>上次启动时间</th>
                        <td id="id-latest-start-time"></td>
                    </tr>
                </table>
            </div>
        </div>
    `,

    program_version: `
        <div class="program-version-content">
            <div class="card">
                <div class="content">
                    <p>程序版本: <span id="version"></span></p>
                </div>
                <div class="loading-icon" style="display: none;"></div>
                <div class="error-message" style="display: none;">获取程序版本失败，请稍后重试。</div>
            </div>
        </div>
    `,

    settings: `
        <div class="settings-content">
            <h1>程序设置</h1>
            <p>这里可以配置程序的各种设置，例如服务器路径、日志级别等。</p>
            <form id="settings-form">
                <div class="form-group">
                    <label>服务器运行内存设置 (MB):</label>
                    <div class="input-row">
                        <input type="number" id="min-memory" name="min_memory" min="1024" placeholder="最小值">
                        <span>至</span>
                        <input type="number" id="max-memory" name="max_memory" min="1024" placeholder="最大值">
                    </div>
                </div>

                <div class="form-group">
                    <label>Nogui 模式:</label>
                    <div class="toggle-switch">
                        <input type="checkbox" id="nogui-enabled" name="nogui_enabled">
                        <label for="nogui-enabled"></label>
                    </div>
                </div>

                <div class="form-group">
                    <label>EULA 生成等待时间 (秒):</label>
                    <input type="number" id="eula-wait-time" name="eula_wait_time" min="1" max="300" value="">
                </div>

                <div class="form-group">
                    <label>开机自启动:</label>
                    <div class="toggle-switch">
                        <input type="checkbox" id="auto-start" name="auto_start">
                        <label for="auto-start"></label>
                    </div>
                </div>

                <div class="form-group">
                    <label>自动更新源:</label>
                    <select id="update-source" name="update_source">
                        <option value="Github">Github</option>
                        <option value="Gitee">Gitee</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>获取测试版本:</label>
                    <div class="toggle-switch">
                        <input type="checkbox" id="test-versions" name="test_versions">
                        <label for="test-versions"></label>
                    </div>
                </div>

                <div class="form-group">
                    <label>服务器存储占用的更新时间:</label>
                    <input type="text" id="storage-update-time" name="storage_update_time" min="1" value="">
                </div>

                <div class="form-group">
                    <label>API端口:</label>
                    <input type="number" id="server-port" name="server_port" min="1024" max="65535" value="">
                </div>

                <button type="submit" class="save-btn">保存设置</button>
            </form>

            <hr class="settings-divider">
            <h2>维护工具</h2>
            <p>以下操作直接生效，请谨慎使用。</p>
            <div class="maintenance-buttons">
                <button type="button" class="maintenance-btn" onclick="clearCache()">
                    <i class="fas fa-broom"></i>清理缓存
                </button>
                <button type="button" class="maintenance-btn" onclick="checkUpdate()">
                    <i class="fas fa-cloud-download-alt"></i>检查更新
                </button>
                <button type="button" class="maintenance-btn warning" onclick="resetSettings()">
                    <i class="fas fa-undo"></i>重置设置
                </button>
                <button type="button" class="maintenance-btn danger" onclick="formatProgram()">
                    <i class="fas fa-exclamation-triangle"></i>格式化程序
                </button>
            </div>
        </div>
    `,

    mods: `
        <div class="mods-content">
            <h1>Mod/Plugin 下载</h1>
            <!-- 添加MOD列表 -->
        </div>
    `
};

// 页面初始化
window.onload = () => {
    fetchServers();
    loadContent('home');
    fetchProgramVersion();
};

// 加载页面内容（带平滑过渡）
function loadContent(page, serverName = '') {
    const contentDiv = document.getElementById('dynamic-content');

    // 清除所有定时器
    if (window.terminalTimers) {
        Object.values(window.terminalTimers).forEach(clearTimeout);
        window.terminalTimers = {};
    }
    // 清除图表刷新定时器并销毁图表实例
    if (chartRefreshTimer) {
        clearTimeout(chartRefreshTimer);
        chartRefreshTimer = null;
    }
    disposeAllCharts();

    // 清除所有终端日志定时器
    if (window.terminalTimers) {
        Object.values(window.terminalTimers).forEach(intervalId => clearInterval(intervalId));
        window.terminalTimers = {};
    }

    // 第一步：淡出当前内容
    contentDiv.classList.add('content-fading');

    // 等待淡出动画完成后替换内容并淡入
    setTimeout(() => {
        // 第二步：替换内容
        switch(page) {
            case 'home':
                contentDiv.innerHTML = pageContents.home;
                fetchProgramVersion();
                break;
            case 'help':
                contentDiv.innerHTML = pageContents.help;
                break;
            case 'servers':
                contentDiv.innerHTML = pageContents.servers;
                preInitCharts();           // 先渲染空图表占位，避免白屏
                fetchCpuRamDiskUsage();    // 再获取数据填充
                fetchServerList();
                break;
            case 'server_info':
                if (serverName) {
                    contentDiv.innerHTML = pageContents.server_info(serverName);
                    fetchServerInfo(serverName);
                }
                break;
            case 'server_latest':
                contentDiv.innerHTML = pageContents.server_latest;
                fetchLatestServerInfo();
                break;
            case 'program_version':
                contentDiv.innerHTML = pageContents.program_version;
                fetchProgramVersion();
                break;
            case 'settings':
                contentDiv.innerHTML = pageContents.settings;
                fetchSettings();
                break;
            case 'mods':
                contentDiv.innerHTML = pageContents.mods;
                break;
            default:
                contentDiv.innerHTML = pageContents.home;
        }

        // 第三步：淡入新内容
        // 用 requestAnimationFrame 确保浏览器先渲染新 DOM 再触发过渡
        requestAnimationFrame(() => {
            contentDiv.classList.remove('content-fading');
        });
    }, 250); // 与 CSS 的 0.25s 过渡时间一致
}

// 获取服务器列表
async function fetchServers() {
    try {
        const response = await fetch('/api/server/list');
        const data = await response.json();
        const serverList = document.getElementById('server-list');
        serverList.innerHTML = '';

        if (data.error) {
            serverList.innerHTML = `<p>${data.error}</p>`;
            return;
        }

        data.serverlist.forEach(server => {
            const li = document.createElement('li');
            li.innerHTML = `<a href="#server_info" onclick="loadContent('server_info', '${server}')">${server}</a>`;
            serverList.appendChild(li);
        });
    } catch (error) {
        console.error('获取服务器列表失败:', error);
    }
}

// 获取服务器列表卡片
async function fetchServerList(AddButton = true) {
    try {
        // 获取圆环元素
        const $text = $('.text');
        // 更新进度条显示
        function updateProgress(value) {
            // 当百分比小于等于50
            if(value <= 50){
                $('.mask-right').remove();
                var html = '<div class="mask-right" style="transform:rotate('+ (value * 3.6) +'deg)"></div>';
                $('.circle-right').append(html);
            }else{
                $('.circle-left, .mask-left').remove();
                const adjustedValue = value - 50;
                var html = '<div class="circle-left">';
                html += '<div class="mask-left" style="transform:rotate('+ (adjustedValue * 3.6) +'deg)"></div>';
                html += '</div>';
                $('.circle-right').after(html);
            }

            // 更新文本显示
            $text.html(Math.round(value) + '%');
        }

        // 设置API请求超时（10秒）
        const timeout = setTimeout(() => {
            updateProgress(0, 0, true); // 显示错误状态
            console.error('获取服务器列表超时');
        }, 10000);

        fetch('/api/server/list')
            .then(response => response.json())
            .then(data => {
                clearTimeout(timeout); // 清除超时计时器

                const serverList = document.getElementById('server-list-container');
                serverList.innerHTML = ''; // 清空加载中的提示

                if (data.error) {
                    serverList.innerHTML = `<p style="color: red;">${data.error}</p>`;
                    return;
                }

                const serverListData = data.serverlist || [];
                if (AddButton)
                {
                    if (serverListData.length == 0) {
                        serverList.innerHTML = '<p>没有可用的服务器。</p>';

                        // 仅添加创建服务器按钮（移除下载按钮）
                        const buttonGroup = document.createElement('div');
                        buttonGroup.className = 'button-group';
                        buttonGroup.style.display = 'flex';
                        buttonGroup.style.justifyContent = 'center';
                        buttonGroup.style.gap = '15px';

                        const createServerBtn = document.createElement('button');
                        createServerBtn.className = 'create-btn';
                        createServerBtn.innerHTML = '<i class="fas fa-plus"></i>创建服务器';
                        createServerBtn.onclick = function() {
                            createServer();
                        };
                        buttonGroup.appendChild(createServerBtn);

                        buttonGroup.appendChild(createAddExistingServerBtn());

                        serverList.parentNode.insertBefore(buttonGroup, serverList);
                        return;
                    }

                    // 在服务器列表容器前添加按钮组
                    const buttonGroup = document.createElement('div');
                    buttonGroup.className = 'button-group'; // 使用现有按钮组样式
                    buttonGroup.style.display = 'flex'; // 确保按钮水平排列
                    buttonGroup.style.justifyContent = 'center'; // 居中显示
                    buttonGroup.style.gap = '15px'; // 设置按钮间距

                    // 创建服务器按钮
                    const createServerBtn = document.createElement('button');
                    createServerBtn.className = 'create-btn';
                    createServerBtn.innerHTML = '<i class="fas fa-plus"></i>创建服务器';
                    createServerBtn.onclick = function() {
                        createServer();
                    };
                    buttonGroup.appendChild(createServerBtn);

                    // 添加现有服务器按钮
                    buttonGroup.appendChild(createAddExistingServerBtn());

                    // 下载所有服务器按钮
                    const downloadAllBtn = document.createElement('button');
                    downloadAllBtn.className = 'download-btn';
                    downloadAllBtn.innerHTML = '<i class="fas fa-file-download"></i>下载所有服务器信息';
                    downloadAllBtn.onclick = function() {
                        downloadAllServers(serverListData);
                    };
                    buttonGroup.appendChild(downloadAllBtn);

                    serverList.parentNode.insertBefore(buttonGroup, serverList);
                }

                const serverElements = serverListData.map(server => `
                    <div class="server-card">
                        <!-- 删除按钮 -->
                        <div class="delete-btn" onclick="deleteServer('${server}'); event.stopPropagation();">
                            <i class="fas fa-trash-alt"></i>
                        </div>
                        <div class="server-card-content" onclick="loadContent('server_info', '${server}')">
                            <h3>${server}</h3>
                            <div class="server-card-info">
                                <div>
                                    <span>在线人数</span>
                                    <span id="online-player-${server}">加载中...</span>
                                </div>
                                <div>
                                    <span>版本</span>
                                    <span id="version-${server}">加载中...</span>
                                </div>
                                <div>
                                    <span>大小</span>
                                    <span id="size-${server}">加载中...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `);

                serverList.innerHTML = serverElements.join('');

                // 异步加载每个服务器的详细信息
                serverListData.forEach(server => {
                    fetchServerBasicInfo(server);
                    fetchServerPlayerInfo(server);
                });
            })
            .catch(error => {
                clearTimeout(timeout); // 清除超时计时器
                console.error('获取服务器列表时出错:', error);
                document.getElementById('server-list-container').innerHTML = '<p style="color: red;">获取服务器列表失败，请稍后重试。</p>';
                // 显示错误状态
                updateProgress(0, 0, true);
            });
    } catch (error) {
        console.error('获取服务器列表失败:', error);
    }
}

// 获取服务器玩家信息
async function fetchServerPlayerInfo(serverName) {
    try {
        const response = await fetch(`/api/server/players/${serverName}`);
        const data = await response.json();
        if (data.error) {
            document.getElementById(`online-player-${serverName}`).textContent = '获取失败';
            return;
        };
        if (!data.players)
        {
            document.getElementById(`online-player-${serverName}`).textContent = '服务器未启动';
            return;
        }

        document.getElementById(`online-player-${serverName}`).textContent = `${data.players[0]} / ${data.players[1]}` || '服务器未启动';
    } catch (error) {
        console.error('获取玩家列表失败:', error);
    }
}

// 获取服务器基本信息（用于卡片展示）
async function fetchServerBasicInfo(serverName) {
    try {
        const response = await fetch(`/api/server/info/${serverName}`);
        const data = await response.json();

        if (data.error) return;

        document.getElementById(`version-${serverName}`).textContent = data.version || '未知';
        document.getElementById(`size-${serverName}`).textContent = data.size || '未知';
    } catch (error) {
        console.error(`获取服务器 ${serverName} 基本信息失败:`, error);
    }
}

// 获取服务器信息
async function fetchServerInfo(serverName) {
    try {
        const response = await fetch(`/api/server/info/${serverName}`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('id-version').innerText = data.version;
        document.getElementById('id-size').innerText = data.size;
        document.getElementById('id-start-counts').innerText = data.startCount;
        document.getElementById('id-latest-start-time').innerText = data.LatestStartedTime;

        // 检查服务器状态
        const statusResponse = await fetch(`/api/server/status/${serverName}`);
        const statusData = await statusResponse.json();

        const buttonServer = document.getElementById('button-server');
        if (statusData.status === 'starting') {
            buttonServer.innerText = '停止服务器';
            buttonServer.onclick = function() { stopServer(serverName); };
        } else {
            buttonServer.innerText = '启动服务器';
            buttonServer.onclick = function() { startServer(serverName); };
        }

        // 获取在线玩家列表
        fetchOnlinePlayers(serverName);

        // 获取封禁玩家列表
        getBannedPlayers(serverName);

        // 获取OP玩家列表
        getOps(serverName);

        // 获取封禁IP列表
        getBannedIps(serverName);

        // 获取白名单列表
        getWhiteList(serverName);

        // 获取历史玩家列表
        fetchHistoryPlayers(serverName)

        // 建立WebSocket连接获取终端消息
        setupTerminalWebSocket(serverName);
    } catch (error) {
        console.error('获取服务器信息失败:', error);
        alert('无法获取服务器信息');
    }
}

// 获取最新服务器信息
async function fetchLatestServerInfo() {
    try {
        const response = await fetch(`/api/server/latest`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('id-name').innerText = data.name;
        document.getElementById('id-version').innerText = data.version;
        document.getElementById('id-size').innerText = data.size;
        document.getElementById('id-start-counts').innerText = data.startCount;
        document.getElementById('id-latest-start-time').innerText = data.LatestStartedTime;
    } catch (error) {
        console.error('获取最新服务器信息失败:', error);
        alert('无法获取服务器信息');
    }
}

// 获取程序版本
async function fetchProgramVersion() {
    try {
        const response = await fetch('/api/program/version');
        const data = await response.json();

        const versionElement = document.getElementById('program-version') ||
                                document.getElementById('version');

        if (versionElement) {
            versionElement.textContent = data.version || '未知版本';
        }
    } catch (error) {
        console.error('获取程序版本失败:', error);
        const errorElement = document.querySelector('.error-message');
        if (errorElement) {
            errorElement.style.display = 'block';
        }
    }
}

// 全局AJAX错误处理
function handleAjaxError(response) {
    if (response.status === 401) {
        // 未授权，跳转到登录页面
        window.location.href = '/login';
        return true;
    }
    return false;
}

// 启动服务器
async function startServer(serverName) {
    document.getElementById('button-server').innerText = '启动中...';

    try {
        const response = await fetch(`/api/server/${serverName}/start`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // 添加AJAX标识头
            }
        });

    // 切换历史玩家上拉框
    function toggleHistoryPlayersDropdown(serverName) {
        const dropdownContent = document.getElementById(`history-players-content-${serverName}`);
        const dropdownToggle = document.querySelector(`[onclick="toggleHistoryPlayersDropdown('${serverName}')"] .dropdown-toggle`);

        if (dropdownContent.style.display === 'none') {
            dropdownContent.style.display = 'block';
            dropdownToggle.style.transform = 'rotate(180deg)';
        } else {
            dropdownContent.style.display = 'none';
            dropdownToggle.style.transform = 'rotate(0deg)';
        }
    }

        // 检查401错误
        if (handleAjaxError(response)) return;

        const data = await response.json();

        const buttonServer = document.getElementById('button-server');
        if (data.status === 'starting') {
            buttonServer.innerText = '停止服务器';
            buttonServer.onclick = function() { stopServer(serverName); };
        } else if (data.error) {
            document.getElementById('button-server').innerText = '启动服务器';
            alert('启动服务器失败');
        }
    } catch (error) {
        console.error('启动服务器失败:', error);
        document.getElementById('button-server').innerText = '启动服务器';
        alert('启动服务器失败');
    }
}

// 停止服务器
async function stopServer(serverName) {
    document.getElementById('button-server').innerText = '停止中...';

    try {
        const response = await fetch(`/api/server/${serverName}/stop`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // 添加AJAX标识头
            }
        });

        // 检查401错误
        if (handleAjaxError(response)) return;

        const data = await response.json();

        const buttonServer = document.getElementById('button-server');
        if (data.status === 'stopped') {
            buttonServer.innerText = '启动服务器';
            buttonServer.onclick = function() { startServer(serverName); };
        } else if (data.error) {
            document.getElementById('button-server').innerText = '停止服务器';
            alert('停止服务器失败');
        }
    } catch (error) {
        console.error('停止服务器失败:', error);
        document.getElementById('button-server').innerText = '停止服务器';
        alert('停止服务器失败');
    }
}

async function ChartImage(serverName) {
    try {
        setTimeout(function () {
            window.location.href = `/server/${serverName}/storage_chart`;
        }, 0);
    } catch (error) {
        console.error('获取图表失败:', error);
        alert('获取图表失败');
    }
}

// 下载服务器函数
function downloadServer(serverName) {
    console.log(`下载服务器信息列表: ${serverName}`);
    fetch(`/api/server/info/${serverName}/excel`, { method: 'POST' })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${serverName}.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error(`下载服务器信息列表失败: ${serverName}`, error);
        })
}

// 下载所有服务器函数
function downloadAllServers(serverList) {
    console.log('下载所有服务器信息列表:', serverList);
    fetch('api/server/list/excel', { method: 'POST' })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'AllServerInfo.xlsx';
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('下载所有服务器信息列表失败:', error);
        })
}

// 创建服务器函数
function createServer() {
    // 这里打开页面创建服务器
    window.open('/server/create');
}

// 创建“添加现有服务器”按钮
function createAddExistingServerBtn() {
    const addExistingBtn = document.createElement('button');
    addExistingBtn.className = 'create-btn add-existing-btn';
    addExistingBtn.innerHTML = '<i class="fas fa-folder-plus"></i>添加现有服务器';
    addExistingBtn.onclick = function() {
        showAddServerDialog();
    };
    return addExistingBtn;
}

// 显示添加现有服务器对话框
async function showAddServerDialog() {
    let versionOptions = '<option value="">加载版本中...</option>';
    try {
        const response = await fetch('/api/program/minecraft_version');
        const data = await response.json();
        const versions = data.minecraft_version || [];
        versionOptions = versions.map(v => `<option value="${v}">${v}</option>`).join('');
    } catch (error) {
        console.error('获取Minecraft版本失败:', error);
        versionOptions = '<option value="">获取版本失败，请手动输入</option>';
    }

    const bodyHtml = `
        <div class="add-server-form">
            <div class="form-group">
                <label>服务器路径 (包含核心 .jar 的文件夹):</label>
                <input type="text" id="add-server-path" placeholder="例如 D:\\MCServer\\1.20.1">
            </div>
            <div class="form-group">
                <label>服务器名称:</label>
                <input type="text" id="add-server-name" placeholder="用于在PCSMT2中显示的名称">
            </div>
            <div class="form-group">
                <label>游戏版本:</label>
                <select id="add-server-version">${versionOptions}</select>
            </div>
            <div class="form-group">
                <label>核心类型:</label>
                <select id="add-server-core-type">
                    <option value="official">official</option>
                    <option value="forge">forge</option>
                    <option value="fabric">fabric</option>
                    <option value="mohist">mohist</option>
                </select>
            </div>
            <button class="save-btn" onclick="addExistingServer()">添加服务器</button>
        </div>
    `;

    createPcsmtModal('添加现有服务器', bodyHtml);
}

// 提交添加现有服务器
async function addExistingServer() {
    const serverPath = document.getElementById('add-server-path').value.trim();
    const serverName = document.getElementById('add-server-name').value.trim();
    const serverVersion = document.getElementById('add-server-version').value.trim();
    const coreType = document.getElementById('add-server-core-type').value;

    if (!serverPath || !serverName || !serverVersion || !coreType) {
        alert('请填写完整信息');
        return;
    }

    try {
        const response = await fetch('/api/server/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                server_path: serverPath,
                server_name: serverName,
                server_version: serverVersion,
                core_type: coreType
            })
        });

        if (handleAjaxError(response)) return;

        const data = await response.json();
        if (data.success) {
            alert(data.message || '添加服务器成功');
            closePcsmtModal();
            refreshServerCards();
            fetchServers(); // 刷新侧边栏列表
        } else {
            alert(`添加服务器失败: ${data.message || data.error || '未知错误'}`);
        }
    } catch (error) {
        console.error('添加服务器失败:', error);
        alert('添加服务器失败，请检查日志');
    }
}

function changeServerProperties(serverName){
    window.open('/server/settings/'+serverName);
}

// 打开文件管理器
function openFileManager(serverName){
    window.open('/manager/' + serverName);
}

// 删除服务器函数
async function deleteServer(serverName) {
    try{
        if (confirm(`确定要删除服务器 "${serverName}" 吗？此操作不可撤销！`)) {
            // 显示加载状态
            const deleteBtn = document.querySelector(`.delete-btn[onclick*="${serverName}"]`);
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                deleteBtn.style.pointerEvents = 'none';
            }

            const response = await fetch(`/api/server/delete/${serverName}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // 添加AJAX标识头
                }
            });

            // 检查401错误
            if (handleAjaxError(response)){
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                return;
            }

            const data = await response.json();

            if (data.status === 'deleted') {
                // 只刷新服务器卡片区域，不重建按钮组
                alert('删除服务器成功');
                refreshServerCards();  // 修改点：替换为专门刷新卡片的函数
            }else if (data.error) {
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                alert('删除服务器失败');
            }
        }
    }catch (error) {
        console.error('删除服务器失败:', error);
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        alert('删除服务器失败');
    }
}

// 专门刷新服务器卡片的函数
async function refreshServerCards() {
    try {
        const response = await fetch('/api/server/list');
        const data = await response.json();
        const serverList = document.getElementById('server-list-container');

        if (data.error) {
            console.error(data.error);
            return;
        }

        const serverListData = data.serverlist || [];
        if (serverListData.length === 0) {
            serverList.innerHTML = '<p>没有可用的服务器。</p>';
            return;
        }

        // 只更新卡片区域，不重建按钮组
        const serverElements = serverListData.map(server => `
            <div class="server-card">
                <!-- 删除按钮 -->
                <div class="delete-btn" onclick="deleteServer('${server}'); event.stopPropagation();">
                    <i class="fas fa-trash-alt"></i>
                </div>
                <div class="server-card-content" onclick="loadContent('server_info', '${server}')">
                    <h3>${server}</h3>
                    <div class="server-card-info">
                        <div>
                            <span>在线人数</span>
                            <span id="online-player-${server}">加载中...</span>
                        </div>
                        <div>
                            <span>版本</span>
                            <span id="version-${server}">加载中...</span>
                        </div>
                        <div>
                            <span>大小</span>
                            <span id="size-${server}">加载中...</span>
                        </div>
                    </div>
                </div>
            </div>
        `);

        serverList.innerHTML = serverElements.join('');

        // 异步加载每个服务器的详细信息
        serverListData.forEach(server => {
            fetchServerBasicInfo(server);
            fetchServerPlayerInfo(server);
        });
    } catch (error) {
        console.error('刷新服务器卡片失败:', error);
    }
}

// 获取设置数据
async function fetchSettings() {
    try {
        const response = await fetch('/api/program/get/settings');
        const settings = await response.json();

        console.log(settings);

        // 填充表单数据
        document.getElementById('min-memory').value = settings.min_memory || '';
        document.getElementById('max-memory').value = settings.max_memory || '';
        document.getElementById('nogui-enabled').checked = settings.nogui_enabled || false;
        document.getElementById('eula-wait-time').value = settings.eula_wait_time || '';
        document.getElementById('auto-start').checked = settings.auto_start || false;
        document.getElementById('update-source').value = settings.update_source || 'Github';
        document.getElementById('test-versions').checked = settings.test_versions || false;
        document.getElementById('storage-update-time').value = settings.storage_update_time || '';
        document.getElementById('server-port').value = settings.server_port || '';

        // 添加表单提交事件
        document.getElementById('settings-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const saveBtn = document.querySelector('.save-btn');
            if (!saveBtn) return;

            const formData = {
                min_memory: document.getElementById('min-memory').value,
                max_memory: document.getElementById('max-memory').value,
                nogui_enabled: document.getElementById('nogui-enabled').checked,
                eula_wait_time: document.getElementById('eula-wait-time').value,
                auto_start: document.getElementById('auto-start').checked,
                update_source: document.getElementById('update-source').value,
                test_versions: document.getElementById('test-versions').checked,
                storage_update_time: document.getElementById('storage-update-time').value,
                server_port: document.getElementById('server-port').value
            };

            console.log('提交表单数据:', formData);

            // 转换数字字段，空字符串转为0
            const numberFields = ['min_memory', 'max_memory', 'eula_wait_time', 'server_port'];
            numberFields.forEach(field => {
                const value = formData[field];
                if (value === '') {
                    formData[field] = 0;
                } else {
                    const num = parseInt(value, 10);
                    formData[field] = isNaN(num) ? 0 : num;
                }
            });

            try {
                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.textContent = '保存中...';
                }

                const response = await fetch('/api/program/set/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                // 检查响应是否为JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('无效的响应格式');
                }

                const result = await response.json();
                if (result.success) {
                    alert('设置保存成功！');
                    location.href = '/';
                } else {
                    alert(`保存失败: ${result.error || '未知错误'}`);
                }
            } catch (error) {
                console.error('保存设置失败:', error);
                alert('保存设置失败: ' + error.message);
            } finally {
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = '保存设置';
                }
            }
        });
    } catch (error) {
        console.error('获取设置失败:', error);
        alert('无法加载设置，请刷新页面重试');
    }
}


// ==================== 程序维护 ====================
async function programMaintenance(url, confirmMessage, actionName) {
    if (confirmMessage && !confirm(confirmMessage)) return;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (handleAjaxError(response)) return;

        const data = await response.json();
        if (data.success) {
            alert(data.message || `${actionName}成功`);
        } else {
            alert(`${actionName}失败: ${data.error || data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error(`${actionName}失败:`, error);
        alert(`${actionName}失败，请检查日志`);
    }
}

function clearCache() {
    programMaintenance('/api/program/clear_cache', '确定要清理缓存吗？将删除历史日志和最近启动记录。', '清理缓存');
}

function resetSettings() {
    programMaintenance('/api/program/reset_settings', '确定要重置所有设置吗？设置将恢复为默认值。', '重置设置');
}

function formatProgram() {
    if (!confirm('警告：格式化程序将清理日志、缓存与所有设置！')) return;
    programMaintenance('/api/program/format_program', '请再次确认：真的要格式化程序吗？此操作不可撤销！', '格式化程序');
}

function checkUpdate() {
    programMaintenance('/api/program/check_update', '确定要检查更新吗？检测到新版本时将自动下载并重启程序。', '检查更新');
}

// 获取在线玩家列表
async function fetchOnlinePlayers(serverName) {
    try {
        const response = await fetch(`/api/server/players/${serverName}`);
        const data = await response.json();
        const playerList = document.getElementById(`player-list-${serverName}`);
        if (!playerList) return;

        if (data.error || !data.players[2] || data.players[2].length === 0) {
            // 当没有玩家时，显示提示信息
            playerList.innerHTML = '<p>服务器没有玩家</p>';
            return;
        }

        // 假设data.players是一个玩家名字数组
        const players = data.players[2];
        if (players == '') {
            playerList.innerHTML = '<p>服务器没有玩家</p>';
            return;
        }

        let playerHtml = '';
        players.forEach(player => {
            playerHtml += `
                <div class="player-card">
                    <span class="player-name">${player}</span>
                    <div class="player-actions">
                        <button onclick="kickPlayer('${serverName}', '${player}')">踢出</button>
                        <button onclick="banPlayer('${serverName}', '${player}')">封禁</button>
                        <button onclick="opPlayer('${serverName}', '${player}')">设OP</button>
                    </div>
                </div>
            `;
        });
        playerList.innerHTML = playerHtml;
    } catch (error) {
        console.error('获取在线玩家失败:', error);
    }
}

// 切换玩家操作按钮的显示状态
function togglePlayerActions(iconElement) {
    const playerCard = iconElement.closest('.player-card');
    const actions = playerCard.querySelector('.player-actions');
    if (actions.style.display === 'none' || actions.style.display === '') {
        actions.style.display = 'block';
        iconElement.textContent = '▲'; // 切换图标为向上箭头
    } else {
        actions.style.display = 'none';
        iconElement.textContent = '▼'; // 切换图标为向下箭头
    }
}

// 通过API请求发送命令
function kickPlayer(serverName, playerName) {
    if (confirm(`确定要踢出玩家 ${playerName} 吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `kick ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功踢出: ${data.message}`);
                setTimeout(() => {
                    fetchOnlinePlayers(serverName);
                    getBannedPlayers(serverName);
                }, 8000);
            } else {
                alert(`踢出玩家失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('踢出玩家失败:', error);
            alert('踢出玩家失败，请检查日志');
        });
    }
}

function banPlayer(serverName, playerName) {
    if (confirm(`确定要封禁玩家 ${playerName} 吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `ban ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功封禁: ${data.message}`);
                // 刷新在线玩家列表和封禁玩家列表
                getBannedPlayers(serverName);
                setTimeout(() => {
                    fetchOnlinePlayers(serverName);
                }, 8000);
            } else {
                alert(`封禁玩家失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('封禁玩家失败:', error);
            alert('封禁玩家失败，请检查日志');
        });
    }
}

function pardonPlayer(serverName, playerName) {
    if (confirm(`确定要解封玩家 ${playerName} 吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `pardon ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功解封: ${data.message}`);
                // 刷新在线玩家列表和封禁玩家列表
                getBannedPlayers(serverName);
                setTimeout(() => {
                    fetchOnlinePlayers(serverName);
                }, 8000);
            } else {
                alert(`解封玩家失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('解封玩家失败:', error);
            alert('解封玩家失败，请检查日志');
        });
    }
}


// ==================== 通用模态框 ====================
function createPcsmtModal(title, bodyHtml) {
    closePcsmtModal();
    const overlay = document.createElement('div');
    overlay.className = 'pcsmt-modal-overlay';
    overlay.id = 'pcsmt-modal-overlay';
    overlay.innerHTML = `
        <div class="pcsmt-modal">
            <div class="pcsmt-modal-header">
                <h3>${title}</h3>
                <button class="pcsmt-modal-close" onclick="closePcsmtModal()">&times;</button>
            </div>
            <div class="pcsmt-modal-body">${bodyHtml}</div>
        </div>
    `;
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closePcsmtModal();
    });
    document.body.appendChild(overlay);
}

function closePcsmtModal() {
    const existing = document.getElementById('pcsmt-modal-overlay');
    if (existing) existing.remove();
}

// ==================== 重启服务器 ====================
async function restartServer(serverName) {
    if (!confirm(`确定要重启服务器 "${serverName}" 吗？`)) return;

    try {
        const response = await fetch(`/api/server/${serverName}/restart`, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (handleAjaxError(response)) return;

        const data = await response.json();
        if (data.success) {
            alert(data.message || '服务器正在重启');
            setTimeout(() => fetchServerInfo(serverName), 10000);
        } else {
            alert(`重启服务器失败: ${data.error || data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('重启服务器失败:', error);
        alert('重启服务器失败，请检查日志');
    }
}

// ==================== 回档服务器 ====================
async function showBackupDialog(serverName) {
    try {
        const response = await fetch(`/api/server/get/backups/${serverName}`);
        const data = await response.json();

        if (!data.success) {
            alert(data.message || '获取备份列表失败');
            return;
        }

        const backups = data.BackupList || [];
        const sourceText = data.source === 'mod' ? 'FTB Backups 2 模组' : 'eBackup 插件';

        let listHtml = `<p class="backup-source">备份来源: ${sourceText}</p>`;
        listHtml += '<div class="backup-list">';
        // 倒序展示，最新备份在前
        [...backups].reverse().forEach(backup => {
            listHtml += `
                <div class="backup-item">
                    <span class="backup-name" title="${backup}">${backup}</span>
                    <button onclick="retracementServer('${serverName}', '${backup}')">回档到此备份</button>
                </div>
            `;
        });
        listHtml += '</div>';
        listHtml += `<p class="backup-tip">提示：回档前请先停止服务器，回档会覆盖当前存档！</p>`;

        createPcsmtModal(`回档服务器 - ${serverName}`, listHtml);
    } catch (error) {
        console.error('获取备份列表失败:', error);
        alert('获取备份列表失败，请检查日志');
    }
}

async function retracementServer(serverName, backupFile) {
    if (!confirm(`确定要将服务器 "${serverName}" 回档到备份 "${backupFile}" 吗？\n当前存档将被覆盖（旧存档会保存为 old-save.zip），此操作不可撤销！`)) return;

    try {
        const response = await fetch(`/api/server/${serverName}/retracement`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ backup_file: backupFile })
        });

        if (handleAjaxError(response)) return;

        const data = await response.json();
        if (data.success) {
            alert(data.message || '回档完成');
            closePcsmtModal();
        } else {
            alert(`回档失败: ${data.message || data.error || '未知错误'}`);
        }
    } catch (error) {
        console.error('回档服务器失败:', error);
        alert('回档服务器失败，请检查日志');
    }
}

// ==================== OP 管理 ====================
function getOps(serverName) {
    fetch(`/api/server/get/ops/${serverName}`)
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById(`op-players-${serverName}`);
        if (!container) return;

        if (data.success) {
            const opsList = data.OpsList || [];
            if (opsList.length === 0) {
                container.innerHTML = '<p>没有OP玩家</p>';
                return;
            }

            let playerHtml = '';
            opsList.forEach(player => {
                playerHtml += `
                    <div class="player-card">
                        <span class="player-name">${player}</span>
                        <div class="player-actions">
                            <button onclick="deopPlayer('${serverName}', '${player}')">移除OP</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = playerHtml;
        } else {
            container.innerHTML = `<p>${data.message || '获取OP玩家列表失败'}</p>`;
        }
    })
    .catch(error => {
        console.error('获取OP玩家列表失败:', error);
        const container = document.getElementById(`op-players-${serverName}`);
        if (container) container.innerHTML = '<p>获取OP玩家列表失败</p>';
    });
}

function opPlayerFromInput(serverName) {
    const input = document.getElementById(`add-op-input-${serverName}`);
    const playerName = input.value.trim();
    if (!playerName) {
        alert('请输入玩家名');
        return;
    }
    opPlayer(serverName, playerName);
    input.value = '';
}

function opPlayer(serverName, playerName) {
    if (!confirm(`确定要给予玩家 ${playerName} OP权限吗？`)) return;

    fetch(`/api/server/${serverName}/op`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ player_name: playerName })
    })
    .then(response => {
        if (handleAjaxError(response)) return null;
        return response.json();
    })
    .then(data => {
        if (!data) return;
        if (data.success) {
            alert(data.message);
            getOps(serverName);
        } else {
            alert(`添加OP失败: ${data.message || data.error || '未知错误'}`);
        }
    })
    .catch(error => {
        console.error('添加OP失败:', error);
        alert('添加OP失败，请检查日志');
    });
}

function deopPlayer(serverName, playerName) {
    if (!confirm(`确定要移除玩家 ${playerName} 的OP权限吗？`)) return;

    fetch(`/api/server/${serverName}/deop`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ player_name: playerName })
    })
    .then(response => {
        if (handleAjaxError(response)) return null;
        return response.json();
    })
    .then(data => {
        if (!data) return;
        if (data.success) {
            alert(data.message);
            getOps(serverName);
        } else {
            alert(`移除OP失败: ${data.message || data.error || '未知错误'}`);
        }
    })
    .catch(error => {
        console.error('移除OP失败:', error);
        alert('移除OP失败，请检查日志');
    });
}

// ==================== IP 封禁管理 ====================
function getBannedIps(serverName) {
    fetch(`/api/server/get/banned/ips/${serverName}`)
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById(`banned-ips-${serverName}`);
        if (!container) return;

        if (data.success) {
            const ipList = data.BannedIpList || [];
            if (ipList.length === 0) {
                container.innerHTML = '<p>没有被封禁的IP</p>';
                return;
            }

            let ipHtml = '';
            ipList.forEach(ip => {
                ipHtml += `
                    <div class="player-card">
                        <span class="player-name">${ip}</span>
                        <div class="player-actions">
                            <button onclick="unbanIp('${serverName}', '${ip}')">解封</button>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = ipHtml;
        } else {
            container.innerHTML = `<p>${data.message || '获取封禁IP列表失败'}</p>`;
        }
    })
    .catch(error => {
        console.error('获取封禁IP列表失败:', error);
        const container = document.getElementById(`banned-ips-${serverName}`);
        if (container) container.innerHTML = '<p>获取封禁IP列表失败</p>';
    });
}

function banIpFromInput(serverName) {
    const input = document.getElementById(`ban-ip-input-${serverName}`);
    const ip = input.value.trim();
    if (!ip) {
        alert('请输入IP地址');
        return;
    }
    if (!confirm(`确定要封禁IP ${ip} 吗？`)) return;

    fetch(`/api/server/${serverName}/ban/ip`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ ip: ip })
    })
    .then(response => {
        if (handleAjaxError(response)) return null;
        return response.json();
    })
    .then(data => {
        if (!data) return;
        if (data.success) {
            alert(data.message);
            input.value = '';
            getBannedIps(serverName);
        } else {
            alert(`封禁IP失败: ${data.message || data.error || '未知错误'}`);
        }
    })
    .catch(error => {
        console.error('封禁IP失败:', error);
        alert('封禁IP失败，请检查日志');
    });
}

function unbanIp(serverName, ip) {
    if (!confirm(`确定要解封IP ${ip} 吗？`)) return;

    fetch(`/api/server/${serverName}/unban/ip`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ ip: ip })
    })
    .then(response => {
        if (handleAjaxError(response)) return null;
        return response.json();
    })
    .then(data => {
        if (!data) return;
        if (data.success) {
            alert(data.message);
            getBannedIps(serverName);
        } else {
            alert(`解封IP失败: ${data.message || data.error || '未知错误'}`);
        }
    })
    .catch(error => {
        console.error('解封IP失败:', error);
        alert('解封IP失败，请检查日志');
    });
}

// ==================== 重定向服务器路径 ====================
async function redirectServerPath(serverName) {
    const newPath = prompt(`请输入服务器 "${serverName}" 的新路径（绝对路径）:`);
    if (!newPath) return;

    if (!confirm(`确定要将服务器路径重定向到:\n${newPath}\n吗？服务器文件需要已移动到新位置。`)) return;

    try {
        const response = await fetch(`/api/server/${serverName}/redirect_path`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ new_path: newPath })
        });

        if (handleAjaxError(response)) return;

        const data = await response.json();
        if (data.success) {
            alert(data.message || '重定向成功');
        } else {
            alert(`重定向失败: ${data.message || data.error || '未知错误'}`);
        }
    } catch (error) {
        console.error('重定向服务器路径失败:', error);
        alert('重定向服务器路径失败，请检查日志');
    }
}

function getBannedPlayers(serverName) {
    fetch(`/api/server/get/banned/players/${serverName}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const bannedPlayersList = data.BannedPlayerList || [];
            const bannedPlayersContainer = document.getElementById(`banned-players-${serverName}`);

            if (bannedPlayersList.length === 0) {
                bannedPlayersContainer.innerHTML = '<p>没有被封禁的玩家</p>';
                return;
            }

            // 动态生成封禁玩家卡片
            let playerHtml = '';
            bannedPlayersList.forEach(player => {
                playerHtml += `
                    <div class="player-card">
                        <span class="player-name">${player}</span>
                        <div class="player-actions">
                            <button onclick="pardonPlayer('${serverName}', '${player}')">解封</button>
                        </div>
                    </div>
                `;
            });

            bannedPlayersContainer.innerHTML = playerHtml;
        } else {
            console.error('获取封禁玩家列表失败:', data.error);
            document.getElementById(`banned-players-${serverName}`).innerHTML = '<p>获取封禁玩家列表失败</p>';
        }
    })
    .catch(error => {
        console.error('获取封禁玩家列表失败:', error);
        document.getElementById(`banned-players-${serverName}`).innerHTML = '<p>获取封禁玩家列表失败</p>';
    });
}

function getWhiteList(serverName) {
    fetch(`/api/server/get/white-list/${serverName}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const whiteListPlayersList = data.WhiteList || [];
            const whiteListPlayersContainer = document.getElementById(`whitelist-players-${serverName}`);

            if (whiteListPlayersList.length === 0) {
                whiteListPlayersContainer.innerHTML = '<p>没有在白名单中的玩家</p>';
                return;
            }

            let playerHtml = '';
            whiteListPlayersList.forEach(player => {
                playerHtml += `
                    <div class="player-card">
                        <span class="player-name">${player}</span>
                        <div class="player-actions">
                            <button onclick="removeFromWhiteList('${serverName}', '${player}')">移出白名单</button>
                        </div>
                    </div>
                `;
            });

            whiteListPlayersContainer.innerHTML = playerHtml;
        } else {
            document.getElementById(`whitelist-players-${serverName}`).innerHTML = '<p>白名单未启用</p>';
        }
    })
    .catch(error => {
        console.error('获取白名单玩家列表失败:', error);
        document.getElementById(`whitelist-players-${serverName}`).innerHTML = '<p>获取白名单玩家列表失败</p>';
    });
}

function addToWhiteList(serverName, playerName) {
    if (confirm(`确定要添加玩家 ${playerName} 到白名单吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `whitelist add ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功添加到白名单: ${data.message}`);
                // 刷新白名单玩家列表
                getWhiteList(serverName);
            }else{
                alert(`添加玩家失败: ${data.error || '未知错误'}`);
            }
        })
    }
}

function removeFromWhiteList(serverName, playerName) {
    if (confirm(`确定要移出玩家 ${playerName} 白名单吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `whitelist remove ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功移出白名单: ${data.message}`);
                // 刷新白名单玩家列表
                getWhiteList(serverName);
            }else{
                alert(`移出玩家失败: ${data.error || '未知错误'}`);
            }
        })
    }
}

// 切换历史玩家下拉框显示状态
function toggleHistoryPlayersDropdown(serverName) {
    const content = document.getElementById(`history-players-content-${serverName}`);
    const toggleIcon = document.querySelector(`#history-players-content-${serverName}`).previousElementSibling.querySelector('.dropdown-toggle');
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        toggleIcon.textContent = '▲'; // 切换图标为向上箭头
    } else {
        content.style.display = 'none';
        toggleIcon.textContent = '▼'; // 切换图标为向下箭头
    }
}

// 获取历史玩家列表
async function fetchHistoryPlayers(serverName) {
    const contentDiv = document.getElementById(`history-players-content-${serverName}`);
    if (!contentDiv) return;

    try {
        const response = await fetch(`/api/server/get/history/players/${serverName}`);
        const data = await response.json();

        if (data.error) {
            contentDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
            return;
        }

        const players = data.HistoryPlayerList || [];
        if (players.length === 0) {
            contentDiv.innerHTML = '<p>没有历史玩家记录</p>';
            return;
        }

        let playerHtml = '';
        players.forEach(player => {
            playerHtml += `
                <div class="player-card">
                    <span class="player-name">${player}</span>
                    <div class="player-actions">
                        <button onclick="addToWhiteList('${serverName}', '${player}')">加入白名单</button>
                    </div>
                </div>
            `;
        });
        contentDiv.innerHTML = playerHtml;
    } catch (error) {
        console.error('获取历史玩家失败:', error);
        contentDiv.innerHTML = '<p style="color: red;">获取历史玩家失败，请稍后重试。</p>';
    }
}

// 建立连接获取终端消息
async function setupTerminalWebSocket(serverName) {
    // 清除该服务器已有的定时器
    if (window.terminalTimers && window.terminalTimers[serverName]) {
        clearInterval(window.terminalTimers[serverName]);
    }

    const terminalOutput = document.getElementById(`terminal-output-${serverName}`);
    if (!terminalOutput) return;

    // 保持最大行数的函数
    function keepMaxLines() {
        const maxLines = 1000;
        while (terminalOutput.childElementCount > maxLines) {
            terminalOutput.removeChild(terminalOutput.firstChild);
        }
    }

    // 存储最后获取的日志快照
    let lastLogsSnapshot = [];

    // 异步获取日志
    const fetchLogs = async () => {
        try {
            const response = await fetch(`/api/server/terminal/${serverName}`);
            const data = await response.json();

            if (data.success) {
                const newLogs = Array.isArray(data.logs) ? data.logs : data.logs.split('\n');
                const diffLogs = getNewLogs(lastLogsSnapshot, newLogs);

                // 先更新快照再追加日志
                lastLogsSnapshot = newLogs.slice(-1000);

                diffLogs.forEach(log => {
                    const div = document.createElement('div');
                    div.textContent = log;
                    terminalOutput.appendChild(div);
                });

                keepMaxLines(); // 新增行数限制
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
        } catch (error) {
            console.error('获取终端日志失败:', error);
        }
    };

    // 差异对比方法
    function getNewLogs(prevLogs, newLogs) {
        if (!prevLogs.length || !newLogs.length) return newLogs;
        const firstMismatch = newLogs.findIndex((log, index) =>
            index >= prevLogs.length || log !== prevLogs[index]
        );
        return firstMismatch === -1 ? [] : newLogs.slice(firstMismatch);
    }

    // 初始获取日志
    await fetchLogs();

    // 定时器, 每3秒获取一次日志
    const intervalId = setInterval(async () => {
        await fetchLogs();
    }, 3000);

    // 保存定时器 ID 以便后续清除
    if (!window.terminalTimers) {
        window.terminalTimers = {};
    }
    window.terminalTimers[serverName] = intervalId;
}

// 发送命令
function sendCommand(serverName) {
    const commandInput = document.getElementById(`command-input-${serverName}`);
    const command = commandInput.value.trim();
    if (!command) return;

    fetch(`/api/server/${serverName}/command`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const terminalOutput = document.getElementById(`terminal-output-${serverName}`);
            if (terminalOutput) {
                terminalOutput.innerHTML += `<div style="color: #4CAF50;">&gt; ${command}</div>`;
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('发送命令失败:', error);
        alert('发送命令失败，请检查日志');
    });

    // 清空输入框
    commandInput.value = '';
}

// 图表实例缓存（单例模式，复用实例避免闪烁）
let chartInstances = {
    cpu: null,
    ram: null,
    disk: null
};

// 图表刷新定时器
let chartRefreshTimer = null;

// ECharts 加载 Promise（确保只加载一次）
let echartsLoadPromise = null;

function loadECharts() {
    if (window.echarts) return Promise.resolve();

    if (!echartsLoadPromise) {
        echartsLoadPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js';
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('ECharts 库加载失败'));
            document.head.appendChild(script);
        });
    }
    return echartsLoadPromise;
}

// 获取或创建图表实例（单例）
function getOrCreateChart(chartId) {
    const dom = document.getElementById(chartId);
    if (!dom) return null;

    if (chartInstances[chartId]) {
        return chartInstances[chartId];
    }

    const instance = echarts.init(dom);
    chartInstances[chartId] = instance;
    return instance;
}

// 销毁所有图表实例
function disposeAllCharts() {
    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
            chartInstances[key].dispose();
            chartInstances[key] = null;
        }
    });
}

// 获取CPU、内存和磁盘使用率（统一入口）
function fetchCpuRamDiskUsage() {
    const containers = ['cpu-usage-chart', 'ram-usage-chart', 'disk-usage-chart'];
    const allExist = containers.every(id => document.getElementById(id));

    if (!allExist) {
        chartRefreshTimer = setTimeout(fetchCpuRamDiskUsage, 200);
        return;
    }

    loadECharts()
        .then(() => refreshAllCharts())
        .catch(err => console.error('ECharts 加载失败:', err));
}

// 并发请求所有数据并刷新图表
async function refreshAllCharts() {
    try {
        const [cpuData, ramData, diskData] = await Promise.all([
            fetch('/api/program/get/CPU/Usage').then(r => r.json()),
            fetch('/api/program/get/RAM/Usage').then(r => r.json()),
            fetch('/api/program/disk_usage').then(r => r.json())
        ]);

        updateCpuChart(cpuData);
        updateRamChart(ramData);
        updateDiskChart(diskData);

        chartRefreshTimer = setTimeout(refreshAllCharts, 5000);
    } catch (error) {
        console.error('获取系统资源数据失败:', error);
        chartRefreshTimer = setTimeout(refreshAllCharts, 5000);
    }
}

// 更新CPU图表（增量更新，不重建实例）
function updateCpuChart(data) {
    const chart = getOrCreateChart('cpu-usage-chart');
    if (!chart) return;

    const used = data.used || 0;
    const absUsed = data.abs_used || 0;
    const absTotal = data.abs_total || 0;

    chart.setOption({
        graphic: [{
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
                text: `${used.toFixed(1)}%`,
                textAlign: 'center',
                fill: '#67afdfff',
                fontSize: 20,
                fontWeight: 'bold'
            }
        }],
        series: [{
            data: [
                { value: used, name: '已使用:' + used.toFixed(2) + '%', itemStyle: { color: '#36a3eb' } },
                { value: 100 - used, name: '未使用:' + (100 - used).toFixed(2) + '%', itemStyle: { color: '#a2c2fcff' } }
            ]
        }]
    }, { notMerge: false });

    const cpuUsedEl = document.getElementById('cpu-used');
    const cpuTotalEl = document.getElementById('cpu-total');
    if (cpuUsedEl) cpuUsedEl.textContent = `${absUsed} MHz`;
    if (cpuTotalEl) cpuTotalEl.textContent = `${absTotal} MHz`;
}

// 更新内存图表（增量更新，不重建实例）
function updateRamChart(data) {
    const chart = getOrCreateChart('ram-usage-chart');
    if (!chart) return;

    const absUsed = data.abs_used || 0;
    const absTotal = data.abs_total || 0;
    const percent = absTotal > 0 ? ((absUsed / absTotal) * 100).toFixed(1) : 0;

    chart.setOption({
        graphic: [{
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
                text: `${percent}%`,
                textAlign: 'center',
                fill: '#67afdfff',
                fontSize: 20,
                fontWeight: 'bold'
            }
        }],
        series: [{
            data: [
                { value: absUsed, name: '已使用:' + absUsed.toFixed(2) + 'MB', itemStyle: { color: '#36a3eb' } },
                { value: absTotal - absUsed, name: '未使用:' + absTotal.toFixed(2) + 'MB', itemStyle: { color: '#a2c2fcff' } }
            ]
        }]
    }, { notMerge: false });

    const ramUsedEl = document.getElementById('ram-used');
    const ramTotalEl = document.getElementById('ram-total');
    if (ramUsedEl) ramUsedEl.textContent = `${absUsed} MB`;
    if (ramTotalEl) ramTotalEl.textContent = `${absTotal} MB`;
}

// 更新磁盘图表（增量更新，不重建实例）
function updateDiskChart(data) {
    if (data.error) {
        console.error('获取磁盘使用率失败:', data.error);
        return;
    }

    const chart = getOrCreateChart('disk-usage-chart');
    if (!chart) return;

    const usedPercent = data.disk_usage || 0;
    const freePercent = data.disk_free || 0;
    const used = data.usage || 0;
    const free = data.free || 0;

    chart.setOption({
        graphic: [{
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
                text: usedPercent + '%',
                textAlign: 'center',
                fill: '#67afdfff',
                fontSize: 20,
                fontWeight: 'bold'
            }
        }],
        series: [{
            data: [
                {
                    value: usedPercent,
                    name: `已使用: ${used} GB\n已使用`,
                    itemStyle: { color: '#386ffcff' }
                },
                {
                    value: freePercent,
                    name: `未使用: ${free} GB\n未使用`,
                    itemStyle: { color: '#a2c2fcff' }
                }
            ]
        }]
    }, { notMerge: false });

    const diskUsedEl = document.getElementById('disk-used');
    const diskTotalEl = document.getElementById('disk-total');
    if (diskUsedEl) diskUsedEl.textContent = `${used} GB`;
    if (diskTotalEl) diskTotalEl.textContent = `${free + used} GB`;
}

// 在首次加载时预初始化图表结构（空的环形图，避免白屏闪烁）
function preInitCharts() {
    loadECharts().then(() => {
        ['cpu-usage-chart', 'ram-usage-chart', 'disk-usage-chart'].forEach(id => {
            const dom = document.getElementById(id);
            if (!dom) return;

            const instance = echarts.init(dom);
            chartInstances[id] = instance;

            instance.setOption({
                tooltip: { formatter: '{b}' },
                graphic: [{
                    type: 'text',
                    left: 'center',
                    top: 'center',
                    style: {
                        text: '加载中...',
                        textAlign: 'center',
                        fill: '#aaa',
                        fontSize: 14,
                        fontWeight: 'normal'
                    }
                }],
                series: [{
                    type: 'pie',
                    radius: ['60%', '80%'],
                    silent: true,
                    data: [
                        { value: 1, itemStyle: { color: '#e0e0e0' } }
                    ]
                }]
            });
        });
    });
=======
// 页面内容映射
const pageContents = {
    home: `
        <div class="home-content">
            <h1>PCSMT2 控制台</h1>
            <p>欢迎使用 Minecraft 服务器管理工具</p>
            <div class="project-info">
                <p>本项目为开源项目</p>
                <div class="link-group">
                    <a target="_blank" rel="noopener" href="https://github.com/Ksayus/PCSMT-2">
                        <i class="fab fa-github"></i> Github 仓库
                    </a>
                    <br>
                    <a href="https://space.bilibili.com/558271819" target="_blank" rel="noopener">
                        <img src="/static/bilibili.png" width=16px height=16px></img> Bilibili 主页
                    </a>
                </div>
                <div class="version-info">
                    <i class="fas fa-code-branch"></i>
                    <span>版本号: <span id="program-version">加载中...</span></span>
                </div>
            </div>
        </div>
    `,

    help: `
        <div class="help-content">
            <h1>PCSMT API</h1>
            <table class="help-table">
                <thead>
                    <tr>
                        <th colspan="2">API 列表</th>
                        <th colspan="2">描述</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>/api</td>
                        <td>这是API的首页</td>
                    </tr>
                    <tr>
                        <td>/api/server</td>
                        <td>这是API Server的首页</td>
                    </tr>
                    <tr>
                        <td>/api/server/list</td>
                        <td>服务器列表</td>
                    </tr>
                    <tr>
                        <td>/api/server/info/{string:server_name}</td>
                        <td>指定服务器信息</td>
                    </tr>
                    <tr>
                        <td>/api/server/latest</td>
                        <td>上次启动服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/start</td>
                        <td>启动指定服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/stop</td>
                        <td>停止指定服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/status</td>
                        <td>获取服务器启动状态</td>
                    </tr>
                    <tr>
                        <td>/api/server/info/<string:server_name>/excel</td>
                        <td>生成并下载指定服务器的Excel表格</td>
                    </tr>
                    <tr>
                        <td>/api/server/list/excel</td>
                        <td>生成并下载所有服务器的Excel表格</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/storage_info</td>
                        <td>获取指定服务器的存储数据</td>
                    </tr>
                    <tr>
                        <td>/api/program</td>
                        <td>这是API Program的首页</td>
                    </tr>
                    <tr>
                        <td>/api/program/version</td>
                        <td>程序版本</td>
                    </tr>
                    <tr>
                        <td>/api/program/minecraft_version</td>
                        <td>获取Minecraft的所有版本</td>
                    </tr>
                    <tr>
                        <td>/api/program/disk_usage</td>
                        <td>获取程序所在硬盘使用状态</td>
                    </tr>
                    <tr>
                        <td>/api/program/get/settings</td>
                        <td>获取程序设置信息</td>
                    </tr>
                    <tr>
                        <td>/api/program/set/settings</td>
                        <td>设置程序设置信息</td>
                    </tr>
                    <tr>
                        <td>/api/static/ico</td>
                        <td>获取图标</td>
                    </tr>
                    <tr>
                        <td>/login</td>
                        <td>登录界面</td>
                    </tr>
                    <tr>
                        <td>/server/create</td>
                        <td>创建服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/<string:server_name>/storage_chart</td>
                        <td>渲染存储图表页面</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,

    // 修改服务器列表页面的布局结构
    servers: `
        <div class="servers-content">
            <h1>服务器列表</h1>
            <div class="charts-container">
                <!-- 磁盘使用率 -->
                <div class="chart-item">
                    <div id="disk-usage-chart" style="width: 200px; height: 200px;"></div>
                    <div class="chart-label">磁盘使用率</div>
                    <div class="chart-stats">
                        <span id="disk-used">0GB</span> /
                        <span id="disk-total">0GB</span>
                    </div>
                </div>

                <!-- CPU使用率 -->
                <div class="chart-item">
                    <div id="cpu-usage-chart" style="width: 200px; height: 200px;"></div>
                    <div class="chart-label">CPU使用率</div>
                    <div class="chart-stats">
                        <span id="cpu-used">0MHz</span> /
                        <span id="cpu-total">0MHz</span>
                    </div>
                </div>

                <!-- 内存使用率 -->
                <div class="chart-item">
                    <div id="ram-usage-chart" style="width: 200px; height: 200px;"></div>
                    <div class="chart-label">内存使用率</div>
                    <div class="chart-stats">
                        <span id="ram-used">0GB</span> /
                        <span id="ram-total">0GB</span>
                    </div>
                </div>
            </div>
            <div class="server-container" id="server-list-container">
                <div class="loading">加载中...</div>
            </div>
        </div>
    `,

    server_info: (serverName) => `
        <div class="server-info-content">
            <!-- 左侧：服务器信息 -->
            <div class="server-info-left">
                <div class="server-card">
                    <table>
                        <tr>
                            <th id="Type-th">类型</th>
                            <td id="Info-td">信息</td>
                        </tr>
                        <tr>
                            <th>服务器名</th>
                            <td id="id-name">${serverName}</td>
                        </tr>
                        <tr>
                            <th>服务器版本</th>
                            <td id="id-version"></td>
                        </tr>
                        <tr>
                            <th>服务器大小</th>
                            <td id="id-size"></td>
                        </tr>
                        <tr>
                            <th>服务器启动次数</th>
                            <td id="id-start-counts"></td>
                        </tr>
                        <tr>
                            <th>上次启动时间</th>
                            <td id="id-latest-start-time"></td>
                        </tr>
                    </table>
                </div>
                <div class="button-group" id="button-group">
                    <button id="button-server" onclick="">检查中...</button>
                    <button id="storage-chart" onclick="ChartImage('${serverName}')">存储占用</button>
                    <button class="download-btn" onclick="downloadServer('${serverName}')">
                        <i class="fas fa-file-download"></i>下载服务器信息
                    </button>
                    <button class="change-properties-btn" onclick="changeServerProperties('${serverName}')">
                        <i class="fas fa-cog"></i>修改服务器属性
                    </button>
                </div>
            </div>

            <!-- 中间：终端消息 -->
            <div class="server-info-center">
                <h3>服务器终端</h3>
                <div class="terminal-output" id="terminal-output-${serverName}">
                    <!-- 终端输出 -->
                </div>
                <div class="terminal-input">
                    <input type="text" id="command-input-${serverName}" placeholder="输入命令...">
                    <button onclick="sendCommand('${serverName}')">发送</button>
                </div>
            </div>

            <!-- 右侧：在线玩家列表及历史玩家抽屉 -->
            <div class="server-info-right">
                <h3>在线玩家</h3>
                <div class="player-list" id="player-list-${serverName}"></div>

                <h3>封禁玩家</h3>
                <div class="banned-player-list" id="banned-players-${serverName}">
                    <p>加载中...</p>
                </div>

                <h3>白名单玩家</h3>
                <div class="whitelist-player-list" id="whitelist-players-${serverName}">
                    <p>加载中...</p>
                </div>

                <!-- 历史玩家下拉框 -->
                <div class="history-players-dropdown">
                    <div class="dropdown-header" onclick="toggleHistoryPlayersDropdown('${serverName}')">
                        <h3>历史玩家</h3>
                        <span class="dropdown-toggle">▼</span>
                    </div>
                    <div class="dropdown-content-history-player" id="history-players-content-${serverName}" style="display: none;">
                        <p>加载中...</p>
                    </div>
                </div>
            </div>
        </div>
`,

    server_latest: `
        <div class="server-latest-content">
            <div class="server-card">
                <table>
                    <tr>
                        <th id="Type-th">类型</th>
                        <td id="Info-td">信息</td>
                    </tr>
                    <tr>
                        <th>服务器名</th>
                        <td id="id-name"></td>
                    </tr>
                    <tr>
                        <th>服务器版本</th>
                        <td id="id-version"></td>
                    </tr>
                    <tr>
                        <th>服务器大小</th>
                        <td id="id-size"></td>
                    </tr>
                    <tr>
                        <th>服务器启动次数</th>
                        <td id="id-start-counts"></td>
                    </tr>
                    <tr>
                        <th>上次启动时间</th>
                        <td id="id-latest-start-time"></td>
                    </tr>
                </table>
            </div>
        </div>
    `,

    program_version: `
        <div class="program-version-content">
            <div class="card">
                <div class="content">
                    <p>程序版本: <span id="version"></span></p>
                </div>
                <div class="loading-icon" style="display: none;"></div>
                <div class="error-message" style="display: none;">获取程序版本失败，请稍后重试。</div>
            </div>
        </div>
    `,

    settings: `
        <div class="settings-content">
            <h1>程序设置</h1>
            <p>这里可以配置程序的各种设置，例如服务器路径、日志级别等。</p>
            <form id="settings-form">
                <div class="form-group">
                    <label>服务器运行内存设置 (MB):</label>
                    <div class="input-row">
                        <input type="number" id="min-memory" name="min_memory" min="1024" placeholder="最小值">
                        <span>至</span>
                        <input type="number" id="max-memory" name="max_memory" min="1024" placeholder="最大值">
                    </div>
                </div>

                <div class="form-group">
                    <label>Nogui 模式:</label>
                    <div class="toggle-switch">
                        <input type="checkbox" id="nogui-enabled" name="nogui_enabled">
                        <label for="nogui-enabled"></label>
                    </div>
                </div>

                <div class="form-group">
                    <label>EULA 生成等待时间 (秒):</label>
                    <input type="number" id="eula-wait-time" name="eula_wait_time" min="1" max="300" value="">
                </div>

                <div class="form-group">
                    <label>开机自启动:</label>
                    <div class="toggle-switch">
                        <input type="checkbox" id="auto-start" name="auto_start">
                        <label for="auto-start"></label>
                    </div>
                </div>

                <div class="form-group">
                    <label>自动更新源:</label>
                    <select id="update-source" name="update_source">
                        <option value="Github">Github</option>
                        <option value="Gitee">Gitee</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>获取测试版本:</label>
                    <div class="toggle-switch">
                        <input type="checkbox" id="test-versions" name="test_versions">
                        <label for="test-versions"></label>
                    </div>
                </div>

                <div class="form-group">
                    <label>服务器存储占用的更新时间:</label>
                    <input type="text" id="storage-update-time" name="storage_update_time" min="1" value="">
                </div>

                <div class="form-group">
                    <label>API端口:</label>
                    <input type="number" id="server-port" name="server_port" min="1024" max="65535" value="">
                </div>

                <button type="submit" class="save-btn">保存设置</button>
            </form>
        </div>
    `,

    mods: `
        <div class="mods-content">
            <h1>Mod/Plugin 下载</h1>
            <!-- 添加MOD列表 -->
        </div>
    `
};

// 页面初始化
window.onload = () => {
    fetchServers();
    loadContent('home');
    fetchProgramVersion();
};

// 加载页面内容
function loadContent(page, serverName = '') {
    const contentDiv = document.getElementById('dynamic-content');
    const loader = document.getElementById('loader');

    // 清除所有定时器
    if (window.terminalTimers) {
        Object.values(window.terminalTimers).forEach(clearTimeout);
        window.terminalTimers = {};
    }
    // 清除CPU/RAM定时器
    Object.values(CpuRamDiskTimers).forEach(clearTimeout);
    CpuRamDiskTimers = { cpu: null, ram: null, disk:null };

    // 清除所有终端日志定时器
    if (window.terminalTimers) {
        Object.values(window.terminalTimers).forEach(intervalId => clearInterval(intervalId));
        window.terminalTimers = {};
    }

    // 显示加载动画
    loader.style.display = 'block';
    contentDiv.innerHTML = '';

    setTimeout(() => {
        loader.style.display = 'none';

        switch(page) {
            case 'home':
                contentDiv.innerHTML = pageContents.home;
                fetchProgramVersion();
                break;
            case 'help':
                contentDiv.innerHTML = pageContents.help;
                break;
            case 'servers':
                contentDiv.innerHTML = pageContents.servers;
                fetchCpuRamDiskUsage();  // 获取CPU、内存和磁盘使用率
                fetchServerList();
                break;
            case 'server_info':
                if (serverName) {
                    contentDiv.innerHTML = pageContents.server_info(serverName);
                    fetchServerInfo(serverName);
                }
                break;
            case 'server_latest':
                contentDiv.innerHTML = pageContents.server_latest;
                fetchLatestServerInfo();
                break;
            case 'program_version':
                contentDiv.innerHTML = pageContents.program_version;
                fetchProgramVersion();
                break;
            case 'settings':
                contentDiv.innerHTML = pageContents.settings;
                fetchSettings(); // 新增：获取设置数据
                break;
            case 'mods':
                contentDiv.innerHTML = pageContents.mods;
                break;
            default:
                contentDiv.innerHTML = pageContents.home;
        }
    }, 300);
}

// 获取服务器列表
async function fetchServers() {
    try {
        const response = await fetch('/api/server/list');
        const data = await response.json();
        const serverList = document.getElementById('server-list');
        serverList.innerHTML = '';

        if (data.error) {
            serverList.innerHTML = `<p>${data.error}</p>`;
            return;
        }

        data.serverlist.forEach(server => {
            const li = document.createElement('li');
            li.innerHTML = `<a href="#server_info" onclick="loadContent('server_info', '${server}')">${server}</a>`;
            serverList.appendChild(li);
        });
    } catch (error) {
        console.error('获取服务器列表失败:', error);
    }
}

// 获取服务器列表卡片
async function fetchServerList(AddButton = true) {
    try {
        // 获取圆环元素
        const $text = $('.text');
        // 更新进度条显示
        function updateProgress(value) {
            // 当百分比小于等于50
            if(value <= 50){
                $('.mask-right').remove();
                var html = '<div class="mask-right" style="transform:rotate('+ (value * 3.6) +'deg)"></div>';
                $('.circle-right').append(html);
            }else{
                $('.circle-left, .mask-left').remove();
                const adjustedValue = value - 50;
                var html = '<div class="circle-left">';
                html += '<div class="mask-left" style="transform:rotate('+ (adjustedValue * 3.6) +'deg)"></div>';
                html += '</div>';
                $('.circle-right').after(html);
            }

            // 更新文本显示
            $text.html(Math.round(value) + '%');
        }

        // 设置API请求超时（10秒）
        const timeout = setTimeout(() => {
            updateProgress(0, 0, true); // 显示错误状态
            console.error('获取服务器列表超时');
        }, 10000);

        fetch('/api/server/list')
            .then(response => response.json())
            .then(data => {
                clearTimeout(timeout); // 清除超时计时器

                const serverList = document.getElementById('server-list-container');
                serverList.innerHTML = ''; // 清空加载中的提示

                if (data.error) {
                    serverList.innerHTML = `<p style="color: red;">${data.error}</p>`;
                    return;
                }

                const serverListData = data.serverlist || [];
                if (AddButton)
                {
                    if (serverListData.length == 0) {
                        serverList.innerHTML = '<p>没有可用的服务器。</p>';

                        // 仅添加创建服务器按钮（移除下载按钮）
                        const buttonGroup = document.createElement('div');
                        buttonGroup.className = 'button-group';
                        buttonGroup.style.display = 'flex';
                        buttonGroup.style.justifyContent = 'center';
                        buttonGroup.style.gap = '15px';

                        const createServerBtn = document.createElement('button');
                        createServerBtn.className = 'create-btn';
                        createServerBtn.innerHTML = '<i class="fas fa-plus"></i>创建服务器';
                        createServerBtn.onclick = function() {
                            createServer();
                        };
                        buttonGroup.appendChild(createServerBtn);

                        serverList.parentNode.insertBefore(buttonGroup, serverList);
                        return;
                    }

                    // 在服务器列表容器前添加按钮组
                    const buttonGroup = document.createElement('div');
                    buttonGroup.className = 'button-group'; // 使用现有按钮组样式
                    buttonGroup.style.display = 'flex'; // 确保按钮水平排列
                    buttonGroup.style.justifyContent = 'center'; // 居中显示
                    buttonGroup.style.gap = '15px'; // 设置按钮间距

                    // 创建服务器按钮
                    const createServerBtn = document.createElement('button');
                    createServerBtn.className = 'create-btn';
                    createServerBtn.innerHTML = '<i class="fas fa-plus"></i>创建服务器';
                    createServerBtn.onclick = function() {
                        createServer();
                    };
                    buttonGroup.appendChild(createServerBtn);

                    // 下载所有服务器按钮
                    const downloadAllBtn = document.createElement('button');
                    downloadAllBtn.className = 'download-btn';
                    downloadAllBtn.innerHTML = '<i class="fas fa-file-download"></i>下载所有服务器信息';
                    downloadAllBtn.onclick = function() {
                        downloadAllServers(serverListData);
                    };
                    buttonGroup.appendChild(downloadAllBtn);

                    serverList.parentNode.insertBefore(buttonGroup, serverList);
                }

                const serverElements = serverListData.map(server => `
                    <div class="server-card">
                        <!-- 删除按钮 -->
                        <div class="delete-btn" onclick="deleteServer('${server}'); event.stopPropagation();">
                            <i class="fas fa-trash-alt"></i>
                        </div>
                        <div class="server-card-content" onclick="loadContent('server_info', '${server}')">
                            <h3>${server}</h3>
                            <div class="server-card-info">
                                <div>
                                    <span>在线人数</span>
                                    <span id="online-player-${server}">加载中...</span>
                                </div>
                                <div>
                                    <span>版本</span>
                                    <span id="version-${server}">加载中...</span>
                                </div>
                                <div>
                                    <span>大小</span>
                                    <span id="size-${server}">加载中...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `);

                serverList.innerHTML = serverElements.join('');

                // 异步加载每个服务器的详细信息
                serverListData.forEach(server => {
                    fetchServerBasicInfo(server);
                    fetchServerPlayerInfo(server);
                });
            })
            .catch(error => {
                clearTimeout(timeout); // 清除超时计时器
                console.error('获取服务器列表时出错:', error);
                document.getElementById('server-list-container').innerHTML = '<p style="color: red;">获取服务器列表失败，请稍后重试。</p>';
                // 显示错误状态
                updateProgress(0, 0, true);
            });
    } catch (error) {
        console.error('获取服务器列表失败:', error);
    }
}

// 获取服务器玩家信息
async function fetchServerPlayerInfo(serverName) {
    try {
        const response = await fetch(`/api/server/players/${serverName}`);
        const data = await response.json();
        if (data.error) {
            document.getElementById(`online-player-${serverName}`).textContent = '获取失败';
            return;
        };
        if (!data.players)
        {
            document.getElementById(`online-player-${serverName}`).textContent = '服务器未启动';
            return;
        }

        document.getElementById(`online-player-${serverName}`).textContent = `${data.players[0]} / ${data.players[1]}` || '服务器未启动';
    } catch (error) {
        console.error('获取玩家列表失败:', error);
    }
}

// 获取服务器基本信息（用于卡片展示）
async function fetchServerBasicInfo(serverName) {
    try {
        const response = await fetch(`/api/server/info/${serverName}`);
        const data = await response.json();

        if (data.error) return;

        document.getElementById(`version-${serverName}`).textContent = data.version || '未知';
        document.getElementById(`size-${serverName}`).textContent = data.size || '未知';
    } catch (error) {
        console.error(`获取服务器 ${serverName} 基本信息失败:`, error);
    }
}

// 获取服务器信息
async function fetchServerInfo(serverName) {
    try {
        const response = await fetch(`/api/server/info/${serverName}`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('id-version').innerText = data.version;
        document.getElementById('id-size').innerText = data.size;
        document.getElementById('id-start-counts').innerText = data.startCount;
        document.getElementById('id-latest-start-time').innerText = data.LatestStartedTime;

        // 检查服务器状态
        const statusResponse = await fetch(`/api/server/status/${serverName}`);
        const statusData = await statusResponse.json();

        const buttonServer = document.getElementById('button-server');
        if (statusData.status === 'starting') {
            buttonServer.innerText = '停止服务器';
            buttonServer.onclick = function() { stopServer(serverName); };
        } else {
            buttonServer.innerText = '启动服务器';
            buttonServer.onclick = function() { startServer(serverName); };
        }

        // 获取在线玩家列表
        fetchOnlinePlayers(serverName);

        // 获取封禁玩家列表
        getBannedPlayers(serverName);

        // 获取白名单列表
        getWhiteList(serverName);

        // 获取历史玩家列表
        fetchHistoryPlayers(serverName)

        // 建立WebSocket连接获取终端消息
        setupTerminalWebSocket(serverName);
    } catch (error) {
        console.error('获取服务器信息失败:', error);
        alert('无法获取服务器信息');
    }
}

// 获取最新服务器信息
async function fetchLatestServerInfo() {
    try {
        const response = await fetch(`/api/server/latest`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        document.getElementById('id-name').innerText = data.name;
        document.getElementById('id-version').innerText = data.version;
        document.getElementById('id-size').innerText = data.size;
        document.getElementById('id-start-counts').innerText = data.startCount;
        document.getElementById('id-latest-start-time').innerText = data.LatestStartedTime;
    } catch (error) {
        console.error('获取最新服务器信息失败:', error);
        alert('无法获取服务器信息');
    }
}

// 获取程序版本
async function fetchProgramVersion() {
    try {
        const response = await fetch('/api/program/version');
        const data = await response.json();

        const versionElement = document.getElementById('program-version') ||
                                document.getElementById('version');

        if (versionElement) {
            versionElement.textContent = data.version || '未知版本';
        }
    } catch (error) {
        console.error('获取程序版本失败:', error);
        const errorElement = document.querySelector('.error-message');
        if (errorElement) {
            errorElement.style.display = 'block';
        }
    }
}

// 全局AJAX错误处理
function handleAjaxError(response) {
    if (response.status === 401) {
        // 未授权，跳转到登录页面
        window.location.href = '/login';
        return true;
    }
    return false;
}

// 启动服务器
async function startServer(serverName) {
    document.getElementById('button-server').innerText = '启动中...';

    try {
        const response = await fetch(`/api/server/${serverName}/start`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // 添加AJAX标识头
            }
        });

    // 切换历史玩家上拉框
    function toggleHistoryPlayersDropdown(serverName) {
        const dropdownContent = document.getElementById(`history-players-content-${serverName}`);
        const dropdownToggle = document.querySelector(`[onclick="toggleHistoryPlayersDropdown('${serverName}')"] .dropdown-toggle`);

        if (dropdownContent.style.display === 'none') {
            dropdownContent.style.display = 'block';
            dropdownToggle.style.transform = 'rotate(180deg)';
        } else {
            dropdownContent.style.display = 'none';
            dropdownToggle.style.transform = 'rotate(0deg)';
        }
    }

        // 检查401错误
        if (handleAjaxError(response)) return;

        const data = await response.json();

        const buttonServer = document.getElementById('button-server');
        if (data.status === 'starting') {
            buttonServer.innerText = '停止服务器';
            buttonServer.onclick = function() { stopServer(serverName); };
        } else if (data.error) {
            document.getElementById('button-server').innerText = '启动服务器';
            alert('启动服务器失败');
        }
    } catch (error) {
        console.error('启动服务器失败:', error);
        document.getElementById('button-server').innerText = '启动服务器';
        alert('启动服务器失败');
    }
}

// 停止服务器
async function stopServer(serverName) {
    document.getElementById('button-server').innerText = '停止中...';

    try {
        const response = await fetch(`/api/server/${serverName}/stop`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'  // 添加AJAX标识头
            }
        });

        // 检查401错误
        if (handleAjaxError(response)) return;

        const data = await response.json();

        const buttonServer = document.getElementById('button-server');
        if (data.status === 'stopped') {
            buttonServer.innerText = '启动服务器';
            buttonServer.onclick = function() { startServer(serverName); };
        } else if (data.error) {
            document.getElementById('button-server').innerText = '停止服务器';
            alert('停止服务器失败');
        }
    } catch (error) {
        console.error('停止服务器失败:', error);
        document.getElementById('button-server').innerText = '停止服务器';
        alert('停止服务器失败');
    }
}

async function ChartImage(serverName) {
    try {
        setTimeout(function () {
            window.location.href = `/server/${serverName}/storage_chart`;
        }, 0);
    } catch (error) {
        console.error('获取图表失败:', error);
        alert('获取图表失败');
    }
}

// 下载服务器函数
function downloadServer(serverName) {
    console.log(`下载服务器信息列表: ${serverName}`);
    fetch(`/api/server/info/${serverName}/excel`, { method: 'POST' })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${serverName}.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error(`下载服务器信息列表失败: ${serverName}`, error);
        })
}

// 下载所有服务器函数
function downloadAllServers(serverList) {
    console.log('下载所有服务器信息列表:', serverList);
    fetch('api/server/list/excel', { method: 'POST' })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'AllServerInfo.xlsx';
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('下载所有服务器信息列表失败:', error);
        })
}

// 创建服务器函数
function createServer() {
    // 这里打开页面创建服务器
    window.open('/server/create');
}

function changeServerProperties(serverName){
    window.open('/server/settings/'+serverName);
}

// 删除服务器函数
async function deleteServer(serverName) {
    try{
        if (confirm(`确定要删除服务器 "${serverName}" 吗？此操作不可撤销！`)) {
            // 显示加载状态
            const deleteBtn = document.querySelector(`.delete-btn[onclick*="${serverName}"]`);
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                deleteBtn.style.pointerEvents = 'none';
            }

            const response = await fetch(`/api/server/delete/${serverName}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  // 添加AJAX标识头
                }
            });

            // 检查401错误
            if (handleAjaxError(response)){
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                return;
            }

            const data = await response.json();

            if (data.status === 'deleted') {
                // 只刷新服务器卡片区域，不重建按钮组
                alert('删除服务器成功');
                refreshServerCards();  // 修改点：替换为专门刷新卡片的函数
            }else if (data.error) {
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                alert('删除服务器失败');
            }
        }
    }catch (error) {
        console.error('删除服务器失败:', error);
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        alert('删除服务器失败');
    }
}

// 专门刷新服务器卡片的函数
async function refreshServerCards() {
    try {
        const response = await fetch('/api/server/list');
        const data = await response.json();
        const serverList = document.getElementById('server-list-container');

        if (data.error) {
            console.error(data.error);
            return;
        }

        const serverListData = data.serverlist || [];
        if (serverListData.length === 0) {
            serverList.innerHTML = '<p>没有可用的服务器。</p>';
            return;
        }

        // 只更新卡片区域，不重建按钮组
        const serverElements = serverListData.map(server => `
            <div class="server-card">
                <!-- 删除按钮 -->
                <div class="delete-btn" onclick="deleteServer('${server}'); event.stopPropagation();">
                    <i class="fas fa-trash-alt"></i>
                </div>
                <div class="server-card-content" onclick="loadContent('server_info', '${server}')">
                    <h3>${server}</h3>
                    <div class="server-card-info">
                        <div>
                            <span>在线人数</span>
                            <span id="online-player-${server}">加载中...</span>
                        </div>
                        <div>
                            <span>版本</span>
                            <span id="version-${server}">加载中...</span>
                        </div>
                        <div>
                            <span>大小</span>
                            <span id="size-${server}">加载中...</span>
                        </div>
                    </div>
                </div>
            </div>
        `);

        serverList.innerHTML = serverElements.join('');

        // 异步加载每个服务器的详细信息
        serverListData.forEach(server => {
            fetchServerBasicInfo(server);
            fetchServerPlayerInfo(server);
        });
    } catch (error) {
        console.error('刷新服务器卡片失败:', error);
    }
}

// 获取设置数据
async function fetchSettings() {
    try {
        const response = await fetch('/api/program/get/settings');
        const settings = await response.json();

        console.log(settings);

        // 填充表单数据
        document.getElementById('min-memory').value = settings.min_memory || '';
        document.getElementById('max-memory').value = settings.max_memory || '';
        document.getElementById('nogui-enabled').checked = settings.nogui_enabled || false;
        document.getElementById('eula-wait-time').value = settings.eula_wait_time || '';
        document.getElementById('auto-start').checked = settings.auto_start || false;
        document.getElementById('update-source').value = settings.update_source || 'Github';
        document.getElementById('test-versions').checked = settings.test_versions || false;
        document.getElementById('storage-update-time').value = settings.storage_update_time || '';
        document.getElementById('server-port').value = settings.server_port || '';

        // 添加表单提交事件
        document.getElementById('settings-form').addEventListener('submit', async (e) => {
            e.preventDefault();

            const saveBtn = document.querySelector('.save-btn');
            if (!saveBtn) return;

            const formData = {
                min_memory: document.getElementById('min-memory').value,
                max_memory: document.getElementById('max-memory').value,
                nogui_enabled: document.getElementById('nogui-enabled').checked,
                eula_wait_time: document.getElementById('eula-wait-time').value,
                auto_start: document.getElementById('auto-start').checked,
                update_source: document.getElementById('update-source').value,
                test_versions: document.getElementById('test-versions').checked,
                storage_update_time: document.getElementById('storage-update-time').value,
                server_port: document.getElementById('server-port').value
            };

            console.log('提交表单数据:', formData);

            // 转换数字字段，空字符串转为0
            const numberFields = ['min_memory', 'max_memory', 'eula_wait_time', 'server_port'];
            numberFields.forEach(field => {
                const value = formData[field];
                if (value === '') {
                    formData[field] = 0;
                } else {
                    const num = parseInt(value, 10);
                    formData[field] = isNaN(num) ? 0 : num;
                }
            });

            try {
                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.textContent = '保存中...';
                }

                const response = await fetch('/api/program/set/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                // 检查响应是否为JSON
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('无效的响应格式');
                }

                const result = await response.json();
                if (result.success) {
                    alert('设置保存成功！');
                    location.href = '/';
                } else {
                    alert(`保存失败: ${result.error || '未知错误'}`);
                }
            } catch (error) {
                console.error('保存设置失败:', error);
                alert('保存设置失败: ' + error.message);
            } finally {
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = '保存设置';
                }
            }
        });
    } catch (error) {
        console.error('获取设置失败:', error);
        alert('无法加载设置，请刷新页面重试');
    }
}


// 获取在线玩家列表
async function fetchOnlinePlayers(serverName) {
    try {
        const response = await fetch(`/api/server/players/${serverName}`);
        const data = await response.json();
        const playerList = document.getElementById(`player-list-${serverName}`);
        if (!playerList) return;

        if (data.error || !data.players[2] || data.players[2].length === 0) {
            // 当没有玩家时，显示提示信息
            playerList.innerHTML = '<p>服务器没有玩家</p>';
            return;
        }

        // 假设data.players是一个玩家名字数组
        const players = data.players[2];
        if (players == '') {
            playerList.innerHTML = '<p>服务器没有玩家</p>';
            return;
        }

        let playerHtml = '';
        players.forEach(player => {
            playerHtml += `
                <div class="player-card">
                    <span class="player-name">${player}</span>
                    <div class="player-actions">
                        <button onclick="kickPlayer('${serverName}', '${player}')">踢出</button>
                        <button onclick="banPlayer('${serverName}', '${player}')">封禁</button>
                    </div>
                </div>
            `;
        });
        playerList.innerHTML = playerHtml;
    } catch (error) {
        console.error('获取在线玩家失败:', error);
    }
}

// 切换玩家操作按钮的显示状态
function togglePlayerActions(iconElement) {
    const playerCard = iconElement.closest('.player-card');
    const actions = playerCard.querySelector('.player-actions');
    if (actions.style.display === 'none' || actions.style.display === '') {
        actions.style.display = 'block';
        iconElement.textContent = '▲'; // 切换图标为向上箭头
    } else {
        actions.style.display = 'none';
        iconElement.textContent = '▼'; // 切换图标为向下箭头
    }
}

// 通过API请求发送命令
function kickPlayer(serverName, playerName) {
    if (confirm(`确定要踢出玩家 ${playerName} 吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `kick ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功踢出: ${data.message}`);
                setTimeout(() => {
                    fetchOnlinePlayers(serverName);
                    getBannedPlayers(serverName);
                }, 8000);
            } else {
                alert(`踢出玩家失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('踢出玩家失败:', error);
            alert('踢出玩家失败，请检查日志');
        });
    }
}

function banPlayer(serverName, playerName) {
    if (confirm(`确定要封禁玩家 ${playerName} 吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `ban ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功封禁: ${data.message}`);
                // 刷新在线玩家列表和封禁玩家列表
                getBannedPlayers(serverName);
                setTimeout(() => {
                    fetchOnlinePlayers(serverName);
                }, 8000);
            } else {
                alert(`封禁玩家失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('封禁玩家失败:', error);
            alert('封禁玩家失败，请检查日志');
        });
    }
}

function pardonPlayer(serverName, playerName) {
    if (confirm(`确定要解封玩家 ${playerName} 吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `pardon ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功解封: ${data.message}`);
                // 刷新在线玩家列表和封禁玩家列表
                getBannedPlayers(serverName);
                setTimeout(() => {
                    fetchOnlinePlayers(serverName);
                }, 8000);
            } else {
                alert(`解封玩家失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('解封玩家失败:', error);
            alert('解封玩家失败，请检查日志');
        });
    }
}


function getBannedPlayers(serverName) {
    fetch(`/api/server/get/banned/players/${serverName}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const bannedPlayersList = data.BannedPlayerList || [];
            const bannedPlayersContainer = document.getElementById(`banned-players-${serverName}`);

            if (bannedPlayersList.length === 0) {
                bannedPlayersContainer.innerHTML = '<p>没有被封禁的玩家</p>';
                return;
            }

            // 动态生成封禁玩家卡片
            let playerHtml = '';
            bannedPlayersList.forEach(player => {
                playerHtml += `
                    <div class="player-card">
                        <span class="player-name">${player}</span>
                        <div class="player-actions">
                            <button onclick="pardonPlayer('${serverName}', '${player}')">解封</button>
                        </div>
                    </div>
                `;
            });

            bannedPlayersContainer.innerHTML = playerHtml;
        } else {
            console.error('获取封禁玩家列表失败:', data.error);
            document.getElementById(`banned-players-${serverName}`).innerHTML = '<p>获取封禁玩家列表失败</p>';
        }
    })
    .catch(error => {
        console.error('获取封禁玩家列表失败:', error);
        document.getElementById(`banned-players-${serverName}`).innerHTML = '<p>获取封禁玩家列表失败</p>';
    });
}

function getWhiteList(serverName) {
    fetch(`/api/server/get/white-list/${serverName}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const whiteListPlayersList = data.WhiteList || [];
            const whiteListPlayersContainer = document.getElementById(`whitelist-players-${serverName}`);

            if (whiteListPlayersList.length === 0) {
                whiteListPlayersContainer.innerHTML = '<p>没有在白名单中的玩家</p>';
                return;
            }

            let playerHtml = '';
            whiteListPlayersList.forEach(player => {
                playerHtml += `
                    <div class="player-card">
                        <span class="player-name">${player}</span>
                        <div class="player-actions">
                            <button onclick="removeFromWhiteList('${serverName}', '${player}')">移出白名单</button>
                        </div>
                    </div>
                `;
            });

            whiteListPlayersContainer.innerHTML = playerHtml;
        } else {
            document.getElementById(`whitelist-players-${serverName}`).innerHTML = '<p>白名单未启用</p>';
        }
    })
    .catch(error => {
        console.error('获取白名单玩家列表失败:', error);
        document.getElementById(`whitelist-players-${serverName}`).innerHTML = '<p>获取白名单玩家列表失败</p>';
    });
}

function addToWhiteList(serverName, playerName) {
    if (confirm(`确定要添加玩家 ${playerName} 到白名单吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `whitelist add ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功添加到白名单: ${data.message}`);
                // 刷新白名单玩家列表
                getWhiteList(serverName);
            }else{
                alert(`添加玩家失败: ${data.error || '未知错误'}`);
            }
        })
    }
}

function removeFromWhiteList(serverName, playerName) {
    if (confirm(`确定要移出玩家 ${playerName} 白名单吗？`)) {
        fetch(`/api/server/${serverName}/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: `whitelist remove ${playerName}` })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`玩家 ${playerName} 已被成功移出白名单: ${data.message}`);
                // 刷新白名单玩家列表
                getWhiteList(serverName);
            }else{
                alert(`移出玩家失败: ${data.error || '未知错误'}`);
            }
        })
    }
}

// 切换历史玩家下拉框显示状态
function toggleHistoryPlayersDropdown(serverName) {
    const content = document.getElementById(`history-players-content-${serverName}`);
    const toggleIcon = document.querySelector(`#history-players-content-${serverName}`).previousElementSibling.querySelector('.dropdown-toggle');
    if (content.style.display === 'none' || content.style.display === '') {
        content.style.display = 'block';
        toggleIcon.textContent = '▲'; // 切换图标为向上箭头
    } else {
        content.style.display = 'none';
        toggleIcon.textContent = '▼'; // 切换图标为向下箭头
    }
}

// 获取历史玩家列表
async function fetchHistoryPlayers(serverName) {
    const contentDiv = document.getElementById(`history-players-content-${serverName}`);
    if (!contentDiv) return;

    try {
        const response = await fetch(`/api/server/get/history/players/${serverName}`);
        const data = await response.json();

        if (data.error) {
            contentDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
            return;
        }

        const players = data.HistoryPlayerList || [];
        if (players.length === 0) {
            contentDiv.innerHTML = '<p>没有历史玩家记录</p>';
            return;
        }

        let playerHtml = '';
        players.forEach(player => {
            playerHtml += `
                <div class="player-card">
                    <span class="player-name">${player}</span>
                    <div class="player-actions">
                        <button onclick="addToWhiteList('${serverName}', '${player}')">加入白名单</button>
                    </div>
                </div>
            `;
        });
        contentDiv.innerHTML = playerHtml;
    } catch (error) {
        console.error('获取历史玩家失败:', error);
        contentDiv.innerHTML = '<p style="color: red;">获取历史玩家失败，请稍后重试。</p>';
    }
}

// 建立连接获取终端消息
async function setupTerminalWebSocket(serverName) {
    // 清除该服务器已有的定时器
    if (window.terminalTimers && window.terminalTimers[serverName]) {
        clearInterval(window.terminalTimers[serverName]);
    }

    const terminalOutput = document.getElementById(`terminal-output-${serverName}`);
    if (!terminalOutput) return;

    // 保持最大行数的函数
    function keepMaxLines() {
        const maxLines = 1000;
        while (terminalOutput.childElementCount > maxLines) {
            terminalOutput.removeChild(terminalOutput.firstChild);
        }
    }

    // 存储最后获取的日志快照
    let lastLogsSnapshot = [];

    // 异步获取日志
    const fetchLogs = async () => {
        try {
            const response = await fetch(`/api/server/terminal/${serverName}`);
            const data = await response.json();

            if (data.success) {
                const newLogs = Array.isArray(data.logs) ? data.logs : data.logs.split('\n');
                const diffLogs = getNewLogs(lastLogsSnapshot, newLogs);

                // 先更新快照再追加日志
                lastLogsSnapshot = newLogs.slice(-1000);

                diffLogs.forEach(log => {
                    const div = document.createElement('div');
                    div.textContent = log;
                    terminalOutput.appendChild(div);
                });

                keepMaxLines(); // 新增行数限制
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
        } catch (error) {
            console.error('获取终端日志失败:', error);
        }
    };

    // 差异对比方法
    function getNewLogs(prevLogs, newLogs) {
        if (!prevLogs.length || !newLogs.length) return newLogs;
        const firstMismatch = newLogs.findIndex((log, index) =>
            index >= prevLogs.length || log !== prevLogs[index]
        );
        return firstMismatch === -1 ? [] : newLogs.slice(firstMismatch);
    }

    // 初始获取日志
    await fetchLogs();

    // 定时器, 每3秒获取一次日志
    const intervalId = setInterval(async () => {
        await fetchLogs();
    }, 3000);

    // 保存定时器 ID 以便后续清除
    if (!window.terminalTimers) {
        window.terminalTimers = {};
    }
    window.terminalTimers[serverName] = intervalId;
}

// 发送命令
function sendCommand(serverName) {
    const commandInput = document.getElementById(`command-input-${serverName}`);
    const command = commandInput.value.trim();
    if (!command) return;

    fetch(`/api/server/terminal/${serverName}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ command })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const terminalOutput = document.getElementById(`terminal-output-${serverName}`);
            if (terminalOutput) {
                terminalOutput.innerHTML += `<div style="color: #4CAF50;">&gt; ${command}</div>`;
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('发送命令失败:', error);
        alert('发送命令失败，请检查日志');
    });

    // 清空输入框
    commandInput.value = '';
}

// 全局定时器对象
let CpuRamDiskTimers = {
    cpu: null,
    ram: null,
    disk: null
};

// 获取CPU、内存和磁盘使用率
function fetchCpuRamDiskUsage() {
    const cpuChart = document.getElementById('cpu-usage-chart');
    const ramChart = document.getElementById('ram-usage-chart');
    const diskChart = document.getElementById('disk-usage-chart');

    if (!cpuChart || !ramChart || !diskChart) {
        console.error('图表容器未找到，等待500ms重试...');
        setTimeout(fetchCpuRamDiskUsage, 500);
        return;
    }

    // 初始化CPU图表
    fetchCpuUsage();
    // 初始化内存图表
    fetchRamUsage();
    // 初始化磁盘图表
    fetchDiskUsage();
}

// 获取CPU使用率
async function fetchCpuUsage() {
    try {
        const response = await fetch('/api/program/get/CPU/Usage');
        const data = await response.json();

        // 动态加载ECharts库
        if (typeof echarts === 'undefined') {
            if (!window.echartsLoading) {
                window.echartsLoading = true;
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js';
                script.onload = () => {
                    window.echartsLoading = false;
                    initCpuUsageChart(data.used, data.total);
                };
                script.onerror = () => {
                    window.echartsLoading = false;
                    console.error('加载ECharts库失败');
                    const chartDom = document.getElementById('cpu-usage-chart');
                    if (chartDom) chartDom.innerHTML = '图表库加载失败';
                };
                document.head.appendChild(script);
            }
        } else {
            initCpuUsageChart(data.used, data.total, data.abs_used, data.abs_total);
        }

        CpuRamDiskTimers.cpu = setTimeout(fetchCpuUsage, 5000);
    } catch (error) {
        console.error('获取CPU使用率失败:', error);
        const chartDom = document.getElementById('cpu-usage-chart');
        if (chartDom) chartDom.innerHTML = '数据获取失败';
    }
}

// 获取内存使用率
async function fetchRamUsage() {
    try {
        const response = await fetch('/api/program/get/RAM/Usage');
        const data = await response.json();

        // 动态加载ECharts库
        if (typeof echarts === 'undefined') {
            if (!window.echartsLoading) {
                window.echartsLoading = true;
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js';
                script.onload = () => {
                    window.echartsLoading = false;
                    initRamUsageChart(data.used, data.total);
                };
                script.onerror = () => {
                    window.echartsLoading = false;
                    console.error('加载ECharts库失败');
                    const chartDom = document.getElementById('ram-usage-chart');
                    if (chartDom) chartDom.innerHTML = '图表库加载失败';
                };
                document.head.appendChild(script);
            }
        } else {
            initRamUsageChart(data.used, data.total, data.abs_used, data.abs_total);
        }

        CpuRamDiskTimers.ram = setTimeout(fetchRamUsage, 5000);
    } catch (error) {
        console.error('获取内存使用率失败:', error);
        const chartDom = document.getElementById('ram-usage-chart');
        if (chartDom) chartDom.innerHTML = '数据获取失败';
    }
}

// 初始化CPU图表
function initCpuUsageChart(used, total, abs_used, abs_total) {
    const chartDom = document.getElementById('cpu-usage-chart');
    if (!chartDom) return;

    const chart = echarts.init(chartDom);

    const option = {
        tooltip: {
            formatter: '{b}'
        },
        graphic: [{
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
                text: `${((used)).toFixed(1)}%`,
                textAlign: 'center',
                fill: '#67afdfff',
                fontSize: 20,
                fontWeight: 'bold'
            }
        }],
        series: [{
            type: 'pie',
            radius: ['60%', '80%'],
            data: [
                { value: used, name: '已使用:' + used.toFixed(2) + '%', itemStyle: { color: '#36a3eb' } },
                { value: 100 - used, name: '未使用:' + (100 - used).toFixed(2) + '%', itemStyle: { color: '#a2c2fcff' } }
            ]
        }]
    };
    chart.setOption(option);

    // 更新统计信息
    document.getElementById('cpu-used').textContent = `${abs_used} MHz`;
    document.getElementById('cpu-total').textContent = `${abs_total} MHz`;
}

// 初始化内存图表
function initRamUsageChart(used, total, abs_used, abs_total) {
    const chartDom = document.getElementById('ram-usage-chart');
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    const option = {
        tooltip: {
            formatter: '{b}'
        },
        graphic: [{
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
                text: `${((abs_used / abs_total) * 100).toFixed(1)}%`,
                textAlign: 'center',
                fill: '#67afdfff',
                fontSize: 20,
                fontWeight: 'bold'
            }
        }],
        series: [{
            type: 'pie',
            radius: ['60%', '80%'],
            data: [
                { value: abs_used, name: '已使用:' + abs_used.toFixed(2) + 'MB', itemStyle: { color: '#36a3eb' } },
                { value: abs_total - abs_used, name: '未使用:' + (abs_total).toFixed(2) + 'MB', itemStyle: { color: '#a2c2fcff' } }
            ]
        }]
    };
    chart.setOption(option);

    // 更新统计信息
    document.getElementById('ram-used').textContent = `${abs_used} MB`;
    document.getElementById('ram-total').textContent = `${abs_total} MB`;
}

// 获取磁盘使用率
async function fetchDiskUsage() {
    try {
        const response = await fetch('/api/program/disk_usage');
        const data = await response.json();

        if (data.error) {
            console.error('获取磁盘使用率失败:', data.error);
            showChartError();
            return;
        }

        // 动态加载 ECharts 库（如果未加载）
        if (typeof echarts === 'undefined') {
            // 防止重复加载
            if (!window.echartsLoading) {
                window.echartsLoading = true;
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js';
                script.onload = () => {
                    window.echartsLoading = false;
                    initDiskUsageChart(data.disk_usage, data.disk_free, data.usage, data.free);
                };
                script.onerror = () => {
                    window.echartsLoading = false;
                    console.error('加载ECharts库失败');
                    showChartError();
                };
                document.head.appendChild(script);
            }
        } else {
            // 初始化 ECharts 图表
            initDiskUsageChart(data.disk_usage, data.disk_free, data.usage, data.free);
        }

        CpuRamDiskTimers.disk = setTimeout(fetchDiskUsage, 5000);
    } catch (error) {
        console.error('获取磁盘使用率失败:', error);
        showChartError();
    }
}

// 初始化磁盘使用率图表
function initDiskUsageChart(usedPercent, freePercent, used, free) {
    const chartDom = document.getElementById('disk-usage-chart');
    if (!chartDom) return;

    const chart = echarts.init(chartDom);
    const option = {
        tooltip: {
            formatter: '{b}: {c}%'
        },
        graphic: [{
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
                text: (usedPercent) + '%',
                textAlign: 'center',
                fill: '#67afdfff',
                fontSize: 20,
                fontWeight: 'bold'
            }
        }],
        series: [{
            type: 'pie',
            radius: ['60%', '80%'],
            data: [
                {
                    value: usedPercent,
                    name: `已使用: ${used} GB
                            已使用`,
                    itemStyle: { color: '#386ffcff' }
                },
                {
                    value: freePercent,
                    name: `未使用: ${free} GB
                            未使用`,
                    itemStyle: { color: '#a2c2fcff' },
                }
            ]
        }]
    };
    chart.setOption(option);

    // 更新统计信息
    document.getElementById('disk-used').textContent = `${used} GB`;
    document.getElementById('disk-total').textContent = `${free + used} GB`;
}

// 显示图表错误状态
function showChartError() {
    const chartDom = document.getElementById('disk-usage-chart');
    if (chartDom) {
        chartDom.innerHTML = `
            <div style="text-align:center; padding:40px 0; color:#e74c3c;">
                <i class="fas fa-exclamation-triangle"></i>
                <p>获取数据失败</p>
            </div>
        `;
    }
>>>>>>> 95e86289eb46f54ed8b7cff04029780dc0b25b16
}
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

    servers: `
        <div class="servers-content">
            <h1>服务器列表</h1>
            <!-- ECharts 容器 -->
            <div id="disk-usage-chart" style="width: 200px; height: 200px; margin: 20px auto;"></div>
            <div id="usage-font" style="margin: auto"> 磁盘使用率 </div>
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
                    <h1>暂未开发完成</h1>
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
                fetchDiskUsage();  // 获取磁盘使用率
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
            name: '磁盘使用率',
            type: 'pie',
            radius: ['60%', '80%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 0,
                borderColor: '#ffffffff',
                borderWidth: 2
            },
            label: {
                show: false
            },
            emphasis: {
                label: {
                    show: false
                }
            },
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

// 建立连接获取终端消息
function setupTerminalWebSocket(serverName) {
    const terminalOutput = document.getElementById(`terminal-output-${serverName}`);
    if (!terminalOutput) return;

    // 定时获取日志
    const fetchLogs = () => {
        fetch(`/api/server/terminal/${serverName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    terminalOutput.innerHTML += `<div>${data.logs}</div>`;
                    terminalOutput.scrollTop = terminalOutput.scrollHeight;
                } else {
                    terminalOutput.innerHTML += `<div style="color: red;">${data.error}</div>`;
                }
            })
            .catch(error => {
                console.error('获取终端日志失败:', error);
                terminalOutput.innerHTML += '<div style="color: red;">获取终端日志失败</div>';
            });
    };

    // 初始获取日志
    fetchLogs();
    // 每 5 秒获取一次日志，可根据需求调整间隔时间
    const intervalId = setInterval(fetchLogs, 5000);

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

// 存储每个服务器最后一次获取的日志最大 ID
const lastLogIds = {};

// 定时获取终端日志
function setupTerminalPolling(serverName) {
    const terminalOutput = document.getElementById(`terminal-output-${serverName}`);
    if (!terminalOutput) return;

    const intervalId = setInterval(() => {
        fetch(`/api/server/terminal/${serverName}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const logs = data.logs;
                    const lastLogId = lastLogIds[serverName] || 0;
                    // 过滤出 ID 大于 lastLogId 的新日志
                    const newLogs = logs.filter(log => log.id > lastLogId);
                    if (newLogs.length > 0) {
                        newLogs.forEach(log => {
                            // 使用 white-space: pre-wrap 样式保留换行符和空白符
                            const logDiv = document.createElement('div');
                            logDiv.style.whiteSpace = 'pre-wrap';
                            // 替换特殊字符为换行符
                            const formattedMessage = log.message.replace(/\\n/g, '\n');
                            logDiv.textContent = formattedMessage;
                            terminalOutput.appendChild(logDiv);
                        });
                        // 自动滚动到底部
                        terminalOutput.scrollTop = terminalOutput.scrollHeight;
                        // 更新最后一次获取的日志最大 ID
                        const maxLogId = newLogs.reduce((max, log) => Math.max(max, log.id), lastLogId);
                        lastLogIds[serverName] = maxLogId;
                    }
                }
            })
            .catch(error => {
                console.error('获取终端日志失败:', error);
                const errorDiv = document.createElement('div');
                errorDiv.style.color = 'red';
                errorDiv.style.whiteSpace = 'pre-wrap';
                errorDiv.textContent = '获取终端日志失败';
                terminalOutput.appendChild(errorDiv);
                // 自动滚动到底部
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            });
    }, 1000); // 每秒轮询一次

    // 保存定时器 ID 以便后续清理
    window.terminalIntervals = window.terminalIntervals || {};
    window.terminalIntervals[serverName] = intervalId;
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
        body: JSON.stringify({ command: command })
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
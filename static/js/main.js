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
                        <td>/login</td>
                        <td>登录界面</td>
                    </tr>
                    <tr>
                        <td>/api/server/{string:server_name}/start</td>
                        <td>启动服务器</td>
                    </tr>
                    <tr>
                        <td>/api/server/{string:server_name}/storage_chart</td>
                        <td>服务器存储占用大小变化图表</td>
                    </tr>
                    <tr>
                        <td>/api/server/{string:server_name}/storage_info</td>
                        <td>服务器存储占用大小变化信息</td>
                    </tr>
                    <tr>
                        <td>/api/program</td>
                        <td>这是API Program的首页</td>
                    </tr>
                    <tr>
                        <td>/api/program/version</td>
                        <td>程序版本</td>
                    </tr>
                </tbody>
            </table>
        </div>
    `,

    servers: `
        <div class="servers-content">
            <h1>服务器列表</h1>
            <div class="server-container" id="server-list-container">
                <div class="loading">加载中...</div>
            </div>
        </div>
    `,

    server_info: (serverName) => `
        <div class="server-info-content">
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
                <button id="button-server" onclick="startServer('${serverName}')">启动服务器</button>
                <button id="storage-chart" onclick="ChartImage('${serverName}')">存储占用</button>
                <button class="download-btn" onclick="downloadServer('${serverName}')">
                    <i class="fas fa-file-download"></i>下载服务器信息
                </button>
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
            <!-- 添加设置表单 -->
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

// 获取服务器列表卡片 - 优化版本
async function fetchServerList() {
    try {
        fetch('/api/server/list')
            .then(response => response.json())
            .then(data => {
                const serverList = document.getElementById('server-list-container');
                serverList.innerHTML = ''; // 清空加载中的提示

                if (data.error) {
                    serverList.innerHTML = `<p style="color: red;">${data.error}</p>`;
                    return;
                }

                const serverListData = data.serverlist || [];
                if (serverListData.length === 0) {
                    serverList.innerHTML = '<p>没有可用的服务器。</p>';
                    return;
                }

                // 在服务器列表容器前添加下载按钮
                const downloadAllBtn = document.createElement('button');
                downloadAllBtn.className = 'download-btn';
                downloadAllBtn.innerHTML = '<i class="fas fa-file-download"></i>下载所有服务器信息';
                downloadAllBtn.onclick = function() {
                    downloadAllServers(serverListData);
                };
                serverList.parentNode.insertBefore(downloadAllBtn, serverList);

                const serverElements = serverListData.map(server => `
                    <div class="server-card">
                        <div class="server-card-content" onclick="loadContent('server_info', '${server}')">
                            <h3>${server}</h3>
                            <div class="server-card-info">
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
                });
            })
            .catch(error => {
                console.error('获取服务器列表时出错:', error);
                document.getElementById('server-list-container').innerHTML = '<p style="color: red;">获取服务器列表失败，请稍后重试。</p>';
            });
    } catch (error) {
        console.error('获取服务器列表失败:', error);
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

        if (statusData.status === 'starting') {
            document.getElementById('button-group').innerHTML = '<button id="button-server" onclick="stopServer(\'' + serverName + '\')">停止服务器</button>';
            document.getElementById('button-group').innerHTML = '<button id="storage-server" onclick="ChartImage(\'' + serverName + '\')">存储占用</button>';
        }
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

// 启动服务器
async function startServer(serverName) {
    document.getElementById('button-server').innerText = '启动中...';

    try {
        const response = await fetch(`/api/server/${serverName}/start`, { method: 'POST' });
        const data = await response.json();

        if (data.status === 'starting') {
            document.getElementById('button-group').innerHTML = '<button id="button-server" onclick="stopServer(\'' + serverName + '\')">停止服务器</button>';
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
        const response = await fetch(`/api/server/${serverName}/stop`, { method: 'POST' });
        const data = await response.json();

        if (data.status === 'stopped') {
            document.getElementById('button-group').innerHTML = '<button id="button-server" onclick="startServer(\'' + serverName + '\')">启动服务器</button>';
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
            window.location.href = `/api/server/${serverName}/storage_chart`;
        }, 0);
    } catch (error) {
        console.error('获取图表失败:', error);
        alert('获取图表失败');
    }
}

// 下载服务器函数（由用户实现具体逻辑）
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

// 下载所有服务器函数（由用户实现具体逻辑）
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

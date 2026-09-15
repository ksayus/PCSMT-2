// 全局变量 - 从服务端变量初始化
let leftPanelPath = window.SERVER_PATH;
let rightPanelPath = window.SERVER_PATH;
let leftSelectedFiles = new Set();
let rightSelectedFiles = new Set();

console.log('服务器路径:', leftPanelPath);
console.log('服务器名称:', window.SERVER_NAME);

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadLeftPanel();
    loadRightPanel();
});

// 加载左侧面板
async function loadLeftPanel() {
    await loadDirectoryTree('left');
    await loadFileList('left', leftPanelPath);
    updatePanelPath('left', leftPanelPath);
}

// 加载右侧面板
async function loadRightPanel() {
    await loadDirectoryTree('right');
    await loadFileList('right', rightPanelPath);
    updatePanelPath('right', rightPanelPath);
}

// 加载目录树
async function loadDirectoryTree(panel) {
    try {
        const path = panel === 'left' ? leftPanelPath : rightPanelPath;
        const response = await fetch('/api/get/directory?path=' + encodeURIComponent(path));
        const data = await response.json();

        if (response.ok) {
            renderDirectoryTree(panel, data.CurrentDirectory, path);
        } else {
            console.error('加载' + panel + '面板目录树失败:', data.error);
        }
    } catch (error) {
        console.error('加载' + panel + '面板目录树时发生错误:', error);
    }
}

// 渲染目录树
function renderDirectoryTree(panel, directories, basePath) {
    const treeContainer = document.getElementById(panel + '-directory-tree');
    treeContainer.innerHTML = '';

    directories.forEach(function(dir) {
        const dirPath = basePath.replace(/\\/g, '/') + '/' + dir;
        const item = document.createElement('div');
        item.className = 'directory-item';
        item.innerHTML =
            '<i class="fas fa-folder" style="color: #ffa500; margin-right: 5px;"></i>' +
            '<span onclick="navigateToDirectory(\'' + panel + '\', \'' + dirPath + '\')">' + dir + '</span>';
        treeContainer.appendChild(item);
    });
}

// 导航到目录
function navigateToDirectory(panel, path) {
    if (panel === 'left') {
        leftPanelPath = path;
        loadLeftPanel();
    } else {
        rightPanelPath = path;
        loadRightPanel();
    }
}

// 加载文件列表
async function loadFileList(panel, path) {
    try {
        const response = await fetch('/api/get/directory?path=' + encodeURIComponent(path));
        const data = await response.json();

        if (response.ok) {
            renderFileList(panel, data.CurrentDirectory, path);
            document.getElementById(panel + '-file-count').textContent = data.FilesCounts + ' 个项目';
        } else {
            console.error('加载' + panel + '面板文件列表失败:', data.error);
        }
    } catch (error) {
        console.error('加载' + panel + '面板文件列表时发生错误:', error);
    }
}

// 渲染文件列表
function renderFileList(panel, files, path) {
    const fileList = document.getElementById(panel + '-file-list');
    fileList.innerHTML = '';

    // 添加上级目录项
    const rootPath = window.SERVER_PATH;
    if (path !== rootPath) {
        const parentItem = createFileItem(panel, '..', 'directory', path.split('/').slice(0, -1).join('/'), true);
        fileList.appendChild(parentItem);
    }

    files.forEach(function(file) {
        const filePath = path + '/' + file;
        const isDirectory = file.includes('.') ? false : true;
        const fileItem = createFileItem(panel, file, isDirectory ? 'directory' : 'file', filePath, false);
        fileList.appendChild(fileItem);
    });
}

// 创建文件项
function createFileItem(panel, name, type, path, isParent) {
    if (isParent === undefined) isParent = false;

    const item = document.createElement('div');
    item.className = 'file-item';
    item.dataset.path = path;
    item.dataset.type = type;

    const icon = type === 'directory' ? 'fa-folder' : getFileIcon(name);
    const iconColor = type === 'directory' ? '#ffa500' : '#666';

    item.innerHTML =
        '<div class="file-icon">' +
            '<i class="fas ' + icon + '" style="color: ' + iconColor + ';"></i>' +
        '</div>' +
        '<div class="file-info">' +
            '<div class="file-name">' + (isParent ? '返回上级目录' : name) + '</div>' +
            '<div class="file-details">' + (type === 'directory' ? '文件夹' : '文件') + '</div>' +
        '</div>' +
        '<div class="file-actions">' +
            (!isParent ?
                '<button onclick="renameItem(\'' + panel + '\', \'' + path + '\', \'' + name + '\')" title="重命名">' +
                    '<i class="fas fa-edit"></i>' +
                '</button>' +
                '<button onclick="deleteItem(\'' + panel + '\', \'' + path + '\', \'' + type + '\')" title="删除" style="color: #e74c3c;">' +
                    '<i class="fas fa-trash"></i>' +
                '</button>'
            : '') +
        '</div>';

    item.addEventListener('click', function(e) {
        if (!e.target.closest('.file-actions')) {
            if (type === 'directory') {
                navigateToDirectory(panel, path);
            } else {
                toggleFileSelection(panel, item);
            }
        }
    });

    return item;
}

// 获取文件图标
function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'txt': 'fa-file-alt',
        'py': 'fa-file-code',
        'js': 'fa-file-code',
        'html': 'fa-file-code',
        'css': 'fa-file-code',
        'json': 'fa-file-code',
        'xml': 'fa-file-code',
        'zip': 'fa-file-archive',
        'rar': 'fa-file-archive',
        'pdf': 'fa-file-pdf',
        'doc': 'fa-file-word',
        'docx': 'fa-file-word',
        'xls': 'fa-file-excel',
        'xlsx': 'fa-file-excel',
        'ppt': 'fa-file-powerpoint',
        'pptx': 'fa-file-powerpoint',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image',
        'png': 'fa-file-image',
        'gif': 'fa-file-image',
        'mp3': 'fa-file-audio',
        'wav': 'fa-file-audio',
        'mp4': 'fa-file-video',
        'avi': 'fa-file-video'
    };
    return iconMap[ext] || 'fa-file';
}

// 切换文件选择
function toggleFileSelection(panel, item) {
    const path = item.dataset.path;
    const selectedFiles = panel === 'left' ? leftSelectedFiles : rightSelectedFiles;

    if (selectedFiles.has(path)) {
        selectedFiles.delete(path);
        item.classList.remove('selected');
    } else {
        selectedFiles.add(path);
        item.classList.add('selected');
    }
    updateSelectedCount(panel);
}

// 更新选择计数
function updateSelectedCount(panel) {
    const selectedFiles = panel === 'left' ? leftSelectedFiles : rightSelectedFiles;
    document.getElementById(panel + '-selected-count').textContent = '已选择 ' + selectedFiles.size + ' 个项目';
}

// 更新面板路径显示
function updatePanelPath(panel, path) {
    document.getElementById(panel + '-panel-path').textContent = path;
}

// 刷新左侧面板
function refreshLeftPanel() {
    leftSelectedFiles.clear();
    updateSelectedCount('left');
    loadLeftPanel();
}

// 刷新右侧面板
function refreshRightPanel() {
    rightSelectedFiles.clear();
    updateSelectedCount('right');
    loadRightPanel();
}

// 左侧面板向上导航
function navigateLeftPanelUp() {
    const rootPath = window.SERVER_PATH;
    if (leftPanelPath !== rootPath) {
        const parentPath = leftPanelPath.split('/').slice(0, -1).join('/');
        leftPanelPath = parentPath;
        loadLeftPanel();
    }
}

// 右侧面板向上导航
function navigateRightPanelUp() {
    const rootPath = window.SERVER_PATH;
    if (rightPanelPath !== rootPath) {
        const parentPath = rightPanelPath.split('/').slice(0, -1).join('/');
        rightPanelPath = parentPath;
        loadRightPanel();
    }
}

// 复制到右侧
function copyToRight() {
    if (leftSelectedFiles.size === 0) {
        alert('请先在左侧选择要复制的文件');
        return;
    }

    const files = Array.from(leftSelectedFiles);
    const targetPath = rightPanelPath;

    if (confirm('确定要将选中的 ' + files.length + ' 个项目复制到右侧目录吗？')) {
        copyFiles(files, targetPath);
    }
}

// 移动到右侧
function moveToRight() {
    if (leftSelectedFiles.size === 0) {
        alert('请先在左侧选择要移动的文件');
        return;
    }

    const files = Array.from(leftSelectedFiles);
    const targetPath = rightPanelPath;

    if (confirm('确定要将选中的 ' + files.length + ' 个项目移动到右侧目录吗？')) {
        moveFiles(files, targetPath);
    }
}

// 复制到左侧
function copyToLeft() {
    if (rightSelectedFiles.size === 0) {
        alert('请先在右侧选择要复制的文件');
        return;
    }

    const files = Array.from(rightSelectedFiles);
    const targetPath = leftPanelPath;

    if (confirm('确定要将选中的 ' + files.length + ' 个项目复制到左侧目录吗？')) {
        copyFiles(files, targetPath);
    }
}

// 移动到左侧
function moveToLeft() {
    if (rightSelectedFiles.size === 0) {
        alert('请先在右侧选择要移动的文件');
        return;
    }

    const files = Array.from(rightSelectedFiles);
    const targetPath = leftPanelPath;

    if (confirm('确定要将选中的 ' + files.length + ' 个项目移动到左侧目录吗？')) {
        moveFiles(files, targetPath);
    }
}

// 复制文件
async function copyFiles(files, targetPath) {
    try {
        const response = await fetch('/api/manager/copy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_paths: files,
                target_path: targetPath
            })
        });

        if (response.ok) {
            alert('文件复制成功');
            refreshLeftPanel();
            refreshRightPanel();
        } else {
            alert('文件复制失败');
        }
    } catch (error) {
        console.error('复制文件时发生错误:', error);
        alert('文件复制失败');
    }
}

// 移动文件
async function moveFiles(files, targetPath) {
    try {
        const response = await fetch('/api/manager/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_paths: files,
                target_path: targetPath
            })
        });

        if (response.ok) {
            alert('文件移动成功');
            refreshLeftPanel();
            refreshRightPanel();
        } else {
            alert('文件移动失败');
        }
    } catch (error) {
        console.error('移动文件时发生错误:', error);
        alert('文件移动失败');
    }
}

// 重命名项目
function renameItem(panel, oldPath, oldName) {
    const newName = prompt('请输入新的名称:', oldName);
    if (newName && newName !== oldName) {
        const newPath = oldPath.replace(oldName, newName);
        renameItemAPI(oldPath, newPath, panel);
    }
}

// 删除项目
function deleteItem(panel, path, type) {
    const itemType = type === 'directory' ? '文件夹' : '文件';
    if (confirm('确定要删除这个' + itemType + '吗？')) {
        deleteItemAPI(path, type, panel);
    }
}

// 在左侧面板创建文件
function createFileInLeft() {
    const fileName = prompt('请输入文件名:');
    if (fileName && fileName.trim()) {
        const filePath = leftPanelPath + '/' + fileName.trim();
        createFileAPI(filePath, 'left');
    }
}

// 在左侧面板创建文件夹
function createFolderInLeft() {
    const folderName = prompt('请输入文件夹名:');
    if (folderName && folderName.trim()) {
        const folderPath = leftPanelPath + '/' + folderName.trim();
        createFolderAPI(folderPath, 'left');
    }
}

// 在右侧面板创建文件
function createFileInRight() {
    const fileName = prompt('请输入文件名:');
    if (fileName && fileName.trim()) {
        const filePath = rightPanelPath + '/' + fileName.trim();
        createFileAPI(filePath, 'right');
    }
}

// 在右侧面板创建文件夹
function createFolderInRight() {
    const folderName = prompt('请输入文件夹名:');
    if (folderName && folderName.trim()) {
        const folderPath = rightPanelPath + '/' + folderName.trim();
        createFolderAPI(folderPath, 'right');
    }
}

// 删除左侧面板选中项
function deleteSelectedInLeft() {
    if (leftSelectedFiles.size === 0) {
        alert('请先在左侧选择要删除的文件');
        return;
    }

    const files = Array.from(leftSelectedFiles);
    if (confirm('确定要删除选中的 ' + files.length + ' 个项目吗？')) {
        deleteMultipleFiles(files, 'left');
    }
}

// 删除右侧面板选中项
function deleteSelectedInRight() {
    if (rightSelectedFiles.size === 0) {
        alert('请先在右侧选择要删除的文件');
        return;
    }

    const files = Array.from(rightSelectedFiles);
    if (confirm('确定要删除选中的 ' + files.length + ' 个项目吗？')) {
        deleteMultipleFiles(files, 'right');
    }
}

// API调用函数
async function createFileAPI(filePath, panel) {
    try {
        const response = await fetch('/api/manager/create/file', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: filePath })
        });

        if (response.ok) {
            if (panel === 'left') {
                refreshLeftPanel();
            } else {
                refreshRightPanel();
            }
        } else {
            alert('创建文件失败');
        }
    } catch (error) {
        console.error('创建文件时发生错误:', error);
        alert('创建文件失败');
    }
}

async function createFolderAPI(folderPath, panel) {
    try {
        const response = await fetch('/api/manager/create/folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: folderPath })
        });

        if (response.ok) {
            if (panel === 'left') {
                refreshLeftPanel();
            } else {
                refreshRightPanel();
            }
        } else {
            alert('创建文件夹失败');
        }
    } catch (error) {
        console.error('创建文件夹时发生错误:', error);
        alert('创建文件夹失败');
    }
}

async function renameItemAPI(oldPath, newPath, panel) {
    try {
        const response = await fetch('/api/manager/rename', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ old_path: oldPath, new_path: newPath })
        });

        if (response.ok) {
            if (panel === 'left') {
                refreshLeftPanel();
            } else {
                refreshRightPanel();
            }
        } else {
            alert('重命名失败');
        }
    } catch (error) {
        console.error('重命名时发生错误:', error);
        alert('重命名失败');
    }
}

async function deleteItemAPI(path, type, panel) {
    try {
        const endpoint = type === 'directory' ? '/api/manager/delete/folder' : '/api/manager/delete/file';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: path })
        });

        if (response.ok) {
            if (panel === 'left') {
                refreshLeftPanel();
            } else {
                refreshRightPanel();
            }
        } else {
            alert('删除失败');
        }
    } catch (error) {
        console.error('删除时发生错误:', error);
        alert('删除失败');
    }
}

async function deleteMultipleFiles(files, panel) {
    try {
        let successCount = 0;
        let errorCount = 0;

        for (let i = 0; i < files.length; i++) {
            const filePath = files[i];
            const isDirectory = !filePath.includes('.');
            const endpoint = isDirectory ? '/api/manager/delete/folder' : '/api/manager/delete/file';

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filePath })
            });

            if (response.ok) {
                successCount++;
            } else {
                errorCount++;
            }
        }

        if (errorCount === 0) {
            alert('成功删除 ' + successCount + ' 个项目');
        } else {
            alert('成功删除 ' + successCount + ' 个项目，失败 ' + errorCount + ' 个项目');
        }

        if (panel === 'left') {
            refreshLeftPanel();
        } else {
            refreshRightPanel();
        }
    } catch (error) {
        console.error('批量删除时发生错误:', error);
        alert('删除失败');
    }
}
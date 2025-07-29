import os
import requests
from flask import Flask, render_template, send_file, redirect, url_for

app = Flask(__name__)

# GitHub仓库信息
GITHUB_REPO = "ksayus/PCSMT-2"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

@app.route('/')
def index():
    return render_template('download.html')

@app.route('/api/latest-download-url')
def get_latest_download_url():
    try:
        # 获取最新版本信息
        response = requests.get(GITHUB_API_URL, verify=False)
        response.raise_for_status()
        release_info = response.json()
        
        # 获取最新版本的下载链接
        assets = release_info.get('assets', [])
        if assets:
            # 假设第一个资产是可执行文件
            download_url = assets[0].get('browser_download_url')
            return {"download_url": download_url}
        else:
            return {"error": "No assets found in the latest release."}, 404
    except Exception as e:
        return {"error": f"Error: {str(e)}"}, 500

@app.route('/download')
def download():
    try:
        # 获取最新版本信息
        response = requests.get(GITHUB_API_URL, verify=False)
        response.raise_for_status()
        release_info = response.json()
        
        # 获取最新版本的下载链接
        assets = release_info.get('assets', [])
        if assets:
            # 假设第一个资产是可执行文件
            download_url = assets[0].get('browser_download_url')
            filename = assets[0].get('name')
            
            # 下载文件
            file_response = requests.get(download_url, verify=False)
            file_response.raise_for_status()
            
            # 保存文件
            file_path = os.path.join('downloads', filename)
            os.makedirs('downloads', exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(file_response.content)
            
            # 提供文件下载
            return send_file(file_path, as_attachment=True)
        else:
            return "No assets found in the latest release.", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
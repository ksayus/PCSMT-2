from bin.export import IsProgramRunning

import os
import psutil
import webbrowser

counts = IsProgramRunning.Is.Running()

import pygetwindow as gw

def SetWindowTop(window_title):
    # 获取具有指定标题的窗口
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        # 激活并置顶窗口
        windows[0].activate()
        windows[0].bringToTop()
    else:
        print(f"未找到标题为 '{window_title}' 的窗口")

NowProgramPID = os.getpid()
ProgramName = psutil.Process(NowProgramPID).name()
if psutil.Process(NowProgramPID).name() == "python.exe":
    if counts > 1:
        SetWindowTop(ProgramName)
        sys.exit()
else:
    if counts > 2:
        SetWindowTop(ProgramName)
        sys.exit()

#检查Java是否安装
import json
from bin.export import Java
from bin.export import Examine
from bin.export import log

java_versions_address = {
    "1.8": "",
    "16": "",
    "17": "",
    "21": ""
}

versions = [1.8, 16, 17, 21]
for version in versions:
    results = Examine.Java.Exist(version)
    if results:
        for path, ver in results.items():
            log.logger.info(f"✔️ 版本: {ver}已安装")
    else:
        log.logger.error(f"❌ 未安装版本{version}版本")
        log.logger.info('尝试安装Java...')
        log.logger.info(f'版本: {version}')
        try:
            result = Java.Install.Windows(version)
            if result == False:
                log.logger.error('Java安装失败')
                log.logger.info(f'请手动安装Java {version}')
            else:
                java_versions_address[f'{version}'] = version
                installed = True
        except Exception as e:
            log.logger.error(f'安装过程中发生异常: {str(e)}')

# for java_address in versions:
#     if java_versions_address[f'{java_address}'] == "":
#         log.logger.warning(f'尝试获取Java {version}版本地址...')
#         java_versions_address[f'{java_address}'] = java.install_java_windows(java_address)

try:
    with open('java_versions.json', 'r', encoding='utf-8') as f:
        java_versions_address = json.load(f)

        for javas in versions:
            if java_versions_address[f'{javas}'] == "":
                log.logger.error(f'未检测到Java {javas}版本地址')
                log.logger.info('自动获取Java版本地址...')
                try:
                    jdks = os.listdir(f'C:\\Program Files\\Java')
                    for jdk in jdks:
                        if f'jdk{javas}' in jdk.lower():
                            log.logger.info(f'已获取Java {javas}版本地址：{jdk}')
                            java_versions_address[f'{javas}'] = f'C:\\Program Files\\Java\\{jdk}\\bin\\java.exe'
                            break
                except  Exception as e:
                    log.logger.error(f'未找到 {javas}版本地址: {e}')
                    log.logger.info('正在安装Java...')
                    java_versions_address[f'{javas}'] = Java.Install.Windows(javas)

except FileNotFoundError:
    log.logger.error('未找到java_versions.json文件，请检查文件是否存在！')
    log.logger.info('正在创建java_versions.json文件...')

with open('java_versions.json', 'w', encoding='utf-8') as f:
    json.dump(java_versions_address, f, indent=4)

from bin.export import Info
from bin.export import Init
from bin.export import timer
import threading

# if program_info.program_version is not None:
#     # 为每一个服务器创建定时任务
#     # 每个定时任务都单独为一个线程
#     server_timer_thread = []  # 初始化为空列表
#     i = 0
#     for server in program_info.server_list:
#         i += 1
#         # 修改：创建Timer实例并正确传递参数
#         timer_instance = timer.Timer()
#         server_timer_thread.append(threading.Thread(target=timer_instance.start_timer, args=(server,), daemon=True))

#     # 新增：确保线程对象正确启动
#     for thread in server_timer_thread:
#         thread.start()

timer.TimerStorageSizeUpdate.thread()
timer.Heartbeat.thread(self=timer.Heartbeat)

Init.Infomation.Program()

from bin.introduction import introduction
from bin.command import Start
from bin.command import Server
from bin.command import Program
from bin.export import numbers

from cmd2 import Cmd

from bin.api import main

Program.Do.CreateShortCut('PCSMT2-v' + Info.Config.PCSMT2_Version(), False)

from bin.export import Key
from bin.export import Admin

Key.Generate.Key()

if Admin.Examine.IsExistAdminAccount():
    pass
else:
    log.logger.info('未检测到管理员账户文件，正在创建...')

    account_name = input("请输入管理员账号名称：")
    password = input("请输入管理员密码：")

    Admin.Set.AdminAccount(account_name, password)

# server_api.app.run()
flask_thread = threading.Thread(target=main.run_flask, daemon=True)
flask_thread.start()

# ========== Tkinter GUI界面 ==========
import tkinter as tk
from tkinter import ttk, scrolledtext
from cmd2 import Cmd

# 在程序开始处添加资源路径设置
import os
import sys

# 获取程序根目录路径
def get_base_path(relative_path=""):
    """获取应用程序路径，适配各种运行环境

    :param relative_path: 需要拼接的相对路径
    :return: 完整绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 打包后的执行模式
        if hasattr(sys, '_MEIPASS'):
            # onefile模式：_MEIPASS指向解压目录
            base_path = sys._MEIPASS
        else:
            # onedir模式：exe所在目录
            base_path = os.path.dirname(sys.executable)
    else:
        # 开发模式：脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.normpath(os.path.join(base_path, relative_path))

# 设置资源基础路径
BASE_PATH = get_base_path()

class TkinterApp:
    def __init__(self, cmd_instance):
        self.cmd = cmd_instance
        self.root = tk.Tk()
        self.root.title("PCSMT2")
        self.root.geometry("1296x729")
        try:
            # 使用PIL加载图标以支持更多格式
            from PIL import Image, ImageTk
            # 使用绝对路径加载图标
            icon_path = os.path.join(BASE_PATH, 'static', 'PCSMT2.ico')
            img = Image.open(icon_path)
            icon = ImageTk.PhotoImage(img)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        except ImportError:
            log.logger.error("请安装PIL库: pip install pillow")
            # 备选方案：使用原生方法加载图标
            icon_path = os.path.join(BASE_PATH, 'static', 'PCSMT2.ico')
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                log.logger.error(f"原生方法加载图标失败: {str(e)}")
        except Exception as e:
            log.logger.error(f"加载图标失败: {str(e)}")
            # 备选方案：使用原生方法加载图标
            icon_path = os.path.join(BASE_PATH, 'static', 'PCSMT2.ico')
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                log.logger.error(f"备选方案加载图标失败: {str(e)}")

        self.root.configure(bg="#f0f2f5")  # 更现代的浅灰色背景

        # 新增：命令历史记录
        self.command_history = []  # 存储历史命令
        self.history_index = -1    # 当前历史命令索引，-1表示不在历史记录中

        # 设置Windows风格
        style = ttk.Style()
        style.theme_use('winnative')

        # 提前绑定圆角矩形方法到Canvas类
        self.bind_rounded_rectangle()

        # 创建蓝白配色界面
        self.create_widgets()

        # 重定向日志输出
        self.redirect_logging()

        # 输出程序的信息
        self.execute_command('about')

        # 启动主循环
        self.root.mainloop()

    # 将StdoutRedirector提升为类级别属性
    class StdoutRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, string):
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, string)
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)

        def flush(self):
            pass

        # 新增：解决AttributeError: 'StdoutRedirector' object has no attribute 'isatty'
        def isatty(self):
            """标识输出设备不是终端类型"""
            return False

    def bind_rounded_rectangle(self):
        """为Canvas添加绘制圆角矩形的方法"""
        def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=30, **kwargs):
            points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1
                ]

            return canvas.create_polygon(points, **kwargs, smooth=True)

        # 将方法绑定到Canvas类
        tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

    def create_widgets(self):
        # 顶部按钮区域 - 使用新的配色方案
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        button_frame.configure(style="Card.TFrame")  # 新增卡片式样式

        # 创建新样式
        style = ttk.Style()
        style.theme_use('winnative')

        # 创建圆角按钮（使用Canvas实现真正的圆角）
        buttons = [
            ("帮助", lambda: self.execute_command("help")),
            ("调试模式", lambda: self.execute_command("set debug true")),
            ("打开Web界面", self.open_web_interface),
            ("退出", lambda: self.execute_command("exit"))
        ]

        for text, cmd in buttons:
            # 创建Canvas作为按钮容器
            btn_canvas = tk.Canvas(
                button_frame,
                width=100,
                height=35,
                highlightthickness=0,
                bg="#f0f2f5"  # 与背景色一致
            )
            btn_canvas.pack(side=tk.LEFT, padx=8, pady=3)

            # 绘制圆角矩形
            btn_canvas.create_rounded_rectangle(
                0, 0, 100, 35,
                radius=15,
                fill="#e0e7ff",
                outline="#4a86e8",
                width=2
            )

            # 添加按钮文本
            btn_canvas.create_text(
                50, 17,
                text=text,
                fill="#4a86e8",
                font=("Arial", 10, "bold")
            )

            # 绑定点击事件
            btn_canvas.bind("<Button-1>", lambda e, c=cmd: c())
            btn_canvas.bind("<Enter>", lambda e, c=btn_canvas: c.itemconfig(1, fill="#3a76d8"))
            btn_canvas.bind("<Leave>", lambda e, c=btn_canvas: c.itemconfig(1, fill="#e0e7ff"))

        # 日志输出区域 - 使用新样式
        log_frame = ttk.LabelFrame(self.root, text="日志输出", padding=10, style="Log.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            bg="#ffffff",  # 纯白背景
            fg="#333333",  # 深灰色文字
            font=("Consolas", 10),
            insertbackground="#4a86e8",  # 插入光标颜色
            selectbackground="#d6e4ff"   # 选中文本背景色
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # 添加分隔线
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)

        # 命令输入区域 - 使用新样式
        cmd_frame = ttk.Frame(self.root, padding=10, style="Cmd.TFrame")
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(cmd_frame, text="输入命令:", font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.cmd_entry = ttk.Combobox(
            cmd_frame,
            width=50,
            postcommand=self.update_autocomplete,
            font=("Segoe UI", 10),
            style="Modern.TCombobox"  # 新样式
        )
        # 创建组合框新样式
        style.configure("Modern.TCombobox",
                            fieldbackground="#ffffff",
                            foreground="#333333",
                            padding=5)
        style.map("Modern.TCombobox",
                fieldbackground=[('readonly', '#ffffff')],
                selectbackground=[('readonly', '#d6e4ff')])

        self.cmd_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.cmd_entry.bind("<Return>", self.on_command_entered)
        self.cmd_entry.bind("<Tab>", self.on_tab_pressed)
        # 绑定上下键事件
        self.cmd_entry.bind("<Up>", self.on_up_key)
        self.cmd_entry.bind("<Down>", self.on_down_key)

        ttk.Button(cmd_frame, text="执行",
                command=self.execute_current_command,
                style="Blue.TButton").pack(side=tk.LEFT)

    def redirect_logging(self):
        """重定向日志输出到文本框"""
        class TextHandler(log.logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                self.text_widget.config(state=tk.NORMAL)
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
                self.text_widget.config(state=tk.DISABLED)

        # 自定义日志处理器
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(log.logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        log.logger.addHandler(text_handler)

        # 使用类级别的StdoutRedirector
        sys.stdout = self.StdoutRedirector(self.log_text)
        sys.stderr = self.StdoutRedirector(self.log_text)

    def update_autocomplete(self):
        """更新命令自动补全列表 - 修复Tab补全问题"""
        # 获取所有命令（包括内置命令和自定义命令）
        cmd_list = self.cmd.get_all_commands()
        self.cmd_entry['values'] = cmd_list

    def on_tab_pressed(self, event):
        """Tab键自动补全处理 - 支持命令参数补全"""
        current_text = self.cmd_entry.get()
        if not current_text:
            return "break"

        # 分割输入行获取命令和参数
        parts = current_text.split()
        command = parts[0] if parts else ""
        arg_index = len(parts) - 1  # 当前正在输入的参数索引

        # 尝试获取命令对应的补全函数
        comp_func_name = f"complete_{command}"
        comp_func = getattr(self.cmd, comp_func_name, None) if command else None

        if comp_func:
            # 调用命令的补全函数
            try:
                # 构建当前参数文本（最后一个单词）
                text = parts[-1] if parts else ""

                # 计算当前参数位置
                line = current_text
                begidx = len(current_text) - len(text)
                endidx = len(current_text)

                completions = comp_func(text, line, begidx, endidx)
            except Exception as e:
                log.logger.error(f"补全错误: {e}")
                completions = []
        else:
            # 没有特定补全函数时，使用命令列表补全
            completions = [cmd for cmd in self.cmd.get_all_commands()
                        if cmd.startswith(current_text)]

        if completions:
            if len(completions) == 1:
                # 单个匹配时直接补全
                if arg_index > 0:
                    # 参数补全：替换当前单词
                    new_parts = parts[:-1] + [completions[0]]
                    new_text = " ".join(new_parts) + " "
                else:
                    # 命令补全
                    new_text = completions[0] + " "
                self.cmd_entry.set(new_text)
                self.cmd_entry.icursor(tk.END)
            else:
                # 多个匹配时显示选项
                self.cmd_entry['values'] = completions
                self.cmd_entry.event_generate('<Down>')
        return "break"

    # 新增：上键事件处理函数
    def on_up_key(self, event):
        """上键按下时，显示上一条历史命令"""
        if not self.command_history:
            return
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_entry.set(self.command_history[self.history_index])
        return "break"

    # 新增：下键事件处理函数
    def on_down_key(self, event):
        """下键按下时，显示下一条历史命令"""
        if not self.command_history:
            return
        if self.history_index > 0:
            self.history_index -= 1
            self.cmd_entry.set(self.command_history[self.history_index])
        elif self.history_index == 0:
            self.history_index = -1
            self.cmd_entry.set('')
        return "break"

    def execute_current_command(self):
        """执行当前输入框中的命令"""
        command = self.cmd_entry.get().strip()
        if command:
            # 新增：将命令添加到历史记录
            if not self.command_history or self.command_history[0] != command:
                self.command_history.insert(0, command)
            # 重置历史索引
            self.history_index = -1
            self.execute_command(command)
            self.cmd_entry.set('')

    def on_command_entered(self, event):
        """回车执行命令"""
        self.execute_current_command()

    def execute_command(self, command):
        """执行命令并显示结果 - 修复所有命令输出问题"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f">>> {command}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

        # 保存原始标准输出
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        # 新增：保存原始cmd2.stdout
        original_cmd_stdout = self.cmd.stdout if hasattr(self.cmd, 'stdout') else None

        try:
            # 重定向所有输出
            redirector = self.StdoutRedirector(self.log_text)
            sys.stdout = redirector
            sys.stderr = redirector

            # 重定向cmd2的输出
            if original_cmd_stdout is not None:
                self.cmd.stdout = redirector

            # 执行命令
            self.cmd.onecmd(command)
        finally:
            # 恢复原始输出
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            # 恢复cmd2.stdout
            if original_cmd_stdout is not None:
                self.cmd.stdout = original_cmd_stdout

        # 确保输出刷新
        sys.stdout.flush()
        sys.stderr.flush()

    def open_web_interface(self):
        """打开Web界面"""
        webbrowser.open("http://127.0.0.1:5000")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "> 已打开Web界面: http://127.0.0.1:5000\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

# ========== GUI代码结束 ==========


class PCSMT2(Cmd):
    intro = "欢迎使用PCSMT2"
    prompt = "PCSMT2>"

    # 版本号
    def do_version(self, arg):
        """查看版本号\nCommand: version"""
        introduction.Version()

    # 关于
    def do_about(self, arg):
        """查看介绍\nCommand: about"""
        introduction.Homepage()

    # 打开文件或目录
    def do_sta(self, file_path):
        """打开文件或目录\nCommand: sta <file_path>"""
        Start.Open.File(file_path)

    # 添加服务器
    def do_add_server(self, arg):
        """添加服务器\nCommand: add_server <server_path> <server_name> <server_version>"""
        try:
            server_path, server_name, server_version = arg.split()
            print(server_path, server_name, server_version)
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Processing.Add(server_path, server_name, False, server_version)
    def complete_add_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return self.path_complete(text, line, begidx, endidx)
        elif arg_counts == 2:
            return [list for list in Info.Information.ServerList if list.startswith(text)]
        elif arg_counts == 3:
            return [list for list in Info.Information.MinecraftVersion if list.startswith(text)]

    # 启动服务器
    def do_start_server(self, arg):
        """启动服务器\nCommand: start_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Start(server_name)
    def complete_start_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 查看服务器列表
    def do_server_list(self, arg):
        """查看服务器列表\nCommand: server_list"""
        Server.Get.List()

    # 修改服务器属性
    def do_change_server_properties(self, arg):
        """修改服务器属性\nCommand: change_server_properties <server_name> <keyword> <argument>"""
        try:
            server_name, keyword, argument = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.Properties(server_name, keyword, argument)
    def complete_change_server_properties(self, text, line, begidx, endidx):
        """
        服务器属性自动补全函数（用于命令行自动补全功能）

        参数:
            text: str - 当前输入的补全文本
            line: str - 完整的命令行输入内容
            begidx: int - 补全起始位置
            endidx: int - 补全结束位置

        返回值:
            list - 包含匹配补全文本的建议值列表

        功能说明:
            根据输入参数数量提供不同层级的自动补全建议：
            - 第1参数补全服务器名称
            - 第2参数补全属性键
            - 第3参数补全特定属性值
        """
        # 解析输入参数（跳过命令本身）
        arg = line.split()[1:]
        arg_counts = len(arg)

        # 第1个参数：补全服务器名称
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

        # 第2个参数：补全属性键列表
        elif arg_counts == 2:
            return [list for list in Info.Information.PropertiesKeys if list.startswith(text)]

        # 第3个参数：根据属性键补全特定值
        elif arg_counts == 3:
            # 游戏模式补全值
            if arg[1] == "gamemode":
                gamemode = ["survival","creative","adventure","spectator"]
                return [list for list in gamemode if list.startswith(text)]

            # 难度级别补全值
            if arg[1] == "difficulty":
                difficulty = ["peaceful","easy","normal","hard"]
                return [list for list in difficulty if list.startswith(text)]

            # 布尔类型属性统一处理（true/false）
            bool_properties = {
                "pvp": ["true","false"],
                "allow-flight": ["true","false"],
                "spawn-protection": ["true","false"],
                "spawn-npcs": ["true","false"],
                "spawn-animals": ["true","false"],
                "spawn-monsters": ["true","false"],
                "online-mode": ["true","false"]
            }
            return [val for val in bool_properties.get(arg[1], []) if val.startswith(text)]

    # 修改服务器启动内存
    def do_change_server_run_memories_config(self, arg):
        """修改写入服务器启动脚本默认使用运行内存\nCommand: change_server_run_memories_config <memories_min> <memories_max>"""
        try:
            argument_min, argument_max = arg.split()
            #检查参数是否为数字
            if not argument_min.isdigit() or not argument_max.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
            if argument_min > argument_max:
                log.logger.warning('参数错误:最小内存不能大于最大内存')
                log.logger.info('已自动调整最小内存为最大内存')
                argument_max, argument_min = numbers.swap_numbers(argument_max, argument_min)
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.RunningMemories_Config(argument_min, argument_max)

    # 查看服务器插件列表
    def do_server_mods(self, arg):
        """查看服务器插件列表\nCommand: server_mods <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Open.Mods_Plugins_Folders(server_name)
    def complete_server_mods(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 重写服务器启动脚本
    def do_server_start_batch_rewrite_run_memories(self, arg):
        """重写服务器启动脚本\nCommand: server_start_batch_rewrite_run_memories <server_name> <memories_min> <memories_max>"""
        try:
            server_name, memories_min, memories_max = arg.split()
            if not memories_min.isdigit() or not memories_max.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
            if memories_min > memories_max:
                log.logger.warning('参数错误:最小内存不能大于最大内存')
                log.logger.info('已自动调整最小内存为最大内存')
                memories_max, memories_min = numbers.swap_numbers(memories_max, memories_min)
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.RunningMemories(server_name, memories_min, memories_max)
    def complete_server_start_batch_rewrite_run_memories(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 修改服务器启动nogui
    def do_change_server_start_nogui(self, arg):
        """修改服务器启动nogui\nCommand: change_server_start_nogui <true/false>"""
        try:
            argument = arg.strip()
            if argument != "true" and argument != "false":
                log.logger.error('参数错误:请输入true或false')
                return
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.Nogui(argument)
    def complete_change_server_start_nogui(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_count = len(arg)

        if arg_count == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    # 下载服务器核心
    def do_build(self, arg):
        """下载服务器核心\nCommand: Build <server_name> <core_type> <game_version>"""
        try:
            server_name, core_type, core_support_version = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Processing.Build(server_name, core_type, core_support_version)
    def complete_build(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_count = len(arg)

        if arg_count == 2:
            core_type = ['fabric', 'forge', 'official', 'mohist']
            return [list for list in core_type if list.startswith(text)]
        elif arg_count == 3:
            return [list for list in Info.Information.MinecraftVersion if list.startswith(text)]


    # 修改等待服务器eula生成时间
    def do_change_wait_server_eula_generate_time(self, arg):
        """修改等待服务器eula生成时间\nCommand: change_wait_server_eula_generate_time <time>"""
        try:
            argument = arg.strip()
            if not argument.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.WaitEulaGenerateTime(argument)

    # 删除服务器
    def do_delete_server(self, arg):
        """删除服务器\nCommand: delete_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Processing.Delete(server_name, True)
    def complete_delete_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 搜索服务器
    def do_search_server(self, arg):
        """搜索服务器\nCommand: search_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Get.Search(server_name)
    def complete_search_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 封禁玩家或ip
    def do_banned(self, arg):
        """封禁玩家或ip\nCommand: banned <players / ips> <server_name> <player_name / ip>"""
        try:
            players_or_ips, server_name, player_name_or_ip = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        if players_or_ips == "ips":
            Server.Do.Ban.Ip(server_name, player_name_or_ip)
        if players_or_ips == "players":
            Server.Do.Ban.Player(server_name, player_name_or_ip)
    def complete_banned(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            types = ['ips', 'players']
            return [type for type in types if type.startswith(text)]
        elif arg_counts == 2:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 解封玩家或ip
    def do_unban(self, arg):
        """解封玩家或ip\nCommand: unban <players / ips> <server_name> <player_name / ip>"""
        try:
            players_or_ips, server_name, player_name_or_ip = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        if players_or_ips == "ips":
            Server.Do.Unban.Ip(server_name, player_name_or_ip)
        elif players_or_ips == "players":
            Server.Do.Unban.Player(server_name, player_name_or_ip)
    def complete_unban(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)

        if arg_counts == 1:
            types = ['ips', 'players']
            return [type for type in types if type.startswith(text)]
        elif arg_counts == 2:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 添加OP玩家
    def do_op(self, arg):
        """添加OP玩家\nCommand: op <server_name> <player_name>"""
        try:
            server_name, player_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Set.Op(server_name, player_name)
    def complete_op(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 删除OP玩家
    def do_deop(self, arg):
        """删除OP玩家\nCommand: deop <server_name> <player_name>"""
        try:
            server_name, player_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Set.Deop(server_name, player_name)
    def complete_deop(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 停止服务器
    def do_stop_server(self, arg):
        """停止服务器\nCommand: stop_server <server_name>"""
        try:
            server_name = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Do.Stop(server_name)
    def complete_stop_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 修改服务器自启动
    def do_change_program_auto_startup(self, arg):
        """修改程序自动启动\nCommand: change_program_auto_startup <True / False>"""
        try:
            argument = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.AutoStartup(argument)
    def complete_change_program_auto_startup(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    # 重命名服务器
    def do_rename_server(self, arg):
        """重命名服务器\nCommand: rename_server <server_name> <new_name>"""
        try:
            server_name, new_name = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.Rename(server_name, new_name)
    def complete_rename_server(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]

    # 重定向服务器路径
    def do_redirected_server_path(self, arg):
        """重定向服务器路径\nCommand: redirected_server_path <server_name> <new_path>"""
        try:
            server_name, new_path = arg.split()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Server.Change.Redirected(server_name, new_path)
    def complete_redirected_server_path(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            return [list for list in Info.Information.ServerList if list.startswith(text)]
        if arg_counts == 2:
            return self.path_complete(text, line, begidx, endidx)

    # 启动最新服务器
    def do_latest_started_server(self, arg):
        """启动最新服务器\nCommand: latest_started_server"""
        Server.Do.StartLatest()

    # 输出程序信息
    def do_output_program_info(self, arg):
        """输出程序信息\nCommand: out_program_info"""
        Program.Output.ProgramInfo()

    # 格式化程序
    def do_format_program(self, arg):
        """格式化程序\nCommand: format_program"""
        Program.Format.Program()

    # 清除缓存
    def do_clear_cache(self, arg):
        """清除缓存\nCommand: clear_cache"""
        Program.Format.Log()
        Program.Format.Latest()

    def do_reset_settings(self, arg):
        """重置设置\nCommand: reset_settings"""
        Program.Format.Settings()

    def do_change_get_minecraft_test_version(self, arg):
        """修改获取测试版服务器版本\nCommand: change_get_minecraft_test_version <True / False>"""
        try:
            argument = arg.strip()
        except ValueError:
            log.logger.error('参数错误，请输入正确的参数！')
            return
        Program.Change.MinecraftTestVersion(argument)
    def complete_change_get_minecraft_test_version(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        if arg_counts == 1:
            types = ['true', 'false']
            return [type for type in types if type.startswith(text)]

    def do_retracement(self, arg):
        """回档服务器\nCommand: retracement [server_name]"""
        args = arg.strip().split(maxsplit=1)  # 允许带空格的服务器名称

        # 参数验证
        if not args or args[0] not in Info.Information.ServerList:
            log.logger.error(f"服务器不存在或参数错误: {args[0] if args else ''}")
            return

        server_name = args[0]
        backup_file = args[1] if len(args) > 1 else None

        # 执行回档操作
        Server.Processing.Retracement(server_name, backup_file)
    def complete_retracement(self, text, line, begidx, endidx):
        arg = line.split()[1:]
        arg_counts = len(arg)
        # 第一个参数补全服务器列表
        if arg_counts == 1:
            return [s for s in Info.Information.ServerList if s.startswith(text)]
        # 第二个参数补全备份文件
        elif arg_counts == 2:
            backups = Server.Get.FindBackupFile(arg[0])
            backups.append('None')
            return [b for b in backups if b.startswith(text)]
        return []

    def do_change_storage_size_update_time(self, arg):
        try:
            time = arg.strip()
            if not time.isdigit():
                log.logger.error('参数错误:请输入数字')
                return
        except ValueError as e:
            log.logger.error('参数错误，请输入正确的参数！')
            log.logger.error(e)
        Program.Change.StorageSizeUpdateTime(time)

    # 退出控制台
    def do_exit(self, arg):
        """退出控制台\nCommand: exit"""
        log.logger.info("再见！")
        log.logger.info("欢迎再次使用PCSMT 2")
        sys.exit(0)
        return True  # 返回True会退出命令行循环

    # 新增：help命令的自动补全
    def complete_help(self, text, line, begidx, endidx):
        """为help命令提供命令名称补全"""
        # 获取所有可用命令
        all_commands = self.get_all_commands()
        # 过滤匹配当前输入的命令
        return [cmd for cmd in all_commands if cmd.startswith(text)]

if __name__ == "__main__":
    console = PCSMT2()

    # GUI启动选项
    use_gui = True  # 设置为True使用GUI界面

    if use_gui:
        log.logger.info("启动图形界面...")
        TkinterApp(console)
    else:
        try:
            console.cmdloop()
        except KeyboardInterrupt:
            log.logger.info("\n退出PCSMT 2，正在安全关闭...")
            sys.exit(0)

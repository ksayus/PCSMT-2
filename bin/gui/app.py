import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import threading
import webbrowser
import sys
import os

from bin.export import Info
from bin.export import log
from bin.command import Server
from bin.command import Program


class TkinterApp:
    def __init__(self, cmd_instance):
        self.cmd = cmd_instance
        self.root = tk.Tk()
        self.root.title("PCSMT2")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = int(screen_width / 2 + 160)
        window_height = int(screen_height  / 2 + 90)

        init_position_X = int(screen_width / 4 - 80)
        init_position_Y = int(screen_height / 4 - 45)

        self.root.geometry(f"{window_width}x{window_height}+{init_position_X}+{init_position_Y}")

        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join(self._get_base_path(), 'static', 'PCSMT2.ico')
            img = Image.open(icon_path)
            icon = ImageTk.PhotoImage(img)
            self.root.tk.call('wm', 'iconphoto', self.root._w, icon)
        except ImportError:
            log.logger.error("请安装PIL库: pip install pillow")
            icon_path = os.path.join(self._get_base_path(), 'static', 'PCSMT2.ico')
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                log.logger.error(f"原生方法加载图标失败: {str(e)}")
        except Exception as e:
            log.logger.error(f"加载图标失败: {str(e)}")
            icon_path = os.path.join(self._get_base_path(), 'static', 'PCSMT2.ico')
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                log.logger.error(f"备选方案加载图标失败: {str(e)}")

        self.root.configure(bg="#a6c9ff")

        self.command_history = []
        self.history_index = -1

        style = ttk.Style()
        style.theme_use('winnative')

        self.bind_rounded_rectangle()

        self.create_menu()

        self.create_widgets()

        self.redirect_logging()

        self.execute_command('about')

        self.root.mainloop()

    def _get_base_path(self, relative_path=""):
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.normpath(os.path.join(base_path, relative_path))

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

        def isatty(self):
            return False

    def bind_rounded_rectangle(self):
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

        tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

    # ==================== 菜单栏与功能对话框 ====================

    def create_menu(self):
        """创建顶部菜单栏，将程序功能以图形化方式提供给用户"""
        menubar = tk.Menu(self.root)

        # 服务器菜单
        server_menu = tk.Menu(menubar, tearoff=0)
        server_menu.add_command(label="服务器列表", command=lambda: self.execute_command_async("server_list"))
        server_menu.add_separator()
        server_menu.add_command(label="启动服务器", command=self.menu_start_server)
        server_menu.add_command(label="停止服务器", command=self.menu_stop_server)
        server_menu.add_command(label="重启服务器", command=self.menu_restart_server)
        server_menu.add_separator()
        server_menu.add_command(label="回档服务器(恢复备份)", command=self.menu_retracement_server)
        server_menu.add_command(label="添加现有服务器", command=self.menu_add_server)
        server_menu.add_command(label="重定向服务器路径", command=self.menu_redirect_server_path)
        server_menu.add_command(label="删除服务器", command=self.menu_delete_server)
        menubar.add_cascade(label="服务器", menu=server_menu)

        # 玩家管理菜单
        player_menu = tk.Menu(menubar, tearoff=0)
        player_menu.add_command(label="添加OP", command=lambda: self.menu_player_command("op", "添加OP", "玩家名"))
        player_menu.add_command(label="移除OP", command=lambda: self.menu_player_command("deop", "移除OP", "玩家名"))
        player_menu.add_separator()
        player_menu.add_command(label="封禁玩家", command=lambda: self.menu_player_command("banned players", "封禁玩家", "玩家名"))
        player_menu.add_command(label="解封玩家", command=lambda: self.menu_player_command("unban players", "解封玩家", "玩家名"))
        player_menu.add_separator()
        player_menu.add_command(label="封禁IP", command=lambda: self.menu_player_command("banned ips", "封禁IP", "IP地址"))
        player_menu.add_command(label="解封IP", command=lambda: self.menu_player_command("unban ips", "解封IP", "IP地址"))
        menubar.add_cascade(label="玩家管理", menu=player_menu)

        # 下载菜单
        download_menu = tk.Menu(menubar, tearoff=0)
        download_menu.add_command(label="下载服务器核心(创建服务器)", command=self.menu_build_server)
        menubar.add_cascade(label="下载", menu=download_menu)

        # 程序菜单
        program_menu = tk.Menu(menubar, tearoff=0)
        program_menu.add_command(label="检查更新", command=self.menu_check_update)
        program_menu.add_separator()
        program_menu.add_command(label="清理缓存", command=lambda: self.execute_command_async("clear_cache"))
        program_menu.add_command(label="重置设置", command=self.menu_reset_settings)
        program_menu.add_command(label="格式化程序", command=self.menu_format_program)
        program_menu.add_separator()
        program_menu.add_command(label="程序信息", command=lambda: self.execute_command_async("output_program_info"))
        program_menu.add_command(label="打开Web界面", command=self.open_web_interface)
        menubar.add_cascade(label="程序", menu=program_menu)

        self.root.config(menu=menubar)

    def _server_list_text(self):
        """获取当前服务器列表文本，用于对话框提示"""
        try:
            servers = Info.Information.ServerList
            return "可用服务器: " + (", ".join(servers) if servers else "(无)")
        except Exception:
            return ""

    def _ask_server_name(self, title):
        """弹出对话框询问服务器名称"""
        return simpledialog.askstring(title, f"请输入服务器名称\n{self._server_list_text()}", parent=self.root)

    def execute_command_async(self, command):
        """在后台线程执行命令，避免阻塞GUI（用于启动/停止等耗时操作）"""
        threading.Thread(target=self.execute_command, args=(command,), daemon=True).start()

    def menu_start_server(self):
        server_name = self._ask_server_name("启动服务器")
        if server_name:
            self.execute_command_async(f"start_server {server_name.strip()}")

    def menu_stop_server(self):
        server_name = self._ask_server_name("停止服务器")
        if server_name:
            self.execute_command_async(f"stop_server {server_name.strip()}")

    def menu_restart_server(self):
        server_name = self._ask_server_name("重启服务器")
        if not server_name:
            return
        server_name = server_name.strip()
        log.logger.info(f"正在重启服务器: {server_name}")
        threading.Thread(target=Server.Do.Restart, args=(server_name,), daemon=True).start()

    def menu_delete_server(self):
        server_name = self._ask_server_name("删除服务器")
        if not server_name:
            return
        server_name = server_name.strip()
        if messagebox.askyesno("删除服务器", f"确定要删除服务器 \"{server_name}\" 吗？\n此操作将永久删除服务器文件，无法恢复！"):
            threading.Thread(target=Server.Processing.Delete, args=(server_name, False), daemon=True).start()

    def menu_retracement_server(self):
        """回档服务器：选择服务器后列出可用备份供选择"""
        server_name = self._ask_server_name("回档服务器")
        if not server_name:
            return
        server_name = server_name.strip()

        messagebox.showinfo("回档服务器", "回档前请确保服务器已停止！\n回档将覆盖当前存档（旧存档会保存为 old-save.zip）。")

        backup_file = None
        try:
            backups = Server.Get.FindBackupFile(server_name)
        except Exception:
            backups = None

        if backups and len(backups) > 1:
            # 列表最后一项为备份来源标记（'mod' 或 'plugin'）
            backup_files = backups[:-1]
            prompt = "可用备份文件:\n" + "\n".join(backup_files) + "\n\n请输入备份文件名（留空使用最新备份）:"
            choice = simpledialog.askstring("回档服务器", prompt, parent=self.root)
            if choice is None:
                return
            backup_file = choice.strip() or None
        else:
            if not messagebox.askyesno("回档服务器", "未找到备份列表（需要 FTB Backups 2 模组或 eBackup 插件）。\n仍要尝试使用最新备份回档吗？"):
                return

        threading.Thread(target=Server.Processing.Retracement, args=(server_name, backup_file), daemon=True).start()

    def menu_add_server(self):
        """添加（导入）现有服务器"""
        server_path = simpledialog.askstring("添加现有服务器", "请输入服务器文件夹路径（包含核心 .jar 文件）:", parent=self.root)
        if not server_path:
            return
        server_name = simpledialog.askstring("添加现有服务器", "请输入服务器名称:", parent=self.root)
        if not server_name:
            return
        server_version = simpledialog.askstring("添加现有服务器", "请输入游戏版本（例如 1.20.1）:", parent=self.root)
        if not server_version:
            return
        core_type = simpledialog.askstring("添加现有服务器", "请输入核心类型（official / forge / fabric / mohist）:", parent=self.root)
        if not core_type:
            return

        threading.Thread(
            target=Server.Processing.Add,
            args=(server_path.strip(), server_name.strip(), False, server_version.strip(), core_type.strip()),
            daemon=True
        ).start()

    def menu_redirect_server_path(self):
        """重定向服务器路径"""
        server_name = self._ask_server_name("重定向服务器路径")
        if not server_name:
            return
        server_name = server_name.strip()
        new_path = simpledialog.askstring("重定向服务器路径", "请输入新的服务器路径（绝对路径）:\n（服务器文件需已移动到新位置）", parent=self.root)
        if not new_path:
            return
        threading.Thread(target=Server.Change.Redirected, args=(server_name, new_path.strip()), daemon=True).start()

    def menu_player_command(self, command_prefix, title, target_label):
        """玩家管理通用对话框：先选服务器，再输入目标玩家/IP"""
        server_name = self._ask_server_name(title)
        if not server_name:
            return
        target = simpledialog.askstring(title, f"请输入{target_label}:", parent=self.root)
        if not target:
            return
        self.execute_command_async(f"{command_prefix} {server_name.strip()} {target.strip()}")

    def menu_build_server(self):
        """下载服务器核心（创建服务器）"""
        server_name = simpledialog.askstring("创建服务器", "请输入新服务器名称:", parent=self.root)
        if not server_name:
            return
        core_type = simpledialog.askstring("创建服务器", "请输入核心类型（official / forge / fabric / mohist）:", parent=self.root)
        if not core_type:
            return
        game_version = simpledialog.askstring("创建服务器", "请输入游戏版本（例如 1.20.1）:", parent=self.root)
        if not game_version:
            return
        self.execute_command_async(f"build {server_name.strip()} {core_type.strip()} {game_version.strip()}")

    def menu_check_update(self):
        """检查程序更新"""
        from bin.download import Update

        source = Info.Config.AutoUpdateSource()
        log.logger.info(f"正在通过 {source} 检查更新...")

        def _check():
            try:
                if source == 'Gitee':
                    Update.Source.Gitee()
                else:
                    Update.Source.Github()
            except Exception as e:
                log.logger.error(f"检查更新失败: {e}")

        threading.Thread(target=_check, daemon=True).start()

    def menu_reset_settings(self):
        if messagebox.askyesno("重置设置", "确定要重置所有设置吗？设置将恢复为默认值。"):
            self.execute_command_async("reset_settings")

    def menu_format_program(self):
        """格式化程序（绕过控制台 input 确认，使用对话框确认）"""
        if not messagebox.askyesno("格式化程序", "警告：格式化程序将清理日志、缓存与所有设置！"):
            return
        if not messagebox.askyesno("格式化程序", "请再次确认：真的要格式化程序吗？此操作不可撤销！"):
            return

        def _format():
            Program.Format.Log()
            Program.Format.Server()
            Program.Format.Latest()
            Program.Format.Settings()
            log.logger.info("程序格式化完成，建议重启程序")

        threading.Thread(target=_format, daemon=True).start()

    def create_widgets(self):
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        button_frame.configure(style="Card.TFrame")

        style = ttk.Style()
        style.theme_use('winnative')

        buttons = [
            ("帮助", lambda: self.execute_command("help")),
            ("调试模式", lambda: self.execute_command("set debug true")),
            ("打开Web界面", self.open_web_interface),
            ("退出", lambda: self.execute_command("exit"))
        ]

        for text, cmd in buttons:
            btn_canvas = tk.Canvas(
                button_frame,
                width=100,
                height=35,
                highlightthickness=0,
                bg="#f0f2f5"
            )
            btn_canvas.pack(side=tk.LEFT, padx=8, pady=3)

            btn_canvas.create_rounded_rectangle(
                0, 0, 100, 35,
                radius=15,
                fill="#e0e7ff",
                outline="#4a86e8",
                width=2
            )

            btn_canvas.create_text(
                50, 17,
                text=text,
                fill="#4a86e8",
                font=("Arial", 10, "bold")
            )

            btn_canvas.bind("<Button-1>", lambda e, c=cmd: c())
            btn_canvas.bind("<Enter>", lambda e, c=btn_canvas: c.itemconfig(1, fill="#629dfc"))
            btn_canvas.bind("<Leave>", lambda e, c=btn_canvas: c.itemconfig(1, fill="#e0e7ff"))

        log_frame = ttk.LabelFrame(self.root, text="日志输出", padding=10, style="Log.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            bg="#bcdbf8",
            fg="#2B79EC",
            font=("Consolas", 10),
            insertbackground="#2fee6f",
            selectbackground="#3c7af7"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)

        cmd_frame = ttk.Frame(self.root, padding=10, style="Cmd.TFrame")
        cmd_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(cmd_frame, text="输入命令:", font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.cmd_entry = ttk.Combobox(
            cmd_frame,
            width=50,
            postcommand=self.update_autocomplete,
            font=("Segoe UI", 10),
            style="Modern.TCombobox"
        )
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
        self.cmd_entry.bind("<Up>", self.on_up_key)
        self.cmd_entry.bind("<Down>", self.on_down_key)

        ttk.Button(cmd_frame, text="执行",
                command=self.execute_current_command,
                style="Blue.TButton").pack(side=tk.LEFT)

        status_bar = ttk.Frame(self.root, padding=(5, 2))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        version_text = f"PCSMT2 v{Info.Config.PCSMT2_Version()}-{Info.Config.ReleaseVersion()}"
        version_label = ttk.Label(
            status_bar,
            text=version_text,
            font=("Segoe UI", 8),
            anchor="e"
        )
        version_label.pack(side=tk.RIGHT, padx=5)

    def redirect_logging(self):
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

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(log.logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        log.logger.addHandler(text_handler)

        sys.stdout = self.StdoutRedirector(self.log_text)
        sys.stderr = self.StdoutRedirector(self.log_text)

    def update_autocomplete(self):
        cmd_list = self.cmd.get_all_commands()
        self.cmd_entry['values'] = cmd_list

    def on_tab_pressed(self, event):
        current_text = self.cmd_entry.get()
        if not current_text:
            return "break"

        parts = current_text.split()
        command = parts[0] if parts else ""
        arg_index = len(parts) - 1

        comp_func_name = f"complete_{command}"
        comp_func = getattr(self.cmd, comp_func_name, None) if command else None

        if comp_func:
            try:
                text = parts[-1] if parts else ""

                line = current_text
                begidx = len(current_text) - len(text)
                endidx = len(current_text)

                completions = comp_func(text, line, begidx, endidx)
            except Exception as e:
                log.logger.error(f"补全错误: {e}")
                completions = []
        else:
            completions = [cmd for cmd in self.cmd.get_all_commands()
                        if cmd.startswith(current_text)]

        if completions:
            if len(completions) == 1:
                if arg_index > 0:
                    new_parts = parts[:-1] + [completions[0]]
                    new_text = " ".join(new_parts) + " "
                else:
                    new_text = completions[0] + " "
                self.cmd_entry.set(new_text)
                self.cmd_entry.icursor(tk.END)
            else:
                self.cmd_entry['values'] = completions
                self.cmd_entry.event_generate('<Down>')
        return "break"

    def on_up_key(self, event):
        if not self.command_history:
            return
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.cmd_entry.set(self.command_history[self.history_index])
        return "break"

    def on_down_key(self, event):
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
        command = self.cmd_entry.get().strip()
        if command:
            if not self.command_history or self.command_history[0] != command:
                self.command_history.insert(0, command)
            self.history_index = -1
            self.execute_command(command)
            self.cmd_entry.set('')

    def on_command_entered(self, event):
        self.execute_current_command()

    def execute_command(self, command):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f">>> {command}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_cmd_stdout = self.cmd.stdout if hasattr(self.cmd, 'stdout') else None

        try:
            redirector = self.StdoutRedirector(self.log_text)
            sys.stdout = redirector
            sys.stderr = redirector

            if original_cmd_stdout is not None:
                self.cmd.stdout = redirector

            self.cmd.onecmd(command)
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            if original_cmd_stdout is not None:
                self.cmd.stdout = original_cmd_stdout

        sys.stdout.flush()
        sys.stderr.flush()

    def open_web_interface(self):
        port = str(Info.Config.Port())
        webbrowser.open(f"http://127.0.0.1:{port}")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"> 已打开Web界面: http://127.0.0.1:{port}\n")
        self.log_text.insert(tk.END, "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
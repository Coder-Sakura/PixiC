# coding=utf8
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import webbrowser
from log_record import logger
from message import VERSION

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')

# 配置结构定义
SCHEMA = [
    {'section': 'Paths', 'label': '路径设置', 'items': [
        {'key': 'ROOT_PATH', 'type': 'text', 'label': '画师作品下载路径', 'desc': '用于存储您关注的画师的作品'},
        {'key': 'BOOKMARK_PATH', 'type': 'text', 'label': '收藏作品下载路径', 'desc': '用于存储您收藏的作品'},
        {'key': 'PRO_DIR', 'type': 'text', 'label': 'Chrome 用户数据目录', 'desc': 'Chrome 浏览器用户数据目录 (用于获取 Cookie)'},
    ]},
    {'section': 'Account', 'label': '账户设置', 'items': [
        {'key': 'USER_ID', 'type': 'text', 'label': 'Pixiv 用户ID', 'desc': '需要获取插画作品的 Pixiv 用户id'},
        {'key': 'COOKIE_UPDATE_ENABLED', 'type': 'bool', 'label': '自动更新 Cookie', 'desc': '勾选后将启动 Chrome 保存 Pixiv 登录状态到本地. 注意: 运行前请关闭所有 Chrome 窗口'},
        {'key': 'ORIGI_COOKIE_LIST', 'type': 'list', 'label': '自定义 Cookie 列表 (可选)', 'desc': '每行输入一个完整 Cookie'},
    ]},
    {'section': 'Switches', 'label': '功能开关', 'items': [
        {'key': 'SKIP_ISEXISTS_ILLUST', 'type': 'bool', 'label': '跳过已存在插画', 'desc': '跳过本地已下载的插画'},
        {'key': 'PIXIV_CRAWLER_ENABLED', 'type': 'bool', 'label': '启用画师爬虫', 'desc': '关注画师作品爬虫'},
        {'key': 'PIXIV_BOOKMARK_ENABLED', 'type': 'bool', 'label': '启用收藏爬虫', 'desc': '用户收藏作品爬虫'},
        {'key': 'BOOKMARK_HIDE_ENABLE', 'type': 'bool', 'label': '获取未公开收藏', 'desc': '是否获取私密收藏'},
        {'key': 'PIXIV_API_ENABLED', 'type': 'bool', 'label': '启用 API', 'desc': 'API 服务开关（需开启数据库）'},
    ]},
    {'section': 'Limits', 'label': '限制与周期', 'items': [
        {'key': 'USERS_CYCLE', 'type': 'number', 'label': '画师检测周期（秒）', 'desc': '默认 86400 秒'},
        {'key': 'USERS_LIMIT', 'type': 'number', 'label': '画师收藏下限', 'desc': '高于此值才下载'},
        {'key': 'BOOKMARK_CYCLE', 'type': 'number', 'label': '收藏检测周期（秒）', 'desc': '默认 86400 秒'},
        {'key': 'BOOKMARK_LIMIT', 'type': 'number', 'label': '收藏作品下限', 'desc': '高于此值才下载'},
    ]},
    {'section': 'API', 'label': 'API 设置', 'items': [
        {'key': 'API_HOST', 'type': 'text', 'label': 'API 主机', 'desc': '默认 0.0.0.0'},
        {'key': 'API_PORT', 'type': 'text', 'label': 'API 端口', 'desc': '本地 API 服务监听端口 (默认 1526)'},
        {'key': 'API_THREAD', 'type': 'number', 'label': 'API 线程数', 'desc': '数据库线程数'},
        {'key': 'RANDOM_LIMIT', 'type': 'number', 'label': '随机接口返回数量', 'desc': '最大返回条数限制'},
    ]},
    {'section': 'Database', 'label': '数据库设置', 'items': [
        {'key': 'DB_ENABLE', 'type': 'bool', 'label': '启用数据库', 'desc': '开启后将插画元数据写入数据库'},
        {'key': 'DB_HOST', 'type': 'text', 'label': '数据库地址', 'desc': '示例：localhost'},
        {'key': 'DB_PORT', 'type': 'number', 'label': '数据库端口', 'desc': '示例：3306'},
        {'key': 'DB_USER', 'type': 'text', 'label': '数据库用户名', 'desc': '示例：pixiv'},
        {'key': 'DB_PASSWD', 'type': 'text', 'label': '数据库密码', 'desc': '示例：******'},
        {'key': 'DB_DATABASE', 'type': 'text', 'label': '数据库名称', 'desc': '示例：moe'},
        {'key': 'DB_CHARSET', 'type': 'text', 'label': '字符集', 'desc': '示例：utf8mb4'},
    ]},
]

def parse_cookie_list(text):
    if not text:
        return []
    return [line.strip() for line in text.split('\n') if line.strip()]

class ConfigManager:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_content(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def get_current_values(self):
        # 动态导入 config 获取当前值
        if os.path.dirname(self.filepath) not in sys.path:
            sys.path.insert(0, os.path.dirname(self.filepath))
        
        try:
            if 'config' in sys.modules:
                import importlib
                import config
                importlib.reload(config)
            else:
                import config
            
            values = {}
            for section in SCHEMA:
                for item in section['items']:
                    key = item['key']
                    if hasattr(config, key):
                        values[key] = getattr(config, key)
                    else:
                        values[key] = None
            return values
        except Exception as e:
            print(f"Error importing config: {e}")
            return {}

    def update_config(self, new_values):
        content = self.read_content()
        
        for key, value in new_values.items():
            # 查找类型
            item_type = 'text'
            for section in SCHEMA:
                for item in section['items']:
                    if item['key'] == key:
                        item_type = item['type']
                        break
            
            # 准备替换字符串
            if item_type == 'text':
                if '\\' in str(value):
                    replacement = f"r'{value}'"
                else:
                    replacement = f"'{value}'"
            elif item_type == 'bool':
                replacement = str(value)
            elif item_type == 'number':
                replacement = str(value)
            elif item_type == 'list':
                if not value:
                    replacement = "[]"
                else:
                    items_str = ",\n\t".join([f"'{v}'" for v in value])
                    replacement = f"[\n\t{items_str},\n]"
            
            if item_type == 'list':
                 # 匹配列表定义
                 pattern = f"({key}\\s*=\\s*\\[)(.*?)(\\])"
                 matches = list(re.finditer(pattern, content, re.DOTALL | re.MULTILINE))
            else:
                # 匹配单行定义
                pattern = f"(^\\s*{key}\\s*=\\s*)(.*?)($)"
                matches = list(re.finditer(pattern, content, re.MULTILINE))

            if matches:
                # 使用最后一个匹配项
                m = matches[-1]
                start, end = m.span()
                new_line = f"{key} = {replacement}"
                content = content[:start] + new_line + content[end:]
            else:
                print(f"Warning: Could not find definition for {key} in config.py")

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(content)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, justify='left',
                       background="#ffffe0", relief='solid', borderwidth=1,
                       font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class PixiCConfigGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PixiC 2.0 配置工具")
        self.root.geometry("600x800")
        self.scheduler = None
        self.scheduler_thread = None
        self.log_sink_id = None
        self.log_lines = []
        self.log_limit = 5000
        self.log_level_var = tk.StringVar(value="INFO")
        self.current_log_level = "INFO"
        self.entry_widgets = {}
        
        self.cm = ConfigManager(CONFIG_FILE)
        self.widgets = {}
        
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        # 定义样式
        style = ttk.Style()
        style.configure("Action.TButton", font=('SimSun', 9, 'bold'))
        style.configure("Start.TButton", foreground="green")
        style.configure("Stop.TButton", foreground="red")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        settings_container = ttk.Frame(notebook)
        logs_container = ttk.Frame(notebook)
        more_container = ttk.Frame(notebook)
        
        notebook.add(settings_container, text="设置")
        notebook.add(logs_container, text="运行日志")
        notebook.add(more_container, text="项目主页")
        self.notebook = notebook

        # 底部按钮栏
        btn_frame = ttk.Frame(settings_container, padding="10")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        ttk.Button(btn_frame, text="保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="重新加载", command=self._load_values).pack(side=tk.RIGHT, padx=5)
        
        # 启动按钮
        self.start_btn = ttk.Button(btn_frame, text="启动项目", style="Start.TButton", command=self.start_project)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # 停止按钮 (默认置灰)
        self.stop_btn = ttk.Button(btn_frame, text="停止项目", style="Stop.TButton", command=self.stop_project, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.status_var = tk.StringVar(value="未启动")
        ttk.Label(btn_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)

        # === 更多页面内容 ===
        self._build_more_tab(more_container)

        # === 设置页滚动内容 ===
        canvas = tk.Canvas(settings_container)
        scrollbar = ttk.Scrollbar(settings_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=580)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for section in SCHEMA:
            frame = ttk.LabelFrame(self.scrollable_frame, text=section['label'], padding="10")
            frame.pack(fill=tk.X, padx=10, pady=5)
            if section['label'] in ("API 设置", "数据库设置"):
                warn = ttk.Label(frame, text="⚠ 警告：错误配置可能导致数据丢失，修改前请确认您了解相关风险", foreground="red")
                warn.pack(fill=tk.X, pady=4)
            for item in section['items']:
                self._create_item_widget(frame, item)

        log_top = ttk.Frame(logs_container, padding="5")
        log_top.pack(fill=tk.X)
        ttk.Label(log_top, text="日志等级过滤").pack(side=tk.LEFT)
        level_cb = ttk.Combobox(log_top, textvariable=self.log_level_var, values=["ERROR","WARN","INFO","DEBUG"], state="readonly", width=8)
        level_cb.pack(side=tk.LEFT, padx=5)
        def _update_level(*args):
            self.current_log_level = self.log_level_var.get()
            self._refresh_log_display()  # 切换等级时实时刷新已显示的日志
        self.log_level_var.trace_add("write", lambda *a: _update_level())
        
        # 日志测试按钮 (用户测试功能)
        ttk.Button(log_top, text="测试日志", command=self._test_log_print).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(log_top, text="清除日志", command=self.clear_logs).pack(side=tk.RIGHT)
        self.log_text = scrolledtext.ScrolledText(logs_container, state="disabled", height=20, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_item_widget(self, parent, item):
        """根据配置项类型创建对应的 GUI 控件"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        key = item['key']
        label_text = item['label']
        desc = item['desc']
        
        # 标签与悬浮提示
        lbl = ttk.Label(frame, text=label_text, width=30, anchor="w")
        lbl.pack(side=tk.LEFT)
        ToolTip(lbl, desc)
        
        if item['type'] == 'bool':
            # 布尔开关
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(frame, variable=var, text="启用")
            chk.pack(side=tk.LEFT)
            # 特殊逻辑：自动更新 Cookie 增加警示文本
            if key == 'COOKIE_UPDATE_ENABLED':
                warn = tk.Label(frame, text="建议仅首次开启,成功后保持关闭", foreground="red", font=("SimSun", 9))
                warn.pack(side=tk.LEFT, padx=5)
            self.widgets[key] = var
            
        elif item['type'] == 'list':
            # 列表输入（Cookie）
            txt = scrolledtext.ScrolledText(frame, height=4, width=30, font=('Consolas', 9))
            txt.pack(side=tk.LEFT, fill=tk.X, expand=True)
            # 添加 Cookie 输入说明与示例
            title = ttk.Label(parent, text="每行输入一个完整Cookie", foreground="#555")
            title.pack(fill=tk.X, padx=2)
            example = ttk.Label(parent, text="示例1: name1=value1; path=/; domain=.example.com\n示例2: name2=value2; expires=Wed, 21 Oct 2025 07:28:00 GMT", foreground="#777", justify="left")
            example.pack(fill=tk.X, padx=2)
            self.widgets[key] = txt
            
        else:
            # 普通文本或数字输入
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            # 路径类设置增加“浏览”按钮
            if key in {"ROOT_PATH","BOOKMARK_PATH","PRO_DIR"}:
                browse = ttk.Button(frame, text="浏览", command=lambda k=key, v=var: self.browse_dir(k, v))
                browse.pack(side=tk.LEFT, padx=5)
            self.widgets[key] = var
            self.entry_widgets[key] = entry

    def _load_values(self):
        """从 config.py 加载配置到 GUI 控件"""
        values = self.cm.get_current_values()
        for key, value in values.items():
            if key not in self.widgets:
                continue
                
            widget = self.widgets[key]
            
            if isinstance(widget, tk.BooleanVar):
                widget.set(bool(value))
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.delete('1.0', tk.END)
                if isinstance(value, list):
                    widget.insert(tk.END, "\n".join(value))
            elif isinstance(widget, tk.StringVar):
                widget.set(str(value) if value is not None else "")

    def save_config(self, silent=False):
        """保存当前 GUI 中的配置到 config.py"""
        new_values = {}
        for section in SCHEMA:
            for item in section['items']:
                key = item['key']
                if key not in self.widgets:
                    continue
                    
                widget = self.widgets[key]
                
                # 根据类型提取值
                if item['type'] == 'bool':
                    new_values[key] = widget.get()
                elif item['type'] == 'number':
                    try:
                        val = widget.get()
                        new_values[key] = int(val) if val else 0
                    except ValueError:
                        new_values[key] = 0
                elif item['type'] == 'list':
                    if isinstance(widget, scrolledtext.ScrolledText):
                        text_content = widget.get('1.0', tk.END).strip()
                        new_values[key] = parse_cookie_list(text_content)
                else:
                    new_values[key] = widget.get()
        
        try:
            # 写入配置文件
            self.cm.update_config(new_values)
            if not silent:
                messagebox.showinfo("成功", "配置已保存！\n点击“启动项目”即可应用新配置。")
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
            return False

    def start_project(self):
        """启动项目（增加确认与状态管理）"""
        if not messagebox.askyesno("确认", "确定要启动项目吗？"):
            return
            
        # 按钮状态切换
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # 自动切换到运行日志页
        self.notebook.select(1)
        
        # 记录日志
        logger.info("用户触发启动项目...")
        
        # === 实际启动逻辑 (此处暂缓，改为用户测试模式) ===
        # self._real_start_project() 
        self._test_start_logic()

    def _real_start_project(self):
        """真正的项目启动逻辑"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return
            
        try:
            import threading
            import importlib
            import sys
            
            # 1. 强制保存当前配置（静默模式）
            if not self.save_config(silent=True):
                return
            
            # 2. 重新加载 config 模块，确保获取最新磁盘值
            if 'config' in sys.modules:
                import config
                importlib.reload(config)
            else:
                import config
                
            # 3. 重新加载 scheduler 模块，确保它使用最新的 config 变量
            # 注意：由于 scheduler 使用 'from config import ...'，必须在 config reload 后 reload scheduler
            from scheduler import Scheduler
            if 'scheduler' in sys.modules:
                import scheduler
                importlib.reload(scheduler)
                from scheduler import Scheduler # 重新获取 reload 后的类
                
            self.scheduler = Scheduler()
            def _run():
                try:
                    self.scheduler.run()
                finally:
                    self.root.after(0, lambda: self.status_var.set("已停止"))
                    self.root.after(0, lambda: self.start_btn.config(state="normal"))
                    self.root.after(0, lambda: self.stop_btn.config(state="disabled"))
            
            self.scheduler_thread = threading.Thread(target=_run, daemon=True)
            self.scheduler_thread.start()
            self.status_var.set("运行中")
            self.attach_log_sink()
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {str(e)}")

    def stop_project(self):
        """停止项目（增加确认与状态管理）"""
        if not messagebox.askyesno("确认", "确定要停止项目吗？"):
            return
            
        # 按钮状态切换
        self.stop_btn.config(state="disabled")
        self.start_btn.config(state="normal")
        
        logger.info("用户触发停止项目...")
        
        # 更新状态为已停止
        self.status_var.set("已停止")
        
        if self.scheduler:
            try:
                self.scheduler.stop()
                self.scheduler = None
                self.detach_log_sink()
            except Exception as e:
                messagebox.showerror("错误", f"停止失败: {str(e)}")

    def browse_dir(self, key, var):
        """弹出文件夹选择对话框"""
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    # === 更多页面与用户测试功能 (高度集中，方便删除) ===
    def _build_more_tab(self, container):
        """构建更多页面内容"""
        content = ttk.Frame(container, padding="20")
        content.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(content, text="项目名称: PixiC", font=("SimSun", 12, "bold")).pack(pady=10)
        ttk.Label(content, text=f"版本号: {VERSION}", font=("SimSun", 10)).pack(pady=5)
        
        link = ttk.Label(content, text="Github", foreground="blue", cursor="hand2", font=("SimSun", 10, "underline"))
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Coder-Sakura/PixiC"))

    def _test_start_logic(self):
        """测试启动逻辑 (不真实运行项目)"""
        self.status_var.set("测试运行中...")
        self.attach_log_sink()
        logger.info("测试模式：项目已启动（模拟）")
        logger.debug("测试模式：调试信息输出...")
        logger.warning("测试模式：警告信息输出...")

    def _test_log_print(self):
        """测试日志打印功能 (验证过滤等级是否生效)"""
        self.attach_log_sink()
        logger.info(f"--- 开始测试日志过滤 (当前过滤等级: {self.current_log_level}) ---")
        logger.debug("这是一条 DEBUG 级别测试日志 (仅在等级为 DEBUG 时可见)")
        logger.info("这是一条 INFO 级别测试日志 (等级为 INFO/DEBUG 时可见)")
        logger.warning("这是一条 WARNING 级别测试日志 (等级为 WARN 及以下可见)")
        logger.error("这是一条 ERROR 级别测试日志 (始终可见)")
        logger.info("--- 测试日志发送完毕 ---")
    # === 用户测试功能结束 ===

    def attach_log_sink(self):
        if getattr(self, "log_sink_id", None):
            return
            
        def sink(msg):
            rec = msg.record
            lvl = rec["level"].name
            text = rec["message"]
            
            # 格式化单行日志
            line = f"[{rec['time'].strftime('%H:%M:%S')}] {lvl} | {text}\n"
            
            # 存储原始日志信息，用于追溯过滤
            self.log_lines.append((lvl, line))
            if len(self.log_lines) > self.log_limit:
                self.log_lines = self.log_lines[-self.log_limit:]
            
            # 检查当前等级，决定是否立即显示
            if self._should_show_log(lvl):
                try:
                    def _update():
                        self.log_text.configure(state="normal")
                        self.log_text.insert(tk.END, line)
                        self.log_text.see(tk.END)
                        self.log_text.configure(state="disabled")
                    self.root.after(0, _update)
                except Exception:
                    pass
        self.log_sink_id = logger.add(sink, level="DEBUG", enqueue=True)

    def _should_show_log(self, lvl_name):
        """判断给定等级的日志是否应该显示"""
        order = {"ERROR": 4, "WARNING": 3, "INFO": 2, "DEBUG": 1}
        want = self.current_log_level
        want_norm = "WARNING" if want == "WARN" else want
        return order.get(lvl_name, 1) >= order.get(want_norm, 2)

    def _refresh_log_display(self):
        """根据当前过滤等级重新渲染所有日志"""
        if not hasattr(self, 'log_text'):
            return
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        
        for lvl, line in self.log_lines:
            if self._should_show_log(lvl):
                self.log_text.insert(tk.END, line)
        
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def detach_log_sink(self):
        if getattr(self, "log_sink_id", None):
            try:
                logger.remove(self.log_sink_id)
            except Exception:
                pass
            self.log_sink_id = None

    def clear_logs(self):
        self.log_lines = []
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def enforce_log_limit(self):
        if len(self.log_lines) > self.log_limit:
            self.log_lines = self.log_lines[-self.log_limit:]
if __name__ == '__main__':
    root = tk.Tk()
    # 尝试设置图标（如果有）
    # root.iconbitmap('icon.ico') 
    
    app = PixiCConfigGUI(root)
    
    # 居中窗口
    window_width = 600
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    root.mainloop()

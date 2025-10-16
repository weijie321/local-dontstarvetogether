#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
饥荒联机版本地服务器配置工具
自动化配置饥荒联机版专用服务器
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import shutil
import zipfile
import subprocess
import threading
import time
from pathlib import Path
import getpass

# 配置文件路径
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".dst_server_config.json")

class DSTServerConfigTool:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 饥荒联机版本地服务器配置工具")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # 获取当前用户 - 必须在create_widgets之前
        self.current_user = getpass.getuser()
        
        # 加载保存的配置
        self.saved_config = self.load_config()
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 18, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Microsoft YaHei', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Microsoft YaHei', 9), foreground='#7f8c8d')
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架容器（带滚动条）
        self.create_scrollable_frame()
        
        # 配置主框架为两列布局
        self.main_frame.columnconfigure(0, weight=1)  # 左列
        self.main_frame.columnconfigure(1, weight=1)  # 右列
        
        # 左侧框架 - 表单组件
        left_frame = ttk.Frame(self.main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.columnconfigure(0, weight=1)
        
        # 右侧框架 - 日志区域
        right_frame = ttk.Frame(self.main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(left_frame, text="🎮 饥荒联机版本地服务器配置工具", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # 当前用户显示
        user_label = ttk.Label(left_frame, text=f"当前用户: {self.current_user}", 
                              style='Info.TLabel')
        user_label.grid(row=1, column=0, pady=(0, 5))
        
        # 添加说明文本
        instructions_text = (
            "首先需要下载服务器配置文件：\n"
            "点击下方按钮\n"
            "在\"服务器\"界面，填写服务器名称（此集群名并非最终展示的服务器名）后点击\"添加新服务器\"，在上方出现的对应服务器中点击\"配置服务器\"\n"
            "然后点\"下载配置\"按钮即可将配置文件下载下来\n\n"
        )
        self.instructions_label = ttk.Label(left_frame, text=instructions_text, style='Info.TLabel', justify=tk.LEFT)
        self.instructions_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # 添加打开链接按钮（在首先需要下载服务器配置文件说明文本下方）
        link_button = ttk.Button(left_frame, text="🌐 打开配置文件下载页面", 
                               command=self.open_server_config_page)
        link_button.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # 配置文件选择
        self.create_file_selection(left_frame, 4, "配置文件位置", "config_file", 
                                  "选择配置文件压缩包...", "zip")
        
        # 添加游戏操作说明（在配置文件选择下方）
        game_instructions_text = (
            "1. 进入游戏\n"
            "打开饥荒联机版游戏，进入主界面，点击创建游戏\n"
            "2. 按照自己的需求创建世界\n"
            "按照正常步骤创建世界，对应的\"世界\"、\"洞穴\"、\"模组\"设置自己调整好，到人物选择界面即可断开连线"
        )
        self.game_instructions_label = ttk.Label(left_frame, text=game_instructions_text, style='Info.TLabel', justify=tk.LEFT)
        self.game_instructions_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 10))
        
        # 绑定配置事件以更新wraplength
        self.main_frame.bind("<Configure>", self.update_all_wraplengths)
        
        # SteamCMD路径
        self.create_path_input(left_frame, 10, "SteamCMD 安装目录", "steamcmd_path", 
                              "C:\\steamcmd", "SteamCMD 安装目录...，例如：C:\\steamcmd")
        
        # Steam路径
        self.create_path_input(left_frame, 13, "Steam 安装目录（用于配置模组）", "steam_path", 
                              "C:\\steam", "Steam 安装目录...，例如：C:\\steam")
        
        # 世界文件夹选择
        self.create_file_selection(left_frame, 19, "世界文件夹位置", "world_folder", 
                                  "选择想要启动的世界文件夹...，例如C:\\Users\\XXX\\Documents\\Klei\\DoNotStarveTogether\\XXX\\Cluster_1", "folder")
        
        # 按钮框架
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=22, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # 开始配置按钮
        self.start_button = ttk.Button(button_frame, text="🚀 开始配置", 
                                      command=self.start_configuration)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 重置按钮
        reset_button = ttk.Button(button_frame, text="🔄 重置", 
                                 command=self.reset_form)
        reset_button.pack(side=tk.LEFT)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left_frame, variable=self.progress_var, 
                                           maximum=100, length=500)
        self.progress_bar.grid(row=23, column=0, pady=(5, 2), sticky=(tk.W, tk.E))
        
        # 日志区域 - 独占右框架
        log_label = ttk.Label(right_frame, text="输出日志:", style='Header.TLabel')
        log_label.grid(row=0, column=0, sticky=tk.W, pady=(2, 0))
        
        self.log_text = scrolledtext.ScrolledText(right_frame, height=20, width=80, 
                                                 font=('Consolas', 8), bg='#2c3e50', fg='#ecf0f1')
        self.log_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)  # 使左右框架能垂直扩展
        
        # 初始化wraplength
        self.root.after(100, self.update_all_wraplengths)
        
        # 配置滚动区域
        self.configure_scroll_region()
        
    def create_scrollable_frame(self):
        """创建可滚动的框架"""
        # 创建主容器
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建画布
        self.canvas = tk.Canvas(container, bg='#ecf0f1')
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建垂直滚动条
        v_scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置画布
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # 创建主框架（放在画布上）
        self.main_frame = ttk.Frame(self.canvas, padding="10")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor=tk.NW)
        
        # 配置容器权重
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 绑定事件以调整滚动区域和画布窗口大小
        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # 绑定鼠标滚轮事件
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.main_frame.bind("<MouseWheel>", self.on_mousewheel)
        
    def on_frame_configure(self, event=None):
        """当框架大小改变时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event=None):
        """当画布大小改变时调整内部窗口宽度"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def on_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    def configure_scroll_region(self):
        """配置滚动区域"""
        self.root.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def create_file_selection(self, parent, row, label_text, var_name, placeholder, file_type):
        """创建文件选择组件"""
        # 标签
        label = ttk.Label(parent, text=label_text, style='Header.TLabel')
        label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(1, 5))
        
        # 帮助文本 - 现在放在标签下方，输入框上方
        help_text = f"💡 {placeholder}"
        help_label = ttk.Label(parent, text=help_text, style='Info.TLabel')
        help_label.grid(row=row+1, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # 输入框和按钮框架
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=row+2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=0, minsize=100)
        
        # 输入框
        setattr(self, var_name, tk.StringVar())
        # 设置默认值为保存的配置
        if var_name in self.saved_config:
            getattr(self, var_name).set(self.saved_config[var_name])
        entry = ttk.Entry(input_frame, textvariable=getattr(self, var_name), font=('Microsoft YaHei', 10))
        entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 浏览按钮
        browse_text = "📁 浏览文件夹" if file_type == "folder" else "📄 浏览文件"
        browse_button = ttk.Button(input_frame, text=browse_text, 
                                  command=lambda: self.browse_file(var_name, file_type))
        browse_button.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
    def create_path_input(self, parent, row, label_text, var_name, placeholder, help_text):
        """创建路径输入组件"""
        # 标签框架 - 将标签和单选框放在同一行
        label_frame = ttk.Frame(parent)
        label_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(1, 5))
        
        # 标签
        label = ttk.Label(label_frame, text=label_text, style='Header.TLabel')
        label.pack(side=tk.LEFT)
        
        # 如果是steam_path，添加单选框到标签右边
        if var_name == "steam_path":
            self.steam_mod_var = tk.BooleanVar(value=self.saved_config.get('steam_mod', True))  # 从配置加载
            check_button = tk.Checkbutton(label_frame, text="需要加载模组", variable=self.steam_mod_var,
                                   command=self.toggle_steam_path, compound='left',
                                   font=('Microsoft YaHei', 10), fg='#34495e', relief='flat')
            check_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 帮助文本 - 现在放在标签下方，输入框上方
        help_label = ttk.Label(parent, text=f"💡 {help_text}", style='Info.TLabel')
        help_label.grid(row=row+1, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # 输入框和按钮框架
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=row+2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=0, minsize=100)
        
        # 输入框
        setattr(self, var_name, tk.StringVar())
        # 设置默认值为保存的配置
        if var_name in self.saved_config:
            getattr(self, var_name).set(self.saved_config[var_name])
        entry = ttk.Entry(input_frame, textvariable=getattr(self, var_name), font=('Microsoft YaHei', 10))
        entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 浏览按钮
        browse_button = ttk.Button(input_frame, text="📁 浏览文件夹", 
                                  command=lambda: self.browse_folder(var_name))
        browse_button.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 如果是steam_path，保存输入框和浏览按钮的引用
        if var_name == "steam_path":
            self.steam_entry = entry
            self.steam_browse_button = browse_button
            self.toggle_steam_path()  # 初始化状态

    def toggle_steam_path(self):
        """切换Steam路径的启用/禁用状态"""
        if self.steam_mod_var.get():
            self.steam_entry.config(state='normal')
            self.steam_browse_button.config(state='normal')
        else:
            self.steam_entry.config(state='disabled')
            self.steam_browse_button.config(state='disabled')
        
        # 只有在所有组件初始化完成后才保存配置
        if hasattr(self, 'world_folder'):
            self.save_config()
            
    def browse_file(self, var_name, file_type):
        """浏览文件或文件夹"""
        var = getattr(self, var_name)
        
        if file_type == "folder":
            path = filedialog.askdirectory(title="选择文件夹")
        else:
            filetypes = [("ZIP文件", "*.zip"), ("所有文件", "*.*")]
            path = filedialog.askopenfilename(title="选择文件", filetypes=filetypes)
        
        if path:
            # 规范化路径
            path = os.path.normpath(path)
            
            # 校验路径
            if var_name == "steamcmd_path" and not path.lower().endswith("steamcmd"):
                messagebox.showerror("错误", "请参考示例选择")
                return
            elif var_name == "steam_path" and not path.lower().endswith("steam"):
                messagebox.showerror("错误", "请参考示例选择")
                return
            elif var_name == "world_folder":
                folder_name = os.path.basename(path)
                if not folder_name.lower().startswith("cluster_"):
                    messagebox.showerror("错误", "请参考示例选择")
                    return
        
            var.set(path)
            # 保存配置
            self.save_config()
            
    def browse_folder(self, var_name):
        """浏览文件夹"""
        var = getattr(self, var_name)
        path = filedialog.askdirectory(title="选择文件夹")
        if path:
            # 规范化路径
            path = os.path.normpath(path)
            
            # 校验路径
            if var_name == "steamcmd_path" and not path.lower().endswith("steamcmd"):
                messagebox.showerror("错误", "请参考示例选择")
                return
            elif var_name == "steam_path" and not path.lower().endswith("steam"):
                messagebox.showerror("错误", "请参考示例选择")
                return
            
            var.set(path)
            # 保存配置
            self.save_config()
            
    def reset_form(self):
        """重置表单"""
        self.config_file.set("")
        self.steamcmd_path.set("")
        self.steam_path.set("")
        self.world_folder.set("")
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        self.start_button.config(state='normal')
        
    def log_message(self, message, level="INFO"):
        """添加日志消息（线程安全）"""
        def _log():
            timestamp = time.strftime("%H:%M:%S")
            
            # 根据级别设置颜色
            color_map = {
                "INFO": "#3498db",
                "SUCCESS": "#2ecc71", 
                "WARNING": "#f39c12",
                "ERROR": "#e74c3c"
            }
            
            color = color_map.get(level, "#3498db")
            
            # 插入带颜色的文本
            self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.log_text.insert(tk.END, f"[{level}] ", level.lower())
            self.log_text.insert(tk.END, f"{message}\n", "message")
            
            # 配置标签颜色
            self.log_text.tag_config("timestamp", foreground="#95a5a6")
            self.log_text.tag_config(level.lower(), foreground=color, font=('Consolas', 9, 'bold'))
            self.log_text.tag_config("message", foreground="#ecf0f1")
            
            self.log_text.see(tk.END)
        
        self.root.after(0, _log)
        self.root.update_idletasks()
        
    def update_progress(self, value):
        """更新进度条（线程安全）"""
        def _update():
            self.progress_var.set(value)
        
        self.root.after(0, _update)
        self.root.update_idletasks()
        
    def validate_inputs(self):
        """验证输入"""
        if not self.config_file.get():
            messagebox.showerror("错误", "请选择配置文件！")
            return False
        if not self.steamcmd_path.get():
            messagebox.showerror("错误", "请选择SteamCMD安装位置！")
            return False
        if self.steam_mod_var.get() and not self.steam_path.get():
            messagebox.showerror("错误", "请选择Steam安装位置！")
            return False
        if not self.world_folder.get():
            messagebox.showerror("错误", "请选择世界文件夹！")
            return False
        return True
        
    def start_configuration(self):
        """开始配置"""
        if not self.validate_inputs():
            return
            
        # 禁用开始按钮
        self.start_button.config(state='disabled')
        
        # 在新线程中运行配置过程
        config_thread = threading.Thread(target=self.run_configuration)
        config_thread.daemon = True
        config_thread.start()
        
    def run_configuration(self):
        """运行配置过程"""
        try:
            self.log_message("开始配置饥荒联机版专用服务器...")
            
            # 步骤1: 设置路径
            klei_path = f"C:\\Users\\{self.current_user}\\Documents\\Klei\\DoNotStarveTogether"
            local_server_path = f"{klei_path}\\MyDediServer"
            
            self.log_message(f"设置Klei路径: {klei_path}")
            self.update_progress(10)
            
            # 步骤2: 解压配置文件
            self.log_message("正在解压配置文件...")
            self.extract_config_file(klei_path)
            self.log_message("配置文件解压完成", "SUCCESS")
            self.update_progress(20)
            
            # 步骤3: 清理本地服务器文件夹
            self.log_message("正在清理本地服务器文件夹...")
            self.clean_server_folder(local_server_path)
            self.log_message("保留cluster_token.txt文件", "WARNING")
            self.log_message("其他文件已删除", "SUCCESS")
            self.update_progress(35)
            
            # 步骤4: 复制世界文件
            self.log_message("正在复制世界文件...")
            self.copy_world_files(local_server_path)
            self.log_message("世界文件复制完成", "SUCCESS")
            self.update_progress(50)
            
            # 步骤5: 复制模组（仅当勾选时执行）
            if self.steam_mod_var.get():
                self.log_message("正在复制模组文件...")
                self.copy_mods()
                self.log_message("模组文件复制完成", "SUCCESS")
            else:
                self.log_message("跳过模组复制", "INFO")
            self.update_progress(70)
            
            # 步骤6: 运行SteamCMD更新
            self.log_message("正在运行SteamCMD更新...")
            self.update_steamcmd()
            self.log_message("SteamCMD更新完成", "SUCCESS")
            self.update_progress(85)
            
            # 步骤7: 启动服务器
            self.log_message("正在启动服务器...")
            self.start_servers()
            self.log_message("服务器启动完成！", "SUCCESS")
            self.update_progress(100)
            
            self.log_message("🎉 配置完成！您的饥荒联机版本地服务器正在启动！", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"配置过程中出现错误: {str(e)}", "ERROR")
            import traceback
            self.log_message(f"详细错误信息: {traceback.format_exc()}", "ERROR")
        finally:
            # 重新启用开始按钮
            self.start_button.config(state='normal')
            
    def extract_config_file(self, target_path):
        """解压配置文件"""
        config_file = self.config_file.get()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
            
        with zipfile.ZipFile(config_file, 'r') as zip_ref:
            zip_ref.extractall(target_path)
            
    def clean_server_folder(self, server_path):
        """清理服务器文件夹"""
        if not os.path.exists(server_path):
            os.makedirs(server_path)
            return
            
        # 备份cluster_token.txt
        cluster_token_path = os.path.join(server_path, "cluster_token.txt")
        backup_path = os.path.join(server_path, "cluster_token.txt.bak")
        
        if os.path.exists(cluster_token_path):
            shutil.copy2(cluster_token_path, backup_path)
            
        # 删除除cluster_token.txt外的所有文件和文件夹
        for item in os.listdir(server_path):
            item_path = os.path.join(server_path, item)
            if item != "cluster_token.txt":
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                    
        # 恢复cluster_token.txt
        if os.path.exists(backup_path):
            shutil.move(backup_path, cluster_token_path)
                    
    def copy_world_files(self, target_path):
        """复制世界文件"""
        world_folder = self.world_folder.get()
        if not os.path.exists(world_folder):
            raise FileNotFoundError(f"世界文件夹不存在: {world_folder}")
            
        for item in os.listdir(world_folder):
            src = os.path.join(world_folder, item)
            dst = os.path.join(target_path, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
                
    def copy_mods(self):
        """复制模组文件"""
        steam_path = self.steam_path.get()
        steamcmd_path = self.steamcmd_path.get()
        
        workshop_path = f"{steam_path}\\steamapps\\workshop\\content\\322330"
        mods_path = f"{steamcmd_path}\\steamapps\\common\\Don't Starve Together Dedicated Server\\mods"
        
        self.log_message(f"Workshop路径: {workshop_path}")
        self.log_message(f"Mods目标路径: {mods_path}")
        
        if not os.path.exists(workshop_path):
            self.log_message(f"警告: Steam Workshop路径不存在: {workshop_path}", "WARNING")
            return
            
        # 初始化计数器
        workshop_count = 0
        local_count = 0
        
        # 删除现有mods文件夹
        if os.path.exists(mods_path):
            self.log_message("删除现有mods文件夹...")
            shutil.rmtree(mods_path)
        os.makedirs(mods_path)
        self.log_message("创建新的mods文件夹")
        
        # 复制workshop内容并重命名
        if os.path.exists(workshop_path):
            self.log_message("开始复制workshop模组...")
            for item in os.listdir(workshop_path):
                src = os.path.join(workshop_path, item)
                dst = os.path.join(mods_path, f"workshop-{item}")
                
                if os.path.isdir(src):
                    try:
                        shutil.copytree(src, dst)
                        workshop_count += 1
                        self.log_message(f"复制workshop模组: {item}")
                    except Exception as e:
                        self.log_message(f"复制workshop模组 {item} 时出错: {str(e)}", "WARNING")
            
            self.log_message(f"共复制 {workshop_count} 个workshop模组")
                    
        # 复制本地mods
        local_mods_path = f"{steam_path}\\steamapps\\common\\Don't Starve Together\\mods"
        if os.path.exists(local_mods_path):
            self.log_message("开始复制本地模组...")
            for item in os.listdir(local_mods_path):
                src = os.path.join(local_mods_path, item)
                dst = os.path.join(mods_path, item)
                
                if os.path.isdir(src):
                    try:
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                        local_count += 1
                        self.log_message(f"复制本地模组: {item}")
                    except Exception as e:
                        self.log_message(f"复制本地模组 {item} 时出错: {str(e)}", "WARNING")
            
            self.log_message(f"共复制 {local_count} 个本地模组")
        
        total_count = workshop_count + local_count
        self.log_message(f"模组复制完成，总计 {total_count} 个模组", "SUCCESS")
            
    def update_steamcmd(self):
        """更新SteamCMD"""
        steamcmd_path = self.steamcmd_path.get()
        steamcmd_exe = f"{steamcmd_path}\\steamcmd.exe"
        
        if not os.path.exists(steamcmd_exe):
            raise FileNotFoundError(f"SteamCMD不存在: {steamcmd_exe}")
            
        cmd = [steamcmd_exe, "+login", "anonymous", "+app_update", "343050", "validate", "+quit"]
        self.log_message(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 使用更安全的方式执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=600,  # 增加超时时间到10分钟
                encoding='utf-8',
                errors='ignore'  # 忽略编码错误
            )
            
            # 输出命令执行结果到日志
            if result.stdout:
                # 限制输出长度，避免日志过长
                output_lines = result.stdout.split('\n')
                for line in output_lines[:50]:  # 只显示前50行
                    if line.strip():
                        self.log_message(f"输出: {line}")
                if len(output_lines) > 50:
                    self.log_message(f"... 还有 {len(output_lines) - 50} 行输出被省略", "INFO")
                    
            if result.stderr:
                error_lines = result.stderr.split('\n')
                for line in error_lines[:20]:  # 只显示前20行错误
                    if line.strip():
                        self.log_message(f"错误: {line}", "WARNING")
                if len(error_lines) > 20:
                    self.log_message(f"... 还有 {len(error_lines) - 20} 行错误被省略", "WARNING")
            
            # 检查返回码
            if result.returncode != 0:
                self.log_message(f"SteamCMD返回非零退出码: {result.returncode}", "WARNING")
                # 不抛出异常，继续执行，因为有些警告不影响使用
            else:
                self.log_message("SteamCMD更新成功完成", "SUCCESS")
                
        except subprocess.TimeoutExpired:
            self.log_message("SteamCMD更新超时，但可能仍在运行中", "WARNING")
        except Exception as e:
            self.log_message(f"执行SteamCMD时发生错误: {str(e)}", "ERROR")
            # 不抛出异常，继续执行
            
    def start_servers(self):
        """启动服务器"""
        steamcmd_path = self.steamcmd_path.get()
        server_path = f"{steamcmd_path}\\steamapps\\common\\Don't Starve Together Dedicated Server\\bin"
        
        if not os.path.exists(server_path):
            raise FileNotFoundError(f"服务器路径不存在: {server_path}")
            
        # 检查可执行文件是否存在
        server_exe = f"{server_path}\\dontstarve_dedicated_server_nullrenderer.exe"
        if not os.path.exists(server_exe):
            raise FileNotFoundError(f"服务器可执行文件不存在: {server_exe}")
            
        # 启动Master服务器
        master_cmd = [
            server_exe,
            "-console", "-cluster", "MyDediServer", "-shard", "Master"
        ]
        
        # 启动Caves服务器
        caves_cmd = [
            server_exe,
            "-console", "-cluster", "MyDediServer", "-shard", "Caves"
        ]
        
        self.log_message(f"切换到目录: {server_path}")
        self.log_message("启动Master服务器...")
        self.log_message(f"Master命令: {' '.join(master_cmd)}")
        
        self.log_message("启动Caves服务器...")
        self.log_message(f"Caves命令: {' '.join(caves_cmd)}")
        
        try:
            # 启动服务器进程
            master_process = subprocess.Popen(master_cmd, cwd=server_path)
            caves_process = subprocess.Popen(caves_cmd, cwd=server_path)
            
            self.log_message(f"Master服务器进程ID: {master_process.pid}")
            self.log_message(f"Caves服务器进程ID: {caves_process.pid}")
            self.log_message("服务器启动命令已执行", "SUCCESS")
        except Exception as e:
            self.log_message(f"启动服务器时出错: {str(e)}", "ERROR")
            # 不抛出异常，继续执行

    def update_wraplength(self, label, event=None):
        """动态更新Label的wraplength以适配左侧框架大小"""
        if event:
            width = event.width  # 无缓冲，精确在边界换行
        else:
            width = label.winfo_width()
        if width > 0:
            label.config(wraplength=width)
            
    def update_all_wraplengths(self, event=None):
        """更新所有需要自动换行的标签"""
        self.update_wraplength(self.instructions_label, event)
        self.update_wraplength(self.game_instructions_label, event)

    def open_server_config_page(self):
        """打开配置文件下载页面"""
        url = "https://accounts.klei.com/account/game/servers?game=DontStarveTogether"
        try:
            import webbrowser
            webbrowser.open(url)
            self.log_message(f"已打开浏览器访问: {url}", "INFO")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开浏览器: {str(e)}\n请手动访问以下链接：\n{url}")
            self.log_message(f"无法打开浏览器，请手动访问: {url}", "ERROR")

    def load_config(self):
        """加载保存的配置"""
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 添加默认值
                    config.setdefault('steam_mod', True)
                    # 调试：输出加载的配置
                    self.log_message(f"加载配置: {config}", "INFO")
                    return config
            except (json.JSONDecodeError, FileNotFoundError):
                self.log_message("配置文件损坏或不存在，使用默认配置", "WARNING")
                return {'steam_mod': True}
        self.log_message("配置文件不存在，使用默认配置", "INFO")
        return {'steam_mod': True}
    
    def save_config(self):
        """保存当前配置到文件"""
        config = {
            'config_file': self.config_file.get(),
            'steamcmd_path': self.steamcmd_path.get(),
            'steam_path': self.steam_path.get(),
            'world_folder': self.world_folder.get(),
            'steam_mod': self.steam_mod_var.get()
        }
        
        try:
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                # 调试：输出保存的配置
                self.log_message(f"保存配置: {config}", "INFO")
        except Exception as e:
            self.log_message(f"保存配置失败: {str(e)}", "ERROR")

def main():
    """主函数"""
    root = tk.Tk()
    app = DSTServerConfigTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
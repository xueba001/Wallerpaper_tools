import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import json
import os

class WallpaperEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("壁纸区域编辑器")
        self.root.geometry("1200x800")
        
        # 数据存储
        self.background_image = None
        self.background_photo = None
        self.original_image_path = None  # 存储原始图片路径
        self.original_image = None  # 存储原始图片（未缩放）
        self.regions = []  # 存储所有区域
        self.selected_region = None
        self.drag_start = None
        self.is_dragging = False
        self.is_resizing = False
        self.resize_handle = None
        
        # 自动保存相关
        self.auto_save_enabled = True  # 是否启用自动保存
        self.auto_save_interval = 30000  # 自动保存间隔（毫秒），默认30秒
        self.auto_save_timer = None  # 自动保存定时器
        self.project_modified = False  # 项目是否已修改
        self.auto_save_path = None  # 自动保存文件路径
        
        self.setup_ui()
        
        # 启动自动保存
        if self.auto_save_enabled:
            self.start_auto_save()
        
    def setup_ui(self):
        # 设置现代化样式
        self.setup_modern_styles()
        
        # 创建主框架 - 使用现代化背景
        main_frame = tk.Frame(self.root, bg='#f8fafc')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板 - 现代化卡片设计
        control_frame = tk.Frame(main_frame, bg='#ffffff', width=260, relief='flat', bd=0)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(15, 10), pady=15)
        control_frame.pack_propagate(False)
        
        # 标题区域
        title_frame = tk.Frame(control_frame, bg='#ffffff', height=50)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        # 应用标题
        title_label = tk.Label(title_frame, text="🎨 壁纸区域编辑器", 
                              font=('Microsoft YaHei UI', 14, 'bold'), 
                              bg='#ffffff', fg='#1e293b')
        title_label.pack(pady=10)
        
        # 文件操作卡片
        file_card = self.create_modern_card(control_frame, "📁 文件操作", 15)
        
        # 现代化按钮
        self.create_modern_button(file_card, "📂 打开壁纸", self.load_wallpaper, '#3b82f6')
        self.create_modern_button(file_card, "💾 保存壁纸", self.save_wallpaper, '#10b981')
        self.create_modern_button(file_card, "💾 保存项目", self.save_project, '#8b5cf6')
        self.create_modern_button(file_card, "📂 加载项目", self.load_project, '#f59e0b')
        
        # 自动保存状态 - 现代化设计
        auto_save_frame = tk.Frame(file_card, bg='#ffffff')
        auto_save_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.auto_save_var = tk.BooleanVar(value=self.auto_save_enabled)
        self.auto_save_check = tk.Checkbutton(auto_save_frame, text="🔄 自动保存", 
                                             variable=self.auto_save_var,
                                             command=self.toggle_auto_save,
                                             font=('Microsoft YaHei UI', 10),
                                             bg='#ffffff', fg='#374151',
                                             selectcolor='#3b82f6', activebackground='#ffffff')
        self.auto_save_check.pack(side=tk.LEFT)
        
        # 自动保存状态指示器 - 现代化设计
        self.auto_save_status = tk.Label(auto_save_frame, text="●", 
                                        font=('Arial', 12), foreground="#10b981", bg='#ffffff')
        self.auto_save_status.pack(side=tk.RIGHT)
        
        # 添加状态文字说明
        self.auto_save_text = tk.Label(auto_save_frame, text="已启用", 
                                      font=('Microsoft YaHei UI', 9), 
                                      foreground="#64748b", bg='#ffffff')
        self.auto_save_text.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 区域操作卡片
        region_card = self.create_modern_card(control_frame, "🎯 区域操作", 15)
        
        self.create_modern_button(region_card, "➕ 添加区域", self.add_region, '#3b82f6')
        self.create_modern_button(region_card, "⚡ 一键生成模板", self.generate_template_regions, '#8b5cf6')
        self.create_modern_button(region_card, "🗑️ 删除选中区域", self.delete_region, '#ef4444')
        self.create_modern_button(region_card, "🧹 清除所有区域", self.clear_regions, '#f59e0b')
        
        # 区域属性卡片
        self.attr_card = self.create_modern_card(control_frame, "⚙️ 区域属性", 15)
        
        # 初始化变量
        self.name_var = tk.StringVar()
        self.text_var = tk.StringVar()
        self.alpha_var = tk.IntVar(value=128)
        
        # 现代化输入框
        self.name_entry = self.create_modern_input(self.attr_card, "区域名称", self.name_var, self.update_region_name)
        self.text_entry = self.create_modern_input(self.attr_card, "区域文字", self.text_var, self.update_region_text)
        
        # 现代化滑块
        self.alpha_scale = self.create_modern_slider(self.attr_card, "透明度", self.alpha_var, self.update_region_alpha)
        
        # 现代化颜色选择
        self.color_button = self.create_modern_color_picker(self.attr_card)
        
        # 右侧画布区域 - 现代化设计
        canvas_frame = tk.Frame(main_frame, bg='#f8fafc')
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)
        
        # 画布标题
        canvas_title = tk.Label(canvas_frame, text="🖼️ 画布预览", 
                               font=('Microsoft YaHei UI', 14, 'bold'), 
                               bg='#f8fafc', fg='#1e293b')
        canvas_title.pack(pady=(0, 10))
        
        # 创建画布 - 现代化边框
        self.canvas = tk.Canvas(canvas_frame, bg='#ffffff', cursor='crosshair', 
                               relief='flat', bd=2, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        self.canvas.bind('<Motion>', self.on_canvas_motion)
        
        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_resize)
        
        # 初始化属性面板状态
        self.update_attribute_panel()
    
    def setup_modern_styles(self):
        """设置现代化样式"""
        # 配置现代化颜色方案
        self.colors = {
            'primary': '#3b82f6',      # 蓝色
            'success': '#10b981',      # 绿色
            'warning': '#f59e0b',      # 橙色
            'danger': '#ef4444',       # 红色
            'purple': '#8b5cf6',       # 紫色
            'background': '#f8fafc',   # 浅灰背景
            'card': '#ffffff',         # 卡片背景
            'text': '#1e293b',         # 深色文字
            'text_light': '#64748b',   # 浅色文字
            'border': '#e2e8f0'        # 边框颜色
        }
    
    def create_modern_card(self, parent, title, padding):
        """创建现代化卡片"""
        # 卡片容器
        card_frame = tk.Frame(parent, bg='#ffffff', relief='flat', bd=0)
        card_frame.pack(fill=tk.X, pady=(0, padding))
        
        # 卡片标题
        title_label = tk.Label(card_frame, text=title, 
                              font=('Microsoft YaHei UI', 12, 'bold'), 
                              bg='#ffffff', fg='#1e293b')
        title_label.pack(anchor=tk.W, pady=(12, 8), padx=12)
        
        # 卡片内容区域
        content_frame = tk.Frame(card_frame, bg='#ffffff')
        content_frame.pack(fill=tk.X, padx=12, pady=(0, 12))
        
        return content_frame
    
    def create_modern_button(self, parent, text, command, color):
        """创建现代化按钮"""
        button = tk.Button(parent, text=text, command=command,
                          font=('Microsoft YaHei UI', 9),
                          bg=color, fg='white', relief='flat', bd=0,
                          activebackground=self.darken_color(color),
                          activeforeground='white',
                          cursor='hand2', padx=15, pady=5)
        button.pack(fill=tk.X, pady=2)
        
        # 添加现代化悬停效果
        def on_enter(e):
            button.config(bg=self.darken_color(color))
            # 添加轻微阴影效果
            button.config(relief='raised', bd=1)
        def on_leave(e):
            button.config(bg=color)
            button.config(relief='flat', bd=0)
        
        # 添加点击效果
        def on_click(e):
            button.config(bg=self.darken_color(color))
            # 短暂延迟后恢复
            self.root.after(100, lambda: button.config(bg=color))
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        button.bind('<Button-1>', on_click)
        
        return button
    
    def create_modern_input(self, parent, label_text, var, callback):
        """创建现代化输入框"""
        # 标签
        label = tk.Label(parent, text=f"{label_text}:", 
                        font=('Microsoft YaHei UI', 10),
                        bg='#ffffff', fg='#374151')
        label.pack(anchor=tk.W, pady=(8, 3))
        
        # 输入框
        entry = tk.Entry(parent, textvariable=var, font=('Microsoft YaHei UI', 10),
                        relief='flat', bd=1, highlightthickness=1,
                        bg='#ffffff', fg='#1e293b', insertbackground='#3b82f6')
        entry.pack(fill=tk.X, pady=(0, 3), ipady=6)
        entry.bind('<KeyRelease>', callback)
        
        # 输入框焦点效果
        def on_focus_in(e):
            entry.config(highlightcolor='#3b82f6', highlightbackground='#3b82f6')
        def on_focus_out(e):
            entry.config(highlightcolor='#e2e8f0', highlightbackground='#e2e8f0')
        
        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)
        
        return entry
    
    def create_modern_slider(self, parent, label_text, var, callback):
        """创建现代化滑块"""
        # 标签
        label = tk.Label(parent, text=f"{label_text}:", 
                        font=('Microsoft YaHei UI', 10),
                        bg='#ffffff', fg='#374151')
        label.pack(anchor=tk.W, pady=(8, 3))
        
        # 滑块容器
        slider_frame = tk.Frame(parent, bg='#ffffff')
        slider_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 滑块
        scale = tk.Scale(slider_frame, from_=0, to=255, variable=var, 
                        orient=tk.HORIZONTAL, command=callback,
                        bg='#ffffff', fg='#1e293b', 
                        activebackground='#3b82f6',
                        troughcolor='#e2e8f0', 
                        highlightthickness=0, bd=0,
                        font=('Microsoft YaHei UI', 9))
        scale.pack(fill=tk.X, pady=3)
        
        return scale
    
    def create_modern_color_picker(self, parent):
        """创建现代化颜色选择器"""
        # 标签
        label = tk.Label(parent, text="区域颜色:", 
                        font=('Microsoft YaHei UI', 10),
                        bg='#ffffff', fg='#374151')
        label.pack(anchor=tk.W, pady=(8, 3))
        
        # 颜色选择按钮
        color_button = tk.Button(parent, text="🎨 选择颜色", 
                               command=self.choose_color,
                               font=('Microsoft YaHei UI', 9),
                               bg='#8b5cf6', fg='white', relief='flat', bd=0,
                               activebackground=self.darken_color('#8b5cf6'),
                               activeforeground='white',
                               cursor='hand2', padx=15, pady=5)
        color_button.pack(fill=tk.X, pady=(0, 3))
        
        # 添加悬停效果
        def on_enter(e):
            color_button.config(bg=self.darken_color('#8b5cf6'))
        def on_leave(e):
            color_button.config(bg='#8b5cf6')
        
        color_button.bind('<Enter>', on_enter)
        color_button.bind('<Leave>', on_leave)
        
        return color_button
    
    def darken_color(self, color):
        """使颜色变暗"""
        color_map = {
            '#3b82f6': '#2563eb',  # 蓝色变暗
            '#10b981': '#059669',  # 绿色变暗
            '#f59e0b': '#d97706',  # 橙色变暗
            '#ef4444': '#dc2626',  # 红色变暗
            '#8b5cf6': '#7c3aed'   # 紫色变暗
        }
        return color_map.get(color, color)
        
    def load_wallpaper(self):
        """加载壁纸"""
        file_path = filedialog.askopenfilename(
            title="🖼️ 选择壁纸",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            try:
                self.original_image = Image.open(file_path)  # 保存原始图片
                self.background_image = self.original_image.copy()  # 工作副本
                self.original_image_path = file_path  # 存储原始文件路径
                # 调整图片大小以适应窗口
                self.resize_image_to_fit()
                self.display_image()
                self.clear_regions()  # 清除之前的区域
            except Exception as e:
                messagebox.showerror("错误", f"无法加载图片: {str(e)}")
    
    def resize_image_to_fit(self):
        """调整图片大小以适应画布"""
        if not self.original_image:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # 如果画布还没有初始化，使用默认大小
            canvas_width, canvas_height = 800, 600
            
        img_width, img_height = self.original_image.size
        
        # 计算缩放比例，允许放大图片
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.scale = min(scale_x, scale_y)  # 移除1.0限制，允许放大
        
        new_width = int(img_width * self.scale)
        new_height = int(img_height * self.scale)
        
        # 从原始图片重新缩放
        self.background_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image_width = new_width
        self.image_height = new_height
    
    def display_image(self):
        """显示图片"""
        if self.background_image:
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_photo)
            self.redraw_regions()
    
    def on_window_resize(self, event):
        """窗口大小变化时的处理"""
        # 只有当窗口大小真正改变时才重新调整图片
        if event.widget == self.root and self.original_image:
            # 延迟执行，避免频繁调整
            self.root.after(100, self.handle_resize)
    
    def handle_resize(self):
        """处理窗口大小变化"""
        if self.original_image:
            self.resize_image_to_fit()
            self.display_image()
    
    def add_region(self):
        """添加新区域"""
        if not self.background_image:
            messagebox.showwarning("警告", "请先加载壁纸")
            return
            
        # 创建默认区域
        region = {
            'x': 50,
            'y': 50,
            'width': 200,
            'height': 100,
            'name': f"区域 {len(self.regions) + 1}",
            'text': f"区域 {len(self.regions) + 1}",
            'color': '#FF6B6B',
            'alpha': 128
        }
        self.regions.append(region)
        self.redraw_regions()
        self.select_region(len(self.regions) - 1)
        # 标记项目已修改，触发自动保存
        self.mark_project_modified()
    
    def delete_region(self):
        """删除选中的区域"""
        if self.selected_region is not None:
            del self.regions[self.selected_region]
            self.selected_region = None
            self.update_attribute_panel()
            self.redraw_regions()
            # 标记项目已修改，触发自动保存
            self.mark_project_modified()
    
    def clear_regions(self):
        """清除所有区域"""
        self.regions = []
        self.selected_region = None
        self.update_attribute_panel()
        self.redraw_regions()
        # 标记项目已修改，触发自动保存
        self.mark_project_modified()
    
    def generate_template_regions(self):
        """一键生成模板区域"""
        if not self.background_image:
            messagebox.showwarning("警告", "请先加载壁纸")
            return
        
        # 清除现有区域
        self.clear_regions()
        
        # 获取图片尺寸
        img_width = self.image_width
        img_height = self.image_height
        
        # 根据图片尺寸计算区域大小和位置
        # 左侧竖条区域 (待处理)
        left_width = int(img_width * 0.15)  # 15%宽度
        left_height = int(img_height * 0.8)  # 80%高度
        left_x = int(img_width * 0.05)  # 5%左边距
        left_y = int(img_height * 0.1)  # 10%上边距
        
        # 顶部绿色区域 (挂起)
        top_width = int(img_width * 0.3)  # 30%宽度
        top_height = int(img_height * 0.15)  # 15%高度
        top_x = left_x + left_width + int(img_width * 0.02)  # 2%间距
        top_y = int(img_height * 0.1)  # 10%上边距
        
        # 中间主区域 (处理中)
        main_width = int(img_width * 0.4)  # 40%宽度
        main_height = int(img_height * 0.6)  # 60%高度
        main_x = left_x + left_width + int(img_width * 0.02)  # 2%间距
        main_y = top_y + top_height + int(img_height * 0.02)  # 2%间距
        
        # 右侧参考区域
        right_width = int(img_width * 0.25)  # 25%宽度
        right_height = int(img_height * 0.8)  # 80%高度
        right_x = main_x + main_width + int(img_width * 0.02)  # 2%间距
        right_y = int(img_height * 0.1)  # 10%上边距
        
        # 底部区域 (迭代)
        bottom_width = int(img_width * 0.3)  # 30%宽度
        bottom_height = int(img_height * 0.15)  # 15%高度
        bottom_x = main_x
        bottom_y = main_y + main_height + int(img_height * 0.02)  # 2%间距
        
        # 创建模板区域
        template_regions = [
            {
                'x': left_x,
                'y': left_y,
                'width': left_width,
                'height': left_height,
                'name': '待处理',
                'text': '待处理',
                'color': '#FFD700',  # 金黄色
                'alpha': 150
            },
            {
                'x': top_x,
                'y': top_y,
                'width': top_width,
                'height': top_height,
                'name': '挂起',
                'text': '挂起',
                'color': '#90EE90',  # 浅绿色
                'alpha': 150
            },
            {
                'x': main_x,
                'y': main_y,
                'width': main_width,
                'height': main_height,
                'name': '处理中',
                'text': '处理中',
                'color': '#CD853F',  # 棕色
                'alpha': 150
            },
            {
                'x': right_x,
                'y': right_y,
                'width': right_width,
                'height': right_height,
                'name': '参考',
                'text': '参考',
                'color': '#D3D3D3',  # 浅灰色
                'alpha': 150
            },
            {
                'x': bottom_x,
                'y': bottom_y,
                'width': bottom_width,
                'height': bottom_height,
                'name': '迭代',
                'text': '迭代',
                'color': '#D3D3D3',  # 浅灰色
                'alpha': 150
            }
        ]
        
        # 添加所有模板区域
        self.regions = template_regions
        self.redraw_regions()
        # 标记项目已修改，触发自动保存
        self.mark_project_modified()
    
    def on_canvas_click(self, event):
        """画布点击事件"""
        if not self.background_image:
            return
            
        x, y = event.x, event.y
        
        # 检查是否点击了区域
        clicked_region = None
        resize_handle = None
        
        for i, region in enumerate(self.regions):
            if (region['x'] <= x <= region['x'] + region['width'] and
                region['y'] <= y <= region['y'] + region['height']):
                clicked_region = i
                
                # 检查是否点击了调整大小的手柄
                handle_size = 8
                if (region['x'] + region['width'] - handle_size <= x <= region['x'] + region['width'] and
                    region['y'] + region['height'] - handle_size <= y <= region['y'] + region['height']):
                    resize_handle = 'se'  # 右下角
                elif (region['x'] <= x <= region['x'] + handle_size and
                      region['y'] <= y <= region['y'] + handle_size):
                    resize_handle = 'nw'  # 左上角
                elif (region['x'] + region['width'] - handle_size <= x <= region['x'] + region['width'] and
                      region['y'] <= y <= region['y'] + handle_size):
                    resize_handle = 'ne'  # 右上角
                elif (region['x'] <= x <= region['x'] + handle_size and
                      region['y'] + region['height'] - handle_size <= y <= region['y'] + region['height']):
                    resize_handle = 'sw'  # 左下角
                break
        
        if clicked_region is not None:
            self.select_region(clicked_region)
            if resize_handle:
                self.is_resizing = True
                self.resize_handle = resize_handle
                self.drag_start = (x, y)
                # 保存拖拽开始时的区域状态
                self.drag_start_region = {
                    'x': self.regions[clicked_region]['x'],
                    'y': self.regions[clicked_region]['y'],
                    'width': self.regions[clicked_region]['width'],
                    'height': self.regions[clicked_region]['height']
                }
            else:
                self.is_dragging = True
                self.drag_start = (x - self.regions[clicked_region]['x'], y - self.regions[clicked_region]['y'])
        else:
            self.selected_region = None
            self.update_attribute_panel()
            self.redraw_regions()
    
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if self.selected_region is None:
            return
            
        x, y = event.x, event.y
        region = self.regions[self.selected_region]
        
        if self.is_dragging and self.drag_start:
            # 拖拽移动区域
            new_x = x - self.drag_start[0]
            new_y = y - self.drag_start[1]
            
            # 限制在画布范围内
            new_x = max(0, min(new_x, self.image_width - region['width']))
            new_y = max(0, min(new_y, self.image_height - region['height']))
            
            region['x'] = new_x
            region['y'] = new_y
            self.redraw_regions()
            
        elif self.is_resizing and self.drag_start and self.resize_handle:
            # 调整区域大小 - 使用绝对位置计算
            start_x, start_y = self.drag_start
            start_region = self.drag_start_region  # 拖拽开始时的区域状态
            
            if self.resize_handle == 'se':  # 右下角
                new_width = max(50, x - start_region['x'])
                new_height = max(30, y - start_region['y'])
                region['width'] = min(new_width, self.image_width - region['x'])
                region['height'] = min(new_height, self.image_height - region['y'])
                
            elif self.resize_handle == 'nw':  # 左上角
                new_width = max(50, start_region['x'] + start_region['width'] - x)
                new_height = max(30, start_region['y'] + start_region['height'] - y)
                new_x = x
                new_y = y
                
                if new_x >= 0 and new_y >= 0:
                    region['x'] = new_x
                    region['y'] = new_y
                    region['width'] = new_width
                    region['height'] = new_height
                    
            elif self.resize_handle == 'ne':  # 右上角
                new_width = max(50, x - start_region['x'])
                new_height = max(30, start_region['y'] + start_region['height'] - y)
                new_y = y
                
                if new_y >= 0 and new_width <= self.image_width - region['x']:
                    region['y'] = new_y
                    region['width'] = new_width
                    region['height'] = new_height
                    
            elif self.resize_handle == 'sw':  # 左下角
                new_width = max(50, start_region['x'] + start_region['width'] - x)
                new_height = max(30, y - start_region['y'])
                new_x = x
                
                if new_x >= 0 and new_height <= self.image_height - region['y']:
                    region['x'] = new_x
                    region['width'] = new_width
                    region['height'] = new_height
            
            self.redraw_regions()
    
    def on_canvas_release(self, event):
        """画布释放事件"""
        # 如果进行了拖拽或调整大小操作，标记项目已修改
        if self.is_dragging or self.is_resizing:
            self.mark_project_modified()
            
        self.is_dragging = False
        self.is_resizing = False
        self.drag_start = None
        self.resize_handle = None
    
    def on_canvas_motion(self, event):
        """画布鼠标移动事件"""
        if not self.background_image:
            return
            
        x, y = event.x, event.y
        
        # 检查鼠标是否在调整大小手柄上
        cursor = 'crosshair'
        if self.selected_region is not None:
            region = self.regions[self.selected_region]
            handle_size = 8
            
            # 检查是否在调整大小手柄上
            if (region['x'] + region['width'] - handle_size <= x <= region['x'] + region['width'] and
                region['y'] + region['height'] - handle_size <= y <= region['y'] + region['height']):
                cursor = 'sizing'  # 右下角
            elif (region['x'] <= x <= region['x'] + handle_size and
                  region['y'] <= y <= region['y'] + handle_size):
                cursor = 'sizing'  # 左上角
            elif (region['x'] + region['width'] - handle_size <= x <= region['x'] + region['width'] and
                  region['y'] <= y <= region['y'] + handle_size):
                cursor = 'sizing'  # 右上角
            elif (region['x'] <= x <= region['x'] + handle_size and
                  region['y'] + region['height'] - handle_size <= y <= region['y'] + region['height']):
                cursor = 'sizing'  # 左下角
            else:
                cursor = 'fleur'  # 移动光标
        
        self.canvas.config(cursor=cursor)
    
    def select_region(self, index):
        """选择区域"""
        self.selected_region = index
        self.update_attribute_panel()
        self.redraw_regions()
    
    def update_attribute_panel(self):
        """更新属性面板"""
        if self.selected_region is not None and self.selected_region < len(self.regions):
            region = self.regions[self.selected_region]
            self.name_var.set(region['name'])
            self.text_var.set(region['text'])
            self.alpha_var.set(region['alpha'])
        else:
            self.name_var.set("")
            self.text_var.set("")
            self.alpha_var.set(128)
    
    def update_region_name(self, event=None):
        """更新区域名称"""
        if self.selected_region is not None:
            self.regions[self.selected_region]['name'] = self.name_var.get()
            # 标记项目已修改，触发自动保存
            self.mark_project_modified()
    
    def update_region_text(self, event=None):
        """更新区域文字"""
        if self.selected_region is not None:
            self.regions[self.selected_region]['text'] = self.text_var.get()
            self.redraw_regions()
            # 标记项目已修改，触发自动保存
            self.mark_project_modified()
    
    def update_region_alpha(self, event=None):
        """更新区域透明度"""
        if self.selected_region is not None:
            self.regions[self.selected_region]['alpha'] = self.alpha_var.get()
            self.redraw_regions()
            # 标记项目已修改，触发自动保存
            self.mark_project_modified()
    
    def choose_color(self):
        """选择颜色"""
        if self.selected_region is not None:
            color = colorchooser.askcolor(title="选择区域颜色")
            if color[1]:  # 如果用户选择了颜色
                self.regions[self.selected_region]['color'] = color[1]
                self.redraw_regions()
                # 标记项目已修改，触发自动保存
                self.mark_project_modified()
    
    def redraw_regions(self):
        """重绘所有区域"""
        if not self.background_image:
            return
            
        # 清除之前的区域绘制
        self.canvas.delete("region")
        
        for i, region in enumerate(self.regions):
            # 创建半透明覆盖层
            overlay = Image.new('RGBA', (region['width'], region['height']), 
                              (*self.hex_to_rgb(region['color']), region['alpha']))
            
            # 创建覆盖层图片
            overlay_photo = ImageTk.PhotoImage(overlay)
            
            # 在画布上绘制区域
            region_id = self.canvas.create_image(
                region['x'], region['y'], 
                anchor=tk.NW, 
                image=overlay_photo,
                tags="region"
            )
            
            # 保存图片引用防止被垃圾回收
            if not hasattr(self, 'overlay_images'):
                self.overlay_images = []
            self.overlay_images.append(overlay_photo)
            
            # 绘制区域文字（左上角位置）
            if region['text']:
                # 检查文字长度，如果太长则截断显示
                display_text = region['text']
                if len(display_text) > 20:  # 如果文字超过20个字符，截断显示
                    display_text = display_text[:17] + "..."
                
                text_id = self.canvas.create_text(
                    region['x'] + 3,  # 置顶显示，留3像素边距
                    region['y'] + 3,  # 置顶显示，留3像素边距
                    text=display_text,
                    fill='white',
                    font=('Arial', 9, 'bold'),  # 使用更小但加粗的字体
                    tags="region",
                    anchor='nw'  # 左对齐
                )
            
            # 如果是选中区域，绘制边框和调整大小手柄
            if i == self.selected_region:
                # 绘制边框
                self.canvas.create_rectangle(
                    region['x'], region['y'],
                    region['x'] + region['width'], region['y'] + region['height'],
                    outline='yellow', width=3, tags="region"
                )
                
                # 绘制调整大小手柄
                handle_size = 8
                # 四个角的手柄
                handles = [
                    (region['x'] - handle_size//2, region['y'] - handle_size//2, 'nw'),  # 左上角
                    (region['x'] + region['width'] - handle_size//2, region['y'] - handle_size//2, 'ne'),  # 右上角
                    (region['x'] - handle_size//2, region['y'] + region['height'] - handle_size//2, 'sw'),  # 左下角
                    (region['x'] + region['width'] - handle_size//2, region['y'] + region['height'] - handle_size//2, 'se')  # 右下角
                ]
                
                for handle_x, handle_y, handle_type in handles:
                    self.canvas.create_rectangle(
                        handle_x, handle_y,
                        handle_x + handle_size, handle_y + handle_size,
                        fill='yellow', outline='black', width=1, tags="region"
                    )
    
    def hex_to_rgb(self, hex_color):
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def save_wallpaper(self):
        """保存壁纸"""
        if not self.original_image or not self.regions:
            messagebox.showwarning("警告", "没有可保存的内容")
            return
            
        # 使用原始图片创建输出图片
        output_image = self.original_image.copy().convert('RGBA')
        
        # 绘制所有区域
        for region in self.regions:
            # 计算原始图片中的坐标和尺寸
            original_x = int(region['x'] / self.scale)
            original_y = int(region['y'] / self.scale)
            original_width = int(region['width'] / self.scale)
            original_height = int(region['height'] / self.scale)
            
            # 创建区域覆盖层
            overlay = Image.new('RGBA', (original_width, original_height), 
                              (*self.hex_to_rgb(region['color']), region['alpha']))
            
            # 将覆盖层粘贴到输出图片上
            output_image.paste(overlay, (original_x, original_y), overlay)
            
            # 添加文字
            if region['text']:
                try:
                    # 尝试使用支持中文的字体，使用更小的字体大小
                    import platform
                    system = platform.system()
                    if system == "Windows":
                        # Windows系统使用微软雅黑
                        font = ImageFont.truetype("msyh.ttc", 14)
                    elif system == "Darwin":  # macOS
                        # macOS系统使用苹方字体
                        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 14)
                    else:  # Linux
                        # Linux系统尝试使用文泉驿字体
                        font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 14)
                except:
                    try:
                        # 备用方案：尝试其他常见中文字体
                        font = ImageFont.truetype("simhei.ttf", 14)
                    except:
                        # 最后使用默认字体
                        font = ImageFont.load_default()
                
                # 创建文字图片（使用原始尺寸）
                text_img = Image.new('RGBA', (original_width, original_height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(text_img)
                
                # 获取文字边界框
                bbox = draw.textbbox((0, 0), region['text'], font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算文字位置（置顶显示，留3像素边距）
                text_x = 3
                text_y = 3
                
                # 检查文字是否超出区域边界
                max_width = original_width - 6  # 留出6px边距（置顶显示）
                max_height = original_height - 6  # 留出6px边距
                
                # 如果文字超出边界，进行自动换行
                if text_width > max_width or text_height > max_height:
                    # 计算每行最大字符数
                    char_width = text_width / len(region['text']) if region['text'] else 1
                    max_chars_per_line = int(max_width / char_width) if char_width > 0 else 1
                    
                    # 分行处理
                    lines = []
                    current_line = ""
                    for char in region['text']:
                        if len(current_line) >= max_chars_per_line:
                            lines.append(current_line)
                            current_line = char
                        else:
                            current_line += char
                    if current_line:
                        lines.append(current_line)
                    
                    # 绘制多行文字
                    line_height = text_height + 2  # 行间距
                    for i, line in enumerate(lines):
                        if text_y + i * line_height + text_height <= max_height:
                            # 先绘制阴影
                            draw.text((text_x + 1, text_y + i * line_height + 1), line, fill=(0, 0, 0, 180), font=font)
                            # 再绘制主文字
                            draw.text((text_x, text_y + i * line_height), line, fill=(255, 255, 255, 255), font=font)
                        else:
                            # 如果还有更多行但空间不够，显示省略号
                            if i < len(lines) - 1:
                                # 省略号也添加阴影
                                draw.text((text_x + 1, text_y + i * line_height + 1), "...", fill=(0, 0, 0, 180), font=font)
                                draw.text((text_x, text_y + i * line_height), "...", fill=(255, 255, 255, 255), font=font)
                            break
                else:
                    # 文字不超出边界，正常绘制
                    # 先绘制阴影效果（黑色，偏移1像素）
                    draw.text((text_x + 1, text_y + 1), region['text'], fill=(0, 0, 0, 180), font=font)
                    # 再绘制主文字（白色）
                    draw.text((text_x, text_y), region['text'], fill=(255, 255, 255, 255), font=font)
                
                # 将文字粘贴到输出图片上（使用原始坐标）
                output_image.paste(text_img, (original_x, original_y), text_img)
        
        # 自动生成文件名
        if not self.original_image_path:
            messagebox.showwarning("警告", "请先加载壁纸")
            return
            
        # 获取原文件路径和扩展名
        import os
        original_dir = os.path.dirname(self.original_image_path)
        original_name = os.path.splitext(os.path.basename(self.original_image_path))[0]
        original_ext = os.path.splitext(self.original_image_path)[1]
        
        # 生成新文件名：原文件名 + edit + 原扩展名
        new_filename = f"{original_name}_edit{original_ext}"
        file_path = os.path.join(original_dir, new_filename)
        
        try:
            if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                # JPEG不支持透明度，转换为RGB，使用最高质量保存
                output_image = output_image.convert('RGB')
                output_image.save(file_path, 'JPEG', quality=100)
            elif file_path.lower().endswith('.png'):
                # PNG格式无损保存，不进行任何压缩
                output_image.save(file_path, 'PNG', compress_level=0)
            else:
                # 其他格式使用默认设置
                output_image.save(file_path)
            messagebox.showinfo("✅ 保存成功", f"🎉 壁纸保存成功！\n📁 保存位置: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def save_project(self):
        """保存项目"""
        if not self.regions:
            messagebox.showwarning("警告", "没有可保存的区域")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="保存项目",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            try:
                project_data = {
                    'regions': self.regions,
                    'image_path': getattr(self, 'original_image_path', '')
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("✅ 保存成功", f"🎉 项目已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def load_project(self):
        """加载项目"""
        file_path = filedialog.askopenfilename(
            title="加载项目",
            filetypes=[("JSON文件", "*.json")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                self.regions = project_data.get('regions', [])
                self.selected_region = None
                self.update_attribute_panel()
                self.redraw_regions()
                messagebox.showinfo("✅ 加载成功", f"🎉 项目已加载: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {str(e)}")
    
    def toggle_auto_save(self):
        """切换自动保存状态"""
        self.auto_save_enabled = self.auto_save_var.get()
        if self.auto_save_enabled:
            self.start_auto_save()
            self.auto_save_status.config(text="●", foreground="#10b981")
            self.auto_save_text.config(text="已启用", foreground="#64748b")
        else:
            self.stop_auto_save()
            self.auto_save_status.config(text="●", foreground="#ef4444")
            self.auto_save_text.config(text="已禁用", foreground="#64748b")
    
    def start_auto_save(self):
        """启动自动保存"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        self.auto_save_timer = self.root.after(self.auto_save_interval, self.auto_save_loop)
    
    def stop_auto_save(self):
        """停止自动保存"""
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None
    
    def auto_save_loop(self):
        """自动保存循环"""
        if self.auto_save_enabled and self.project_modified:
            self.perform_auto_save()
        
        # 重新设置定时器
        if self.auto_save_enabled:
            self.auto_save_timer = self.root.after(self.auto_save_interval, self.auto_save_loop)
    
    def perform_auto_save(self):
        """执行自动保存"""
        try:
            # 如果没有自动保存路径，创建一个
            if not self.auto_save_path:
                import os
                auto_save_dir = os.path.join(os.getcwd(), "auto_save")
                if not os.path.exists(auto_save_dir):
                    os.makedirs(auto_save_dir)
                self.auto_save_path = os.path.join(auto_save_dir, "auto_save.json")
            
            # 保存项目数据
            project_data = {
                'regions': self.regions,
                'background_image_path': self.original_image_path
            }
            
            with open(self.auto_save_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            # 更新状态指示器
            self.auto_save_status.config(text="●", foreground="#3b82f6")
            self.auto_save_text.config(text="保存中...", foreground="#3b82f6")
            self.root.after(1000, lambda: (
                self.auto_save_status.config(text="●", foreground="#10b981"),
                self.auto_save_text.config(text="已启用", foreground="#64748b")
            ))
            
            # 标记为已保存
            self.project_modified = False
            
        except Exception as e:
            print(f"自动保存失败: {str(e)}")
            self.auto_save_status.config(text="●", foreground="#ef4444")
            self.auto_save_text.config(text="保存失败", foreground="#ef4444")
    
    def mark_project_modified(self):
        """标记项目已修改"""
        self.project_modified = True
        if self.auto_save_enabled and not self.auto_save_timer:
            self.start_auto_save()

def main():
    root = tk.Tk()
    app = WallpaperEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()

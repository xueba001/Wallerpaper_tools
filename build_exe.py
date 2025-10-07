#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
壁纸编辑器 - 可执行文件构建脚本
使用PyInstaller将Python程序打包为可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller 安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller 安装失败")
            return False

def build_executable():
    """构建可执行文件"""
    print("🚀 开始构建可执行文件...")
    
    # 使用python -m pyinstaller来确保能找到pyinstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # 无控制台窗口
        "--name=壁纸编辑器",            # 可执行文件名称
        "--hidden-import=PIL",          # 隐藏导入
        "--hidden-import=PIL.Image",    # 隐藏导入
        "--hidden-import=PIL.ImageTk",  # 隐藏导入
        "--hidden-import=tkinter",      # 隐藏导入
        "--hidden-import=tkinter.ttk",  # 隐藏导入
        "--hidden-import=tkinter.filedialog", # 隐藏导入
        "--hidden-import=tkinter.messagebox", # 隐藏导入
        "--hidden-import=tkinter.colorchooser", # 隐藏导入
        "--clean",                      # 清理临时文件
        "wallpaper_editor.py"           # 主程序文件
    ]
    
    # 如果有图标文件，添加图标参数
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
        print("✅ 使用自定义图标")
    else:
        print("⚠️  未找到图标文件，将使用默认图标")
    
    # 如果有requirements.txt文件，添加数据文件
    if os.path.exists("requirements.txt"):
        cmd.insert(-1, "--add-data=requirements.txt;.")
        print("✅ 包含依赖文件")
    
    try:
        # 执行构建命令
        print(f"🔧 执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("✅ 可执行文件构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        return False
    except FileNotFoundError:
        print("❌ 找不到PyInstaller，请确保已正确安装")
        return False

def create_icon():
    """创建简单的图标文件"""
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的图标
        size = 64
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制一个简单的壁纸图标
        draw.rectangle([8, 8, size-8, size-8], fill=(59, 130, 246, 255), outline=(30, 64, 175, 255), width=2)
        draw.rectangle([16, 16, size-16, size-16], fill=(147, 197, 253, 255))
        
        # 保存为ICO文件
        img.save("icon.ico", format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("✅ 图标文件创建成功")
        return True
    except Exception as e:
        print(f"⚠️  图标创建失败: {e}")
        return False

def cleanup():
    """清理构建过程中的临时文件"""
    cleanup_dirs = ["build", "__pycache__"]
    cleanup_files = ["*.spec"]
    
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 清理目录: {dir_name}")
    
    # 清理spec文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 清理文件: {spec_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("🎨 壁纸编辑器 - 可执行文件构建工具")
    print("=" * 50)
    
    # 检查主程序文件
    if not os.path.exists("wallpaper_editor.py"):
        print("❌ 未找到 wallpaper_editor.py 文件")
        return False
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return False
    
    # 创建图标（如果不存在）
    if not os.path.exists("icon.ico"):
        create_icon()
    
    # 构建可执行文件
    if build_executable():
        print("\n🎉 构建完成！")
        print("📁 可执行文件位置: dist/壁纸编辑器.exe")
        print("💡 您可以将 dist 文件夹中的可执行文件复制到任何位置运行")
        
        # 询问是否清理临时文件
        try:
            cleanup_choice = input("\n🧹 是否清理构建过程中的临时文件？(y/n): ").lower()
            if cleanup_choice in ['y', 'yes', '是']:
                cleanup()
                print("✅ 清理完成")
        except KeyboardInterrupt:
            print("\n👋 构建完成，未清理临时文件")
        
        return True
    else:
        print("❌ 构建失败")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 构建已取消")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

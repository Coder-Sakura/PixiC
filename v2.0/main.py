# coding=utf8
import tkinter as tk
from gui_config import PixiCConfigGUI

def main():
    """程序主入口，初始化并启动 GUI 界面"""
    root = tk.Tk()
    
    # 初始化配置界面类
    app = PixiCConfigGUI(root)
    
    # 设置窗口初始尺寸
    window_width = 600
    window_height = 800
    
    # 获取屏幕尺寸以实现窗口居中显示
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    
    # 设置窗口位置和大小
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # 进入 Tkinter 主循环
    root.mainloop()

if __name__ == '__main__':
    main()

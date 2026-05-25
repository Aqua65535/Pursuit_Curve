import sys
import tkinter as tk
from tkinter import messagebox


def main():
    """主函数"""
    try:
        # 导入UI模块
        from ui import run_ui
        run_ui()

    except ImportError as e:
        print(f"错误：无法导入必要模块 - {e}")
        print("请确保以下文件在同一目录下：")
        print("  - main.py (本文件)")
        print("  - ui.py (图形界面)")
        print("  - algo.py (算法核心)")

        # 创建一个简单的错误提示窗口

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "启动失败",
            f"无法启动图形界面：\n{str(e)}\n\n请确保所有文件完整。"
        )
        root.destroy()
        sys.exit(1)


if __name__ == "__main__":
    main()
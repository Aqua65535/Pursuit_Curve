"""
导弹追踪飞机模拟 - Tkinter图形界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# 导入算法模块
from algo import run_simulation, dt as DEFAULT_DT

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class MissileSimulationUI:
    """导弹追踪模拟图形界面"""

    def __init__(self, root):
        self.root = root
        self.root.title("导弹追踪飞机模拟")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 默认参数
        self.default_params = {
            'v_plane': 100,
            'x_plane': 10000,
            'y_plane': 5000,
            'v_missile': 300,
            'x_missile': 0,
            'y_missile': 0,
            'dt': DEFAULT_DT
        }

        # 存储当前模拟结果
        self.current_result = None
        self.animation = None
        self.is_animating = False  # 添加动画状态标志

        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # 参数输入区域
        params = [
            ('飞机速度 (m/s):', 'v_plane', 0, 1000),
            ('飞机初始X坐标 (m):', 'x_plane', 0, 50000),
            ('飞机初始Y坐标 (m):', 'y_plane', 0, 50000),
            ('导弹速度 (m/s):', 'v_missile', 0, 2000),
            ('导弹初始X坐标 (m):', 'x_missile', 0, 50000),
            ('导弹初始Y坐标 (m):', 'y_missile', 0, 50000),
            ('时间步长 (s):', 'dt', 0.001, 1.0)
        ]

        self.entries = {}
        for i, (label, key, min_val, max_val) in enumerate(params):
            ttk.Label(control_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            var = tk.StringVar(value=str(self.default_params[key]))
            entry = ttk.Entry(control_frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, padx=(10, 0), pady=5)
            self.entries[key] = (var, min_val, max_val)

        # 按钮框架
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=len(params), column=0, columnspan=2, pady=15)

        ttk.Button(button_frame, text="开始模拟", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置默认", command=self.reset_defaults).pack(side=tk.LEFT, padx=5)
        # ttk.Button(button_frame, text="清除动画", command=self.clear_animation).pack(side=tk.LEFT, padx=5)

        # 结果显示区域
        result_frame = ttk.LabelFrame(control_frame, text="模拟结果", padding="10")
        result_frame.grid(row=len(params) + 1, column=0, columnspan=2, pady=10, sticky=tk.W + tk.E)

        self.result_text = tk.Text(result_frame, width=25, height=8, state=tk.DISABLED)
        self.result_text.pack()

        # 右侧图形区域
        graph_frame = ttk.LabelFrame(main_frame, text="轨迹动画", padding="5")
        graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建matplotlib图形
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 初始化图形元素
        self.missile_trail, = self.ax.plot([], [], 'r-', linewidth=1.5, alpha=0.7, label="导弹轨迹")
        self.plane_trail, = self.ax.plot([], [], 'b-', linewidth=1.5, alpha=0.7, label="飞机轨迹")
        self.missile_point, = self.ax.plot([], [], 'ro', markersize=6, label="导弹")
        self.plane_point, = self.ax.plot([], [], 'bs', markersize=8, label="飞机")
        self.hit_point, = self.ax.plot([], [], 'g*', markersize=12, label="击中点")

        self.ax.set_xlabel("x (m)")
        self.ax.set_ylabel("y (m)")
        self.ax.set_title("导弹追踪飞机模拟")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.set_aspect('equal')

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def get_params(self):
        """获取用户输入的参数"""
        try:
            params = {}
            for key, (var, min_val, max_val) in self.entries.items():
                value = float(var.get())
                if value < min_val:
                    raise ValueError(f"{key} 不能小于 {min_val}")
                if value > max_val:
                    raise ValueError(f"{key} 不能大于 {max_val}")
                params[key] = value
            return params
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return None

    def validate_params(self, params):
        """验证参数合理性"""
        if params['v_plane'] <= 0:
            messagebox.showerror("参数错误", "飞机速度必须大于0！")
            return False
        if params['v_missile'] <= params['v_plane']:
            messagebox.showerror("参数错误", "导弹速度必须大于飞机速度，否则追不上！")
            return False
        if params['x_missile'] >= params['x_plane']:
            messagebox.showerror("参数错误", "导弹初始X坐标必须小于飞机初始X坐标！")
            return False
        if params['y_missile'] >= params['y_plane']:
            messagebox.showerror("参数错误", "导弹初始Y坐标必须小于飞机初始Y坐标！")
            return False
        if params['dt'] <= 0:
            messagebox.showerror("参数错误", "时间步长必须大于0！")
            return False
        return True

    def stop_animation(self):
        """停止当前动画"""
        if self.animation is not None:
            try:
                self.animation.event_source.stop()
            except:
                pass  # 忽略停止动画时的错误
            self.animation = None
        self.is_animating = False

    def start_simulation(self):
        """开始模拟"""
        # 停止当前动画
        self.stop_animation()

        params = self.get_params()
        if params is None:
            return

        if not self.validate_params(params):
            return

        self.status_var.set("正在计算模拟...")
        self.root.update()

        try:
            # 运行模拟
            self.current_result = run_simulation(
                params['v_plane'], params['x_plane'], params['y_plane'],
                params['v_missile'], params['x_missile'], params['y_missile'],
                params['dt']
            )

            # 显示结果
            self.show_results()

            # 更新图形范围
            self.update_plot_limits()

            # 播放动画
            self.status_var.set("正在播放动画...")
            self.play_animation()

            self.status_var.set(f"模拟完成 | 击中时间: {self.current_result['hit_time']:.2f}秒")

        except Exception as e:
            messagebox.showerror("模拟错误", f"模拟过程中发生错误：\n{str(e)}")
            self.status_var.set("模拟出错")

    def show_results(self):
        """显示模拟结果"""
        if self.current_result is None:
            return

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        result_str = (
            f"击中时间: {self.current_result['hit_time']:.2f} 秒\n"
            f"击中位置:\n"
            f"  X = {self.current_result['hit_x']:.1f} m\n"
            f"  Y = {self.current_result['hit_y']:.1f} m\n"
            f"计算步数: {self.current_result['steps']}\n"
            f"时间步长: {self.current_result['times'][1] - self.current_result['times'][0] if len(self.current_result['times']) > 1 else 0:.3f} s"
        )
        self.result_text.insert(1.0, result_str)
        self.result_text.config(state=tk.DISABLED)

    def update_plot_limits(self):
        """更新图形显示范围"""
        if self.current_result is None:
            return

        all_x = self.current_result['x_missile'] + self.current_result['x_plane']
        all_y = self.current_result['y_missile'] + self.current_result['y_plane']

        margin_x = max(1000, (max(all_x) - min(all_x)) * 0.1)
        margin_y = max(1000, (max(all_y) - min(all_y)) * 0.1)

        self.ax.set_xlim(min(all_x) - margin_x, max(all_x) + margin_x)
        self.ax.set_ylim(min(all_y) - margin_y, max(all_y) + margin_y)
        self.ax.set_title(f"导弹追踪飞机模拟 (击中时间: {self.current_result['hit_time']:.2f}秒)")

        self.canvas.draw()

    def play_animation(self):
        """播放动画"""
        if self.current_result is None:
            return

        # 停止之前的动画
        self.stop_animation()

        x_missile = self.current_result['x_missile']
        y_missile = self.current_result['y_missile']
        x_plane = self.current_result['x_plane']
        y_plane = self.current_result['y_plane']
        hit_x = self.current_result['hit_x']
        hit_y = self.current_result['hit_y']

        def init():
            self.missile_trail.set_data([], [])
            self.plane_trail.set_data([], [])
            self.missile_point.set_data([], [])
            self.plane_point.set_data([], [])
            self.hit_point.set_data([], [])
            return self.missile_trail, self.plane_trail, self.missile_point, self.plane_point, self.hit_point

        def update(frame):
            self.missile_trail.set_data(x_missile[:frame + 1], y_missile[:frame + 1])
            self.plane_trail.set_data(x_plane[:frame + 1], y_plane[:frame + 1])
            self.missile_point.set_data([x_missile[frame]], [y_missile[frame]])
            self.plane_point.set_data([x_plane[frame]], [y_plane[frame]])

            if frame == len(x_missile) - 1:
                self.hit_point.set_data([hit_x], [hit_y])

            return self.missile_trail, self.plane_trail, self.missile_point, self.plane_point, self.hit_point

        self.animation = FuncAnimation(
            self.fig, update, frames=len(x_missile),
            init_func=init, interval=1, repeat=False, blit=True
        )

        self.is_animating = True
        self.canvas.draw()

    def clear_animation(self):
        """清除动画"""
        # 停止动画
        self.stop_animation()

        # 清除轨迹数据
        self.missile_trail.set_data([], [])
        self.plane_trail.set_data([], [])
        self.missile_point.set_data([], [])
        self.plane_point.set_data([], [])
        self.hit_point.set_data([], [])

        # 重置标题
        self.ax.set_title("导弹追踪飞机模拟")

        # 如果有模拟结果，保持坐标范围不变，否则重置
        if self.current_result is not None:
            self.update_plot_limits()
        else:
            # 重置为默认范围
            self.ax.set_xlim(0, 12000)
            self.ax.set_ylim(0, 6000)

        self.canvas.draw()
        self.status_var.set("动画已清除")

    def reset_defaults(self):
        """重置为默认参数"""
        # 停止动画
        self.stop_animation()

        # 重置输入框
        for key, (var, _, _) in self.entries.items():
            var.set(str(self.default_params[key]))

        # 清除当前结果
        self.current_result = None

        # 清除动画显示
        self.missile_trail.set_data([], [])
        self.plane_trail.set_data([], [])
        self.missile_point.set_data([], [])
        self.plane_point.set_data([], [])
        self.hit_point.set_data([], [])

        # 重置图形
        self.ax.set_title("导弹追踪飞机模拟")
        self.ax.set_xlim(0, 12000)
        self.ax.set_ylim(0, 6000)
        self.canvas.draw()

        # 清空结果文本
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

        self.status_var.set("已重置为默认参数")


def run_ui():
    """运行图形界面"""
    root = tk.Tk()

    app = MissileSimulationUI(root)

    # 确保程序退出时清理资源
    def on_closing():
        app.stop_animation()
        plt.close('all')
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    run_ui()
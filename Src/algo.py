import sys
import argparse
import numpy as np

dt = 0.05  # 时间步长


def update_plane(x_plane, y_plane, v_plane, dt):
    """更新飞机位置"""
    x_plane += v_plane * dt
    return x_plane, y_plane


def update_missile(x_missile, y_missile, x_plane, y_plane, v_missile, dt):
    """更新导弹位置（纯追踪法）"""
    dx = x_plane - x_missile
    dy = y_plane - y_missile
    distance = np.sqrt(dx ** 2 + dy ** 2)

    if distance > 0:
        vx_missile = v_missile * (dx / distance)
        x_missile += vx_missile * dt
        vy_missile = v_missile * (dy / distance)
        y_missile += vy_missile * dt

    return x_missile, y_missile


def run_simulation(v_plane, x_plane, y_plane, v_missile, x_missile, y_missile, dt=dt):
    """
    运行模拟，记录完整轨迹

    参数:
        v_plane: 飞机速度
        x_plane: 飞机初始x坐标
        y_plane: 飞机初始y坐标
        v_missile: 导弹速度
        x_missile: 导弹初始x坐标
        y_missile: 导弹初始y坐标
        dt: 时间步长

    返回:
        dict: 包含轨迹数据和击中信息
    """
    t = 0

    # 复制初始值，避免修改原值
    x_p, y_p = x_plane, y_plane
    x_m, y_m = x_missile, y_missile

    # 存储轨迹
    x_missile_lst = [x_m]
    y_missile_lst = [y_m]
    x_plane_lst = [x_p]
    y_plane_lst = [y_p]
    times = [t]

    while True:
        # 检查是否击中（导弹x坐标超过飞机x坐标）
        if x_m >= x_p:
            hit_time = t
            hit_x = x_m
            hit_y = y_m
            break

        # 更新
        x_p, y_p = update_plane(x_p, y_p, v_plane, dt)
        x_m, y_m = update_missile(x_m, y_m, x_p, y_p, v_missile, dt)
        t += dt

        # 记录
        x_missile_lst.append(x_m)
        y_missile_lst.append(y_m)
        x_plane_lst.append(x_p)
        y_plane_lst.append(y_p)
        times.append(t)

    return {
        'x_missile': x_missile_lst,
        'y_missile': y_missile_lst,
        'x_plane': x_plane_lst,
        'y_plane': y_plane_lst,
        'times': times,
        'hit_time': hit_time,
        'hit_x': hit_x,
        'hit_y': hit_y,
        'steps': len(x_missile_lst)
    }


def print_results(result):
    """打印模拟结果"""
    print(f"击中！时间: {result['hit_time']:.2f} 秒")
    print(f"击中位置: ({result['hit_x']:.1f}, {result['hit_y']:.1f})")
    print(f"共计算 {result['steps']} 步")


def main_cli():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='导弹追踪飞机模拟算法')
    parser.add_argument('--v_plane', type=float, default=100, help='飞机速度 (默认: 100)')
    parser.add_argument('--x_plane', type=float, default=10000, help='飞机初始x坐标 (默认: 10000)')
    parser.add_argument('--y_plane', type=float, default=5000, help='飞机初始y坐标 (默认: 5000)')
    parser.add_argument('--v_missile', type=float, default=300, help='导弹速度 (默认: 300)')
    parser.add_argument('--x_missile', type=float, default=0, help='导弹初始x坐标 (默认: 0)')
    parser.add_argument('--y_missile', type=float, default=0, help='导弹初始y坐标 (默认: 0)')
    parser.add_argument('--dt', type=float, default=0.05, help='时间步长 (默认: 0.05)')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式，只输出结果')

    args = parser.parse_args()

    # 参数验证
    if args.v_plane <= 0:
        print("错误：飞机速度必须大于0")
        sys.exit(1)
    if args.v_missile < args.v_plane:
        print("错误：导弹速度应大于飞机速度，否则追不上！")
        sys.exit(1)
    if args.x_missile >= args.x_plane:
        print("错误：开始时，导弹的x坐标应小于飞机的x坐标！")
        sys.exit(1)
    if args.y_missile >= args.y_plane:
        print("错误：开始时，导弹的y坐标应小于飞机的y坐标！")
        sys.exit(1)

    if not args.quiet:
        print(f"参数：飞机速度={args.v_plane}, 飞机初始位置=({args.x_plane}, {args.y_plane})")
        print(f"      导弹速度={args.v_missile}, 导弹初始位置=({args.x_missile}, {args.y_missile})")
        print(f"      时间步长={args.dt}")
        print("开始计算...")

    # 运行模拟
    result = run_simulation(
        args.v_plane, args.x_plane, args.y_plane,
        args.v_missile, args.x_missile, args.y_missile,
        args.dt
    )

    # 输出结果
    print_results(result)

    if not args.quiet:
        print(f"\n轨迹点数: {result['steps']}")


if __name__ == "__main__":
    main_cli()
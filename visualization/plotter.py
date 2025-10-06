# visualization/plotter.py
import os
import matplotlib
matplotlib.use('Agg')  # 使用非交互后端
import matplotlib.pyplot as plt

# === 新增：配置中文字体 ===
import platform
def set_chinese_font():
    system = platform.system()
    if system == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
    elif system == "Darwin":  # macOS
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
    else:  # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

set_chinese_font()
# =========================

from config import OUTPUT_DIR

def plot_comparison(results, loss_rate):
    plt.figure(figsize=(14, 12))

    # 吞吐量
    plt.subplot(4, 1, 1)
    for name, data in results.items():
        plt.plot(data["time"], [t/1e6 for t in data["throughput"]], label=name)
    plt.ylabel("吞吐量 (Mbps)")
    plt.title(f"丢包率: {loss_rate*100:.1f}% 下的算法对比")
    plt.legend()
    plt.grid(True)

    # 带宽利用率
    plt.subplot(4, 1, 2)
    for name, data in results.items():
        plt.plot(data["time"], [u*100 for u in data["bandwidth_utilization"]], label=name)
    plt.ylabel("带宽利用率 (%)")
    plt.legend()
    plt.grid(True)

    # cwnd
    plt.subplot(4, 1, 3)
    for name, data in results.items():
        plt.plot(data["time"], [c/1024 for c in data["cwnd_bytes"]], label=name)
    plt.ylabel("拥塞窗口 cwnd (KB)")
    plt.legend()
    plt.grid(True)

    # RTT
    plt.subplot(4, 1, 4)
    for name, data in results.items():
        plt.plot(data["time"], data["rtt"], label=name)
    plt.xlabel("时间 (秒)")
    plt.ylabel("往返时延 RTT (秒)")
    plt.legend()
    plt.grid(True)

    filename = os.path.join(OUTPUT_DIR, f"对比_丢包率_{int(loss_rate*100)}pct.png")
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
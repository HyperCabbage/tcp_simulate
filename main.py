# main.py
from config import *
from simulator.network_simulator import NetworkSimulator
from algorithms.tcp_reno import TCPReno
from algorithms.tcp_cubic import TCPCubic
from algorithms.tcp_bbr import TCPBBR
from visualization.plotter import plot_comparison
import time

def run_experiment(loss_rate):
    results = {}
    algorithms = {
        "Reno": TCPReno(RTT_SEC),
        "CUBIC": TCPCubic(RTT_SEC),
        "BBR": TCPBBR(RTT_SEC)
    }

    for name, sender in algorithms.items():
        print(f"正在运行 {name} 算法，丢包率: {loss_rate*100:.1f}% ...")
        start_time = time.time()
        simulator = NetworkSimulator(
            sender=sender,
            loss_rate=loss_rate,
            bandwidth_mbps=BANDWIDTH_MBPS,
            timeout_sec=TIMEOUT
        )
        data = simulator.run(SIM_DURATION, dt=0.01)  # 使用 10ms 时间步长
        elapsed = time.time() - start_time
        print(f"  ✅ 完成！耗时: {elapsed:.2f} 秒")
        results[name] = data

    plot_comparison(results, loss_rate)

def main():
    print("🚀 开始 TCP 拥塞控制算法对比实验...")
    print(f"仿真时长: {SIM_DURATION} 秒，测试丢包率: {[f'{r*100:.1f}%' for r in LOSS_RATES]}")

    for loss in LOSS_RATES:
        run_experiment(loss)

    print(f"\n🎉 所有实验已完成！结果图表已保存至 '{OUTPUT_DIR}' 目录。")

if __name__ == "__main__":
    main()
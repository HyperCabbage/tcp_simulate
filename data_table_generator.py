from config import *
from simulator.network_simulator import NetworkSimulator
from algorithms.tcp_reno import TCPReno
from algorithms.tcp_cubic import TCPCubic
from algorithms.tcp_bbr import TCPBBR
import time
import csv
import os

def calculate_statistics(data):
    """计算数据集的统计指标"""
    if not data:
        return 0, 0, 0, 0
    
    # 计算平均、最小、最大和中位数
    avg = sum(data) / len(data)
    min_val = min(data)
    max_val = max(data)
    sorted_data = sorted(data)
    median = sorted_data[len(sorted_data) // 2]
    
    return avg, min_val, max_val, median

def run_experiment_for_table(loss_rate):
    """运行实验并返回关键统计数据"""
    results = {}
    algorithms = {
        "Reno": TCPReno(RTT_SEC),
        "CUBIC": TCPCubic(RTT_SEC),
        "BBR": TCPBBR(RTT_SEC)
    }

    for name, sender in algorithms.items():
        print(f"正在收集 {name} 算法数据，丢包率: {loss_rate*100:.1f}% ...")
        start_time = time.time()
        simulator = NetworkSimulator(
            sender=sender,
            loss_rate=loss_rate,
            bandwidth_mbps=BANDWIDTH_MBPS,
            timeout_sec=TIMEOUT
        )
        data = simulator.run(SIM_DURATION, dt=0.01)
        elapsed = time.time() - start_time
        print(f"  ✅ 完成！耗时: {elapsed:.2f} 秒")
        
        # 计算统计指标
        avg_throughput, min_throughput, max_throughput, med_throughput = calculate_statistics(data["throughput"])
        avg_cwnd, min_cwnd, max_cwnd, med_cwnd = calculate_statistics(data["cwnd_bytes"])
        avg_rtt, min_rtt, max_rtt, med_rtt = calculate_statistics(data["rtt"])
        avg_util, min_util, max_util, med_util = calculate_statistics(data["bandwidth_utilization"])
        
        # 存储结果
        results[name] = {
            "loss_rate": loss_rate,
            "avg_throughput_mbps": avg_throughput / 1e6,
            "max_throughput_mbps": max_throughput / 1e6,
            "avg_cwnd_kb": avg_cwnd / 1024,
            "max_cwnd_kb": max_cwnd / 1024,
            "avg_rtt_sec": avg_rtt,
            "max_rtt_sec": max_rtt,
            "avg_util_percent": avg_util * 100,
            "max_util_percent": max_util * 100
        }
    
    return results

def generate_table_data():
    """生成表格数据并保存为CSV格式"""
    all_results = []
    
    print("🚀 开始收集表格数据...")
    print(f"仿真时长: {SIM_DURATION} 秒，测试丢包率: {[f'{r*100:.1f}%' for r in LOSS_RATES]}")

    for loss in LOSS_RATES:
        exp_results = run_experiment_for_table(loss)
        for algo, metrics in exp_results.items():
            row = {
                "丢包率 (%)": f"{loss*100:.1f}",
                "算法": algo,
                "平均吞吐量 (Mbps)": f"{metrics['avg_throughput_mbps']:.2f}",
                "最大吞吐量 (Mbps)": f"{metrics['max_throughput_mbps']:.2f}",
                "平均拥塞窗口 (KB)": f"{metrics['avg_cwnd_kb']:.2f}",
                "最大拥塞窗口 (KB)": f"{metrics['max_cwnd_kb']:.2f}",
                "平均RTT (秒)": f"{metrics['avg_rtt_sec']:.3f}",
                "最大RTT (秒)": f"{metrics['max_rtt_sec']:.3f}",
                "平均带宽利用率 (%)": f"{metrics['avg_util_percent']:.2f}",
                "最大带宽利用率 (%)": f"{metrics['max_util_percent']:.2f}"
            }
            all_results.append(row)
    
    # 保存为CSV文件
    csv_file = os.path.join(OUTPUT_DIR, "simulation_results_table.csv")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if all_results:
        fieldnames = all_results[0].keys()
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"🎉 表格数据生成完成！已保存至 '{csv_file}'")
        
        print("\n==== 仿真结果表格（简化版） ====")
        print("{:<10} {:<10} {:<20} {:<20} {:<20}".format(
            "丢包率 (%)", "算法", "平均吞吐量 (Mbps)", "平均RTT (秒)", "平均带宽利用率 (%)"
        ))
        print("=" * 80)
        for row in all_results:
            print("{:<10} {:<10} {:<20} {:<20} {:<20}".format(
                row["丢包率 (%)"],
                row["算法"],
                row["平均吞吐量 (Mbps)"],
                row["平均RTT (秒)"],
                row["平均带宽利用率 (%)"]
            ))
    
    return all_results

def main():
    generate_table_data()

if __name__ == "__main__":
    main()
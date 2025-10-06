# config.py
import os

# 网络参数
BANDWIDTH_MBPS = 100          # 链路带宽 (Mbps)
RTT_SEC = 0.1                 # 基础往返时延 (秒)
MSS = 1460                    # 最大段大小 (bytes)

# 仿真参数
SIM_DURATION = 60.0           # 仿真总时长 (秒)
SAMPLE_INTERVAL = 0.1         # 指标采样间隔 (秒)
TIMEOUT = 1.0                 # 超时阈值 (秒)

# 实验配置
LOSS_RATES = [0.001, 0.01, 0.05, 0.1]  # 丢包率: 0.1%, 1%, 5%, 10%

# 输出目录
OUTPUT_DIR = "results"
os.makedirs(OUTPUT_DIR, exist_ok=True)
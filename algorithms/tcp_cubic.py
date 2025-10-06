# algorithms/tcp_cubic.py
import math
from .base import TCPSender

class TCPCubic(TCPSender):
    BETA = 0.7  # 窗口减少因子
    C = 0.4     # 三次函数系数
    MAX_CWND_INCREASE = 4.0  # 增加单次ACK最大窗口增长

    def __init__(self, rtt: float):
        super().__init__(rtt)
        self.w_max = 1.0        # 上次丢包前的窗口大小
        self.last_loss_time = 0.0  # 上次丢包时间
        self.epoch_start = 0.0   # 上次窗口重置时间
        self.ack_cnt = 0        # ACK计数器，用于精细窗口调整
        self.d_min = rtt        # 最小RTT记录

    def on_ack(self, ack_seq: int, rtt_sample: float):
        # 更新RTT估计和最小RTT记录
        self.rtt = 0.875 * self.rtt + 0.125 * rtt_sample
        self.d_min = min(self.d_min, rtt_sample)

        # 检查并记录已确认的包
        if ack_seq in self.acked_packets:
            return
        self.acked_packets.add(ack_seq)
        self.in_flight = max(0, self.in_flight - 1)

        # 增加ACK计数器
        self.ack_cnt += 1

        # 确保在没有丢包时也能更新w_max
        if self.cwnd > self.w_max:
            self.w_max = self.cwnd
            self.last_loss_time = self.time
            self.epoch_start = self.time

        # CUBIC窗口增长计算（修正版）
        if self.time - self.epoch_start > 0:
            t = self.time - self.epoch_start
            K = (self.w_max * (1 - self.BETA) / self.C) ** (1 / 3)
            w_cubic = self.C * (t - K) ** 3 + self.w_max

            # 标准Reno式增长作为对比
            w_reno = self.cwnd * (1 - self.BETA) + 1.0

            # 窗口调整 - 修正版
            cwnd_target = max(w_cubic, w_reno, 1.0)
            # 限制单次调整幅度，避免震荡
            cwnd_increase = min(cwnd_target - self.cwnd, self.MAX_CWND_INCREASE)
            # 修正增长公式，移除错误的除法项
            self.cwnd = max(self.cwnd + cwnd_increase, 1.0)
        else:
            # 改进初始阶段增长，更快速提升窗口
            self.cwnd += 1.0

        # 重置ACK计数器 - 调整触发条件
        if self.ack_cnt >= self.cwnd:
            self.ack_cnt = 0

    def on_timeout(self, seq: int):
        # 保存当前窗口的一半作为新的w_max
        self.w_max = max(self.cwnd * 0.5, 1.0)
        self.last_loss_time = self.time
        self.epoch_start = self.time
        # 窗口减半（更符合CUBIC规范）
        self.cwnd = max(1.0, self.cwnd * self.BETA)
        self.in_flight = 0
        self.acked_packets.clear()
        self.ack_cnt = 0  # 重置ACK计数器

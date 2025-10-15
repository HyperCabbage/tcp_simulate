# simulator/network_simulator.py
import random
from algorithms.base import TCPSender
from metrics.collector import MetricsCollector
from config import RTT_SEC  # 引入基础 RTT

class NetworkSimulator:
    def __init__(self, sender: TCPSender, loss_rate: float, bandwidth_mbps: float, timeout_sec: float):
        self.sender = sender
        self.loss_rate = loss_rate
        self.bandwidth_bps = bandwidth_mbps * 1e6
        self.timeout_sec = timeout_sec
        self.time = 0.0
        self.seq = 0
        self.metrics = MetricsCollector(duration=60, interval=0.1)

        self.packet_send_times = {}
        self.acked_seqs = set()
        self.bytes_acked_total = 0
        self.in_flight_bytes = 0  # 新增：网络中未确认字节数
        self.base_rtt = RTT_SEC   # 基础传播时延

    def run(self, duration: float, dt=0.01):
        steps = int(duration / dt)
        for step in range(steps):
            self.time = step * dt
            self.sender.time = self.time

            # === 动态计算当前 RTT ===
            queue_delay = self.in_flight_bytes / (self.bandwidth_bps / 8)
            current_rtt = self.base_rtt + queue_delay

            # === 发送新包（基于带宽限制）===
            max_bytes_this_step = (self.bandwidth_bps / 8) * dt
            max_packets_by_bandwidth = int(max_bytes_this_step // TCPSender.MSS)
            can_send_packets = int(self.sender.cwnd - (self.in_flight_bytes / TCPSender.MSS))
            num_to_send = min(max_packets_by_bandwidth, can_send_packets, 50)

            for _ in range(num_to_send):
                if self.seq not in self.packet_send_times:
                    # 添加丢包逻辑：根据丢包率决定是否丢弃此包
                    if random.random() >= self.loss_rate:
                        self.packet_send_times[self.seq] = self.time
                        self.in_flight_bytes += TCPSender.MSS
                        # 调用算法的send方法，保持状态同步
                        self.sender.send(self.seq)
                    self.seq += 1

            # === 处理 ACKs（按 current_rtt 到达）===
            newly_acked_bytes = 0
            acked_now = []
            for s, send_t in list(self.packet_send_times.items()):
                if s not in self.acked_seqs and (self.time - send_t) >= current_rtt:
                    self.acked_seqs.add(s)
                    acked_now.append(s)
                    newly_acked_bytes += TCPSender.MSS
                    self.in_flight_bytes = max(0, self.in_flight_bytes - TCPSender.MSS)

            # === 超时检测 ===
            timeout_occurred = False
            for s, send_t in list(self.packet_send_times.items()):
                if s not in self.acked_seqs and (self.time - send_t) > self.timeout_sec:
                    if not timeout_occurred:
                        self.sender.on_timeout(s)  # 只调用一次
                        timeout_occurred = True
                    # 从packet_send_times中移除超时包
                    del self.packet_send_times[s]
                    self.in_flight_bytes = max(0, self.in_flight_bytes - TCPSender.MSS)

            # 不要清空 packet_send_times 或 in_flight_bytes！
            # 只标记这个包丢失，继续等待其他包被 ACK

            # === 记录数据 ===
            if acked_now:
                latest_ack = max(acked_now)
                self.sender.on_ack(latest_ack, current_rtt)

            self.metrics.record(self.time, self.sender, newly_acked_bytes)

        # 返回收集到的指标数据
        return self.metrics.get_data()
# algorithms/tcp_bbr.py
from .base import TCPSender


class TCPBBR(TCPSender):
    INIT_CWND = 10
    MIN_RTT_FILTER_LEN = 10.0  # seconds

    def __init__(self, rtt: float):
        super().__init__(rtt)
        self.cwnd = self.INIT_CWND
        self.btl_bw = 0.0
        self.min_rtt = float('inf')
        self.delivered = 0
        self.delivered_time = 0.0
        self.state = "startup"
        self.state_start_time = 0.0

    def on_ack(self, ack_seq: int, rtt_sample: float):
        now = self.time
        delivered_bytes = ack_seq * self.MSS

        if self.delivered > 0:
            dt = now - self.delivered_time
            if dt > 0:
                bw = (delivered_bytes - self.delivered) / dt
                self.btl_bw = max(self.btl_bw, bw)

        self.delivered = delivered_bytes
        self.delivered_time = now

        # Update min_rtt
        if now - self.state_start_time > self.MIN_RTT_FILTER_LEN:
            self.min_rtt = rtt_sample
            self.state_start_time = now
        else:
            self.min_rtt = min(self.min_rtt, rtt_sample)

        # BBR状态机改进版
        bdp = self.btl_bw * self.min_rtt
        target_cwnd = bdp / self.MSS if bdp > 0 else self.INIT_CWND

        if self.state == "startup":
            if self.cwnd < target_cwnd:
                self.cwnd *= 2
            else:
                self.state = "drain"
        elif self.state == "drain":
            self.cwnd = max(self.INIT_CWND, target_cwnd * 0.9)
            if self.in_flight < target_cwnd:
                self.state = "probe_bw"
                self.state_start_time = now
        else:  # probe_bw
            # 添加带宽探测机制
            cycle_time = self.min_rtt * 8
            if now - self.state_start_time > cycle_time:
                self.state_start_time = now
                # 每8个RTT周期增加窗口进行带宽探测
                self.cwnd = min(self.cwnd * 1.25, target_cwnd * 2)
            else:
                # 保持接近目标窗口
                self.cwnd = max(self.INIT_CWND, target_cwnd)

        if ack_seq in self.acked_packets:
            return
        self.acked_packets.add(ack_seq)
        self.in_flight = max(0, self.in_flight - 1)

    def on_timeout(self, seq: int):
        self.cwnd = max(1.0, self.cwnd * 0.5)
        self.in_flight = 0
        self.acked_packets.clear()

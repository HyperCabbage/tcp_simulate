# metrics/collector.py
class MetricsCollector:
    def __init__(self, duration: float, interval: float):
        self.interval = interval
        self.timestamps = []
        self.throughput = []
        self.cwnd = []
        self.rtt = []
        self.bytes_acked = 0
        self.last_sample_time = 0.0
        self.last_acked_bytes = 0

    def record(self, time: float, sender, newly_acked_bytes: int):
        self.bytes_acked += newly_acked_bytes

        if time - self.last_sample_time >= self.interval:
            dt = time - self.last_sample_time
            if dt > 0:
                thr = (self.bytes_acked - self.last_acked_bytes) / dt
                self.throughput.append(thr)
                self.cwnd.append(sender.cwnd * sender.MSS)
                self.rtt.append(sender.rtt)
                self.timestamps.append(time)

            self.last_acked_bytes = self.bytes_acked
            self.last_sample_time = time

    def get_data(self):
        # 计算带宽利用率 (吞吐量 / 带宽)
        from config import BANDWIDTH_MBPS
        bandwidth_utilization = [t/(BANDWIDTH_MBPS*1e6) for t in self.throughput]  # 转换为比例
        
        return {
            "time": self.timestamps,
            "throughput": self.throughput,
            "cwnd_bytes": self.cwnd,
            "rtt": self.rtt,
            "bandwidth_utilization": bandwidth_utilization
        }
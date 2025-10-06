# algorithms/base.py
from abc import ABC, abstractmethod


class TCPSender(ABC):
    MSS = 1460

    def __init__(self, rtt: float):
        self.cwnd = 1.0
        self.rtt = rtt
        self.time = 0.0
        self.sent_packets = []  # [(seq, send_time), ...]
        self.acked_packets = set()  # 已确认序列号
        self.in_flight = 0  # 未确认包数

    @abstractmethod
    def on_ack(self, ack_seq: int, rtt_sample: float):
        pass

    @abstractmethod
    def on_timeout(self, seq: int):
        pass

    def can_send(self) -> bool:
        return self.in_flight < self.cwnd

    def send(self, seq: int):
        self.sent_packets.append((seq, self.time))
        self.in_flight += 1

    def get_inflight_seq(self):
        acked = set(self.acked_packets)
        return [seq for seq, _ in self.sent_packets if seq not in acked]

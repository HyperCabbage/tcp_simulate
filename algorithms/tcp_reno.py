# algorithms/tcp_reno.py
from .base import TCPSender


class TCPReno(TCPSender):
    def __init__(self, rtt: float):
        super().__init__(rtt)
        self.ssthresh = float('inf')
        self.dup_acks = 0
        self.recovery_seq = -1
        self.state = "slow_start"  # slow_start, congestion_avoidance, fast_recovery

    def on_ack(self, ack_seq: int, rtt_sample: float):
        self.rtt = 0.875 * self.rtt + 0.125 * rtt_sample

        if ack_seq in self.acked_packets:
            self.dup_acks += 1
            if self.dup_acks == 3 and self.state != "fast_recovery":
                # Fast Retransmit
                self.ssthresh = max(2.0, self.cwnd / 2)
                self.cwnd = self.ssthresh + 3
                self.state = "fast_recovery"
                self.recovery_seq = ack_seq
        else:
            self.acked_packets.add(ack_seq)
            self.in_flight = max(0, self.in_flight - 1)
            self.dup_acks = 0

            if self.state == "fast_recovery":
                if ack_seq > self.recovery_seq:
                    self.cwnd = self.ssthresh
                    self.state = "congestion_avoidance"
                else:
                    self.cwnd += 1
            else:
                if self.cwnd < self.ssthresh:
                    self.cwnd += 1
                    self.state = "slow_start"
                else:
                    self.cwnd += 1 / self.cwnd
                    self.state = "congestion_avoidance"

    def on_timeout(self, seq: int):
        self.ssthresh = max(2.0, self.cwnd / 2)
        self.cwnd = 1.0
        self.state = "slow_start"
        self.dup_acks = 0
        self.in_flight = 0
        self.acked_packets.clear()


import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5001

N = 4
TOTAL_PACKETS = 10
TIMEOUT = 3


class Sender:

    def __init__(self):
        self.send_base = 0
        self.next_seq = 0

        self.acked = set()
        self.sent_time = {}

        self.lock = threading.Lock()

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def connect(self):
        self.sock.connect((HOST, PORT))
        print("Sender connected to channel")

        threading.Thread(
            target=self.receive_acks,
            daemon=True
        ).start()

    def send_packet(self, seq_num):
        message = f"{seq_num}\n"
        self.sock.sendall(message.encode())

        with self.lock:
            self.sent_time[seq_num] = time.time()

        print("Sent packet:", seq_num)

    def receive_acks(self):
        file = self.sock.makefile("r")

        for line in file:
            message = line.strip()

            if message == "NONE":
                continue

            try:
                ack = int(message)
            except ValueError:
                continue

            with self.lock:
                self.acked.add(ack)

            print("ACK received:", ack)

        file.close()

    def start(self):
        self.connect()

        while self.send_base < TOTAL_PACKETS:

            with self.lock:

                while (
                    self.next_seq < TOTAL_PACKETS
                    and self.next_seq < self.send_base + N
                ):
                    seq = self.next_seq
                    self.next_seq += 1

                    self.sock.sendall(
                        f"{seq}\n".encode()
                    )

                    self.sent_time[seq] = time.time()

                    print("Sent packet:", seq)

                now = time.time()

                for seq in range(
                    self.send_base,
                    self.next_seq
                ):

                    if seq in self.acked:
                        continue

                    if (
                        seq in self.sent_time
                        and now - self.sent_time[seq] >= TIMEOUT
                    ):
                        print("Timeout! Retransmitting:", seq)

                        self.sock.sendall(
                            f"{seq}\n".encode()
                        )

                        self.sent_time[seq] = time.time()

                while self.send_base in self.acked:
                    self.send_base += 1

            time.sleep(0.05)

        print("\nAll packets successfully acknowledged!")

        self.sock.close()


if __name__ == "__main__":
    sender = Sender()
    sender.start()

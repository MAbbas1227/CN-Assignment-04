import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 5001
WINDOW_SIZE = 4
TOTAL_PACKETS = 10
TIMEOUT = 6.0


class Sender:
    def __init__(self):
        self.send_base = 0
        self.next_seq = 0
        self.acked = set()
        self.sent_time = {}
        self.lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ack_thread = None

    def connect(self):
        self.sock.connect((HOST, PORT))
        print("Sender connected to channel.")
        self.ack_thread = threading.Thread(
            target=self.receive_acks, name="ack-receiver", daemon=True
        )
        self.ack_thread.start()

    def receive_acks(self):
        reader = self.sock.makefile("r", encoding="utf-8")
        try:
            for line in reader:
                message = line.strip()
                if not message or message == "NONE":
                    continue
                try:
                    ack = int(message)
                except ValueError:
                    print("Ignoring invalid ACK:", message)
                    continue
                with self.lock:
                    if 0 <= ack < TOTAL_PACKETS:
                        self.acked.add(ack)
                print("ACK received:", ack)
        except (ConnectionError, OSError) as error:
            print("ACK connection ended:", error)
        finally:
            reader.close()

    def start(self):
        self.connect()
        try:
            while True:
                with self.lock:
                    if self.send_base >= TOTAL_PACKETS:
                        break

                    while (
                        self.next_seq < TOTAL_PACKETS
                        and self.next_seq < self.send_base + WINDOW_SIZE
                    ):
                        seq = self.next_seq
                        self.sock.sendall(f"{seq}\n".encode("utf-8"))
                        self.sent_time[seq] = time.monotonic()
                        self.next_seq += 1
                        print("Sent packet:", seq)

                    now = time.monotonic()
                    for seq in range(self.send_base, self.next_seq):
                        if seq not in self.acked:
                            last_sent = self.sent_time.get(seq)
                            if last_sent is not None and now - last_sent >= TIMEOUT:
                                self.sock.sendall(f"{seq}\n".encode("utf-8"))
                                self.sent_time[seq] = now
                                print("Timeout! Retransmitting:", seq)

                    while self.send_base in self.acked:
                        self.send_base += 1

                time.sleep(0.05)

            print("\nAll packets successfully acknowledged.")
        finally:
            try:
                self.sock.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            if self.ack_thread is not None:
                self.ack_thread.join(timeout=10)
            self.sock.close()


if __name__ == "__main__":
    Sender().start()

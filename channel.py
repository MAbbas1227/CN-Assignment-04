import random
import socket
import threading
import time

HOST = "127.0.0.1"
SENDER_PORT = 5001
RECEIVER_PORT = 5002
LOSS_PROBABILITY = 0.30
MAX_DELAY = 2.0


def forward_packets(sender_conn, receiver_conn):
    reader = sender_conn.makefile("r", encoding="utf-8")
    try:
        for line in reader:
            message = line.strip()
            if not message:
                continue
            if random.random() < LOSS_PROBABILITY:
                print(f"Channel DROPPED packet: {message}")
                continue
            delay = random.uniform(0, MAX_DELAY)
            if delay >= 0.5:
                print(f"Channel DELAYED packet {message} by {delay:.2f}s")
            time.sleep(delay)
            receiver_conn.sendall((message + "\n").encode("utf-8"))
            print(f"Channel FORWARDED packet: {message}")
    except (ConnectionError, OSError) as error:
        print("Data forwarding ended:", error)
    finally:
        reader.close()
        try:
            receiver_conn.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def forward_acks(receiver_conn, sender_conn):
    reader = receiver_conn.makefile("r", encoding="utf-8")
    try:
        for line in reader:
            message = line.strip()
            if message:
                sender_conn.sendall((message + "\n").encode("utf-8"))
                print(f"Channel FORWARDED ACK: {message}")
    except (ConnectionError, OSError) as error:
        print("ACK forwarding ended:", error)
    finally:
        reader.close()
        try:
            sender_conn.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def start_channel():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, SENDER_PORT))
        server.listen(1)
        print(f"Channel waiting for sender on {HOST}:{SENDER_PORT}")

        sender_conn, sender_address = server.accept()
        print("Sender connected:", sender_address)

        with sender_conn:
            receiver_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                receiver_conn.connect((HOST, RECEIVER_PORT))
                print("Channel connected to receiver.")

                data_thread = threading.Thread(
                    target=forward_packets,
                    args=(sender_conn, receiver_conn),
                    name="data-forwarder",
                )
                ack_thread = threading.Thread(
                    target=forward_acks,
                    args=(receiver_conn, sender_conn),
                    name="ack-forwarder",
                )
                data_thread.start()
                ack_thread.start()
                data_thread.join()
                ack_thread.join()
            finally:
                receiver_conn.close()

    print("Channel stopped.")


if __name__ == "__main__":
    start_channel()

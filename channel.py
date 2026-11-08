
import socket
import threading
import random
import time

HOST = "127.0.0.1"
SENDER_PORT = 5001
RECEIVER_PORT = 5002

LOSS_PROBABILITY = 0.3
MAX_DELAY = 2


def sender_to_receiver(sender_conn, receiver_conn):
    file = sender_conn.makefile("r")

    for line in file:
        message = line.strip()

        if random.random() < LOSS_PROBABILITY:
            print("Channel DROPPED packet:", message)
            continue

        delay = random.uniform(0, MAX_DELAY)

        if delay > 0.5:
            print(f"Channel DELAYED packet {message} by {delay:.2f}s")

        time.sleep(delay)

        receiver_conn.sendall((message + "\n").encode())
        print("Channel FORWARDED packet:", message)


def receiver_to_sender(receiver_conn, sender_conn):
    file = receiver_conn.makefile("r")

    for line in file:
        message = line.strip()

        sender_conn.sendall((message + "\n").encode())
        print("Channel FORWARDED ACK:", message)


def start_channel():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, SENDER_PORT))
    server.listen(1)

    print("Channel waiting for sender...")

    sender_conn, sender_addr = server.accept()
    print("Sender connected:", sender_addr)

    receiver_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_conn.connect((HOST, RECEIVER_PORT))

    print("Channel connected to receiver")

    t1 = threading.Thread(
        target=sender_to_receiver,
        args=(sender_conn, receiver_conn)
    )

    t2 = threading.Thread(
        target=receiver_to_sender,
        args=(receiver_conn, sender_conn)
    )

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    sender_conn.close()
    receiver_conn.close()
    server.close()


if __name__ == "__main__":
    start_channel()


import socket

HOST = "127.0.0.1"
PORT = 5002
N = 4

rcv_base = 0
buffer = []

def process_packet(seq_num, rcv_base, N, buffer):
    if rcv_base <= seq_num < rcv_base + N:
        if seq_num not in buffer:
            buffer.append(seq_num)
        return seq_num

    elif seq_num < rcv_base:
        return seq_num

    else:
        return None


def start_receiver():
    global rcv_base, buffer

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(1)

    print("Receiver is listening on port", PORT)

    conn, addr = server.accept()
    print("Connected to channel:", addr)

    with conn:
        file = conn.makefile("r")

        for line in file:
            try:
                seq_num = int(line.strip())
            except ValueError:
                continue

            ack = process_packet(seq_num, rcv_base, N, buffer)

            delivered = []

            while rcv_base in buffer:
                buffer.remove(rcv_base)
                delivered.append(rcv_base)
                rcv_base += 1

            print(
                f"Received: {seq_num}, ACK: {ack}, "
                f"rcv_base: {rcv_base}, Buffer: {buffer}, "
                f"Delivered: {delivered}"
            )

            response = f"{ack if ack is not None else 'NONE'}\n"
            conn.sendall(response.encode())

    server.close()


if __name__ == "__main__":
    start_receiver()

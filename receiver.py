import socket

HOST = "127.0.0.1"
PORT = 5002
WINDOW_SIZE = 4


def process_packet(seq_num, rcv_base, window_size, buffer):
    if rcv_base <= seq_num < rcv_base + window_size:
        if seq_num not in buffer:
            buffer.append(seq_num)
        return seq_num
    if seq_num < rcv_base:
        return seq_num
    return None


def start_receiver():
    rcv_base = 0
    buffer = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)
        print(f"Receiver listening on {HOST}:{PORT}")

        conn, address = server.accept()
        print("Channel connected:", address)

        with conn:
            reader = conn.makefile("r", encoding="utf-8")
            try:
                for line in reader:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        seq_num = int(line)
                    except ValueError:
                        print("Ignoring invalid packet:", line)
                        continue

                    ack = process_packet(seq_num, rcv_base, WINDOW_SIZE, buffer)
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
                    response = "NONE" if ack is None else str(ack)
                    conn.sendall((response + "\n").encode("utf-8"))
            finally:
                reader.close()

    print("Receiver stopped.")


if __name__ == "__main__":
    start_receiver()

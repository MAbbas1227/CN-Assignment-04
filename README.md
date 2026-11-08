# Computer Networks Assignment IV
## Full Selective Repeat (SR) Implementation in Python

This project implements a Selective Repeat ARQ simulation using three Python programs.

## Files
- `sender.py` — sliding sending window, ACK tracking, and timeout retransmission.
- `channel.py` — connects sender and receiver; randomly drops or delays data packets.
- `receiver.py` — packet processing, buffering, in-order delivery, and ACK generation.

## Configuration
- Window size: 4
- Total packets: 10
- Data packet loss probability: 30%
- Maximum simulated data delay: 2 seconds
- Sender timeout: 6 seconds

## Requirements
Python 3. No third-party packages are required.

## Run
Open three terminals in this folder and start in this order:

1. `python receiver.py`
2. `python channel.py`
3. `python sender.py`

The channel accepts the sender on port 5001 and connects to the receiver on port 5002. All programs use `127.0.0.1`, so they run on one computer.

## Notes
TCP provides a reliable byte stream. Packet loss is simulated by the channel at the application level by discarding selected sequence-number messages. ACKs are forwarded without simulated loss. Newline delimiters separate messages because TCP does not preserve application message boundaries.

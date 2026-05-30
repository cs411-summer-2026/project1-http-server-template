# Project 1 — HTTP Server
# CS411 — Computer Networks — Summer 2026
#
# Team: <Lastname1-Lastname2>
#
# Instructions: see README.md
# Run:  python3 server.py
# Test: python3 test_server.py   (server must be running first)

import socket
import threading
import os
import mimetypes
from datetime import datetime

HOST = ''
PORT = 8080

# ── TODO: implement handle_client() ───────────────────────────
# This function receives one connection and must:
#   1. Read the raw request bytes
#   2. Parse the request line (method, path, version)
#   3. Serve the file from www/ with correct headers
#   4. Return 404 if the file does not exist
#   5. Return 405 if the method is not GET
#   6. Log the request to stdout

def handle_client(conn, addr):
    pass   # replace this


# ── Main server loop — do not modify below this line ──────────
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Server running on http://localhost:{PORT}')
    print('Press Ctrl+C to stop.\n')

    try:
        while True:
            conn, addr = sock.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        print('\nServer stopped.')
    finally:
        sock.close()


if __name__ == '__main__':
    main()

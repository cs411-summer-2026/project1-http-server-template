# Project 1 — Understanding HTTP Through a Minimal Server

**Course:** Computer Networks — Summer 2026  
**Layer:** Application Layer  
**Team size:** 2 students  
**Duration:** Monday → Thursday (4 sessions × 1.5h)  
**Language:** Python 3.8+  
**Demo:** Thursday, live, 8 minutes per team

---

## The problem

Every time you open a website, your browser sends a few lines of structured text over a TCP connection and waits for a response. That exchange is HTTP — and it is simpler than you think.

This week you will build a minimal HTTP server in Python using only the `socket` module. The goal is not to build a production web server. The goal is to **understand HTTP as a protocol**: what a request looks like, what a response must contain, what each status code means, and what all of it looks like at the byte level in Wireshark.

The website your server serves is entirely your choice. The protocol is not.

---

## What you will build

A minimal HTTP/1.1 server that:

- Accepts TCP connections from a real browser on **port 8080**
- Parses the incoming HTTP request line (method, path, version)
- Serves static files from a `www/` directory
- Sets the correct `Content-Type` header for each file type
- Returns the correct HTTP status codes: **200**, **404**, **405**
- Handles **2 concurrent clients** using threads
- Logs each request to stdout: `[timestamp] METHOD path → status`

---

## What you do NOT need to build

- Keep-alive connections
- POST body parsing
- HTTPS / TLS
- Cookies, sessions, authentication
- Any dynamic content beyond what you choose as your optional feature

---

## Key concepts

### HTTP is just text over TCP

Open a terminal and run:

```bash
python3 -c "
import socket
s = socket.socket()
s.connect(('example.com', 80))
s.send(b'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n')
print(s.recv(4096).decode())
"
```

You just made an HTTP request with 5 lines of Python. No library. HTTP is text.

---

### The HTTP request

This is exactly what a browser sends when you type a URL:

```
GET /index.html HTTP/1.1\r\n
Host: localhost:8080\r\n
Connection: close\r\n
Accept: text/html,*/*\r\n
\r\n
```

| Part | Example | What it means |
|------|---------|---------------|
| Method | `GET` | The action — what the client wants to do |
| Path | `/index.html` | Which resource to retrieve |
| Version | `HTTP/1.1` | The protocol version |
| Headers | `Host: localhost:8080` | Metadata about the request |
| Blank line | `\r\n` | Signals end of headers — always present |

> **Important:** HTTP uses `\r\n` (CRLF — carriage return + line feed) as the line separator, not just `\n`. If you use `\n` only, some browsers will not parse your response correctly.

---

### The HTTP response

This is what your server must build and send back:

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 512\r\n
Connection: close\r\n
\r\n
<html>...</html>
```

| Part | Example | What it means |
|------|---------|---------------|
| Status line | `HTTP/1.1 200 OK` | Protocol version + result code + reason phrase |
| `Content-Type` | `text/html` | What kind of data is in the body |
| `Content-Length` | `512` | Exact byte count of the body |
| Blank line | `\r\n` | End of headers — the body starts after this |
| Body | `<html>...` | The actual content (file bytes) |

> **Why does `Content-Length` matter?** The browser reads exactly that many bytes as the body. If you get it wrong — even by 1 — the browser either cuts the content short or hangs waiting for bytes that never come.

---

### HTTP status codes

Your server must return the right code for every situation:

| Code | Reason phrase | When to use it |
|------|--------------|----------------|
| `200` | `OK` | File found — everything worked |
| `404` | `Not Found` | The requested path does not exist in `www/` |
| `405` | `Method Not Allowed` | The method is anything other than `GET` |
| `500` | `Internal Server Error` | Your code threw an uncaught exception |

The code is not cosmetic. The browser uses it to decide what to do next. A 404 tells the browser "this page does not exist." A 200 tells it "here is your content, start rendering."

---

### MIME types and Content-Type

The `Content-Type` header tells the browser how to interpret the bytes it receives. Without it, the browser cannot know whether to render the bytes as HTML, display them as an image, or offer a download.

| File extension | Content-Type value |
|----------------|--------------------|
| `.html` | `text/html; charset=utf-8` |
| `.css` | `text/css` |
| `.js` | `application/javascript` |
| `.png` | `image/png` |
| `.jpg` / `.jpeg` | `image/jpeg` |
| `.ico` | `image/x-icon` |
| `.json` | `application/json` |

Use Python's built-in `mimetypes` module — it detects the type from the file extension automatically:

```python
import mimetypes
mime, _ = mimetypes.guess_type('index.html')   # → 'text/html'
mime, _ = mimetypes.guess_type('logo.png')     # → 'image/png'
```

---

### The TCP socket API

You will use these calls. Nothing else.

| Call | What it does |
|------|-------------|
| `socket.socket(AF_INET, SOCK_STREAM)` | Create a TCP socket |
| `sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)` | Reuse port after restart |
| `sock.bind(('', 8080))` | Bind to all interfaces, port 8080 |
| `sock.listen(5)` | Accept up to 5 queued connections |
| `sock.accept()` | Block until a client connects — returns `(conn, addr)` |
| `conn.recv(4096)` | Read up to 4096 bytes |
| `conn.sendall(data)` | Send bytes — retries until all are sent |
| `conn.close()` | Close the connection |

---

## Project constraints

### Hard constraints — these are not negotiable

- `socket` module only — **no** `http.server`, `Flask`, `FastAPI`, `Django`, `asyncio.start_server`
- No HTTP parsing libraries — **no** `httptools`, `h11`, `httpx`
- Must serve real files from `www/` — not hardcoded HTML strings in your code
- Must return correct status codes: 200, 404, 405
- Must handle 2 concurrent clients (threading)
- Wireshark capture during demo must be **live** — no pre-recorded `.pcap` files

### Your creative space

- The website content and purpose — entirely up to you
- Your 404 page design
- Your request log format
- One optional feature (see below)

---

## Optional feature — pick one

| Feature | Description |
|---------|-------------|
| **Directory listing** | If the path is a folder with no `index.html`, return an HTML page listing the files in it |
| **Query string** | `GET /search?q=hello` — parse the `?key=value` part and return something meaningful |
| **Request log file** | Write all requests to `server.log` with timestamps, persisted to disk |
| **Custom error pages** | A styled 404 page and a styled 500 page (not just `<h1>404</h1>`) |

---

## Repository structure

```
project1-http-server/
├── README.md           ← this file
├── server.py           ← your server (the file you write)
├── www/                ← your website files
│   ├── index.html      ← required
│   └── ...             ← any other files your site needs
└── test_server.py      ← automated tests (provided — do not modify)
```

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/<org>/cn2026-project1-<teamname>.git
cd cn2026-project1-<teamname>
python3 --version    # must be 3.8 or higher
```

### 2. Create your site

```bash
mkdir www
echo '<h1>Hello from my HTTP server</h1>' > www/index.html
```

### 3. Build the server — step by step

**Step 1 — Echo server (start here)**

Before writing any HTTP logic, just print what the browser sends. Create `server.py`:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 8080))
sock.listen(5)
print('Listening on http://localhost:8080')

while True:
    conn, addr = sock.accept()
    data = conn.recv(4096)
    print(data.decode())    # print the raw request — read every line
    conn.close()
```

Run it: `python3 server.py`

Open `http://localhost:8080` in your browser. You will see the full HTTP request printed in the terminal. **Read every line.** That is exactly what you will parse.

Open Wireshark → select **Loopback** interface → start capture → reload the browser → stop capture → filter `tcp.port == 8080`. Find the 3 packets before any HTTP data: `SYN`, `SYN-ACK`, `ACK`. That is the TCP handshake.

---

**Step 2 — Parse the request line**

```python
# data is bytes — decode to string first
request_text = data.decode('utf-8', errors='ignore')

# The first line is the request line
request_line = request_text.split('\r\n')[0]
method, path, version = request_line.split(' ')

# method = 'GET'    path = '/index.html'    version = 'HTTP/1.1'
```

> Why `split('\r\n')`? Because HTTP uses CRLF line endings. If you split on `'\n'` only, you get a stray `\r` at the end of each value, and your paths will never match.

---

**Step 3 — Serve a file**

```python
import os, mimetypes

# Map URL path to a file on disk
if path == '/':
    path = '/index.html'

file_path = 'www' + path    # e.g. www/index.html

if os.path.isfile(file_path):
    # Detect MIME type from file extension
    mime, _ = mimetypes.guess_type(file_path)
    if mime is None:
        mime = 'application/octet-stream'

    # Read in binary mode — works for ALL file types (images, HTML, CSS)
    with open(file_path, 'rb') as f:
        body = f.read()

    # Build the response — headers are text, body is bytes
    headers  = 'HTTP/1.1 200 OK\r\n'
    headers += f'Content-Type: {mime}\r\n'
    headers += f'Content-Length: {len(body)}\r\n'
    headers += 'Connection: close\r\n'
    headers += '\r\n'    # blank line — end of headers

    conn.sendall(headers.encode() + body)
```

> Always open files with `'rb'` (binary mode). HTML is text but images, fonts, and other assets are binary — text mode will corrupt them. The headers are always text: encode them with `.encode()` and concatenate with the binary body before sending.

---

**Step 4 — Handle errors**

```python
else:
    # 404 — file does not exist
    body = b'<h1>404 Not Found</h1>'
    headers  = 'HTTP/1.1 404 Not Found\r\n'
    headers += 'Content-Type: text/html\r\n'
    headers += f'Content-Length: {len(body)}\r\n'
    headers += 'Connection: close\r\n\r\n'
    conn.sendall(headers.encode() + body)

# Check the method before serving — do this before the file logic
if method != 'GET':
    conn.sendall(b'HTTP/1.1 405 Method Not Allowed\r\nContent-Length: 0\r\n\r\n')
    conn.close()
    return
```

---

**Step 5 — Add threading for concurrent clients**

```python
import threading

def handle_client(conn, addr):
    try:
        data = conn.recv(4096)
        if not data:
            return
        # ... your parsing and response code from steps 2-4 ...
    except Exception as e:
        print(f'[ERROR] {addr}: {e}')
        try:
            conn.sendall(b'HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\n\r\n')
        except:
            pass
    finally:
        conn.close()    # always close the connection

# Main loop
while True:
    conn, addr = sock.accept()
    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.daemon = True
    t.start()
```

Test concurrency — open two terminals and run both at the same time:

```bash
curl http://localhost:8080/ &
curl http://localhost:8080/style.css &
```

Both should receive a response. In Wireshark, you will see two TCP connections open simultaneously.

---

## Useful commands

```bash
# Run your server
python3 server.py

# Stop it
Ctrl + C

# Test with curl (verbose — shows all headers)
curl -v http://localhost:8080/
curl -v http://localhost:8080/index.html

# Test a 404
curl -v http://localhost:8080/doesnotexist.html

# Test 405 (POST method)
curl -v -X POST http://localhost:8080/

# Check what is listening on port 8080
ss -tlnp | grep 8080

# Kill a process holding port 8080
lsof -i :8080
kill -9 <PID>
```

---

## Wireshark guide

### Setup

1. Open Wireshark
2. Select the **Loopback** interface — `lo` on Linux, `Loopback` on macOS
   *(not Wi-Fi or Ethernet — your browser and server are on the same machine)*
3. Start capture
4. Open `http://localhost:8080` in your browser
5. Stop capture
6. Filter: `tcp.port == 8080` → Enter

### What to find and explain

| What | How to find it | What to say |
|------|---------------|-------------|
| **3-way handshake** | First 3 packets: `[SYN]` → `[SYN, ACK]` → `[ACK]` | "TCP sets up the connection before any HTTP is exchanged" |
| **Your GET request** | Packet with `GET` in the Info column | "This is the browser asking for the file — method, path, HTTP version" |
| **Your 200 response** | Packet with `HTTP/1.1 200` in Info | "Our server responds with the status line, then headers, then the file" |
| **Content-Type in headers** | Click response packet → expand `Hypertext Transfer Protocol` | "This tells the browser it's HTML so it knows to render it" |
| **Response body** | Same expansion → `Line-based text data` | "These are the actual bytes of our index.html" |
| **Full conversation** | Right-click any packet → **Follow → TCP Stream** | "Here you can read the full exchange as text" |
| **Connection teardown** | Last packets: `[FIN, ACK]` → `[FIN, ACK]` | "Both sides say goodbye — TCP is closed" |

### Checkpoint questions

Your instructor will ask these during build days. Be ready:

- "Show me the Content-Length value in Wireshark. Is it correct?"
- "What happens in Wireshark when you request a file that doesn't exist?"
- "Open Follow TCP Stream — find the blank line between headers and body"
- "You have two browser tabs open — how many TCP connections do you see?"

---

## Running the automated tests

```bash
# Terminal 1 — start your server
python3 server.py

# Terminal 2 — run the tests
python3 test_server.py
```

The tests verify:

- `GET /` returns `200` with a `text/html` Content-Type
- `GET /doesnotexist` returns `404`
- `POST /` returns `405`
- Response includes `Content-Length` header with the correct value
- Response uses `\r\n` line endings, not `\n`
- `Content-Length` value matches the actual body byte count

All tests must pass before Thursday.

---

## Common mistakes

**Using `\n` instead of `\r\n`**  
HTTP requires CRLF. Using only `\n` causes browsers to misparse your response. Always write `\r\n` in every header line and in the blank line between headers and body.

**Wrong Content-Length**  
`len(body)` where `body` is already `bytes`. Do not call `len()` on a string — the byte count may differ if non-ASCII characters are present.

**Opening files in text mode**  
Always `open(file_path, 'rb')`. Text mode (`'r'`) corrupts images and other binary files.

**`recv()` returns empty bytes**  
The client disconnected before sending. Guard against it:
```python
data = conn.recv(4096)
if not data:
    conn.close()
    return
```

**Port already in use**  
```bash
lsof -i :8080    # find the PID
kill -9 <PID>    # kill it
```
Or change the port number in your code to `8081`.

**Server crashes on unexpected input**  
Browsers send keep-alive probes. Wireshark may send test packets. Always wrap your handler in `try/except` and close the connection in `finally`.

---

## Thursday demo checklist

Run through this before standing up to present:

- [ ] `python3 server.py` starts cleanly and prints the listening message
- [ ] Browser loads your site at `http://localhost:8080`
- [ ] At least 2 file types served correctly: HTML + one of (CSS / image / JS)
- [ ] `curl -v http://localhost:8080/missing` returns 404
- [ ] `curl -v -X POST http://localhost:8080/` returns 405
- [ ] Two concurrent `curl` requests both succeed
- [ ] All automated tests pass: `python3 test_server.py`
- [ ] Wireshark filter `tcp.port == 8080` is ready
- [ ] You can point to the 3-way handshake in Wireshark
- [ ] You can point to your `Content-Type` and `Content-Length` headers
- [ ] Optional feature works and you know how to demo it

---

## Demo structure (8 minutes)

| Time | What happens |
|------|-------------|
| 0:00 – 1:00 | Start server, open browser, show the site |
| 1:00 – 3:30 | Walk through Wireshark: handshake → GET → 200 response → headers → body → FIN |
| 3:30 – 4:30 | Trigger 404 live — find it in Wireshark |
| 4:30 – 5:30 | Trigger 405 — show the response |
| 5:30 – 6:30 | Demo optional feature |
| 6:30 – 8:00 | Peer Q&A — 2 questions from the other team |

The instructor will send one request using `netcat` with a malformed or unexpected message. Your server must not crash.

---

## Grading

| Criterion | Weight |
|-----------|--------|
| Server works: correct status codes, headers, file serving | 30% |
| HTTP protocol correctness: CRLF, Content-Length, Content-Type | 25% |
| Wireshark narration: can explain every packet shown | 25% |
| Optional feature working with live proof | 10% |
| Code robustness: handles errors, does not crash | 10% |

---

*Computer Networks — Summer 2026*

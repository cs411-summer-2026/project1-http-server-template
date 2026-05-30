"""
test_server.py — Automated tests for Project 1
Run with:  python3 test_server.py
Your server must be running on port 8080 before running these tests.
"""

import http.client
import sys

HOST = 'localhost'
PORT = 8080
PASS = 0
FAIL = 0


def check(name, condition, detail=''):
    global PASS, FAIL
    if condition:
        print(f'  \033[32mPASS\033[0m  {name}')
        PASS += 1
    else:
        print(f'  \033[31mFAIL\033[0m  {name}' + (f' — {detail}' if detail else ''))
        FAIL += 1


def get(path):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    conn.request('GET', path)
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    return resp, body


def method(verb, path):
    conn = http.client.HTTPConnection(HOST, PORT, timeout=5)
    conn.request(verb, path)
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    return resp, body


print(f'\nRunning tests against http://{HOST}:{PORT}\n')

# ── Test 1: GET / returns 200 ──────────────────────────────────
print('1. GET / → 200 OK')
try:
    resp, body = get('/')
    check('Status code is 200', resp.status == 200, f'got {resp.status}')
    check('Content-Type is text/html', 'text/html' in (resp.getheader('Content-Type') or ''),
          f'got {resp.getheader("Content-Type")}')
    check('Body is not empty', len(body) > 0)
    cl = resp.getheader('Content-Length')
    check('Content-Length header is present', cl is not None, 'header missing')
    if cl:
        check('Content-Length matches body length', int(cl) == len(body),
              f'header says {cl}, body is {len(body)} bytes')
except Exception as e:
    print(f'  \033[31mERROR\033[0m  Could not connect — is your server running? ({e})')
    sys.exit(1)

# ── Test 2: GET missing file → 404 ────────────────────────────
print('\n2. GET /this-file-does-not-exist.html → 404')
try:
    resp, body = get('/this-file-does-not-exist.html')
    check('Status code is 404', resp.status == 404, f'got {resp.status}')
    check('Body is not empty (custom 404 page)', len(body) > 0)
except Exception as e:
    check('Request completed', False, str(e))

# ── Test 3: POST / → 405 ──────────────────────────────────────
print('\n3. POST / → 405 Method Not Allowed')
try:
    resp, body = method('POST', '/')
    check('Status code is 405', resp.status == 405, f'got {resp.status}')
except Exception as e:
    check('Request completed', False, str(e))

# ── Test 4: Content-Length is correct ─────────────────────────
print('\n4. Content-Length accuracy')
try:
    resp, body = get('/')
    cl = resp.getheader('Content-Length')
    check('Content-Length header present', cl is not None)
    if cl:
        check('Content-Length matches actual body', int(cl) == len(body),
              f'declared {cl} bytes but received {len(body)} bytes')
except Exception as e:
    check('Request completed', False, str(e))

# ── Test 5: Concurrent clients ────────────────────────────────
print('\n5. Concurrent clients')
import threading

results = []

def worker(path):
    try:
        resp, body = get(path)
        results.append(resp.status)
    except Exception as e:
        results.append(str(e))

t1 = threading.Thread(target=worker, args=('/index.html',))
t2 = threading.Thread(target=worker, args=('/index.html',))
t1.start(); t2.start()
t1.join(); t2.join()

check('Both concurrent requests completed', len(results) == 2)
check('Both returned 200', all(r == 200 for r in results), f'got {results}')

# ── Summary ───────────────────────────────────────────────────
total = PASS + FAIL
print(f'\n{"─" * 40}')
print(f'Results: {PASS}/{total} passed', end='  ')
if FAIL == 0:
    print('\033[32m✓ All tests pass\033[0m')
else:
    print(f'\033[31m✗ {FAIL} test(s) failed\033[0m')
print()

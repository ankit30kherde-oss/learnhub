"""
Real terminal-practice server (TESTING SCOPE — see README warnings).

For every browser WebSocket connection:
  1. Start a fresh, ephemeral 'learnhub-sandbox' container via the
     host's Docker daemon (mounted in via /var/run/docker.sock).
  2. Open a real interactive `docker exec bash` session inside it.
  3. Pipe raw bytes both ways between the browser and that shell.
  4. On disconnect (or after an idle timeout), kill + remove the container.

This is intentionally simple (no queueing or multi-instance scaling)
because it's for local testing only. The WebSocket now requires a short-lived
HMAC token from an authenticated/enrolled lesson page. See README "Before this
goes anywhere near real users" section for the hardening checklist.
"""
import asyncio
import hashlib
import hmac
import json
import os
import threading
import time
import uuid

import docker
import websockets

client = docker.from_env()

SANDBOX_IMAGE = "learnhub-sandbox"
IDLE_TIMEOUT_SECONDS = 15 * 60  # auto-kill an abandoned container after 15 min
MEM_LIMIT = "256m"
CPU_QUOTA_NANO = int(0.5 * 1e9)  # ~0.5 CPU core
SHARED_SECRET = os.environ.get("SECRET_KEY", "")


def valid_token(token):
    if not SHARED_SECRET or not token or "." not in token:
        return False
    payload, signature = token.rsplit(".", 1)
    expected = hmac.new(
        SHARED_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return False
    parts = payload.split(":")
    if len(parts) != 3:
        return False
    try:
        expires = int(parts[2])
    except ValueError:
        return False
    return expires >= int(time.time())


async def handler(websocket):
    print(f"[WS] connection received from {websocket.remote_address}", flush=True)
    # Authentication happens before a Docker container is created. The web
    # application only renders a short-lived token to enrolled learners.
    try:
        auth_message = await asyncio.wait_for(websocket.recv(), timeout=10)
        if not isinstance(auth_message, str):
            await websocket.close(code=1008, reason="authentication required")
            return
        payload = json.loads(auth_message)
        if payload.get("type") != "auth" or not valid_token(payload.get("token", "")):
            await websocket.close(code=1008, reason="invalid or expired token")
            return
    except (asyncio.TimeoutError, json.JSONDecodeError, websockets.exceptions.ConnectionClosed):
        try:
            await websocket.close(code=1008, reason="authentication required")
        except Exception:
            pass
        return

    container = client.containers.run(
        SANDBOX_IMAGE,
        command="sleep infinity",
        detach=True,
        tty=True,
        mem_limit=MEM_LIMIT,
        nano_cpus=CPU_QUOTA_NANO,
        name=f"lab-{uuid.uuid4().hex[:10]}",
        remove=True,
    )
    print(f"[+] started sandbox container {container.name}")

    exec_id = client.api.exec_create(
        container.id, "bash", stdin=True, tty=True,
    )["Id"]
    sock = client.api.exec_start(exec_id, socket=True, tty=True)
    raw_sock = sock._sock if hasattr(sock, "_sock") else sock

    loop = asyncio.get_event_loop()
    closed = threading.Event()
    last_activity = time.monotonic()

    def reader_thread():
        while not closed.is_set():
            try:
                data = raw_sock.recv(4096)
            except OSError:
                break
            if not data:
                break
            try:
                asyncio.run_coroutine_threadsafe(websocket.send(data), loop)
            except RuntimeError:
                break
        closed.set()

    t = threading.Thread(target=reader_thread, daemon=True)
    t.start()

    async def idle_watchdog():
        while not closed.is_set():
            await asyncio.sleep(30)
            if time.monotonic() - last_activity > IDLE_TIMEOUT_SECONDS:
                print(f"[!] {container.name} idle too long, closing")
                await websocket.close()
                break

    watchdog_task = asyncio.create_task(idle_watchdog())

    try:
        async for message in websocket:
            last_activity = time.monotonic()
            if isinstance(message, str):
                try:
                    payload = json.loads(message)
                    if payload.get("type") == "resize":
                        client.api.exec_resize(
                            exec_id,
                            height=payload["rows"],
                            width=payload["cols"],
                        )
                        continue
                except (json.JSONDecodeError, KeyError):
                    pass
                raw_sock.send(message.encode())
            else:
                raw_sock.send(message)
    finally:
        closed.set()
        watchdog_task.cancel()
        try:
            raw_sock.close()
        except OSError:
            pass
        try:
            container.stop(timeout=1)
            print(f"[-] stopped sandbox container {container.name}")
        except docker.errors.NotFound:
            pass


async def main():
    print("Terminal server listening on ws://0.0.0.0:8765", flush=True)
    async with websockets.serve(handler, "0.0.0.0", 8765, max_size=None):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

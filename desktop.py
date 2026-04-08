from __future__ import annotations

import sys
import threading
import time
import urllib.request

from app import build_local_url, create_server, find_available_port


APP_TITLE = "VantaVault"
WINDOW_WIDTH = 1460
WINDOW_HEIGHT = 940
WINDOW_MIN_WIDTH = 980
WINDOW_MIN_HEIGHT = 720


def wait_until_server_ready(url: str, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{url}/api/status", timeout=0.5):
                return
        except Exception:
            time.sleep(0.15)
    raise RuntimeError("Не удалось запустить локальный сервер VantaVault.")


def run_browser_fallback(url: str) -> None:
    import webbrowser

    webbrowser.open(url)


def main() -> None:
    host = "127.0.0.1"
    port = find_available_port(host)
    server = create_server(host, port)
    url = build_local_url(host, port)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    wait_until_server_ready(url)

    try:
        import webview
    except ModuleNotFoundError:
        run_browser_fallback(url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
            server.server_close()
        return

    window = webview.create_window(
        APP_TITLE,
        url,
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT),
        background_color="#080808",
        text_select=True,
    )

    def handle_close() -> None:
        server.shutdown()
        server.server_close()

    window.events.closed += handle_close

    try:
        webview.start(debug=False)
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"VantaVault failed: {exc}", file=sys.stderr)
        raise
